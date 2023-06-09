import model.osrs.AI_Sandstone.BotSpecImageSearch as imsearch
import time
import random
import pyautogui
import numpy as np
import utilities.game_launcher as launcher    # |Allows for custom profile launch
import pathlib                                # |
import utilities.ocr as ocr
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot
from pynput.keyboard import Controller as KeyboardController, Key    # | Had to change the name a bit to avoid errors
from pynput.mouse import Controller as MouseController               # |



class SandstoneMiner(OSRSBot, launcher.Launchable):
    def __init__(self):
        #Initialize the bot when some predefined variables, can change some with options
        bot_title = "AI Sandstone"
        description = "Mines and deposits Sandstone"
        super().__init__(bot_title=bot_title, description=description)
        self.hop_for_players = False
        self.player_count = 0
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
        #Saves the Running Time and the Hop When Player Nearby options
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

    def launch_game(self):
        settings = pathlib.Path(__file__).parent.joinpath("custom_settings.properties")
        launcher.launch_runelite(
            properties_path=settings,
            game_title=self.game_title,
            use_profile_manager=True,
            profile_name="AI Sandstone",  # Supply a name if you'd like to save it to PM permanently
            callback=self.log_msg,
        )

    def main_loop(self):
        #Main loop where the bot functions
        self.last_inv_slot = self.win.inventory_slots[27].screenshot()
        self.total_xp = ocr.extract_text(self.win.total_xp, ocr.PLAIN_12, [clr.WHITE])
        self.start_xp = ocr.extract_text(self.win.total_xp, ocr.PLAIN_12, [clr.WHITE])     
        self.open_inventory()
        self.camera_setup()

        

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            ### ----- Perform bot actions here ----- ####
            
            if self.hop_for_players == True:
                self.check_for_players()
                self.hop_for_players_function()
            self.check_last_inv()    
            self.mine_sandstone()            
            self.total_xp_change()
            self.update_progress((time.time() - start_time) / end_time)

               
        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.stop()

    def open_inventory(self):
        #Clicks the inv icon on the control panel
        self.log_msg("Opening Inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()

    def camera_setup(self):        
        #Sets camera facing south, then moves up to a bird eyes view
        self.set_compass_south()
        self.scroll_down()
        pyautogui.keyDown('up')
        time.sleep(random.randint(1010,1300)/1000)
        pyautogui.keyUp('up')        

    def total_xp_change(self):
        #Extracts total xp as a string, loops untill change then updates new total xp
        new_total_xp = ocr.extract_text(self.win.total_xp, ocr.PLAIN_12, [clr.WHITE])
        total_xp_start_time = time.time()    
        while new_total_xp == self.total_xp:
            new_total_xp = ocr.extract_text(self.win.total_xp, ocr.PLAIN_12, [clr.WHITE])
            elapsed_time = time.time() - total_xp_start_time #If no XP change for more than 5 seconds       
            if elapsed_time > 5:  
                self.log_msg("No XP change detected. Retrying mine_sandstone...")
                return self.mine_sandstone()
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
    
    def mine_sandstone(self):
        #Mines tagged sandstone and stops when 
        self.log_msg("mining...")
        sandstone = self.get_nearest_tag(clr.CYAN)
        #If the color recognition bot fails it will run the command again    
        try:
            self.mouse.move_to(sandstone.random_point(), mouseSpeed=self.mouse_speed)
            click_result = self.mouse.click(check_red_click=True)
            if not click_result:
                self.mine_sandstone()
                self.log_msg("Didn't see red click, mining again...")
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying mine_sandstone...")
            time.sleep(1)
            return self.mine_sandstone()

    def calculate_sand(self):
        #Uses total_xp_change() calculations to Calulate total sand earned 
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
        inventory_screenshots = []
        new_inventory_screenshots = []
        for i in range(28):
            inventory_screenshot = self.win.inventory_slots[i].screenshot()
            inventory_screenshots.append(inventory_screenshot)
        for i in range(28):
            new_inventory_screenshot = self.win.inventory_slots[i].screenshot()
            new_inventory_screenshots.append(new_inventory_screenshot)            
        #If the color recognition bot fails it will run the command again  
        try:
            self.mouse.move_to(grinder.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click(check_red_click=True)
        except AttributeError:
            return self.deposit_sandstone()
        #Loops untill the inventory deposits then after the inventory changes it'll reset items and wait a 1.5-2 seconds
        deposit_start_time = time.time()
        while all(np.array_equal(img1, img2) for img1, img2 in zip(inventory_screenshots, new_inventory_screenshots)):
            new_inventory_screenshots = [self.win.inventory_slots[i].screenshot() for i in range(28)]
            elapsed_time = time.time() - deposit_start_time      
            if elapsed_time > 15:  
                self.log_msg("No XP change detected. Retrying mine_sandstone...")
                return self.mine_sandstone()   
        else:
            self.find_text_full()
            print("action grinder finished")
            time.sleep(random.randint(1500, 2000) / 1000)            
    
    def check_for_players(self):
        #Checks the minimap for players then returns +1 to the player count
        other_player = imsearch.BOT_IMAGES.joinpath("sandstone_images", "pink_player_dot.png")        
        if npc_contact := imsearch.search_img_in_rect(other_player, self.win.minimap):       
            self.player_count += 1
            self.log_msg(f"Players nearby notice for {self.player_count} loop")
            return self.player_count
        
        elif self.player_count > 0:
            self.player_count = 0            
            self.log_msg(f"Players loop count reset")
            return self.player_count

    def hop_for_players_function(self):
        #Hops previous world if player was detected for 3 loops
        if self.player_count > 4:
            self.player_count = 0
            self.log_msg("Hopping...")
            self.press_hop_previous()
            time.sleep(20)
            self.open_inventory()
        else:
            return
           
    def check_last_inv(self):
        found_empty_slot = False  # Boolean variable to track if any empty slot is found
        
        for i in range(28):
            slot_location = self.win.inventory_slots[i]
            slot_img = imsearch.BOT_IMAGES.joinpath("sandstone_images", "emptyslot.png")
            
            if slot := imsearch.search_img_in_rect(slot_img, slot_location):
                found_empty_slot = True  # Set the flag to True if any empty slot is found
                break  # Exit the loop if an empty slot is found
        
        if not found_empty_slot:
            self.log_msg("Going to Deposit...")
            self.deposit_sandstone()

    def press_hop_previous(self):
        # Presses hotkey for Quick-hop previous
        keyboard = KeyboardController()

        # Define the hotkey combination
        hotkey_combination = [Key.ctrl_l, Key.shift, Key.left]

        # Simulate the hotkey combination
        for key in hotkey_combination:
            keyboard.press(key)

        time.sleep(random.randint(500, 1000) / 1000)

        # Release the keys in reverse order
        for key in reversed(hotkey_combination):
            keyboard.release(key)

    def scroll_down(self):
        # Scrolls down
        mouse = MouseController()
        for i in range(30):
            mouse.scroll(0, -1)
            random_value = random.choice([0.001, 0.002])
            time.sleep(random_value)

    def find_text_full(self):
        found_text = ocr.find_text("full",self.win.chat,ocr.QUILL_8,clr.BLACK)
        result = bool(found_text)
        if result is True:
            self.logout()
            self.stop()

            
            



    
#need to check full inventory differently to do full inv log off


#pip install pynput

