# Discord Developers Guide


## How to set up your own bot to run the project

1. Log in to **[Discord Developer Portal](https://discord.com/developers/)**
2. Create your new project with the ``New Application`` button.
3. Activate the ``PRESENCE INTENT``, ``SERVER MEMBERS INTENT``, ``MESSAGE CONTENT INTENT`` in the ``Bot > Privileged Gateway Intents`` section.
4. After creating your project, make the necessary settings in the ``Settings > OAuth2`` tab.
   - Select the ``bot`` option from the OAuth2 URL Generator section
   - Below, select the permissions you wish for the bot to have in the server. We recommend `Administrator` for testing purposes
5. After clicking on the ``bot``, you can choose the permissions your bot will have from the window that opens.

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
         - Use External Emojis
         - Use External Stickers
         - Add Reactions
         - Use Slash Commands
         - Use Embeded activites
         - Create Polls
      ````
   - Depending on the options you set, you can add your bot to your server by opening the ``GENERATED URL`` in your browser, authenticating with discord, and adding it to a server of your choosing.
   - Make sure you give your bot enough room to play.
