'''记录美鸭梨时间，并根据自然时间流逝推测美鸭梨时间(暂时用不着)'''

import re
import time

from whimbox.interaction.interaction_core import itt
from whimbox.ui.ui_assets import *
from whimbox.ui.ui import ui_control
import whimbox.ui.page as UIPage
from whimbox.common.logger import logger


class MiralandTimeError(Exception):
    pass

class MiralandTime():
    def __init__(self):
        self.realworld_start_time = None
        self.miraland_start_time = None

    def is_valid_time(self, s: str) -> bool:
        pattern = r'^(?:[01]\d|2[0-3]):[0-5]\d$'
        return re.match(pattern, s) is not None

    def time_to_minutes(self, time_str: str) -> int:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
    def minutes_to_time(self, minutes: int) -> str:
        hours = minutes // 60 % 24
        minutes = minutes % 60
        return f'{hours:02d}:{minutes:02d}'

    def init_time(self):
        ui_control.ensure_page(UIPage.page_esc)
        time_str = itt.ocr_single_line(AreaUITime, padding=50)
        time_str = time_str.replace(' ', '')
        retry_count = 3
        while not self.is_valid_time(time_str) and retry_count > 0:
            logger.error(f"Invalid Time String:: {time_str}")
            time_str = itt.ocr_single_line(AreaUITime, padding=50)
            time_str = time_str.replace(' ', '')
            retry_count -= 1
        if retry_count <= 0:
            raise MiralandTime(f"Invalid Time String: {time_str}")
        else:
            logger.info(f"Now Miraland Time: {time_str}")
            ui_control.goto_page(UIPage.page_main)
            self.miraland_start_time = self.time_to_minutes(time_str)
            self.realworld_start_time = time.time()

    def get_time(self):
        # 现实世界1秒=奇迹大陆1分钟
        realworld_gap_time = time.time() - self.realworld_start_time
        miraland_now_time = self.miraland_start_time + realworld_gap_time
        return self.minutes_to_time(miraland_now_time)
    
    def get_day_or_night(self):
        # 现实世界1秒=奇迹大陆1分钟
        realworld_gap_time = time.time() - self.realworld_start_time
        miraland_now_time = self.miraland_start_time + realworld_gap_time
        hour = miraland_now_time // 60 % 24
        if hour >= 4 and hour < 22:
            return 'day'
        else:
            return 'night'



if __name__ == '__main__':
    m = MiralandTime()
    m.init_time()
    print(m.get_day_or_night())