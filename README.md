roles-bot
=========

A simple discord bot that allows you to create rules.  
When a user has all the required roles in a rule, an extra role can be assigned.  
This allows combining integration perks into an even bigger bonus.  
bot interactions require server administrator permissions for all actions.

[See the Demo](demo.mp4)

# Setup
## Creating application
- Go to the [Discord developer portal](https://discord.com/developers/applications).
- Login
- Click `New Application`
- Name the Application
- Click the `Add Bot` button
- Name your bot in the dialog
- Click `Reveal token` and make a note while we're here
- Enable `SERVER MEMBERS INTENT` to allow the bot to read users on a server
- Click the `Oauth` Tab
- Check the `bot` Scope
- underneath, in `BOT PERMISSIONS` check `manage roles`
- Now copy the URL from the scopes window
- Paste the URL into a web browser and hit Enter
- Select the Server you wish to add the bot to
- Success! the bot is created and added to the server
- Now this application can interact with your server

## roles-bot client
This code forms the `client` of the bot, that actually drives the interactions in your server.  
Download the latest [release](https://github.com/ashnasbot/roles-bot/releases) or clone the repository.

## Config
With a created bot, create a `.env` file next to the application add the bot `TOKEN` to the `.env` file as `BOT_TOKEN`.  
See [the example .env file](.env).  
run the application to start.  
```
.\roles-bot.exe
```
or
```bash
pip3 install -r requirements.txt
python3 __main__.py
```

# Commands/Rules
Once connected to a sever, a member with the `Administrator` Role can use the following commands to configure rules.  
All bot commands start with $rb, implemented commands are as follows:  
```
  $rbhelp  Shows help message
  $rbadd @role1 @role2 @role3  If user has role1 and role2, assign the third roles (can be used with multiple roles)
  $rbdel <id>  Remove a rule
  $rblist  List the current rules in this guild.
```
use `$rbadd` to add roles to a guild - commands must be run in the server you wish to modify rules for.  
The last argument to `$rbadd` is the role to assign, a user must have all other roles in order to be granted the final role.  
Multiple rules can share the same assigned role, if a user meets any of the requirements they will gain the role.  
(hint: create a new channel to interact with the bot in private)

# Privacy
This bot accesses Member information such as usernames and assigned roles, this is privlidged information and should be handled with care.  
This information is used only to assign bots but will be stored in the logs.  
Only the Rules and thus role-names are stored in this applications database.  
Be careful who you give access to the bot logs.  

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
- [x] bundled app (exe)
- [x] privacy statement
- [ ] Configurable log level
- [ ] Log to file
