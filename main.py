import json

from PGBot import PasswordGeneratorBot

CONFIG_FILE = "config.json"

def main() -> None:
    with open(CONFIG_FILE, "r") as f:
        config_data = json.load(f)
        
    bot_token = config_data["bot_token"]
    database = config_data["database"]
    logfile = config_data["logfile"]

    bot = PasswordGeneratorBot(bot_token, database, logfile)
    bot.run()

if __name__ == '__main__':
    main()
