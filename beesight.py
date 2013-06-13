import ConfigParser
import datetime
import urllib
import urllib2
import requests
import sys
import simplejson
import time

# complain on config file issues
# complain on bad login
# don't hardcode timezone to japan

CONFIG_FILE_NAME = 'config.ini'
INSIGHT_SECTION = 'insight'
BEEMINDER_SECTION = 'beeminder'

LOGIN_URL = "https://insighttimer.com/user_session"
INSIGHT_CSV_URL = "https://insighttimer.com/users/export"

BASE_URL= "https://www.beeminder.com/api/v1/"
GET_DATAPOINTS_URL = BASE_URL + "users/%s/goals/%s/datapoints.json?auth_token=%s"
POST_MANY_DATAPOINTS_URL = BASE_URL + "users/%s/goals/%s/datapoints/create_all.json?auth_token=%s"
POST_DATAPOINTS_URL = GET_DATAPOINTS_URL + "&timestamp=%s&value=%s"

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

def post_beeminder_entry(entry):
        config = ConfigParser.RawConfigParser()
        config.read(CONFIG_FILE_NAME)

        username = config.get(BEEMINDER_SECTION, "username")
        auth_token = config.get(BEEMINDER_SECTION, "auth_token")
        goal_name = config.get(BEEMINDER_SECTION, "goal_name")

        session = requests.session()
        full_url = POST_DATAPOINTS_URL % (username, goal_name, auth_token, entry["timestamp"], entry["value"])
        r = session.post(full_url)

        print "Posted entry: %s" % r.text

def get_beeminder():
        config = ConfigParser.RawConfigParser()
        config.read(CONFIG_FILE_NAME)

        username = config.get(BEEMINDER_SECTION, "username")
        auth_token = config.get(BEEMINDER_SECTION, "auth_token")
        goal_name = config.get(BEEMINDER_SECTION, "goal_name")

        response = urllib2.urlopen(GET_DATAPOINTS_URL % (username, goal_name, auth_token))
        the_page = response.read()
        return the_page

def beeminder_to_one_per_day(beeminder_output):
    bm = simplejson.loads(beeminder_output)

    s = {}

    # skip first two header lines
    for entry in bm:
        ts = entry['timestamp']
        dt = datetime.datetime.fromtimestamp(ts)

        # need to move back one dayfrom the beeminder time, because it
        # pushes the day forward to 01:00 on day + 1, at least in JST
        d = dt.date() - datetime.timedelta(days=1)

        if not d in s:
            s[d] = 1

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

def date_to_jp_timestamp(dt):
    d = datetime.datetime.combine(dt, datetime.time())
    return int(time.mktime(d.timetuple()))

if __name__ == "__main__":
    # get dates of days meditated, from insight
    insight_dates = csv_to_one_per_day(get_insight_data())
    print "%s days meditated according to insighttimer.com" % len(insight_dates)

    # get dates of days meditated, from beeminder
    beeminder_dates = beeminder_to_one_per_day(get_beeminder())
    print "%s datapoints in beeminder" % len(beeminder_dates)

    # get dates which beeminder doesn't know about yet
    new_dates = sorted(list(set(insight_dates) - set(beeminder_dates)))

    # create beeminder-friendly datapoints
    new_datapoints = [{'timestamp': date_to_jp_timestamp(d), 'value':1.0, "comment":"test"} for d in new_dates]

    print "%s datapoints to post" % len(new_datapoints)

    for dp in new_datapoints:
        post_beeminder_entry(dp)
