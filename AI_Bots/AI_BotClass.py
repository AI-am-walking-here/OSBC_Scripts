from abc import ABCMeta
import pyautogui as pag
import time
import random
import pyautogui
import numpy as np
import utilities.ocr as ocr
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd

from model.osrs.osrs_bot import OSRSBot, RuneLiteWindow
import model.osrs.AI_Bots.BotSpecImageSearch as imsearch 


class AI_BotClass(OSRSBot, metaclass=ABCMeta):
    win: RuneLiteWindow = None

    def __init__(self, bot_title, description) -> None:
        super().__init__("AI_BotClass", bot_title, description)
        self.mouse_speed = "fast"


    def close_bank(self, close='esc', logs=False,):
        """
        Leaves the bank menu using 'ESC' key or top-right '[X]'.

        Args:
            close: 'esc'/'escape/ or 'click' method of closing the bank (default = 'esc')
            logs: (T/F) Logs messages throughout the function (default = False)
        
        """
        close = close.lower

        if close in ['escape', 'esc']: # Close choice is 'esc'
            if logs:
                self.log_msg("Closing bank with 'ESC'")
            pag.keyDown('esc')
            time.sleep(rd.fancy_normal_sample(120,170)/1000)
            pag.keyUp('esc')

        elif close == 'click': # Close choice is 'close'
            if logs:
                self.log_msg("Closing bank with 'Top-right [X]'")
            bank_close_button_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_close.png")
            bank_close_button = imsearch.search_img_in_rect(bank_close_button_image, self.win.game_view)

        try:
            self.mouse.move_to(bank_close_button.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()
            
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying click_angler_spot...")
            time.sleep(2)
            return self.close_bank(close,logs)


        

        