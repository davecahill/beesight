Usage
---------

Copy default_config.ini to config.ini and fill in your insighttimer.com and beeminder credentials.

Your beeminder auth token can be found at this URL when logged in:
https://www.beeminder.com/api/v1/auth_token.json

To run:
```
python beeminder.py
```

I set this up on a cron so that it runs occasionally, and posts new datapoints to beeminder if there are any.

Notes
------
beesight.py currently subtracts one from the dates it gets from beeminder,
because beeminder returns JST (Japanese Standard Time) 01:00 on (correct_day + 1)
in my timezone. If you're in another timezone, this may cause your dates
to be off by one. 

