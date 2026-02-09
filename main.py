from NOAA_tide_data import tides_data
from plotter import generate_trace
import eink_writer
import pygame as pg
import sys
import os

picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)
os.environ["SDL_VIDEODRIVER"] = "dummy"

import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont
import traceback

main_dir = os.path.split(os.path.abspath(__file__))[0]
img_dir = os.path.join(main_dir, "img")

def load_image(name, scale=1):
    fullname = os.path.join(main_dir, name)
    image = pg.image.load(fullname)

    size = image.get_size()
    size = (size[0] * scale, size[1] * scale)
    image = pg.transform.smoothscale(image, size)

    image = image.convert()
    return image, image.get_rect()

screenx = 800
screeny = 480

# pointreyes, monterey
sg_tides = tides_data(["9415020", "9413450"], 6, 18, 5)
tide_levels = sg_tides.get_tide_info()
plot_png = generate_trace(tide_levels)

pg.init
pg.display.init()
screen = pg.display.set_mode((screenx, screeny))
background = pg.Surface((screenx, screeny))
bgimg, bgimg_rect = load_image("background.png")
background.blit(bgimg, bgimg_rect)

trace, trace_rect = load_image(plot_png, scale=0.95)
#centered_trace_rect = trace_rect(centerx=screenx/2, centery=screeny/2)
trace_rect.centerx = screenx/2
trace_rect.centery = screeny/2
background.blit(trace, trace_rect)
screen.blit(background, (0,0))
pg.display.flip()
fullname = os.path.join(main_dir, "clock_img.bmp")
pg.image.save(background, fullname)

pg.quit()

logging.basicConfig(level=logging.DEBUG)

try:
    logging.info("epd7in5_V2 Demo")
    epd = epd7in5_V2.EPD()
    
    logging.info("init and Clear")
    epd.init()
    epd.Clear()

    logging.info("read bmp file")
    Himage = Image.open(os.path.join(picdir, 'clock_img.bmp'))
    epd.display(epd.getbuffer(Himage))
    time.sleep(2)

    logging.info("Goto Sleep...")
    epd.sleep()
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit(cleanup=True)
    exit()