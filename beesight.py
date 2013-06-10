import ConfigParser
import datetime

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

def csv_to_one_per_day(csv_lines):

    s = {}

    # skip first two header lines
    for l in csv_lines[2:]:
        datetime_part = l.split(",")[0]
        date_part = datetime_part.split(" ")[0]
        m, d, y = map(int, date_part.split("/"))
        dt = datetime.date(y, m, d)

        if not dt in s:
            s[dt] = 0

    return sorted(s.keys())

if __name__ == "__main__":
    #get_insight()

    f = open("sample_data.csv")
    csv_to_one_per_day(f.readlines())
