"""roles-bot - create role combinations to grant new roles."""
from collections import defaultdict, Counter
import logging
import os

from dotenv import load_dotenv
import discord
from discord.ext import commands
from tinydb import TinyDB, Query

logging.basicConfig(encoding='utf-8', level=logging.INFO)
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='$rb', intents=intents)

db = TinyDB('db.json')

# This holds our rules
# {
#    <target rule>: [
#        [ <required rule> <required rule>],
#        [ <alt required rule> <alt required rule>]
#    ]
# }
RULES = defaultdict(dict)

# EVENTS

@bot.event
async def on_ready():
    """Connected - check existing rules."""
    logging.info(f'{bot.user} has connected to Discord!')
    for guild in bot.guilds:
        await update_roles(guild)
        await check_guild_rules(guild)


@bot.event
async def on_member_update(before, after):
    """Member updated - check if roles have changed and update."""
    if Counter(before.roles) == Counter(after.roles):
        return
    await check_member_rules(after)


@bot.event
async def on_guild_role_update(before, after):
    """Role updated - check if role names have changed."""
    if before.name != after.name:
        logging.info("role %s on %d updated to %s", before.name, before.guild.id, after.name)
        Rules = Query()
        # Check targets
        db.update({'target': after.name}, (Rules.guild == before.guild.id) & (Rules.target == before.name))
        # Check requireds
        res = db.search((Rules.guild == after.guild.id) & (Rules.roles.any([before.name])))
        for r in res:
            row = list(r["roles"])
            row.remove(before.name)
            row.append(after.name)
            db.update({'roles': row}, doc_ids=[r.doc_id])


@bot.event
async def on_guild_role_delete(role):
    """Role removed - remove references."""

    if role.guild.id not in RULES:
        return

    for target, rolesets in RULES[role.guild.id].items():
        if role == target:
            del RULES[role.guild.id][target]
            continue
        for i, roles in enumerate(rolesets):
            if role in roles:
                RULES[role.guild.id][target][i].remove(role)


@bot.event
async def on_guild_remove(guild):
    """Left a server - cleanup roles."""
    logging.info("Left guild %d", guild.id)
    await remove_roles(guild)

# FUNCTIONS

async def update_roles(guild):
    """Check current rules against roles in server, update RULES."""
    Rules = Query()
    res = db.search(Rules.guild == guild.id)
    if not res:
        if guild.id in RULES:
            del RULES[guild.id]
        return
    
    for rule in res:
        target = discord.utils.get(guild.roles, name=rule["target"])
        if not target:
            logging.warning("Rule %d target `%s` not found in guild %d", rule.doc_id, rule["target"], guild.id)
            continue
        roles = []
        for r in rule["roles"]:
            role = discord.utils.get(guild.roles, name=r)
            if role is None:
                logging.warning("Rule %d target `%s` not found in guild %d", rule.doc_id, rule["target"], guild.id)
                continue
            roles.append(role)
        if target in RULES[guild.id]:
            RULES[guild.id][target].append(roles)
        else:
            RULES[guild.id][target] = [roles]


async def remove_roles(guild):
    """Remove all roles for this guild."""
    Rules = Query()
    db.remove(Rules.guild == guild.id)
    del RULES[guild.id]


async def check_guild_rules(guild):
    """Check all RULES in guild and assign member roles."""
    logging.debug("Checking roles for %s", guild.name)
    member_roles = {}
    allowed_roles = defaultdict(list)
    if not RULES[guild.id]:
        return

    # Get the roles a member *should* have
    for target, rolesets in RULES[guild.id].items():
        for roles in rolesets:
            if not roles:
                continue
            for member in guild.members:
                if all(bool(role in member.roles) for role in roles):
                    allowed_roles[member.name].append(target)

    # Remove roles we no longer have, and add new roles
    for member in guild.members:
        member_roles[member.name] = [r for r in RULES[guild.id] if r in member.roles] 
        disallowed_roles = [r for r in member_roles[member.name] if r not in allowed_roles[member.name]] 
        new_roles = [r for r in allowed_roles[member.name] if r not in member_roles[member.name]] 
        for role in disallowed_roles:
            logging.info(f"{member.name} lost role {role.name} in guild {guild.id}")
            await member.remove_roles(role)
        for role in new_roles:
            logging.info(f"{member.name} gained role {role.name} in guild {guild.id}")
            await member.add_roles(role)

async def check_member_rules(member):
    """Check all rules against current Member of guild."""
    guild = member.guild
    logging.debug("Checking member roles for member %s of guild %d", member.name, guild.id)
    allowed_roles = []

    if not RULES[guild.id]:
        logging.debug("No roles for member %s of guild %d", member.name, guild.id)
        return

    # Get the roles we care about
    for target, rolesets in RULES[guild.id].items():
        for roles in rolesets:
            if not roles:
                continue
            if all(bool(role in member.roles) for role in roles):
                allowed_roles.append(target)

    # Remove roles we no longer have, and add new roles
    member_roles = [r for r in RULES[guild.id] if r in member.roles] 
    disallowed_roles = [r for r in member_roles if r not in allowed_roles] 
    new_roles = [r for r in allowed_roles if r not in member_roles] 
    for role in disallowed_roles:
        logging.info(f"{member.name} lost role {role.name} in guild {guild.id}")
        await member.remove_roles(role)
    for role in new_roles:
        logging.info(f"{member.name} gained role {role.name} in guild {guild.id}")
        await member.add_roles(role)

# COMMANDS

@bot.command()
@commands.has_permissions(administrator=True)
async def add(ctx, *args: commands.clean_content):
    """Add a rule to the current guild.

    Parameters
    ----------
    *req : role-name
        The name or @ of a requsite role, can be provided multiple times to add several roles.
    target : role-name
        The name or @ of a of the target role, users with all the requsites will game the target role.
    """
    if len(args) < 2:
        await ctx.send('Add takes 2+ parameters')
        return

    tgt_role = args[-1]
    if tgt_role.startswith('@'):
        tgt_role = tgt_role[1:]
        if not discord.utils.get(ctx.guild.roles, name=tgt_role):
            await ctx.send(f'Role {args[-1]} does not exist')
            return

    roles = list(args[:-1])

    for index, role in enumerate(roles):
        if role.startswith('@'):
            role = role[1:]
            roles[index] = role
        print(role)
        if not discord.utils.get(ctx.guild.roles, name=role):
            await ctx.send(f'Role {role} does not exist')
            return

    docid = db.insert({'guild': ctx.guild.id, 'roles': roles, 'target': tgt_role})
    await ctx.send(f'Rule {docid} created')
    await update_roles(ctx.guild)
    await check_guild_rules(ctx.guild)


@bot.command(name='del')
@commands.has_permissions(administrator=True)
async def command_del(ctx, *args):
    """Remove a rule by it's ID.

    Parameters
    ----------
    id : integer
        The rule if of the rule to remove (see `list`)
    """
    if len(args) != 1:
        await ctx.send('Del takes 1 parameter: id')
        return

    try:
        docid = int(args[0])
    except:
        await ctx.send(f'Rem expects a number: id')
        return

    if not db.contains(doc_id=docid):
        await ctx.send(f'No rule with id {docid}')
        return

    db.remove(doc_ids=[docid])
    await ctx.send(f'Removed rule {docid}')
    await update_roles(ctx.guild)


@bot.command(name='list')
@commands.has_permissions(administrator=True)
async def command_list(ctx, *args):
    """List the current rules added to the guild by id."""
    Rules = Query()
    res = db.search(Rules.guild == ctx.guild.id)
    if res:
        lines = []
        for doc in res:
            target = discord.utils.get(ctx.guild.roles, name=doc["target"])
            target_name = f'{target.mention}' if target else f'@rule["target"]'
            processed_roles = []
            for r in doc["roles"]:
                role = discord.utils.get(ctx.guild.roles, name=r)
                role_name = f'{role.mention}' if role else f'@rule["target"]'
                processed_roles.append(role_name)

            lines.append(f'{doc.doc_id}: {" + ".join(processed_roles)}  = {target_name}')
        msg = " - " + "\n - ".join(lines)
        await ctx.send(f'Current rules:\n{msg}')
    else:
        await ctx.send(f'No rules defined')

if __name__ == "__main__":
    bot.run(TOKEN)
