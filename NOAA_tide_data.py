from noaa_coops import Station
from datetime import date
from datetime import timedelta
from datetime import datetime
from datetime import time


def get_tide_info():

    #create NOAA station objects for Point Reyes and Monterey
    pointreyes = Station(id="9415020")
    monterey = Station(id="9413450")

    #create datetime date objects for the start and end of the possible tide time ranges
    #i.e., beginning of yesterday until end of tomorrow
    today = date.today()
    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=2)

    #get the current number of minutes since the start of our time interval, midnight yesterday
    currenttime = datetime.now()
    currentminute = (currenttime - datetime.combine(yesterday, time())).total_seconds() // 60

    #string formatter for NOAA API call (i.e. YYYYMMDD)
    datefmtstr = "%Y%m%d"

    #create formatted strings for dates to use in NOAA API call
    yesterdayfmt = yesterday.strftime(datefmtstr)
    tomorrowfmt = tomorrow.strftime(datefmtstr)

    #number of hours before and after current time to display tide information for
    hrs_past = 6
    hrs_future = 18

    #number of minutes between tide prediction data
    dpinterval = 5

    #data point corresponding to the current time, floored to last multiple of dpinterval minutes
    curr_pt = int(currentminute // dpinterval)

    #data points corresponding to the beginning and end of our display interval
    past_pt = curr_pt - (hrs_past * 60 // dpinterval)
    future_pt = curr_pt + (hrs_future * 60 // dpinterval) + 1

    #get water level data for Point Reyes and Monterey using NOAA API call
    pr_water_levels = pointreyes.get_data(begin_date=yesterdayfmt, end_date=tomorrowfmt, product="predictions", interval=f'{dpinterval}', datum="MLLW", units="english", time_zone="lst_ldt")
    mr_water_levels = monterey.get_data(begin_date=yesterdayfmt, end_date=tomorrowfmt, product="predictions", interval=f'{dpinterval}', datum="MLLW", units="english", time_zone="lst_ldt")

    #average the water level data for the two stations to approximate San Gregorio beach
    sg_water_levels = (pr_water_levels.iloc[past_pt:future_pt] + mr_water_levels[past_pt:future_pt]) / 2

    return sg_water_levels
