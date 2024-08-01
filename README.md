# Python Adventures

https://github.com/user-attachments/assets/8f392225-6d21-464f-9e55-bc74ca643df3

*🔈Volume on*

Python Adventures is a Discord game bot where you learn about Python features while progressing your character through a map filled with challenges and secrets!

## Theme: Information Overload
Python Adventures immerses players in a learning environment filled with information-rich levels. Each level combines multiple-choice questions and intricate coding challenges, demanding players process and apply vast amounts of information quickly and accurately. The special code golfing levels take this to the next level by requiring players to deal with dense, compact code — all while keeping it light and playful.

# Gameplay

Follow the main character Maria as she sets out on an epic journey to becoming a true Pythonista! The main storyline of the game consists of 11 levels, where completing one unlocks the next.

## Map

![Map](presentation/levels.png)

The levels 1-11 consist of both multiple-choice questions and code writing challenges, to make learning exciting and really challenge your unstanding of the topics at hand.

There are also three *special* levels A, B and C, outside of the main storyline, which tackle code golfing. If your brain doesn't get overloaded from the compact information in oneliners and hacky ways of writing code, these levels perfect for you!

### Navigation
![Map navigation](/presentation/map-navigation.png)

To move between levels in Python Adventures, we have created a vibrant map that can be easily navigated using Discord's interaction buttons. The map is dynamically generated for the user, taking into account factors such as the following:
- **Unlocked levels**, including special levels
- **Completed levels**
- **Current player position**, persisted between sessions
- **Player display name**, for the name tag

In order to not clutter up the chat, navigation simply edits the original interaction response embed with the new map state. Buttons are also dynamically enabled/disabled based on whether or not an action can be taken. For example, if a tree is in the way, moving that direction will be disabled.

## Levels
### Limited lives
![Lives](bot/assets/guide-hearts.png)

With three lives comes a maximum of three mistakes before you have to restart the level. This keeps the game exciting and turns the difficulty of even the multiple choice questions up a notch.

### Code evaluation
The most important part of learning to code is writing code and actually trying things yourself. Because of this, we have made code writing an integral part of the levels, providing a Code Playground to test run your code before submitting. And once submitted, we run a battery of unit tests on the code to ensure it passes the requirements.

By utilizing the [Tio.run](https://tio.run) API to evaluate code, we are able to evaluate and test user code without needing to set up a sandboxed environment and without risking malicious input causing issues for the machine running the bot.

### Hints
Sometimes you get stuck on a problem. While revealing the answer straight away won't help you much in learning, getting a hint or two in the right direction can be a game changer. We have provided hints for all questions that can be accessed one at a time by pressing the **Hint** button:

![Hints](presentation/hints.png)

### Success/defeat/win screens
![Status screens](presentation/level-statuses.png)

With vibrant success/fail messages depending on how a level went for the player, we hope to keep the player engaged and excited to move toward the next goal. The images above are some of these and are displayed in the following situations:
- **Level failed**: the user fails a level
- **Level success**: the user completes a level
- **New level unlocked**: displayed after "level success" when the B or C level is unlocked
- **You win**: displayed when completing the final level of the game (level C) together with a message from the developers :)

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
