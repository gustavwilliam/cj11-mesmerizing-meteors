# Python Adventures

![Alt title](bot/assets/title-art.png)

Python Adventures is a discord game bot where you learn about Python features while progressing your character through a map.

# Installation
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

For more information, Consult The [Discord Developer Portal](https://discord.com/developers/docs/intro) Documentation.

## Installation and Setup
To get your Discord bot up and running, follow these steps:
1. **Clone the repository**: `git clone github.com/gustavwilliam/cj11-mesmerizing-meteors && cd cj11-mesmerizing-meteors`

2. **Install Requirements**:
   > - You can create a virtual environment by `python -m venv .venv`
   > - Activate it by `.venv/bin/activate` then pursue the setup

Ensure you have `python` installed then install dependencies by `pip install -r requirements.txt`

3. **Set Up Your Environment Variables**:
   - Create a .env file in the root of your project and add your Discord API Token: `DISCORD_BOT_KEY="your-discord-token-here"`

4. **Run the Bot**: `python bot/main.py`

# Conclusion
This project has successfully created a Discord game bot that offers a unique, level-based experience focused on Pythonic themes. Each level of the game introduces users to a different aspect of Python programming, providing an engaging and educational experience.

## Key Achievements
- Interactive Experience: The bot provides a dynamic and interactive experience for users on Discord, enhancing engagement through quizzes and challenges.
- Level-Based Gameplay: The bot features a structured gameplay approach, where users progress through levels, each themed around different Pythonic concepts.
- Educational Value: By covering various Pythonic themes, the bot helps users deepen their understanding of Python in an interactive and fun way.
- User Engagement: The progression through levels ensures continuous engagement, keeping users motivated to advance and learn more.

This project illustrates how combining gamification with educational content can create an engaging and informative tool for Python enthusiasts.

Thank you for exploring this project. We hope it serves as both a valuable resource and a source of enjoyment for Python enthusiasts on Discord.
