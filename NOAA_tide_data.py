from noaa_coops import Station
from datetime import date
from datetime import timedelta
from datetime import datetime
from datetime import time
import pickle
import os
import logging

class tides_data:
    def __init__(self, stationIds, hrsPrior, hrsFuture, dpInterval, cache_file='tide_cache.pkl'):
        self.stations = []
        for stationId in stationIds:
            self.stations.append(Station(id=stationId))
        self.hrsPrior = hrsPrior
        self.hrsFuture = hrsFuture
        self.dpInterval = dpInterval
        self.waterLevels = []
        self.cache_file = cache_file
        self.logger = logging.getLogger(__name__)

    def _validate_tide_data(self, data, past_pt, future_pt):
        """Validate that tide data is reasonable and complete."""
        if data is None or len(data) == 0:
            self.logger.warning("Tide data is empty or None")
            return False

        # Check if we have enough data points for the requested range
        if future_pt >= len(data):
            self.logger.warning(f"Not enough data points. Need {future_pt}, got {len(data)}")
            return False

        # Check if water levels are within reasonable bounds (e.g., -5 to 15 feet for MLLW)
        try:
            water_values = data.iloc[:, 0]
            if water_values.min() < -5 or water_values.max() > 15:
                self.logger.warning(f"Water levels out of reasonable range: {water_values.min()} to {water_values.max()}")
                return False
        except Exception as e:
            self.logger.warning(f"Error validating water level range: {e}")
            return False

        return True

    def _save_cache(self, data, metadata):
        """Save tide data and metadata to pickle file."""
        try:
            cache_data = {
                'data': data,
                'metadata': metadata,
                'cached_at': datetime.now()
            }
            with open(self.cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            self.logger.info(f"Cached tide data to {self.cache_file}")
        except Exception as e:
            self.logger.error(f"Failed to save cache: {e}")

    def _load_cache(self):
        """Load tide data from pickle file if available and recent."""
        if not os.path.exists(self.cache_file):
            self.logger.info("No cache file found")
            return None

        try:
            with open(self.cache_file, 'rb') as f:
                cache_data = pickle.load(f)

            cached_at = cache_data.get('cached_at')
            if cached_at:
                age_hours = (datetime.now() - cached_at).total_seconds() / 3600
                self.logger.info(f"Cache age: {age_hours:.1f} hours")

                # Cache is still useful if less than 24 hours old
                if age_hours > 24:
                    self.logger.warning("Cache is too old (>24 hours)")
                    return None

            return cache_data
        except Exception as e:
            self.logger.error(f"Failed to load cache: {e}")
            return None

    def get_tide_info(self):
        """Fetch tide data from NOAA API with error handling and caching fallback."""

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

        # Try to fetch fresh data from NOAA API
        try:
            self.logger.info("Fetching tide data from NOAA API")

            #get water level data for Point Reyes and Monterey using NOAA API call
            for station in self.stations:
                station_data = station.get_data(
                    begin_date=yesterdayfmt,
                    end_date=tomorrowfmt,
                    product="predictions",
                    interval=f'{self.dpInterval}',
                    datum="MLLW",
                    units="english",
                    time_zone="lst_ldt"
                )

                if len(self.waterLevels):
                    self.waterLevels += station_data
                else:
                    self.waterLevels = station_data

            #average the water level data for the two stations to approximate San Gregorio beach
            self.waterLevels = self.waterLevels / len(self.stations)

            # Validate the data
            if self._validate_tide_data(self.waterLevels, past_pt, future_pt):
                self.logger.info("Successfully fetched and validated tide data")

                # Save to cache
                metadata = {
                    'yesterday': yesterdayfmt,
                    'tomorrow': tomorrowfmt,
                    'curr_pt': curr_pt,
                    'past_pt': past_pt,
                    'future_pt': future_pt
                }
                self._save_cache(self.waterLevels, metadata)

                return self.waterLevels[past_pt:future_pt]
            else:
                raise ValueError("Tide data validation failed")

        except Exception as e:
            self.logger.error(f"Failed to fetch tide data from NOAA: {e}")

            # Try to load from cache as fallback
            self.logger.info("Attempting to load tide data from cache")
            cache_data = self._load_cache()

            if cache_data:
                self.logger.info("Using cached tide data")
                cached_waterLevels = cache_data['data']
                cached_metadata = cache_data['metadata']

                # Recalculate indices for current time
                cached_past_pt = cached_metadata.get('past_pt', past_pt)
                cached_future_pt = cached_metadata.get('future_pt', future_pt)

                # Adjust indices based on time shift if needed
                time_shift_pts = curr_pt - cached_metadata.get('curr_pt', curr_pt)
                adjusted_past_pt = cached_past_pt + time_shift_pts
                adjusted_future_pt = cached_future_pt + time_shift_pts

                # Ensure indices are within bounds
                adjusted_past_pt = max(0, adjusted_past_pt)
                adjusted_future_pt = min(len(cached_waterLevels), adjusted_future_pt)

                if adjusted_future_pt > adjusted_past_pt:
                    return cached_waterLevels[adjusted_past_pt:adjusted_future_pt]
                else:
                    self.logger.error("Cached data is insufficient for current time window")
                    raise Exception("No valid tide data available (API failed and cache insufficient)")
            else:
                raise Exception("No valid tide data available (API failed and no cache found)")
