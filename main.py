from NOAA_tide_data import tides_data
from plotter import generate_trace

# pointreyes, monterey
sg_tides = tides_data(["9415020", "9413450"], 6, 18, 5)
tide_levels = sg_tides.get_tide_info()
plot_png = generate_trace(tide_levels)

