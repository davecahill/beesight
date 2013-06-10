import ConfigParser

# complain on config file issues

CONFIG_FILE_NAME = 'config.ini'
SECTION_HEADER = 'insight'

def get_insight():
        config = ConfigParser.RawConfigParser()
        config.read(CONFIG_FILE_NAME)

        username = config.get(SECTION_HEADER, "username")
        password = config.get(SECTION_HEADER, "password")

        print username
        print password

def csv_to_values():
    pass

def cap_one_per_day():
    pass


if __name__ == "__main__":
    get_insight()
