beesight.py
-------------
This is a small script which retrieves meditation data from insighttimer.com and posts the data points to your beeminder goal, so that you can easily track how often you're meditating.

beesight.py only counts 1 point per day (meditated or not), as my aim is to track frequency rather than overall minutes.

It is intended to be run on a cron, picking up new datapoints and posting them to beeminder.

Usage
---------

Copy default_config.ini to config.ini and fill in your insighttimer.com and beeminder credentials.

Your beeminder auth token can be found at this URL when logged in:
https://www.beeminder.com/api/v1/auth_token.json

To run:
```
python beeminder.py
```

Notes
------
beesight.py currently subtracts one from the dates it gets from beeminder,
because beeminder returns JST (Japanese Standard Time) 01:00 on (correct_day + 1)
in my timezone. If you're in another timezone, this may cause your dates
to be off by one. 

