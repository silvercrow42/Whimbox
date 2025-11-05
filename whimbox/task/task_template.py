# 因为我们的task将直接被mcp调用
# 所以就不整原项目thread管理那一套了，怎么简单怎么来
from whimbox.common.logger import logger
from whimbox.ingame_ui.ingame_ui import win_ingame_ui
from whimbox.common.cvars import DEBUG_MODE, global_stop_flag
from whimbox.common.utils.ui_utils import back_to_page_main

from pynput import keyboard
import time
import traceback

STATE_TYPE_SUCCESS = "success"
STATE_TYPE_ERROR = "error"
STATE_TYPE_STOP = "stop"

class state:
    def __init__(self, type="", msg=""):
        self.type = type
        self.msg = msg

class TaskStep:
    def __init__(self, func, name=None, state_type="", state_msg=""):
        self.func = func
        self.state = state(state_type, state_msg)
        self.name = name or func.__name__

    def run(self):
        """运行步骤函数，返回下一步的名称（可选）"""
        return self.func()

def register_step(state_msg=""):
    """类方法装饰器，用于标记需要注册的步骤"""
    def wrapper(func):
        func._register_step = True
        func._state_msg = state_msg
        return func
    return wrapper

class TaskResult:
    def __init__(self, status=STATE_TYPE_SUCCESS, message="", data=None):
        self.status = status
        self.message = message
        self.data = data
    
    def to_dict(self):
        return self.__dict__

    def __str__(self) -> str:
        return f"{{'status': {self.status}, 'message': {self.message}}}"

class TaskTemplate:
    def __init__(self, name="", check_stop_func=None):
        self.name = name
        global_stop_flag.clear()
        self.check_stop_func = check_stop_func
        self.step_sleep = 0.2   # 步骤执行后等待时间
        self.steps_dict = {}    # {step_name: TaskStep} 步骤字典
        self.step_order = []    # [step_name, ...] 默认执行顺序
        self.current_step: TaskStep = None
        self.error_step = TaskStep(lambda step, task: None, STATE_TYPE_ERROR, "")
        self.task_result = TaskResult()
        self.__auto_register_steps()

        # 创建pynput监听器
        self.key_callbacks = {}  # 存储按键回调
        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.daemon = True  # 设为守护线程
        self.listener.start()

        # 添加默认停止热键
        self.add_hotkey("/", self.task_stop)

        
    def _on_key_press(self, key):
        """处理按键事件"""
        try:
            # 检查是否是字符键
            if hasattr(key, 'char') and key.char in self.key_callbacks:
                self.key_callbacks[key.char]()
            # 检查是否是特殊键
            elif key in self.key_callbacks:
                self.key_callbacks[key]()
        except Exception as e:
            logger.error(f"热键处理错误: {e}")

    def add_hotkey(self, key_str, callback):
        """添加热键监听"""
        # 将字符串键转换为pynput键对象
        if len(key_str) == 1:  # 单个字符
            self.key_callbacks[key_str] = callback
        else:
            # 处理特殊键，如'space', 'esc'等
            try:
                # 尝试将键名转换为pynput.keyboard.Key对象
                key_obj = getattr(keyboard.Key, key_str)
                self.key_callbacks[key_obj] = callback
            except AttributeError:
                logger.warning(f"无法识别的键: {key_str}")


    def __auto_register_steps(self):
        """自动注册带有_register_step标记的方法"""
        # 获取类的所有方法，包括继承的
        for method_name in dir(self):
            # 跳过私有方法和特殊方法
            if method_name.startswith('__'):
                continue
            
            method = getattr(self, method_name)
            # 检查是否是可调用的方法且有注册标记
            if callable(method) and hasattr(method, "_register_step"):
                task_step = TaskStep(method, method_name, STATE_TYPE_SUCCESS, method._state_msg)
                self.steps_dict[method_name] = task_step
                self.step_order.append(method_name)


    def on_error(self, state_msg=""):
        """定义 error_step"""
        def wrapper(func):
            self.error_step = TaskStep(func, "error_step", STATE_TYPE_ERROR, state_msg)
            return func
        return wrapper

    def task_run(self):
        res = self._task_run()
        if res.status in [STATE_TYPE_SUCCESS, STATE_TYPE_STOP]:
            return res
        else:
            # 非手动停止导致的失败，就再试一次
            if not self.need_stop():
                self.log_to_gui(f"自动返回主界面，重试一次")
                back_to_page_main()
                res = self._task_run()
                return res
            else:
                return res

    def _task_run(self):
        """核心执行逻辑"""
        current_step_name = self.step_order[0] if self.step_order else None
        
        try:
            while current_step_name and not self.need_stop():
                # 获取当前步骤
                step = self.steps_dict.get(current_step_name)
                if not step:
                    raise Exception(f"步骤 '{current_step_name}' 不存在")
                
                self.current_step = step
                
                # 显示步骤信息
                self.log_to_gui(step.state.msg)
                
                # 运行步骤
                next_step_name = step.run()
                
                # 确定下一步
                if next_step_name:
                    # 步骤函数指定了下一步
                    current_step_name = next_step_name
                else:
                    # 使用默认顺序的下一步
                    current_index = self.step_order.index(current_step_name)
                    if current_index + 1 < len(self.step_order):
                        current_step_name = self.step_order[current_index + 1]
                    else:
                        # 已到达最后一步
                        current_step_name = None
                
                time.sleep(self.step_sleep)

        except Exception as e:
            self.handle_exception(e)
            self.error_step.state.msg = str(e)
            self.current_step = self.error_step
            self.log_to_gui(self.error_step.state.msg, is_error=True)
            self.task_result = TaskResult(STATE_TYPE_ERROR, self.error_step.state.msg)
            logger.error(traceback.format_exc())
        
        finally:
            self.handle_finally()
            back_to_page_main()
            # 停止键盘监听器
            self.key_callbacks.clear()
            if self.listener.is_alive():
                self.listener.stop()
                self.listener.join()
            return self.task_result


    def handle_exception(self, e):
        '''处理异常，如果子类有异常要处理，就实现这个方法'''
        pass

    def handle_finally(self):
        '''
        如果子类有需要在finally时进行的操作，就实现这个方法
        比如需要在结束时释放资源等等
        '''
        pass


    def task_stop(self, message=None, data=None):
        '''如果子类有自己额外的停止代码，就实现这个方法，并调用父类的这个方法'''
        global_stop_flag.set()
        self.update_task_result(status=STATE_TYPE_STOP, message=message or "停止任务", data=data)

    def need_stop(self):
        # 综合判断是否需要停止
        return global_stop_flag.is_set() or (self.check_stop_func and self.check_stop_func())

    def get_state_msg(self):
        """获得当前任务的状态信息，供agent显示"""
        return self.current_step.state.msg if self.current_step else ""


    def log_to_gui(self, msg, is_error=False):
        if not is_error:
            msg = f"✅ {msg}\n"
        else:
            msg = f"❌ {msg}\n"
        if win_ingame_ui:
            win_ingame_ui.update_message(msg)
        logger.info(msg)


    def update_task_result(self, status=STATE_TYPE_SUCCESS, message="", data=None):
        self.task_result = TaskResult(status, message, data)