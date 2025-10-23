import traceback
from typing import List, Union

from whimbox.ui.template.img_manager import ImgIcon
from whimbox.ui.template.text_manager import Text
from whimbox.ui.ui_assets import AreaPageTitleFeature

class UIPage():
    parent = None

    def __init__(self, check_icon: Union[ImgIcon, Text, List]):
        self.links = {}
        (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
        self.name = text[:text.find('=')].strip()
        self.check_icon_list = []
        if isinstance(check_icon, List):
            self.check_icon_list = check_icon
        elif isinstance(check_icon, ImgIcon):
            self.check_icon_list.append(check_icon)
        elif isinstance(check_icon, Text):
            self.check_icon_list.append(check_icon)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def link(self, button, destination):
        """
        
        button:Button/Str
        """
        self.links[destination] = button

    def is_current_page(self, itt):
        for imgicon in self.check_icon_list:
            ret = False
            if isinstance(imgicon, ImgIcon):
                ret = itt.get_img_existence(imgicon)
            elif isinstance(imgicon, Text):
                ret = itt.get_text_existence(imgicon)
            if ret:
                return True
        return False

    def add_check_icon(self, check_icon: ImgIcon):
        self.check_icon_list.append(check_icon)

class TitlePage(UIPage):
    def __init__(self, title: str):
        (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
        self.name = text[:text.find('=')].strip()
        self.title = title
        self.links = {}

    def is_current_page(self, itt):
        return itt.ocr_single_line(area = AreaPageTitleFeature) == self.title

