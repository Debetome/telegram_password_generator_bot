import json

from PGBot import PasswordGeneratorBot

CONFIG_FILE = "config.json"

def main() -> None:
    with open(CONFIG_FILE, "r") as f:
        config_data = json.load(f)
        
    token = config_data["token"]
    database = config_data["database"]
    logfile = config_data["logfile"]

    bot = PasswordGeneratorBot(token, database, logfile)
    bot.run()

if __name__ == '__main__':
    main()
