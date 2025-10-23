from whimbox.common.cvars import *
from whimbox.interaction.interaction_core import itt
from whimbox.ui.page_assets import *
from whimbox.ui.template.button_manager import Button
from whimbox.common.timer_module import AdvanceTimer
from whimbox.common.logger import logger
from whimbox.ui.page import TitlePage
from whimbox.common.utils.ui_utils import back_to_page_main

from threading import Lock
import time

class UI():

    def __init__(self) -> None:
        self.switch_ui_lock = Lock()

    def ui_additional(self):
        """
        Handle all annoying popups during UI switching.
        """
        while page_loading.is_current_page(itt):
            itt.delay(1, comment='game is loading...')

    def is_valid_page(self):
        try:
            self.get_current_page()
            return True
        except Exception as e:
            return False

    def get_current_page(self):
        ret_page = None
        title_text = itt.ocr_single_line(area = AreaPageTitleFeature)
        for page in ui_pages:
            if isinstance(page, TitlePage) and page.title == title_text:
                ret_page = page
                break
            elif page.is_current_page(itt):
                ret_page = page
                break
        if not ret_page:
            raise Exception("无法识别当前页面")
        else:
            return ret_page

    # def get_page(self, retry_times=0, raise_exception=True, max_retry=5):
    #     ret_page = None

    #     # when ui_addition is complete, enable it
    #     if raise_exception and retry_times >= max_retry:
    #         logger.info(f"Unknown page, try pressing esc")
    #         itt.key_press('esc')

    #     for page in ui_pages:
    #         if page.is_current_page(itt):
    #             if ret_page is None:
    #                 ret_page = page
    #             else:
    #                 logger.warning(f"检测到多个Page")
    #     if ret_page is None:
    #         logger.warning("未知Page, 重新检测")
    #         self.ui_additional()
    #         time.sleep(5)
    #         ret_page = self.get_page(retry_times=retry_times + 1)
    #     return ret_page

    def verify_page(self, page: UIPage) -> bool:
        return page.is_current_page(itt)

    def goto_page(self, target_page: UIPage, retry_times=0, max_retry=1):
        from collections import deque
        try:
            self.switch_ui_lock.acquire()
            
            logger.info(f"Goto page: {target_page}")
            
            # Get current page
            try:
                current_page = self.get_current_page()
            except Exception as e:
                logger.warning(f"Cannot recognize current page, going back to main page: {e}")
                back_to_page_main()
                current_page = page_main
            
            # Check if already at destination
            if current_page == target_page:
                logger.debug(f'Already at destination page: {target_page}')
                self.switch_ui_lock.release()
                return
            
            # Use BFS to find path from current page to target page
            queue = deque([(current_page, [current_page])])
            visited = {current_page}
            path = None
            
            while queue:
                page, current_path = queue.popleft()
                
                # Check all links from this page
                for next_page, button in page.links.items():
                    if next_page in visited:
                        continue
                    
                    visited.add(next_page)
                    new_path = current_path + [next_page]
                    
                    if next_page == target_page:
                        path = new_path
                        break
                    
                    queue.append((next_page, new_path))
                
                if path:
                    break
            
            # If no path found, raise exception
            if not path:
                error_msg = f"No path found from {current_page} to {target_page}"
                logger.error(error_msg)
                self.switch_ui_lock.release()
                raise Exception(error_msg)
            
            # Log the complete path
            path_str = " -> ".join([str(p) for p in path])
            logger.info(f"Navigation path: {path_str}")
            
            # Execute the path step by step
            success = True
            for i in range(len(path) - 1):
                from_page = path[i]
                to_page = path[i + 1]
                button = from_page.links.get(to_page, None)
                
                if button is None:
                    error_msg = f"No button found to go from {from_page} to {to_page}"
                    logger.error(error_msg)
                    self.switch_ui_lock.release()
                    raise Exception(error_msg)
                
                logger.debug(f'Page switch: {from_page} -> {to_page}')
                
                # Click the button
                if isinstance(button, str):
                    itt.key_press(button)
                elif isinstance(button, Button):
                    itt.appear_then_click(button)
                elif isinstance(button, Text):
                    itt.appear_then_click(button)
                
                itt.delay(0.7, comment="goto_page is waiting for page transition")
                
                # Handle loading screen
                self.ui_additional()
                
                # Verify we reached the expected page
                if not to_page.is_current_page(itt):
                    logger.warning(f"Expected to be at {to_page}, but verification failed. Retrying...")
                    success = False
                    break
            
            if not success:
                self.switch_ui_lock.release()
                if retry_times >= max_retry:
                    raise Exception(f"Failed to navigate to {target_page} after {max_retry} retries")
                self.goto_page(target_page, retry_times=retry_times + 1, max_retry=max_retry)
            else:
                logger.info(f"Successfully arrived at {target_page}")
                self.switch_ui_lock.release()
            
        except Exception as e:
            logger.error(f"goto_page failed: {e}")
            if self.switch_ui_lock.locked():
                self.switch_ui_lock.release()
            raise e


    # def ui_goto(self, destination: UIPage, confirm_wait=0.5):
    #     """
    #     Args:
    #         destination (Page):
    #         confirm_wait:
    #     """
    #     try:
    #         retry_timer = AdvanceTimer(1)
    #         self.switch_ui_lock.acquire()
    #         # Reset connection
    #         for page in ui_pages:
    #             page.parent = None

    #         # Create connection
    #         visited = [destination]
    #         visited = set(visited)
    #         while 1:
    #             new = visited.copy()
    #             for page in visited:
    #                 for link in ui_pages:
    #                     if link in visited:
    #                         continue
    #                     if page in link.links:
    #                         link.parent = page
    #                         new.add(link)
    #             if len(new) == len(visited):
    #                 break
    #             visited = new

    #         logger.info(f"UI goto {destination}")
    #         while 1:
    #             # Destination page
    #             if destination.is_current_page(itt):
    #                 logger.debug(f'Page arrive: {destination}')
    #                 break

    #             # Other pages
    #             clicked = False
    #             for page in visited:
    #                 if page.parent is None or len(page.check_icon_list) == 0:
    #                     continue
    #                 if page.is_current_page(itt):
    #                     logger.debug(f'Page switch: {page} -> {page.parent}')
    #                     button = page.links[page.parent]
    #                     if isinstance(button, str):
    #                         if retry_timer.reached():
    #                             itt.key_press(button)
    #                             retry_timer.reset()
    #                     elif isinstance(button, Button):
    #                         itt.appear_then_click(button)
    #                     elif isinstance(button, Text):
    #                         itt.appear_then_click(button)
    #                     clicked = True
    #                     itt.delay(0.5, comment="ui goto is waiting game animation")
    #                     break
    #             if clicked:
    #                 continue

    #             # Additional
    #             if self.ui_additional():
    #                 continue

    #         # Reset connection
    #         for page in ui_pages:
    #             page.parent = None
    #         self.switch_ui_lock.release()
    #         itt.delay(0.5, comment="ui goto is waiting game animation")
    #         # itt.wait_until_stable()
    #     except Exception as e:
    #         logger.error(f"UI goto failed: {e}")
    #         self.switch_ui_lock.release()
    #         raise e

    def ensure_page(self, page: UIPage):
        if not self.verify_page(page):
            self.goto_page(page)

    # def wait_until_stable(self, threshold=0.9995, timeout=10):
    #     while 1:
    #         itt.wait_until_stable(threshold=threshold, timeout=timeout, additional_break_func=self.is_valid_page)
    #         if not self.verify_page(page_loading):
    #             break


ui_control = UI()

if __name__ == '__main__':
    # ui_control.goto_page(page_esc)
    # ui_control.goto_page(page_huanjing_jihua)
    ui_control.goto_page(page_huanjing_jihua)
