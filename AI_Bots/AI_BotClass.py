from abc import ABCMeta
import pyautogui as pag
import time
import random
import numpy as np
import utilities.ocr as ocr
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
import cv2
from utilities.geometry import Rectangle, Point
from typing import Union

from model.osrs.osrs_bot import OSRSBot, RuneLiteWindow
import model.osrs.AI_Bots.BotSpecImageSearch as imsearch 


class AI_BotClass(OSRSBot, metaclass=ABCMeta):
    win: RuneLiteWindow = None

    def __init__(self, bot_title, description) -> None:
        super().__init__(bot_title, description)
        self.mouse_speed = "fast"
        self.pin = "7412" # Must be a string
        self.bank_custom_quantity_set = False
        self.bank_withdraw_as = "item"    
        self.bank_setup_set = False

    def bank_open(self):
        #Clicks Yellopw marker for epen bank
        bank = self.get_nearest_tag(clr.YELLOW)
        
        #Trys to click bank, if the color recognition bot fails it will run the command again    
        try:
            self.mouse.move_to(bank.random_point(), mouseSpeed=self.mouse_speed)
            click_result = self.mouse.click(check_red_click=True)
            if not click_result:
                self.bank_open()
                self.log_msg("Didn't see red click, clicking again...")
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying click_bank...")
            time.sleep(1)
            return self.bank_open()
        
        while True:
            bank_pin_template_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_pin_template.png")
            bank_pin_template = imsearch.search_img_in_rect(bank_pin_template_image, self.win.game_view)
            bank_tag_layout_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_tag_layout.png")
            bank_tag_layout = imsearch.search_img_in_rect(bank_tag_layout_image, self.win.game_view)

            if bank_pin_template is None:            
                bank_pin_template = imsearch.search_img_in_rect(bank_pin_template_image, self.win.game_view)
            else:
                self.bank_pin()
                break

            if bank_tag_layout is None:            
                bank_tag_layout = imsearch.search_img_in_rect(bank_tag_layout_image, self.win.game_view)
            else:
                break
        
    def bank_close(self, close='esc', logs=False,):
        """
        Leaves the bank menu using 'ESC' key or top-right '[X]'.

        Args:
            close: 'esc'/'escape/ or 'click' method of closing the bank (default = 'esc')
            logs: (T/F) Logs messages throughout the function (default = False)
        
        """

        ### add a way to scan the screen and wait for the bank interface to close to finish the function
        close = close.lower()

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
                return self.bank_close(close,logs)
               
    def bank_pin(self):
        """
        Enters 4-Digit PIN number.

        Args:
            self.pin = 4-Digit 'string', using numbers 0-9
                            Example: '1234' or '1523'
        
        """

        # 'Bank' plugin - 'Keyboard Bankpin' option
        bank_pin_template_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_pin_template.png")
        bank_pin_template = imsearch.search_img_in_rect(bank_pin_template_image, self.win.game_view)
        # Checks to make sure bank pin template is showing, before going forward

        while bank_pin_template: #Loops while the bank bin template is up
            pin_entered = False #Loops while the pin hasnt been entered then waits till template is gone

            if len(self.pin) != 4:
                self.log_msg("Your pin does not meet the required length of 4 numbers")
                raise SystemExit #Gracefully stops the script if pin isnt 4 characters
            
            

            for digit in self.pin: # Presses the pin with natural keystroke intervals
                if digit not in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
                    self.log_msg("Your pin does not meet the required symboles [0-9]")
                    raise SystemExit #Gracefully stops the script if pin isnt 4 characters
            
                key = 'num' + digit            
                pag.keyDown(key)
                time.sleep(rd.fancy_normal_sample(150,250)/1000) # Key down time
                pag.keyUp(key)
                time.sleep(rd.fancy_normal_sample(150,250)/1000) # Time Between clicks
                
            self.log_msg("Pin Entered")
            pin_entered = True #Returns pin_entered True so the while loop will wait for the pin interface to close without looping again 
            return pin_entered
        while True:
            bank_tag_layout_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_tag_layout.png")
            bank_tag_layout = imsearch.search_img_in_rect(bank_tag_layout_image, self.win.game_view)

            if bank_tag_layout is None:            
                bank_tag_layout = imsearch.search_img_in_rect(bank_tag_layout_image, self.win.game_view)
            else:
                break
             
    def bank_quantity(self, quantity: Union[str, int], x=14):
        """
        sets custom quantity.

        Args:
            button: '1', '5', '10', 'X', or 'ALL' (case doesn't matter)
            x : Custom Quantity Number (Default = 14") 
                    
        """
        # Converts string to lower for edge cases
        button = str(quantity.lower())

        # Image loading
        bank_1_on_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_1_on.png")
        bank_1_off_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_1_off.png")
        bank_5_on_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_5_on.png")
        bank_5_off_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_5_off.png")
        bank_10_on_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_10_on.png")
        bank_10_off_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_10_off.png")
        bank_x_on_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_x_on.png") # Not currently used
        bank_x_off_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_x_off.png")
        bank_all_on_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_all_on.png")
        bank_all_off_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_all_off.png")

        if button == '1':
            # Checks to see if 'off quantity' image needs to be turned on, Then clicks
            bank_1_off = imsearch.search_img_in_rect(bank_1_off_image, self.win.game_view)
            try:
                self.mouse.move_to(bank_1_off.random_point(), mouseSpeed=self.mouse_speed)
                self.mouse.click()
                self.log_msg(f"Bank Quantity Set to {button}")

            # Checks to see if 'on quantity' is already turned on, then returns
            except AttributeError:
                bank_1_on = imsearch.search_img_in_rect(bank_1_on_image, self.win.game_view)
                if bank_1_on != None:                
                    self.log_msg(f"Bank Quantity already set to {button}")

                # If off or on image isn't found Close script    
                else:
                    self.log_msg(f"Couldn't find image of '{button}' quantity, ending script")
                    raise SystemExit #Gracefully stops the script if pin isnt 4 characters

        elif button == '5':
            # Checks to see if 'off quantity' image needs to be turned on, Then clicks
            bank_5_off = imsearch.search_img_in_rect(bank_5_off_image, self.win.game_view)
            try:
                self.mouse.move_to(bank_5_off.random_point(), mouseSpeed=self.mouse_speed)
                self.mouse.click()
                self.log_msg(f"Bank Quantity Set to {button}")

            # Checks to see if 'on quantity' is already turned on, then returns
            except AttributeError:
                bank_5_on = imsearch.search_img_in_rect(bank_5_on_image, self.win.game_view)
                if bank_5_on != None:                
                    self.log_msg(f"Bank Quantity already set to {button}")

                # If off or on image isn't found Close script    
                else:
                    self.log_msg(f"Couldn't find image of '{button}' quantity, ending script")
                    raise SystemExit #Gracefully stops the script if pin isnt 4 characters
                
        elif button == '10':
            # Checks to see if 'off quantity' image needs to be turned on, Then clicks
            bank_10_off = imsearch.search_img_in_rect(bank_10_off_image, self.win.game_view)
            try:
                self.mouse.move_to(bank_10_off.random_point(), mouseSpeed=self.mouse_speed)
                self.mouse.click()
                self.log_msg(f"Bank Quantity Set to {button}")

            # Checks to see if 'on quantity' is already turned on, then returns
            except AttributeError:
                bank_10_on = imsearch.search_img_in_rect(bank_10_on_image, self.win.game_view)
                if bank_10_on != None:                
                    self.log_msg(f"Bank Quantity already set to {button}")

                # If off or on image isn't found Close script    
                else:
                    self.log_msg(f"Couldn't find image of '{button}' quantity, ending script")
                    raise SystemExit #Gracefully stops the script if pin isnt 4 characters

        elif button == 'all':
            # Checks to see if 'off quantity' image needs to be turned on, Then clicks
            bank_all_off = imsearch.search_img_in_rect(bank_all_off_image, self.win.game_view)
            try:
                self.mouse.move_to(bank_all_off.random_point(), mouseSpeed=self.mouse_speed)
                self.mouse.click()
                self.log_msg(f"Bank Quantity Set to {button}")

            # Checks to see if 'on quantity' is already turned on, then returns
            except AttributeError:
                bank_all_on = imsearch.search_img_in_rect(bank_all_on_image, self.win.game_view)
                if bank_all_on != None:                
                    self.log_msg(f"Bank Quantity already set to {button}")

                # If off or on image isn't found Close script    
                else:
                    self.log_msg(f"Couldn't find image of '{button}' quantity, ending script")
                    raise SystemExit #Gracefully stops the script if pin isnt 4 characters

        elif button == 'x':

            #If the quantity was set earlier skip over function
            if self.bank_custom_quantity_set == True:
                self.log_msg(f"Custom bank quantity already set too {x}")

            # Checks to see if 'off quantity' image needs to be turned on, Then clicks
            else:
                bank_x_off = imsearch.search_img_in_rect(bank_x_off_image, self.win.game_view)
                try:
                    self.mouse.move_to(bank_x_off.random_point(), mouseSpeed=self.mouse_speed)
                    self.mouse.right_click()
                    set_custom_quantity_dropbox = ocr.find_text("custom",self.win.game_view,ocr.BOLD_12,clr.WHITE)
                    self.mouse.move_to(set_custom_quantity_dropbox[0].random_point(), mouseSpeed=self.mouse_speed)
                    self.mouse.click()                    
                    enter_amount_text = ocr.find_text("Enter amount",self.win.chat,ocr.BOLD_12,clr.BLACK)
                    while enter_amount_text == []:
                        enter_amount_text = ocr.find_text("Enter amount",self.win.chat,ocr.BOLD_12,clr.BLACK)
                    time.sleep(rd.fancy_normal_sample(300,600)/1000) # Natural mental processing speed break before typing
                    for digit in str(x): # Presses the custom quantity with natural presses
                        key = 'num' + digit          
                        pag.keyDown(key)
                        time.sleep(rd.fancy_normal_sample(90,150)/1000) # Key down time
                        pag.keyUp(key)
                        time.sleep(rd.fancy_normal_sample(90,150)/1000) # Time Between clicks
                    self.log_msg(f"Bank Quantity Set to {button}={x}")
                    self.bank_custom_quantity_set = True
                    return self.bank_custom_quantity_set

                # If 'off quantity' isn't found and wasn't previously set stop running script
                except AttributeError:
                    self.log_msg(f"Couldn't find image of '{button}' quantity, ending script")
                    raise SystemExit #Gracefully stops the script if pin isnt 4 characters
    
    def bank_quick_deposit_inv(self):
        """
        Quickly Deposits inventory by clicking the deposit inventory icon in the bottom right

        Args: None
        """
        bank_depo_inv_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_depo_inv.png")
        bank_depo_inv = imsearch.search_img_in_rect(bank_depo_inv_image, self.win.game_view)
        try:
            self.log_msg("Quick Depositing Inventory")
            self.mouse.move_to(bank_depo_inv.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()
            time.sleep(rd.fancy_normal_sample(150,250)/1000)
        
        except AttributeError:
            self.log_msg("AttributeError occurred. can't find Quick Deposit Inventory")
            raise SystemExit #Gracefully stops the script if deposit inventory isnt found
        
    def bank_quick_deposit_worn(self):
        """
        Quickly Deposits Worn Items by clicking the deposit worn items icon in the bottom right
        
        Args: None
        """
        bank_depo_worn_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_depo_worn.png")
        bank_depo_worn = imsearch.search_img_in_rect(bank_depo_worn_image, self.win.game_view)
        try:
            self.log_msg("Quick Depositing Worn Items")
            self.mouse.move_to(bank_depo_worn.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()
            time.sleep(rd.fancy_normal_sample(150,250)/1000)
        
        except AttributeError:
            self.log_msg("AttributeError occurred. Can't find Quick Deposit Worn Items")
            raise SystemExit #Gracefully stops the script if deposit inventory isnt found

    def bank_withdraw_note(self):
        """
        Clicks the withdraw as note icon to switch from items to notes. Skips if already set to notes
        
        Args: None
        """
        if self.bank_withdraw_as != "note":        
            bank_note_toggle_off_img = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_note_toggle_off.png")
            bank_note_toggle_off = imsearch.search_img_in_rect(bank_note_toggle_off_img, self.win.game_view)
            try:
                self.log_msg("Clicking Bank Note Toggle ON")
                self.mouse.move_to(bank_note_toggle_off.random_point(), mouseSpeed=self.mouse_speed)
                self.mouse.click()
                self.bank_withdraw_as = "note"
                return self.bank_withdraw_as
            
            except AttributeError:
                self.log_msg("AttributeError occurred. Can't find Bank Note Toggle trying 1 more time")
                time.sleep(1)
                bank_note_toggle_off = imsearch.search_img_in_rect(bank_note_toggle_off_img, self.win.game_view)
                try:                
                    self.log_msg("Clicking Bank Note Toggle ON")
                    self.mouse.move_to(bank_note_toggle_off.random_point(), mouseSpeed=self.mouse_speed)
                    self.mouse.click()
                    self.bank_withdraw_as = "note"
                    return self.bank_withdraw_as
                    

                except AttributeError:
                    self.log_msg("AttributeError occurred. Can't find Bank Note Toggle cutting script")
                    raise SystemExit #Gracefully stops the script if deposit inventory isnt found
        
    def bank_withdraw_item(self):
        """
        Clicks the withdraw as item icon to switch from notes to items. Skips if already set to items
        
        Args: None
        """
        if self.bank_withdraw_as != "item":        
            bank_item_toggle_off_img = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_item_toggle_off.png")
            bank_item_toggle_off = imsearch.search_img_in_rect(bank_item_toggle_off_img, self.win.game_view)
            try:
                self.log_msg("Clicking Bank item Toggle ON")
                self.mouse.move_to(bank_item_toggle_off.random_point(), mouseSpeed=self.mouse_speed)
                self.mouse.click()
                self.bank_withdraw_as = "item"
                return self.bank_withdraw_as
            
            except AttributeError:
                self.log_msg("AttributeError occurred. Can't find Bank item Toggle")
                raise SystemExit #Gracefully stops the script if deposit inventory isnt found
            
    def bank_search(self, item: str, set_quantity: Union[str, int] =1, click_times=1, x_value=14,):
        """
        Searches bank for desired item, clicks if avaliable. 
        Ability to set custom quantity, number of times to click item, and set custom x quantity value.

        Args:
            item: 'item name'
                    
        Kwargs:
            set_quantity: 1, 5, 10, 'all', 'x'
            click_times: Number of times for mouse to click the item
            x_value: custom x value when setting [x] quantity
                    
        """
        quantity = str(set_quantity).lower()

        if quantity == 'all':
            self.deposit_quantity_set('all')
        elif quantity == '1':
            self.deposit_quantity_set('1')
        elif quantity == '5':
            self.deposit_quantity_set('5')
        elif quantity == '10':
            self.deposit_quantity_set('10')
        elif quantity == 'x':
            self.deposit_quantity_set('x', x= x_value)

        item_formated = item.replace(' ', '_')
        item_name_png = item_formated + "_bank.png"
        item_name_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images","bank_items", item_name_png)
        item_name = imsearch.search_img_in_rect(item_name_image, self.win.game_view)

        # If item is found move mouse to item
        if item_name != None:
            self.log_msg(f"Moving mouse to '{item}'")
            self.mouse.move_to(item_name.random_point(), mouseSpeed=self.mouse_speed)

        # If item isn't found, search bank for the item
        elif item_name == None:
            self.log_msg(f"Couldn't find image of '{item}' in screen, will search for it")
            bank_search_off_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_search_off.png")
            bank_search_off = imsearch.search_img_in_rect(bank_search_off_image, self.win.game_view)
            bank_search_on_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_search_on.png") #Used in attribution error block later
            bank_search_on = imsearch.search_img_in_rect(bank_search_on_image, self.win.game_view)
            # Move mouse to search icon and click
            try:                
                self.mouse.move_to(bank_search_off.random_point(), mouseSpeed=self.mouse_speed)
                self.mouse.click()

                #Loops after search icon clicked and waits for search text
                while True:
                    found_text = ocr.find_text("Show items",self.win.chat,ocr.BOLD_12,clr.BLACK)
                    text_found_result = bool(found_text)
                    # Once search text found use PyAutoGUI to type in the 'item' parameter
                    if text_found_result is True:
                        for char in item:
                            time.sleep(rd.fancy_normal_sample(90,150)/1000) 
                            pag.keyDown(char)
                            time.sleep(rd.fancy_normal_sample(90,150)/1000)
                            pag.keyUp(char)
                        time.sleep(rd.fancy_normal_sample(300,600)/1000) # Natural time delay to look for searched item
                        break

                # Search for item again after typing to search
                item_name = imsearch.search_img_in_rect(item_name_image, self.win.game_view)
                try:
                    self.log_msg(f"Moving mouse to '{item}'")
                    self.mouse.move_to(item_name.random_point(), mouseSpeed=self.mouse_speed)
                    

                # If a NONE type error occurs finding the searched item, move on without item
                except AttributeError:
                    self.log_msg(f"Couldn't find image of '{item}', make sure it is in the bank")
                    raise SystemExit #Gracefully stops the script if item isn't found                 

            # If a NONE type error occurs finding the search icon, Cut the Script    
            except AttributeError:   
                try:                
                    self.mouse.move_to(bank_search_on.random_point(), mouseSpeed=self.mouse_speed)
                    self.mouse.click()
                    time.sleep(rd.fancy_normal_sample(90,150)/1000)
                    self.mouse.click()
                    time.sleep(rd.fancy_normal_sample(90,150)/1000) 
                    #Loops after search icon clicked and waits for search text
                    while True:
                        found_text = ocr.find_text("Show items",self.win.chat,ocr.BOLD_12,clr.BLACK)
                        text_found_result = bool(found_text)
                        # Once search text found use PyAutoGUI to type in the 'item' parameter
                        if text_found_result is True:
                            for char in item:
                                time.sleep(rd.fancy_normal_sample(90,150)/1000) 
                                pag.keyDown(char)
                                time.sleep(rd.fancy_normal_sample(90,150)/1000)
                                pag.keyUp(char)
                            time.sleep(rd.fancy_normal_sample(300,600)/1000) # Natural time delay to look for searched item
                            break

                    # Search for item again after typing to search
                    item_name = imsearch.search_img_in_rect(item_name_image, self.win.game_view)
                    try:
                        self.log_msg(f"Moving mouse to '{item}'")
                        self.mouse.move_to(item_name.random_point(), mouseSpeed=self.mouse_speed)
                        

                    # If a NONE type error occurs finding the searched item, move on without item
                    except AttributeError:
                        self.log_msg(f"Couldn't find image of '{item}', make sure it is in the bank")
                        raise SystemExit #Gracefully stops the script if item isn't found                 

                # If a NONE type error occurs finding the search icon, Cut the Script    
                except AttributeError:
                    self.log_msg(f"Couldn't find image of search icon on/off")
                    raise SystemExit #Gracefully stops the script if item isn't found  
            
    
        # Loops number of times equal to 'click_times' parameter after image has been (found) or (searched and found)
        for i in range(click_times):
            self.mouse.click()
            time.sleep(rd.fancy_normal_sample(150,250)/1000)

    def bank_tab(self,bank_tab_number):
        """
        Clicks the bank tag number selected.
        
        Args: 
            bank_tab_number (int): 1-10 
        """

        bank_tag_layout_image = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_tag_layout.png")
        bank_tag_layout = imsearch.search_img_in_rect(bank_tag_layout_image, self.win.game_view) #start 3 pixel from left              
        
        tag_width = 35 # Clickable area
        tag_height = 31 # Height before the tag curve top-right
        tag_gap = 5 # Dead space between tags
        tag_number = 10 # Number of possible tags

        x = bank_tag_layout.left + 3  # start 3 pixels to the right of bank_tag_layout
        y = bank_tag_layout.top  # aligned with the top of bank_tag_layout

        self.bank_tags = []
        for i in range(tag_number):
            left = x + i * (tag_width + tag_gap)
            top = y
            self.bank_tags.append(Rectangle(left, top, tag_width, tag_height))

        self.mouse.move_to(self.bank_tags[bank_tab_number].random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()

    def bank_rearrange_swap(self):
        bank_swap_off_img = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_swap_off.png")
        bank_swap_off = imsearch.search_img_in_rect(bank_swap_off_img, self.win.game_view)
        if bank_swap_off != None:
            self.mouse.move_to(bank_swap_off.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()

    def bank_rearrange_insert(self):
        bank_insert_off_img = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_insert_off.png")
        bank_insert_off = imsearch.search_img_in_rect(bank_insert_off_img, self.win.game_view)
        if bank_insert_off != None:
            self.mouse.move_to(bank_insert_off.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()

    def bank_placeholder_on(self):
        bank_placeholder_off_img = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_placeholder_off.png")
        bank_placeholder_off = imsearch.search_img_in_rect(bank_placeholder_off_img, self.win.game_view)
        if bank_placeholder_off != None:
            self.mouse.move_to(bank_placeholder_off.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()     

    def bank_placeholder_off(self):
        bank_placeholder_on_img = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_placeholder_on.png")
        bank_placeholder_on = imsearch.search_img_in_rect(bank_placeholder_on_img, self.win.game_view)
        if bank_placeholder_on != None:
            self.mouse.move_to(bank_placeholder_on.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()        
        

#### TODO Check below functions

    def bank_setup(self,
                   rearrange_mode="swap",
                   withdraw="item",
                   quantity: Union[str,int]="1", x_quantity=14,
                   placeholder="on") -> bool:
        """
        Sets up the intial look at your bank and toggles the desired buttons. Will pass if done before. 
        
        Args: 
            rearrange_mode (str) = "swap" or "insert" --- Toggles the swap 'swap' or 'insert' rearrange buttons

            withdraw (str) = "item" or "note" --- Toggles the item/note withdrawl button

            quantity (str or int) = '1' '5' '10' 'x' 'all' ---- Changes quantity selected

            x_quantity (int) = Changes the custom quantity for 'x'

            placeholder (str) = "on" or "off" ---- Chances is placeholders are set or not

        Returns:
            self.bank_setup_set = True
        """

        if self.bank_setup_set is False:
            # Input pin if screen is up
            self.log_msg("Bank setup: Inputting Bank Pin")
            self.bank_pin()
            self.log_msg(f"Bank setup: Bank Pin set to ****")

            # Rearrange buttons
            self.log_msg(f"Bank setup: Setting up Rearrange")
            if rearrange_mode == "swap":
                self.bank_rearrange_swap()
                self.log_msg(f"Bank setup: Rearrange set to {rearrange_mode}")
            elif rearrange_mode == "insert":
                self.bank_rearrange_insert()
                self.log_msg(f"Bank setup: Rearrange set to {rearrange_mode}")
            else:
                self.log_msg("Rearrange_mode input invalid, check spelling.")

            # Withdraw as buttons
            self.log_msg(f"Bank setup: Setting up Withdraw")
            if withdraw == "item":
                self.bank_withdraw_item()
                self.log_msg(f"Bank setup: Withdraw set to {withdraw}")
            elif withdraw == "note":
                self.bank_withdraw_note()
                self.log_msg(f"Bank setup: Withdraw set to {withdraw}")
            else:
                self.log_msg("Withdraw input invalid, check spelling.")

            # Bank quantity
            self.log_msg(f"Bank setup: Setting up Quantity")
            if quantity == "1":
                self.bank_quantity(quantity)
                self.log_msg(f"Bank setup: Quantity set to {quantity}")
            elif quantity == "5":
                self.bank_quantity(quantity)
                self.log_msg(f"Bank setup: Quantity set to {quantity}")
            elif quantity == "10":
                self.bank_quantity(quantity)
                self.log_msg(f"Bank setup: Quantity set to {quantity}")
            elif quantity == "all":
                self.bank_quantity(quantity)
                self.log_msg(f"Bank setup: Quantity set to {quantity}")
            elif quantity == "x":
                self.bank_quantity(quantity,x=x_quantity)
                self.log_msg(f"Bank setup: Quantity set to {quantity}, and x set to {x_quantity}")            
            else:
                self.log_msg("Quantity input invalid, check spelling.")

            # Placeholders Inserters
            self.log_msg(f"Bank setup: Setting up Placehoder")
            if placeholder == "on":
                self.bank_withdraw_item()
                self.log_msg(f"Bank setup: Placehoder {placeholder}")
            elif placeholder == "off":
                self.bank_withdraw_note()
                self.log_msg(f"Bank setup: Placehoder {placeholder}")
            else:
                self.log_msg("Withdraw input invalid, check spelling.")

            # Setting Class veriable to skip future function calls
            self.bank_setup_set = True
            return self.bank_setup_set

    def inv_full_check(self) -> bool:
        """
        Checks if inventory is full.

        Returns:
            True: If inventory is full
            False: If inventory is not full 
                
        """
        self.log_msg("Checking if 'inv' is full")        
        for i in range(28):
            slot_location = self.win.inventory_slots[i]
            empty_slot_img = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_empty_slot.png")
            if slot := imsearch.search_img_in_rect(empty_slot_img, slot_location):
                self.log_msg("Empty slot found 'inv' is not full")
                return False
        self.log_msg("No empty slot found, 'inv' is full")
        return True

    def inv_empty_check(self) -> bool:
        """
        Checks if inventory is empty.

        Returns:
            True: If inventory is empty
            False: If inventory is not empty 
                
        """
        self.log_msg("Checking if 'inv' is empty")        
        for i in range(28):
            slot_location = self.win.inventory_slots[i]
            empty_slot_img = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_empty_slot.png")
            slot = imsearch.search_img_in_rect(empty_slot_img, slot_location)
            if slot == None:
                self.log_msg("No empty slots found, 'inv' is full")
                return False
        self.log_msg("Empty slot found 'inv' is not full")
        return True
    
    def inv_empty_slot_count(self) -> int:
        """
        Counts the Number of empty spots in an inventory.

        Returns:
            int = Number of empty slots 
                
        """
        self.log_msg("Checking number of empty slots")
        empty_slot_count = 0        
        for i in range(28):
            slot_location = self.win.inventory_slots[i]
            empty_slot_img = imsearch.BOT_IMAGES.joinpath("AI_BotClass_Images", "bank_empty_slot.png")
            if slot := imsearch.search_img_in_rect(empty_slot_img, slot_location):
                empty_slot_count += 1
        return empty_slot_count
                
           

    def camera_zoom(self):
        pass

    def camera_angle(self):
        pass

    def camera_setup(self):
        pass

    def minimap_zoom(self):
        #24 clicks to zoom all the way out
        pass

    def camera_compass(self):
        pass










        

        