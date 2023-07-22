#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import time
import logging
from lib.waveshare_epd import epd2in7, epdconfig
from pregnancy import Pregnancy
from screen_ui import ScreenUI

logging.basicConfig(level=logging.DEBUG)

config = json.load(open('config.json'))

try:
    epd = epd2in7.EPD()

    logging.info("init and Clear")
    epd.init()
    epd.Clear(0xFF)
    epd.Init_4Gray()

    pregnancy = Pregnancy(config['expected_birth_timestamp'])

    screen_ui = ScreenUI(epd.height, epd.width, pregnancy)
    himage = screen_ui.draw()
    epd.display_4Gray(epd.getbuffer_4Gray(himage))
    time.sleep(2)

    logging.info("Goto Sleep...")
    epd.sleep()

except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    epdconfig.module_exit()
    exit()