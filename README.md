# OSMbot

OSMbot is a bot that automates player training in an online soccer game called OSM (Online Soccer Manager). The bot allows users to set a specific goal in the `Lineup.json` file, and it will train the players until that goal is achieved. If the training is not completed before a match, the bot will skip the training session, set up the lineup, and wait for the match to finish.


## Requirements

Before using OSMbot, make sure you have the following installed:

- Python 3.x
- Required Python libraries (listed in the `requirements.txt` file)

## Configuration

1. Clone or download the OSMbot repository to your computer.
2. Open the terminal and navigate to the project directory.

## Installing dependencies

3. Run the following command to install the necessary libraries:

pip install -r requirements.txt

## Configuring credentials

4. In the `Credentials.json` file, enter your OSM account credentials to allow the bot to access the game.

## Setting goals

5. In the `Lineup.json` file, set the desired goal for the bot. You can specify the desired training level for each position in the game's lineup.

## Running the bot

6. Run the following command to start the bot:
python osmbot.py

7. The bot will start training the players until it achieves the goal set in the `Lineup.json` file.

## Caution

- Use OSMbot with moderation and comply with the terms of service of the OSM game. Improper or excessive use of the bot may violate the game's rules and result in the suspension of your account.

- The author of OSMbot takes no responsibility for any consequences arising from the use of the bot.

## Contributions

If you would like to contribute to the development of OSMbot, feel free to send pull requests or open issues in the repository.

## Questions or Issues

For any questions or issues regarding OSMbot, open an issue in the repository or contact the author.

## License

OSMbot is distributed under the MIT license. See the LICENSE file for more information.
