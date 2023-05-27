import model.osrs.AI_GOTR.BotSpecImageSearch as imsearch
import time
import random
import pyautogui
import numpy as np
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket


class SandstoneMiner(OSRSBot):
    def __init__(self):
        bot_title = "AI Sandstone"
        description = "Mines and deposits Sandstone"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 60
        self.mouse_speed = "fastest"

    def create_options(self):
        """
        Use the OptionsBuilder to define the options for the bot. For each function call below,
        we define the type of option we want to create, its key, a label for the option that the user will
        see, and the possible values the user can select. The key is used in the save_options function to
        unpack the dictionary of options after the user has selected them.
        """
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 500)
        self.options_builder.add_text_edit_option("text_edit_example", "Text Edit Example", "Placeholder text here")
        self.options_builder.add_checkbox_option("multi_select_example", "Multi-select Example", ["A", "B", "C"])
        self.options_builder.add_dropdown_option("menu_example", "Menu Example", ["A", "B", "C"])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "text_edit_example":
                self.log_msg(f"Text edit example: {options[option]}")
            elif option == "multi_select_example":
                self.log_msg(f"Multi-select example: {options[option]}")
            elif option == "menu_example":
                self.log_msg(f"Menu example: {options[option]}")
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):

        # Setup APIs
        # api_m = MorgHTTPSocket()
        # api_s = StatusSocket()
        self.items = 0
        self.last_inv_slot = self.win.inventory_slots[27].screenshot()
        self.is_inv_full()

        # self.open_inventory()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # -- Perform bot actions here --







             #deposits too fast and ties to click rock while moving causing a miss click
           
            # Code within this block will LOOP until the bot is stopped.

            self.update_progress((time.time() - start_time) / end_time)

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()




    def open_inventory(self):
        #Clicks the inv icon
        self.log_msg("Opening Inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()

    def mine_sandstone(self):
        #mines tagged sandstone and stops when 
        # self.log_msg("mining...")
        sandstone = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(sandstone.random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()

    def deposit_sandstone(self):
        #clicks to deposit at grinder
        self.log_msg("depo...")
        grinder = self.get_nearest_tag(clr.YELLOW)
        self.mouse.move_to(grinder.random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()
        inventory_1 = self.win.inventory_slots[27].screenshot()
        inventory_2 = self.win.inventory_slots[27].screenshot()
        while np.array_equal(inventory_1, inventory_2):
            inventory_2 = self.win.inventory_slots[27].screenshot()    
        else:
            print("action grinder finished")
            self.items = 0
            return self.items
 
    def mining_complete(self, n):
        start_time = time.time()
        inventory_1 = self.win.inventory_slots[n].screenshot()
        inventory_2 = self.win.inventory_slots[n].screenshot()
        
        while True:
            if not np.array_equal(inventory_1, inventory_2):
                break
            
            if time.time() - start_time >= 5:
                new_time = time.time() - start_time
                print("had to click mining again")
                self.mine_sandstone()
                self.mining_complete(n)
                return
            inventory_2 = self.win.inventory_slots[n].screenshot()

    def check_last_inv(self):
        # Takes the screenshot at the beginning of the bot and compares it to the current screenshot to determine the full inventory
        self.new_last_inv = self.win.inventory_slots[27].screenshot()
        while True:
            if np.array_equal(self.new_last_inv, self.last_inv_slot):
                print("last inv is equal")
                break
            else:
                print("tryna depo")
                self.deposit_sandstone()
                time.sleep(random.randint(1500, 2000) / 1000)
                self.new_last_inv = self.win.inventory_slots[27].screenshot()

    def camera_setup(self):
        #Sets camera facing east, then move to a bird eyes view
        self.set_compass_south()
        pyautogui.keyDown('up')
        time.sleep(random.randint(1010,1300)/1000)
        pyautogui.keyUp('up')
        #need zoom out

    def is_inv_full(self):
        """
        Checks if inventory is full.
        Returns: bool
        """
        for i in range(27):            
            slot_img = imsearch.BOT_IMAGES.joinpath("sandstone_images", "emptyslot.png")
            compare = imsearch.search_img_in_rect(slot_img,self.win.inventory_slots[i])
            while not compare:
                print(f"slot in {i+1}")
            
        
            

    

#geods
#sometime it doesnt see rocks with one error
#has to mine again at 28
#issue with none object on grinder
#add total sand counter
#add mined coutner
#add time running counter

#1k= 1
#2k = 2
#5k = 4
#10k = 8
