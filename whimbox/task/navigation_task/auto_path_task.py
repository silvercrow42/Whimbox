"""自动跑图"""
from whimbox.task.task_template import TaskTemplate, register_step, STATE_TYPE_STOP
from whimbox.interaction.interaction_core import itt
import time, os
from whimbox.common.path_lib import *
from whimbox.task.navigation_task.common import *
from whimbox.map.map import nikki_map
from whimbox.view_and_move.view import *
from whimbox.view_and_move.move import *
from whimbox.ability.ability import ability_manager
from whimbox.action.pickup import PickupTask
from whimbox.action.catch_insect import CatchInsectTask
from whimbox.action.clean_animal import CleanAnimalTask
from whimbox.action.fishing import FishingTask
from whimbox.task.navigation_task.common import path_manager


class AutoPathTask(TaskTemplate):
    def __init__(self, path_record: PathRecord=None, path_name: str=None, excepted_num=None):
        super().__init__("auto_path_task")
        self.excepted_num = excepted_num # 期望的素材数量，获取到该数量后就停止
        self.step_sleep = 0.01
        if path_record is not None:
            self.path_info = path_record.info
            self.path_points = path_record.points
        elif path_name is not None:
            path_record = path_manager.query_path(path_name=path_name)
            if path_record is None:
                raise ValueError(f"路线{path_name}不存在")
            self.path_info = path_record.info
            self.path_points = path_record.points
        else:
            raise ValueError("path_record和path_name不能同时为空")
        # 各种状态记录
        self.last_position = None
        self.curr_position = None
        self.curr_target_point_id = 0
        self.target_point: PathPoint = None
        self.need_move_mode = MOVE_MODE_WALK
        self.last_need_move_mode = MOVE_MODE_WALK
        self.current_game_move_mode = MOVE_MODE_WALK

        # 各类材料获取任务的结果记录
        self.material_count_dict = {}

        # 一些常量
        self.walk2jump_stop_time = 0.5
        self.jump2walk_stop_time = 0.2
        self.offset = 2 # 当距离必经点offset以内，就视作已经到达

    def merge_material_count_dict(self, material_count_dict):
        if material_count_dict is None:
            return
        for key, value in material_count_dict.items():
            if key in self.material_count_dict:
                self.material_count_dict[key] += value
            else:
                self.material_count_dict[key] = value

    def task_stop(self):
        if not self.need_stop():
            super().task_stop(message="手动停止跑图")
            self.log_to_gui("手动停止跑图", is_error=True)

    def _update_next_target_point(self):
        """更新下一个必经点"""
        if self.curr_target_point_id < len(self.path_points) - 1:
            for index in range(self.curr_target_point_id+1, len(self.path_points)):
                if self.path_points[index].point_type == POINT_TYPE_TARGET:
                    self.curr_target_point_id = index
                    self.target_point = self.path_points[index]
                    return
    
    def start_move(self, current_posi, target_posi, offset):
        if self.move_controller:
            self.move_controller.start_move_ahead(current_posi, target_posi, offset)

    def stop_move(self):
        if self.move_controller:
            self.move_controller.stop_move_ahead()

    def is_moving(self):
        if self.move_controller:
            return self.move_controller.is_moving

    def change_to_jump(self):
        """切换到跳跃模式"""
        if self.jump_controller:
            self.current_game_move_mode, rate = get_move_mode_in_game(ret_rate=True)
            if self.current_game_move_mode == MOVE_MODE_WALK:
                logger.debug(f"change to jump, rate: {rate}")
                # 游戏中二段跳瞬间，会出现一帧WALK状态的图标，所以这里还要判断连续两帧都是WALK，避免误判
                if self.jump_controller.is_double_jumping() \
                    and self.jump_controller.double_jump_begin_time \
                    and time.time() - self.jump_controller.double_jump_begin_time > 0.1:
                        self.jump_controller.clear_jump_state()
                self.jump_controller.start_jump()
            # 如果游戏中是跳跃图标，但是控制器不在跳跃，就说明被什么机制弹起来了或是下落中，触发一下二段跳
            elif self.current_game_move_mode == MOVE_MODE_JUMP and (not self.jump_controller.is_jumping()):
                self.jump_controller._start_double_jump()

    def change_to_walk(self):
        """切换到行走模式"""
        if self.jump_controller:
            self.current_game_move_mode, rate = get_move_mode_in_game(ret_rate=True)
            if self.current_game_move_mode == MOVE_MODE_JUMP:
                logger.debug(f"change to walk, rate: {rate}")
                self.jump_controller.stop_jump()
            # 有可能游戏中已经落地了，但是脚本中还记录当前为跳跃状态，所以强制清除跳跃
            elif self.current_game_move_mode == MOVE_MODE_WALK and self.jump_controller.is_jumping():
                self.jump_controller.clear_jump_state()


    @register_step("初始化各种信息")
    def step0(self):
        # 启动动作控制线程
        self.jump_controller = JumpController()
        self.move_controller = MoveController()
        self.jump_controller.start_threading()
        self.move_controller.start_threading()
        # 初始化地图信息
        nikki_map.reinit_smallmap()
        self.curr_position = nikki_map.get_position(use_cache=True)
        # 校准视角旋转比例
        calibrate_view_rotation_ratio()
        # 初始化能力盘
        ability_manager.reinit()


    @register_step("自动跑图中……")
    def step1(self):
        last_t = time.time()
        while not self.need_stop():
            if DEBUG_MODE:
                t = time.time()
                print(f"cost {round(t - last_t, 2)}")
                last_t = t
            is_end = self.inner_step_update_target()
            if is_end:
                break
            # 采集到预期数量的素材后，也可以停止跑图流程
            if self.excepted_num is not None:
                if self.path_info.target and self.path_info.target in self.material_count_dict \
                and self.material_count_dict[self.path_info.target] >= self.excepted_num:
                    break
            if self.need_stop():
                break
            self.inner_step_change_view()
            if self.need_stop():
                break
            self.inner_step_control_move()
            time.sleep(self.step_sleep)
        return "step2"


    def inner_step_update_target(self):
        is_end = False
        self.last_position = self.curr_position
        self.curr_position = nikki_map.get_position()
        self.target_point = self.path_points[self.curr_target_point_id]

        # 计算当前位置与必经点的距离
        # 只根据当前位置计算距离，会出现一种情况：
        # 已经走过了必经点，导致离必经点的距离会越走越远
        # 所以要结合上次的位置，计算离必经点的最小距离
        if self.last_position is not None:
            equal_points = linspace(self.last_position, self.curr_position)
            min_dist = euclidean_distance_plist(self.target_point.position, equal_points).min()
            target_dist = min_dist
        else:
            target_dist = euclidean_distance(self.target_point.position, self.curr_position)
        
        if target_dist <= self.offset:
            logger.debug(f"arrive target point {self.target_point.id}")
            if self.curr_target_point_id >= len(self.path_points) - 1:
                # 走到终点了
                is_end = True
            else:
                # 处理各种ACTION
                if self.target_point.action:
                    self.stop_move()
                    self.change_to_walk()
                    if self.target_point.action == ACTION_PICK_UP:
                        pickup_task = PickupTask(check_stop_func=self.need_stop)
                        task_result = pickup_task.task_run()
                        self.merge_material_count_dict(task_result.data)
                    elif self.target_point.action == ACTION_CATCH_INSECT:
                        excepted_count = int(self.target_point.action_params)
                        catch_insect_task = CatchInsectTask(
                            self.path_info.target, 
                            expected_count=excepted_count,
                            check_stop_func=self.need_stop)
                        task_result = catch_insect_task.task_run()
                        self.merge_material_count_dict(task_result.data)
                    elif self.target_point.action == ACTION_CLEAN_ANIMAL:
                        excepted_count = int(self.target_point.action_params)
                        clean_animal_task = CleanAnimalTask(
                            self.path_info.target, 
                            expected_count=excepted_count,
                            check_stop_func=self.need_stop)
                        task_result = clean_animal_task.task_run()
                        self.merge_material_count_dict(task_result.data)
                    elif self.target_point.action == ACTION_FISHING:
                        fishing_task = FishingTask(check_stop_func=self.need_stop)
                        task_result = fishing_task.task_run()
                        self.merge_material_count_dict(task_result.data)
                    elif self.target_point.action == ACTION_WAIT:
                        wait_time = self.target_point.action_params
                        if wait_time is None:
                            wait_time = self.jump2walk_stop_time
                        time.sleep(float(wait_time))
                    
                # 当行动模式切换时停一下，避免因为状态切换时图标显示比较乱而错判
                self.need_move_mode = self.target_point.move_mode
                if self.is_moving() and self.target_point.action != ACTION_WAIT:
                    if self.last_need_move_mode == MOVE_MODE_WALK and self.need_move_mode == MOVE_MODE_JUMP:
                        self.stop_move()
                        time.sleep(self.walk2jump_stop_time)
                    elif self.last_need_move_mode == MOVE_MODE_JUMP and self.need_move_mode == MOVE_MODE_WALK:
                        self.stop_move()
                        time.sleep(self.jump2walk_stop_time)
                
                self.last_need_move_mode = self.need_move_mode
                self._update_next_target_point()
        
        if self.target_point.action == ACTION_TELEPORT:
            if target_dist >= not_teleport_offset:
                self.log_to_gui(f"传送到附近的流转之柱")
                self.stop_move()
                self.change_to_walk()
                nikki_map.bigmap_tp(self.target_point.position, self.path_info.map, csf=self.need_stop)
                self.curr_position = nikki_map.get_position()
        return is_end


    def inner_step_change_view(self):
        # 距离太近就不转视角了，避免观感太差
        self.curr_position = nikki_map.get_position()
        distance = euclidean_distance(self.curr_position, self.target_point.position)
        if distance < 0.5:
            return
        target_degree = calculate_posi2degree(self.curr_position, self.target_point.position)
        delta_degree = abs(calculate_delta_angle(nikki_map.get_rotation(), target_degree))
        # 如果要转很大的角度，需要先停下来
        if delta_degree >= 45 and self.is_moving():
            self.stop_move()
        change_view_to_angle(target_degree, offset=3, use_last_rotation = True)


    def inner_step_control_move(self):
        # # 有可能游戏中已经落地了，但是脚本中还记录当前为跳跃状态，所以强制清除跳跃
        # # 游戏中二段跳瞬间，会出现一帧WALK状态的图标，所以这里还要判断连续两帧都是WALK，避免误判
        # if game_move_mode == MOVE_MODE_WALK and self.jump_controller.is_double_jumping():
        #     time.sleep(0.1) 
        #     game_move_mode = get_move_mode_in_game()
        #     if game_move_mode == MOVE_MODE_WALK:
        #         self.jump_controller.clear_jump_state()
            
        if self.need_move_mode == MOVE_MODE_WALK:
            self.change_to_walk()
        elif self.need_move_mode == MOVE_MODE_JUMP:
            self.change_to_jump()
        
        self.start_move(self.curr_position, self.target_point.position, self.offset)
        

    def clear_all(self):
        self.stop_move()
        self.change_to_walk()
        if self.jump_controller is not None and self.move_controller is not None:
            self.jump_controller.stop_threading()
            self.move_controller.stop_threading()
            self.jump_controller.join()
            self.move_controller.join()
            self.jump_controller = None
            self.move_controller = None


    @register_step("结束自动跑图")
    def step2(self):
        self.clear_all()
        if len(self.material_count_dict) > 0:
            message = "自动跑图完成，获得材料："
            res = []
            for material_name, count in self.material_count_dict.items():
                res.append(f"{material_name} x {count}")
            message += ", ".join(res)
            self.update_task_result(message=message)
        else:
            self.update_task_result(message="自动跑图完成")


    def handle_finally(self):
        self.clear_all()


if __name__ == "__main__":
    task = AutoPathTask(path_name="example2_跳跃测试")
    task_result = task.task_run()
    print(task_result.to_dict())