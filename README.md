roles-bot
=========

A simple discord bot that allows you to create rules.
When a user has all the required roles in a rule, an extra role can be assigned.
This allows combining integration perks into an even bigger bonus.

[See the Demo](demo.mp4)

# Setup
Create an application on the [Discord developer portal](https://discord.com/developers/applications).
roles-bot needs `bot` oauth scope, adn the `Server Members` privlidged intent in order to view and assign user roles.
Create the oauth token and follow it to add the bot to a server.

# Privacy
This bot accesses Member information such as usernames and assigned roles, this is privlidged information and should be handled with care.
This information is used only to assign bots but will be stored in the logs.
Only the Rules and thus role-names are stored in this applications database.
Be careful who you give access to the bot logs.

# Config
With a created bot, add the bot `TOKEN` to the `.env` file as `BOT_TOKEN`
run the python file to start.
```bash
python3 __main__.py
```

# Commands/Rules
Once connected to a sever, a member with the `Administrator` Role can use the following commands to configure rules.
All bot commands start with $rb, implemented commands are as follows.
```
  $rbhelp  Shows help message
  $rbadd @role1 @role2 @role3  If user has role1 and role2, assign the third roles (can be used with multiple roles)
  $rbdel <id>  Remove a rule
  $rblist  List the current rules in this guild.
```

# Issues/Notes
- Reconnection logic hasn't been robustly tested
- If roles change name while bot is disconnected rules will fail
- If roles are remove they will be removed from active rules

# TODO
- [x] respond to commands
- [x] List current role combos
- [x] Add role combo
- [x] Del role combo
- [x] Rename role
    - [x] target
    - [x] required role
- [x] remove target on del rule
- [x] Handle leaving server
- [x] Handle deleted role
- [x] help text
- [x] full command help
- [x] scan on join
- [x] reconnect logic
- [x] readme
- [x] gitlab
- [x] bot/moderator permission for commands
- [ ] Configurable log level
- [ ] Log to file
- [ ] bundled app (exe)
- [ ] privacy statement