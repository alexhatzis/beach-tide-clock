from NOAA_tide_data import get_tide_info
from plotter import generate_trace

sg_tides = get_tide_info()

plot_png = generate_trace(sg_tides)

