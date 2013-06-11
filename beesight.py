import ConfigParser
import datetime
import urllib
import urllib2
import requests
import sys
import simplejson

# complain on config file issues

# complain on bad login


CONFIG_FILE_NAME = 'config.ini'
INSIGHT_SECTION = 'insight'
BEEMINDER_SECTION = 'beeminder'
GOAL_NAME = 'meditate'
BASE_URL= "https://www.beeminder.com/api/v1/"

DATAPOINTS_URL = BASE_URL + "/users/%s/goals/%s/datapoints.json?auth_token=%s"

LOGIN_URL = "https://insighttimer.com/user_session"
INSIGHT_CSV_URL = "https://insighttimer.com/users/export"

headers = {}
"""
headers = {
"Host": "insighttimer.com",
"Connection": "keep-alive",
"Content-Length": "80",
"Cache-Control": "max-age=0",
"Origin": "https://insighttimer.com",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.163 Safari/535.19",
"Content-Type": "application/x-www-form-urlencoded",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
"Referer": "https://insighttimer.com/user_session/new",
#"Accept-Encoding": "gzip,deflate,sdch",
"Accept-Language": "en-US,en;q=0.8",
"Accept-Charset": "ISO-8859-1,utf-8;q=0.7,*;q=0.3"
}
"""

def get_insight_data():
        config = ConfigParser.RawConfigParser()
        config.read(CONFIG_FILE_NAME)

        username = config.get(INSIGHT_SECTION, "username")
        password = config.get(INSIGHT_SECTION, "password")

        values = {'user_session[email]' : username,
                  'user_session[password]' : password }
        login_data = urllib.urlencode(values)

        # Start a session so we can have persistent cookies
        session = requests.session()

        r = session.post(LOGIN_URL, data=login_data)

        r = session.get(INSIGHT_CSV_URL)

        return r.text.split('\n')

def get_beeminder():
        config = ConfigParser.RawConfigParser()
        config.read(CONFIG_FILE_NAME)

        username = config.get(BEEMINDER_SECTION, "username")
        auth_token = config.get(BEEMINDER_SECTION, "auth_token")

        response = urllib2.urlopen(DATAPOINTS_URL % (username, GOAL_NAME, auth_token))
        the_page = response.read()
        return the_page

def beeminder_to_one_per_day(beeminder_output):
    bm = simplejson.loads(beeminder_output)

    s = {}

    # skip first two header lines
    for entry in bm:
        dt = datetime.date.fromtimestamp(entry['timestamp'])
        if not dt in s:
            s[dt] = 1

    return s.keys()


def csv_to_one_per_day(csv_lines):

    s = {}

    # skip first two header lines
    for l in csv_lines[2:]:
        datetime_part = l.split(",")[0]
        date_part = datetime_part.split(" ")[0]
        date_parts = date_part.split("/")
        if len(date_parts) == 3:
            m, d, y = map(int, date_parts)
            dt = datetime.date(y, m, d)

            if not dt in s:
                s[dt] = 0

    return s.keys()

if __name__ == "__main__":

    insight_dates = csv_to_one_per_day(get_insight_data())
    beeminder_dates = beeminder_to_one_per_day(get_beeminder())

    print insight_dates
    print beeminder_dates

