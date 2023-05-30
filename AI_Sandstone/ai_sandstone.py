import model.osrs.AI_Sandstone.BotSpecImageSearch as imsearch
import time
import random
import pyautogui
import numpy as np
import utilities.ocr as ocr
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
        self.rocks_mined = 0
        self.gained_xp = 0
        self.one_kg = 0
        self.two_kg = 0
        self.five_kg = 0
        self.ten_kg = 0
        self.buckets_of_sand = 0        
        self.running_time = 180
        self.mouse_speed = "fastest"

    def create_options(self):
        #Creates the UI options at startup, running time is [1minute to 6hrs], option to hop when players are nearby the bot   
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 360)
        self.options_builder.add_checkbox_option("hop_when_people_nearby", "Hop when people are nearby?", ["Yes"])

    def save_options(self, options: dict):
        """
        For each option in the dictionary, if it is an expected option, save the value as a property of the bot.
        If any unexpected options are found, log a warning. If an option is missing, set the options_set flag to
        False.
        """
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "hop_when_people_nearby":
                self.hop_for_players = options[option] != []
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"Hop for nearby players: {'True' if self.hop_for_players else 'False'}.")
        self.log_msg("Options set successfully.")
        self.options_set = True

    def main_loop(self):

        # Setup APIs
        # api_m = MorgHTTPSocket()
        # api_s = StatusSocket()

        self.last_inv_slot = self.win.inventory_slots[27].screenshot()
        self.total_xp = ocr.extract_text(self.win.total_xp, ocr.PLAIN_12, [clr.WHITE])
        self.start_xp = ocr.extract_text(self.win.total_xp, ocr.PLAIN_12, [clr.WHITE])
        
        

        # self.open_inventory()

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            #### ----- Perform bot actions here ----- ###
            self.mine_sandstone()
            self.total_xp_change()
            self.check_last_inv()



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

    def camera_setup(self):        
        #Sets camera facing south, then move to a bird eyes view
        self.set_compass_south()
        pyautogui.keyDown('up')
        time.sleep(random.randint(1010,1300)/1000)
        pyautogui.keyUp('up')
        #TODO implement zoom out

    def total_xp_change(self):
        #Extracts total xp as a string, loops untill change then updates new total xp
        new_total_xp = ocr.extract_text(self.win.total_xp, ocr.PLAIN_12, [clr.WHITE])    
        while new_total_xp == self.total_xp:
            new_total_xp = ocr.extract_text(self.win.total_xp, ocr.PLAIN_12, [clr.WHITE])
            pass
        else:      
            #Rock mined counter goes up      
            self.rocks_mined += 1
            self.log_msg(f"You've mined {self.rocks_mined} rocks!")

            #Calcualtes what sand you mined based on xp change and logs it
            gained_xp = int(new_total_xp) - int(self.total_xp)
            if gained_xp == 30:
                self.one_kg += 1
            elif gained_xp == 40:
                self.two_kg += 1
            elif gained_xp == 50:
                self.five_kg += 1
            else:
                self.ten_kg +=1

            #Sets new total XP and calculates total gained
            self.total_xp = ocr.extract_text(self.win.total_xp, ocr.PLAIN_12, [clr.WHITE])
            total_gained_xp = int(self.total_xp) - int(self.start_xp)
            formated_gained_xp = format(total_gained_xp, ",")
            self.log_msg(f"You've gained {formated_gained_xp} xp!")

            #Calculates sand and logs the assosiated logs for loggging purposes
            self.calculate_sand()
            self.log_msg(f"1kg Sandstone x{self.one_kg},  2kg Sandstone x{self.two_kg},  5kg Sandstone x{self.five_kg},  10kg Sandstone x{self.ten_kg}")
            self.log_msg(f"You have collected in total {self.buckets_of_sand} buckets of sand")

                        
            return self.total_xp
    
    def mine_sandstone(self):
        # Mines tagged sandstone and stops when 
        self.log_msg("mining...")
        sandstone = self.get_nearest_tag(clr.CYAN)    
        try:
            self.mouse.move_to(sandstone.random_point(), mouseSpeed=self.mouse_speed)
            click_result = self.mouse.click(check_red_click=True)
            if not click_result:
                self.mine_sandstone()
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying mine_sandstone...")
            time.sleep(1)
            return self.mine_sandstone()

    def calculate_sand(self):
        one_sand = self.one_kg * 1
        two_sand = self.two_kg * 2
        four_sand = self.five_kg * 4
        eight_sand = self.ten_kg * 8
        self.buckets_of_sand = one_sand + two_sand + four_sand + eight_sand
        return self.buckets_of_sand

    def deposit_sandstone(self):
        #clicks to deposit at grinder
        self.log_msg("depo...")
        grinder = self.get_nearest_tag(clr.YELLOW)
        inventory_1 = self.win.inventory_slots[27].screenshot()
        inventory_2 = self.win.inventory_slots[27].screenshot()
        try:
            self.mouse.move_to(grinder.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click(check_red_click=True)
        except AttributeError:
            return self.deposit_sandstone()
        
        while np.array_equal(inventory_1, inventory_2):
            inventory_2 = self.win.inventory_slots[27].screenshot()    
        else:
            print("action grinder finished")
            time.sleep(random.randint(1500, 2000) / 1000)            
            self.items = 0
            return self.items
 

            
            

    def check_last_inv(self):
        #TODO, UPDATE SO IT CHECKS AGAINST A TRUE EMPTY TILE AND IF FILLED BY GEOD CHECK NEXT ONE DOWN
        # Takes the screenshot at the beginning of the bot and compares it to the current screenshot to determine the full inventory
        self.new_last_inv = self.win.inventory_slots[27].screenshot()
        while True:
            if np.array_equal(self.new_last_inv, self.last_inv_slot):
                break
            else:
                print("tryna depo")
                self.deposit_sandstone()                
                self.new_last_inv = self.win.inventory_slots[27].screenshot()



    
        
            

    
#check for xp change doesnt always work incase someone steals your sandstone
#geods last inventory
#sometime it doesnt see rocks with one error
#has to mine again at 28


#add time running counter


