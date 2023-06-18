from abc import ABCMeta
import pyautogui as pag
import time
import random
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
        self.pin = "1234" # Must be a string


    def close_bank(self, close='esc', logs=False,):
        """
        Leaves the bank menu using 'ESC' key or top-right '[X]'.

        Args:
            close: 'esc'/'escape/ or 'click' method of closing the bank (default = 'esc')
            logs: (T/F) Logs messages throughout the function (default = False)
        
        """

        ### add a way to scan the screen and wait for the bank interface to close to finish the function
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

   
    def enter_pin(self):
        # 'Bank' plugin - 'Keyboard Bankpin' option
        bank_pin_template_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_pin_template.png")
        bank_pin_template = imsearch.search_img_in_rect(bank_pin_template_image, self.win.game_view)
        # Checks to make sure bank pin template is showing, before going forward

        while bank_pin_template: #Loops while the bank bin template is up
            pin_entered = False #Loops while the pin hasnt been entered then waits till template is gone

            if len(self.pin) != 4:
                self.log_msg("Your pin does not meet the required length of 4 numbers")
                raise SystemExit #Gracefully stops the script if pin isnt 4 characters
            
            if digit not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
                self.log_msg("Your pin does not meet the required symboles [0-9]")
                raise SystemExit #Gracefully stops the script if pin isnt 4 characters

            for digit in self.pin: # Presses the pin with natural keystroke intervals
                key = 'num' + digit            
                pag.keyDown(key)
                time.sleep(rd.fancy_normal_sample(150,250)/1000) # Key down time
                pag.keyUp(key)
                time.sleep(rd.fancy_normal_sample(150,250)/1000) # Time Between clicks
                
            pin_entered = True #Returns pin_entered True so the while loop will wait for the pin interface to close without looping again 
            return pin_entered
            

        
    


        

        