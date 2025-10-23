"""
检查并领取朝夕心愿
"""

from whimbox.task.task_template import TaskTemplate, register_step
from whimbox.ui.ui import ui_control
from whimbox.ui.page_assets import *
from whimbox.interaction.interaction_core import itt
import time
from whimbox.common.utils.ui_utils import wait_until_appear
from whimbox.task.daily_task.cvar import *


zxxy_task_info_list = [
    {
        "key_words": ["素材激化幻境"],
        "score": 200,
        "priority": 5,
        "task_name": DAILY_TASK_JIHUA
    },
    {
        "key_words": ["幻境", "祝福闪光"],
        "score": 200,
        "priority": 5,
        "task_name": DAILY_TASK_GET_BLESS
    },
    {
        "key_words": ["植物"],
        "score": 200,
        "priority": 5,
        "task_name": DAILY_TASK_PICKUP
    },
    {
        "key_words": ["昆虫"],
        "score": 200,
        "priority": 5,
        "task_name": DAILY_TASK_CATCH_INSECT
    },
    {
        "key_words": ["魔物试炼幻境"],
        "score": 200,
        "priority": 5,
        "task_name": DAILY_TASK_MONSTER
    },
    {
        "key_words": ["小游戏"],
        "score": 200,
        "priority": 0,
        "task_name": DAILY_TASK_MINI_GAME
    },
    {
        "key_words": ["活跃能量"],
        "score": 150,
        "priority": 5,
        "task_name": DAILY_TASK_COST_ENERGY
    },
    {
        "key_words": ["照片"],
        "score": 100,
        "priority": 5,
        "task_name": DAILY_TASK_TAKE_PHOTO
    },
    {
        "key_words": ["挖掘"],
        "score": 100,
        "priority": 5,
        "task_name": DAILY_TASK_DIG
    },
    {
        "key_words": ["升级", "祝福闪光"],
        "score": 100,
        "priority": 0,
        "task_name": DAILY_TASK_UPGRADE_BLESSED
    },
    {
        "key_words": ["魔气怪"],
        "score": 100,
        "priority": 0,
        "task_name": DAILY_TASK_FIGHT
    },
    {
        "key_words": ["制作"],
        "score": 100,
        "priority": 0,
        "task_name": DAILY_TASK_MAKE_CLOTHES
    },
]


class ZhaoxiTask(TaskTemplate):
    def __init__(self):
        super().__init__("zhaoxi_task")
        self.current_score = 0
        self.todo_list = []


    @register_step("正在前往朝夕心愿")
    def step1(self):
        ui_control.goto_page(page_zxxy)


    @register_step("查看完成情况")
    def step2(self):
        try:
            time.sleep(2) # 等待分数变化
            score_str = itt.ocr_single_line(AreaZxxyScore, padding=50)
            score = int(score_str.strip())
            if score % 100 != 0:
                raise Exception(f"朝夕心愿分数识别异常:{score_str}")
        except:
            raise Exception(f"朝夕心愿分数识别异常:{score_str}")
        self.current_score = score
        if score == 500:
            return "step4"
        else:
            self.log_to_gui(f"朝夕心愿完成度：{score}/500")
            return "step3"


    @register_step("查看具体任务")
    def step3(self):

        def check_task(task_btn: Button):
            itt.move_and_click(task_btn.click_position())
            time.sleep(0.3)
            if not itt.get_img_existence(IconUIZxxyTaskFinished):
                task_text = itt.ocr_single_line(AreaZxxyTaskText)
                for task_info in zxxy_task_info_list:
                    is_match = True
                    for key_word in task_info["key_words"]:
                        if key_word not in task_text:
                            is_match = False
                            break
                    if is_match:
                        return task_info
                return None
            else:
                return None

        # 获得未完成任务列表
        unfinished_task_list = []
        button_list = [ButtonZxxyTask1, ButtonZxxyTask2, ButtonZxxyTask3, ButtonZxxyTask4, ButtonZxxyTask5]
        for i in range(5):
            unfinished_task = check_task(button_list[i])
            if unfinished_task == None:
                continue
            else:
                self.log_to_gui(f"未完成任务：{unfinished_task['task_name']}")
                unfinished_task_list.append(unfinished_task)
        
        # 根据优先级和分数，判断应该做什么任务
        temp_score = self.current_score
        unfinished_task_list.sort(
            key=lambda x: (x['priority'], x['score']),
            reverse=True
        )
        # 优先完成活跃能量任务
        if DAILY_TASK_COST_ENERGY in unfinished_task_list:
            unfinished_task_list.remove(DAILY_TASK_COST_ENERGY)
            self.todo_list.append(DAILY_TASK_COST_ENERGY)
            temp_score += 150
        # 然后根据分数和优先级完成其他任务
        for task in unfinished_task_list:
            if task['priority'] == 0:
                continue
            if temp_score >= 500:
                break
            self.todo_list.append(task['task_name'])
            temp_score += task['score']
        
        if len(self.todo_list) > 0:
            self.update_task_result(
                message=f"需要继续完成以下任务：{", ".join(self.todo_list)}",
                data=self.todo_list)
            return "step5"
        else:
            raise Exception("没办法凑齐分数了")
                

    @register_step("领取奖励")
    def step4(self):
        if not itt.get_img_existence(ButtonZxxyRewarded):
            itt.move_and_click(ButtonZxxyRewarded.click_position())
            time.sleep(0.2)
            if wait_until_appear(TextClickSkip):
                itt.key_press('f')
            self.update_task_result(message="成功领取朝夕心愿奖励", data=self.todo_list)
        else:
            self.update_task_result(message="朝夕心愿奖励已被领取过，无需再次领取", data=self.todo_list)


    @register_step("退出朝夕心愿")
    def step5(self):
        ui_control.goto_page(page_main)
    

if __name__ == "__main__":
    zhaoxi_task = ZhaoxiTask()
    zhaoxi_task.task_run()
    print(zhaoxi_task.task_result)