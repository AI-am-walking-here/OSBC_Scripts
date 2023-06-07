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
        #Initialize the bot when some predefined variables, can change some with options
        bot_title = "AI_Angler Fisher"
        description = "Fishes Angler fish at Port Piscarilius"
        super().__init__(bot_title=bot_title, description=description)
        self.hop_for_players = False
        self.player_count = 0 
        self.running_time = 180
        self.mouse_speed = "fast"       

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
            profile_name="AI AnglerFisher",  # Supply a name if you'd like to save it to PM permanently
            callback=self.log_msg,
        )

    def main_loop(self):
        #Main loop where the bot functions       
        #Put launch setup code here


        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:

            ### ----- Perform bot actions below here ----- ####
            
            if self.hop_for_players == True:
                self.check_for_players()
                self.hop_for_players_function()      
            self.click_bank()

            self.update_progress((time.time() - start_time) / end_time)
            ### ----- Perform bot actions above here ----- ####

               
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

    def click_thing(self):
        #Mines tagged sandstone and stops when 
        self.log_msg("clicking...")
        thing = self.get_nearest_tag(clr.CYAN)
        #If the color recognition bot fails it will run the command again    
        try:
            self.mouse.move_to(thing.random_point(), mouseSpeed=self.mouse_speed)
            click_result = self.mouse.click(check_red_click=True)
            if not click_result:
                self.click_thing()
                self.log_msg("Didn't see red click, clicking again...")
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying click_thing...")
            time.sleep(1)
            return self.click_thing()

    
    def check_for_players(self):
        #Checks the minimap for players then returns +1 to the player count
        other_player = imsearch.BOT_IMAGES.joinpath("sandstone_images", "pink_player_dot.png")        
        if player_noticed := imsearch.search_img_in_rect(other_player, self.win.minimap):       
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
     

    def click_angler_spot(self):
        #clicks fishing spot by searching for angler icon
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

    def click_bank(self):
        #clicks fishing spot by searching for angler icon
        bank = self.get_nearest_tag(clr.YELLOW)
        
        #If the color recognition bot fails it will run the command again    
        try:
            self.mouse.move_to(bank.random_point(), mouseSpeed=self.mouse_speed)
            click_result = self.mouse.click(check_red_click=True)
            if not click_result:
                self.click_bank()
                self.log_msg("Didn't see red click, clicking again...")
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying click_bank...")
            time.sleep(1)
            return self.click_bank()
        
    def click_minimap_bank(self):
    #clicks fishing spot by searching for angler icon
    bank_minimap_location = imsearch.BOT_IMAGES.joinpath("angler_images", "angler_icon.png")
    bank_location_rect = imsearch.search_img_in_rect(fishing_spot_icon, self.win.game_view)
    #If the color recognition bot fails it will run the command again    
    try:
        self.mouse.move_to(fishing_spot_location.random_point(), mouseSpeed=self.mouse_speed)
        click_result = self.mouse.click(check_red_click=True)
        if not click_result:
            self.click_minimap_bank()
            self.log_msg("Didn't see red click, clicking again...")
    except AttributeError:
        self.log_msg("AttributeError occurred. Retrying click_minimap_bank...")
        time.sleep(1)
        return self.click_minimap_bank()




#Bank
###deposit inventory
###fish barrel open/close, 
###if barrrel closed open it
###
#
#
#
#
#