'''奇迹之冠'''
from whimbox.common.utils.ui_utils import scroll_find_click
from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.ui.ui import ui_control
from whimbox.ui.page_assets import *
from whimbox.ui.ui_assets import *
from whimbox.interaction.interaction_core import itt

import time

class MiraCrownTask(TaskTemplate):
    def __init__(self):
        super().__init__("mira_crown_task")
    
    @register_step("检查奇迹之冠进度")
    def step1(self):
        ui_control.goto_page(page_daily_task)
        texts = itt.ocr_multiple_lines(AreaMiraCrownOverview)
        for text in texts:
            if text.endswith("/45"):
                star_num = int(text.split("/")[0])
                if star_num < 45:
                    self.task_stop(msg="请先完成基础搭配赛")
                    break
            if text.endswith("/24"):
                star_num = int(text.split("/")[0])
                if star_num < 24:
                    self.log_to_gui(f"奇迹之冠进度为{text}")
                    itt.move_and_click(AreaMiraCrownOverview.position)
                    itt.delay(1, comment="等待奇迹之冠页面加载")
                else:
                    ui_control.goto_page(page_main)
                    self.task_stop(msg="奇迹之冠进度已满")
                break

    @register_step("快速通关")
    def step2(self):
        itt.appear_then_click(ButtonMiraCrownQuickPlay)

    # 未完待续


if __name__ == "__main__":
    # task = MiraCrownTask()
    # result = task.task_run()
    # print(result.to_dict())
    texts = itt.ocr_multiple_lines(AreaMiraCrownOverview)
    print(texts)