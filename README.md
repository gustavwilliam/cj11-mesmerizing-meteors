# Python Adventures

![Title art](bot/assets/title-art.png)

Python Adventures is a discord game bot where you learn about Python features while progressing your character through a map.

# Setup instructions
## Discord API Token
What is a Discord API Token?
A Discord API Token is a unique identifier used to authenticate requests to the Discord API. It acts as a password for your bot, allowing it to interact with Discord's servers, join channels, send messages, and perform other actions as defined by the Discord API.

## How to Obtain a Discord API Token
1. Create a New Application:
  - Go to the [***Discord Developer Portal***](https://discord.com/developers/applications)
  -  Click on ***New Application***
  -   Give your application a name and click **Create**.

2. Create a Bot:
  - Navigate to the ***Bot*** section in the sidebar.
  -  Click on "Add Bot" and confirm by clicking ***Yes, do it!***

3. Copy the Token:
   - Under the "TOKEN" section, click "Copy" to copy your bot's token.
   - Keep this token secure and never share it publicly. If your token is exposed, you should regenerate it immediately.

## Discord Developer Portal Settings

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


## Installation and Setup
To get your Discord bot up and running, follow these steps:
1. **Clone the repository**: `git clone https://github.com/gustavwilliam/cj11-mesmerizing-meteors.git && cd cj11-mesmerizing-meteors`

2. **Install Requirements**:
   > - You can create a virtual environment by `python -m venv .venv`
   > - Activate it by `source .venv/bin/activate` then pursue the setup

Install the dependencies using `pip install -r requirements.txt`. If you are developing the bot and not just running it, also consider installing dev requirements: `pip install -r dev-requirements.txt`.

3. **Set Up Your Environment Variables**:
   - Create a .env file in the root of your project and add your Discord API Token: `DISCORD_BOT_KEY="your-discord-token-here"`

4. **Update Emoji Config**:
   - Under `bot/assets/icons` you will find all the required emojis for the bot
   - Add all these emojis to a server that your bot will be invited to
   - Copy the ID of every emoji (send the custom emoji in a Discord channel and add `\` before it to see the ID. It will look something like this: `<:arrowright:1265077270515552339>`
   - Update the IDs of every emoji in `bot/config.py`

5. **Run the Bot**: `python bot/main.py`
