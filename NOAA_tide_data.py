from noaa_coops import Station
from datetime import date
from datetime import timedelta
from datetime import datetime
from datetime import time

class tides_data:
    def __init__(self, stationIds, hrsPrior, hrsFuture, dpInterval):
        self.stations = []
        for stationId in stationIds:
            self.stations.append(Station(id=stationId))
        self.hrsPrior = hrsPrior
        self.hrsFuture = hrsFuture
        self.dpInterval = dpInterval
        self.waterLevels = []

    def get_tide_info(self):

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

        #data point corresponding to the current time, floored to last multiple of dpinterval minutes
        curr_pt = int(currentminute // self.dpInterval)

        #data points corresponding to the beginning and end of our display interval
        past_pt = curr_pt - (self.hrsPrior * 60 // self.dpInterval)
        future_pt = curr_pt + (self.hrsFuture * 60 // self.dpInterval) + 1

        #get water level data for Point Reyes and Monterey using NOAA API call
        for station in self.stations:
            if len(self.waterLevels):
                self.waterLevels += station.get_data(begin_date=yesterdayfmt, end_date=tomorrowfmt, product="predictions", interval=f'{self.dpInterval}', datum="MLLW", units="english", time_zone="lst_ldt")
            else:
                self.waterLevels = station.get_data(begin_date=yesterdayfmt, end_date=tomorrowfmt, product="predictions", interval=f'{self.dpInterval}', datum="MLLW", units="english", time_zone="lst_ldt")

        #average the water level data for the two stations to approximate San Gregorio beach
        self.waterLevels = self.waterLevels / len(self.stations)

        return self.waterLevels[past_pt:future_pt]
