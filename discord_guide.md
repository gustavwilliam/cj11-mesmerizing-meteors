# Discord Developers Guide


## How to set up your own bot to run the project

1. Log in to **[Discord Developer Portal](https://discord.com/developers/)**
2. Create your new project with the ``New Application`` button.
3. After creating your project, make the necessary settings in the ``Settings>OAuth2`` tab.
   - Select the ``bot`` option from the OAuth2 URL Generator section
   - After clicking on the ``bot``, you can choose the permissions your bot will have from the window that opens.

      **Recommended settings:**
      ````
      Bot > General Permissions
         - Manage Expressions
         - Create Expressions
         - View Channels
         - View Server Insights

      Bot > Text Permissions
         - Send Messages
         - Manage Messages
         - Embed Links
         - Attach Files
         - Use External Emojşs
         - Use External Stickers
         - Add Reactions
         - Use Slash Commands
         - Use Embeded activites
         - Create Polls
      ````
   - Depending on the options you set, you can add your bot to your server from the ``GENERATED URL`` section created below.
   - Make sure you give your bot enough room to play.