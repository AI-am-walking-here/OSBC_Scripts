import model.osrs.AI_Angler.BotSpecImageSearch as imsearch         # Image 
from pynput.keyboard import Controller as KeyboardController, Key    # | 
from pynput.mouse import Controller as MouseController               # |

import utilities.game_launcher as launcher    # |Allows for custom profile launch
import pathlib                                # |

import time
import random
import pyautogui
import numpy as np
import utilities.ocr as ocr
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.random_util as rd
from model.osrs.osrs_bot import OSRSBot



class AnglerFisher(OSRSBot, launcher.Launchable):
    def __init__(self):
        # Initialize the bot when some predefined variables, can change some with options
        bot_title = "AI_Angler Fisher"
        description = "Fishes Angler fish at Port Piscarilius"
        super().__init__(bot_title=bot_title, description=description)
        self.angler_hat = 0
        self.angler_top = 0
        self.angler_waders = 0
        self.angler_boots = 0
        self.angler_gloves = 0

        self.running_time = 180
        self.mouse_speed = "fast"       

    def create_options(self):
        # Creates the UI options at startup, running time is [1minute to 6hrs], option to hop when players are nearby the bot   
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 360)


    def save_options(self, options: dict):
        # Saves the Running Time and the Hop When Player Nearby options
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
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
            profile_name="AI AnglerFisher",  # Supply a name if you'd like to save it to PM permanently
            callback=self.log_msg,
        )

    def main_loop(self):
        # Main loop where the bot functions       
        # Put launch setup code here


        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            ### ----- Perform bot actions below here ----- ####
            self.check_equiptment()

            # self.camera_setup()     
            # self.click_minimap_from_bank()
            # self.click_minimap_from_fishing_spot()
            self.update_progress((time.time() - start_time) / end_time)
            ### ----- Perform bot actions above here ----- ####

               
        self.update_progress(1)
        self.log_msg("Finished.")
        self.logout()
        self.stop()


    def open_bank(self):
        #Clicks Yellopw marker for epen bank
        bank = self.get_nearest_tag(clr.YELLOW)
        
        #Trys to click bank, if the color recognition bot fails it will run the command again    
        try:
            self.mouse.move_to(bank.random_point(), mouseSpeed=self.mouse_speed)
            click_result = self.mouse.click(check_red_click=True)
            if not click_result:
                self.open_bank()
                self.log_msg("Didn't see red click, clicking again...")
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying click_bank...")
            time.sleep(1)
            return self.open_bank()

    def open_inventory(self):
        # Clicks the inv icon on the control panel
        self.log_msg("Opening Inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()

    def click_equipment(self):
        # Clicks the inv icon on the control panel
        self.log_msg("Opening Equipment...")
        self.mouse.move_to(self.win.cp_tabs[4].random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()
        equipment_on = imsearch.BOT_IMAGES.joinpath("angler_images", "tab_equipment_on.png")
        equipment_is_open = imsearch.search_img_in_rect(equipment_on, self.win.control_panel)
        if equipment_is_open is None:
            self.click_equipment()
        else:
            return


    def check_equiptment(self):
        angler_hat = imsearch.BOT_IMAGES.joinpath("angler_images", "Angler_hat.png")
        angler_top = imsearch.BOT_IMAGES.joinpath("angler_images", "Angler_top.png")
        angler_waders = imsearch.BOT_IMAGES.joinpath("angler_images", "Angler_waders.png")
        angler_boots = imsearch.BOT_IMAGES.joinpath("angler_images", "Angler_boots.png")

        angler_hat_is_on = imsearch.search_img_in_rect(angler_hat, self.win.control_panel)
        angler_top_is_on = imsearch.search_img_in_rect(angler_top, self.win.control_panel)
        angler_waders_is_on = imsearch.search_img_in_rect(angler_waders, self.win.control_panel)
        angler_boots_is_on = imsearch.search_img_in_rect(angler_boots, self.win.control_panel)
        
        if angler_hat_is_on is not None:
            self.angler_hat = 1
        if angler_top_is_on is not None:
            self.angler_top = 1
        if angler_waders_is_on is not None:
            self.angler_waders = 1
        if angler_boots_is_on is not None:
            self.angler_boots = 1

        total_angler_outfit_pieces = self.angler_hat + self.angler_top + self.angler_waders + self.angler_boots
        outfit_xp_bonus = (self.angler_hat * 0.4) + (self.angler_top * 0.8) + (self.angler_waders * 0.6) + (self.angler_boots * 0.2) 
        if total_angler_outfit_pieces == 4:
            outfit_xp_bonus += 0.5
        rounded_outfit_xp_bonus = round(outfit_xp_bonus,1)

        self.log_msg(f"You have on {total_angler_outfit_pieces}/4 Angler Set pieces, a {rounded_outfit_xp_bonus}% XP Bonus")
        

            
        







    def camera_setup(self):        
        # Sets camera facing south, then moves up to a bird eyes view
        self.compass_north()
        self.scroll_down_minimap()
        self.scroll_down_main_window()
        pyautogui.keyDown('up')
        time.sleep(random.randint(1010,1300)/1000)
        pyautogui.keyUp('up')        
  
    def scroll_down_main_window(self):
        # Scrolls out in the main screen used in camera_setup()
        main_window = self.win.game_view
        self.mouse.move_to(main_window.random_point(), mouseSpeed=self.mouse_speed)
        mouse = MouseController()
        #Random scroll distance and speed
        random_scroll_range = random.randint(30,40)
        for i in range(random_scroll_range):
            mouse.scroll(0, -1)
            random_scroll_speed = random.choice([0.001, 0.002])
            time.sleep(random_scroll_speed)

    def scroll_down_minimap(self):
        # Scrolls out in the minimap used in camera_setup()
        minimap = self.win.minimap
        self.mouse.move_to(minimap.random_point(), mouseSpeed=self.mouse_speed)
        mouse = MouseController()
        #Random scroll distance and speed 
        random_scroll_range = random.randint(30,40)
        for i in range(random_scroll_range):
            mouse.scroll(0, -1)
            random_scroll_speed = random.choice([0.001, 0.002])
            time.sleep(random_scroll_speed)

    def compass_north(self):
        #Same as set_compass_nort(), but allows me to adjust speed.
        self.log_msg("Setting compass North...")
        self.mouse.move_to(self.win.compass_orb.random_point(),mouseSpeed="fast")
        self.mouse.click()


    def click_angler_spot(self):
        # Clicks fishing spot by searching for angler icon
        fishing_spot_icon = imsearch.BOT_IMAGES.joinpath("angler_images", "angler_icon.png")
        fishing_spot_location = imsearch.search_img_in_rect(fishing_spot_icon, self.win.game_view)
        #If the color recognition bot fails it will run the command again    
        try:
            self.mouse.move_to(fishing_spot_location.random_point(), mouseSpeed=self.mouse_speed)
            click_result = self.mouse.click(check_red_click=True)
            if not click_result:
                self.click_angler_spot()
                self.log_msg("Didn't see red click, clicking again...")
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying click_angler_spot...")
            time.sleep(1)
            return self.click_angler_spot()
        
    def click_minimap_from_bank(self):
        #clicks fishing spot by searching for angler icon
        bank_minimap_location = imsearch.BOT_IMAGES.joinpath("angler_images", "minimap_at_bank.png")
        bank_location_rect = imsearch.search_img_in_rect(bank_minimap_location, self.win.minimap)
        #If the color recognition bot fails it will run the command again    
        try:
            self.mouse.move_to(bank_location_rect.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying click_minimap_from_bank...")
            time.sleep(1)
            return self.click_minimap_from_bank()
        
    def click_minimap_from_fishing_spot(self):
        #clicks fishing spot by searching for angler icon
        fishing_minimap_location = imsearch.BOT_IMAGES.joinpath("angler_images", "minimap_at_fishing.png")
        fishing_location_rect = imsearch.search_img_in_rect(fishing_minimap_location, self.win.minimap)
        #If the color recognition bot fails it will run the command again    
        try:
            self.mouse.move_to(fishing_location_rect.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying click_minimap_from_fishing_spot...")
            time.sleep(1)
            return self.click_minimap_from_fishing_spot()


#Bank click_bank()
###deposit inventory need to remove everything that isn't needed
###fish barrel open/close, 
###if barrrel closed open it
###
#
#
#
#
#