#!/usr/bin/python
# -*- coding:utf-8 -*-
import json
import os
import time
import logging
import epaper
from birthday_tracker import ScreenUI, Birthday

logging.basicConfig(level=logging.WARN)

config_file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
config = json.load(open(config_file_path))

try:
    epd = epaper.epaper(config['display_version']).EPD()
    epd.Init_4Gray()

    birthday = Birthday(config['birth_date'])

    screen_ui = ScreenUI(epd.height, epd.width, birthday)
    himage = screen_ui.draw()
    epd.display_4Gray(epd.getbuffer_4Gray(himage))
    time.sleep(2)

    epd.sleep()

except IOError as e:
    logging.info(e)

