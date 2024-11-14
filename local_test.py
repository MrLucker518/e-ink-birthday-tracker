#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
from datetime import datetime, timedelta

from birthday_tracker import ScreenUI, Birthday

logging.basicConfig(level=logging.DEBUG)

try:
    birth_time = datetime.now() + timedelta(days=100)
    birthday = Birthday(birth_time.strftime("%Y-%m-%d"))
    screen_ui = ScreenUI(264, 176, birthday)
    himage = screen_ui.draw()
    himage.show()


except IOError as e:
    logging.info(e)

except KeyboardInterrupt:
    logging.info("ctrl + c:")
    exit()
