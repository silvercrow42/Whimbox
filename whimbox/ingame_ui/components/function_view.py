from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from whimbox.common.logger import logger


# 功能按钮配置列表
FUNCTION_BUTTONS = [
    {
        'label': '一条龙',
        'task_name': 'all_in_one_task',
        'task_params': {},
        'start_message': '开始一条龙，按 / 结束任务\n',
    },
    {
        'label': '自动跑图',
        'task_name': 'load_path',
        'needs_dialog': True,  # 需要弹出对话框
        'dialog_type': 'path_selection',
    },
    {
        'label': '录制路线',
        'task_name': 'record_path',
        'task_params': {},
        'start_message': '开始录制路线，按 / 停止录制\n',
    },
    {
        'label': '打开路线文件夹',
        'task_name': 'open_path_folder',
        'task_params': {},
        'start_message': '打开路线文件夹\n',
    },
]


class FunctionView(QWidget):
    """功能菜单视图组件"""
    # 统一的功能按钮点击信号
    function_clicked = pyqtSignal(dict)  # 传递按钮配置字典
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 按钮字典，key为button_id，value为QPushButton对象
        self.buttons = []
        
        # 初始化UI
        self.init_ui()
    
    def init_ui(self):
        """初始化功能视图UI"""
        self.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # 功能区域容器
        function_container = QWidget()
        function_container.setStyleSheet("""
            QWidget {
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                background-color: rgba(240, 240, 240, 150);
            }
        """)
        
        function_layout = QVBoxLayout(function_container)
        function_layout.setContentsMargins(16, 16, 16, 16)
        function_layout.setSpacing(12)
        
        # 根据配置创建所有功能按钮
        for config in FUNCTION_BUTTONS:
            button = self.create_function_button(config)
            self.buttons.append(button)
            function_layout.addWidget(button)
        
        # 添加弹性空间
        function_layout.addStretch()
        
        layout.addWidget(function_container)
    
    def create_function_button(self, config: dict) -> QPushButton:
        """根据配置创建功能按钮"""
        button = QPushButton(config['label'])
        button.setFixedHeight(50)
        button.clicked.connect(lambda: self.on_function_button_clicked(config))
        button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 24px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #BDBDBD;
                color: #757575;
            }
        """)
        return button
    
    def on_function_button_clicked(self, config: dict):
        """功能按钮点击统一处理"""
        logger.info(f"Function button clicked: {config['label']}")
        self.function_clicked.emit(config)
    
    def set_all_buttons_enabled(self, enabled: bool):
        """设置所有按钮是否可用"""
        for button in self.buttons:
            button.setEnabled(enabled)

