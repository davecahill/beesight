import ConfigParser
import datetime
import urllib
import urllib2
import requests
import sys
import simplejson
import pytz
import time

# complain on config file issues
# complain on bad login
# don't hardcode timezone to japan

CONFIG_FILE_NAME = 'config.ini'
INSIGHT_SECTION = 'insight'
BEEMINDER_SECTION = 'beeminder'
GOAL_NAME = 'meditate'
BASE_URL= "https://www.beeminder.com/api/v1/"

GET_DATAPOINTS_URL = BASE_URL + "users/%s/goals/%s/datapoints.json?auth_token=%s"
POST_MANY_DATAPOINTS_URL = BASE_URL + "users/%s/goals/%s/datapoints/create_all.json?auth_token=%s"
POST_DATAPOINTS_URL = GET_DATAPOINTS_URL + "&timestamp=%s&value=%s"


LOGIN_URL = "https://insighttimer.com/user_session"
INSIGHT_CSV_URL = "https://insighttimer.com/users/export"

headers = {}

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

def post_beeminder_data(data):
        config = ConfigParser.RawConfigParser()
        config.read(CONFIG_FILE_NAME)

        username = config.get(BEEMINDER_SECTION, "username")
        auth_token = config.get(BEEMINDER_SECTION, "auth_token")


        # json_headers
        headers = {'content-type': 'application/json'}
        values = {'datapoints' : data}
        json_data = simplejson.dumps(values)

        session = requests.session()
        full_url = POST_MANY_DATAPOINTS_URL % (username, GOAL_NAME, auth_token)

        """
        r = session.post(full_url, data=json_data) #btry w/o headers, headers=headers)
        print r.url
        print r.text
        """
        print json_data

def get_beeminder():
        config = ConfigParser.RawConfigParser()
        config.read(CONFIG_FILE_NAME)

        username = config.get(BEEMINDER_SECTION, "username")
        auth_token = config.get(BEEMINDER_SECTION, "auth_token")

        response = urllib2.urlopen(GET_DATAPOINTS_URL % (username, GOAL_NAME, auth_token))
        the_page = response.read()
        return the_page

def beeminder_to_one_per_day(beeminder_output):
    bm = simplejson.loads(beeminder_output)

    print bm

    s = {}

    # skip first two header lines
    for entry in bm:
        tz = pytz.timezone('Asia/Tokyo')
        ts = entry['timestamp']
        print ts
        dt = datetime.datetime.fromtimestamp(ts)
        print "bmdt", dt
        ld = tz.localize(dt)
        d = ld.date()
        print "d", d

        if not d in s:
            s[d] = 1

    return s.keys()


def csv_to_one_per_day(csv_lines):

    print csv_lines
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
    tz = pytz.timezone('Asia/Tokyo')
    d = datetime.datetime.combine(dt, datetime.time())
    offset = tz.utcoffset(d)
    ld = d - offset
    return int(time.mktime(ld.timetuple()))

if __name__ == "__main__":

    insight_dates = csv_to_one_per_day(get_insight_data())
    beeminder_dates = beeminder_to_one_per_day(get_beeminder())

    print "------"
    print sorted(insight_dates)
    print sorted(beeminder_dates)
    print "------"
    new_dates = sorted(list(set(insight_dates) - set(beeminder_dates)))

    print new_dates[0]
    new_datapoints = [{'timestamp': date_to_jp_timestamp(d), 'value':1.0, "comment":"test"} for d in new_dates]

    print new_datapoints
    print "**** %s to be posted" % len(new_datapoints)

    post_beeminder_data(new_datapoints[0:1])
    print "posted"

