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

        self.sandworm_count = 0

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
            #The bot should start at the bank after the player has gotten the inventory set up and input bank pin
            
            time.sleep(5)
            # Setup cam
                # self.camera_setup()
            # click fishing spot works
                # self.click_angler_spot()
            #TODO move when spot moves
            # when full click minimap from fishing
                # self.click_minimap_from_fishing_spot()
                # time.sleep(10)
                # self.click_minimap_from_bank()
                # time.sleep(10)
            #Open bank
                # self.open_bank()
            #TODO depo fish and barrel
            self.depo_angler_and_barrel()
            #TODO click minimap from bank
        
            
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

    def camera_setup(self):        
        # Sets camera facing south, then moves up to a bird eyes view
        self.compass_north()
        self.scroll_down_minimap()
        self.scroll_down_main_window()
        pyautogui.keyDown('up')
        time.sleep(random.randint(1010,1300)/1000)
        pyautogui.keyUp('up')        

    def compass_north(self):
        #Same as set_compass_nort(), but allows me to adjust speed.
        self.log_msg("Setting compass North...")
        self.mouse.move_to(self.win.compass_orb.random_point(),mouseSpeed="fast")
        self.mouse.click()

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
        print('set photo')
        fishing_location_rect = imsearch.search_img_in_rect(fishing_minimap_location, self.win.minimap)
        print('search phtoto')
        print(type(fishing_location_rect))
        #If the color recognition bot fails it will run the command again    

        try:
            self.mouse.move_to(fishing_location_rect.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying click_minimap_from_fishing_spot...")
            time.sleep(1)
            return self.click_minimap_from_fishing_spot()

    def depo_angler_and_barrel(self):
        raw_angler_img = imsearch.BOT_IMAGES.joinpath("angler_images", "angler_icon.png")
        fish_barrel_img = imsearch.BOT_IMAGES.joinpath("angler_images", "open_fishing_barrel.png")
        raw_angler = imsearch.search_img_in_rect(raw_angler_img , self.win.control_panel)
        fish_barrel = imsearch.search_img_in_rect(fish_barrel_img, self.win.control_panel)

        self.mouse.move_to(raw_angler.random_point(), mouse_speed=self.mouse_speed)
        self.mouse.click()
        self.mouse.move_to(fish_barrel.random_point(), mouse_speed=self.mouse_speed)
        self.mouse.click()
        time.sleep(rd.fancy_normal_sample(700, 1400) / 1000)
        esc_or_map_choice = random.randint(1,5)
        if esc_or_map_choice == 1:
            pyautogui.keyDown('esc')
            time.sleep(rd.fancy_normal_sample(120,170)/1000)
            pyautogui.keyUp('esc')
            self.click_minimap_from_bank()
        else:
            self.click_minimap_from_bank()
        

        


            
       




### ----- Below Functions are Unused ----- ###

    def open_inventory_tab(self):
        # Clicks the inv icon on the control panel
        self.log_msg("Opening Inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()
  
    def check_angler_equiptment(self):
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

    def click_equipment_tab(self):
        # Clicks the equipment icon on the control panel and searches to make sure it is complete
        self.log_msg("Opening Equipment...")
        self.mouse.move_to(self.win.cp_tabs[4].random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()
        equipment_on = imsearch.BOT_IMAGES.joinpath("angler_images", "tab_equipment_on.png")
        equipment_is_open = imsearch.search_img_in_rect(equipment_on, self.win.control_panel)
        if equipment_is_open is None:
            self.click_equipment_tab()
        else:
            return
                
    def check_sandworms(self):
        #bank image didn't work/Scraped my own # cut 2 pixels off the top
        sandworms = imsearch.BOT_IMAGES.joinpath("angler_images", "Sandworms_inv.png")     
        sandworms_in_inv = imsearch.search_img_in_rect(sandworms, self.win.control_panel) 

        if sandworms_in_inv:
            self.log_msg("Sandworms Found in Inv")    
            for i in range(28):
                sandworm_found = imsearch.search_img_in_rect(sandworms, self.win.inventory_slots[i])                
                if sandworm_found is not None:
                    #if find the slot sandworms are at, counts them, then updates self.sandworms
                    self.log_msg(f"Sandworms At Inv slot{i+1}")
                    sandworm_count_extr = ocr.extract_text(self.win.inventory_slots[i],ocr.PLAIN_11,clr.YELLOW) #OCR getting the Number in a stack
                    cleaned_sandworm_count = int(sandworm_count_extr.replace('O', '').replace('o', '')) #Fixing OCRs mistakes with 0s/Os                         
                    self.sandworm_count = cleaned_sandworm_count # Updating self.sandworm_Count
                    formatted_count = f"{self.sandworm_count:,}"
                    self.log_msg(f"Total Sandworm count: {formatted_count}!")
                    break
        else:
            self.log_msg("No Sandworms found in Inv")
            self.sandworm_count == 0

    def deposit_inv(self):
        #clicks the deposit button
        deposit_inv = imsearch.BOT_IMAGES.joinpath("angler_images", "bank_depo_inv.png")     
        deposit_inv_button = imsearch.search_img_in_rect(deposit_inv, self.win.game_view) 
        try:
            self.mouse.move_to(deposit_inv_button.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()

        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying deposit_inv...")
            time.sleep(1)
            return self.deposit_inv()





### ----- Below Functions are Broken ----- ###


        

        
    def depo_angler(self):
        # Clicks fishing spot by searching for angler icon
        fishing_spot_icon = imsearch.BOT_IMAGES.joinpath("angler_images", "angler_icon.png")
        fishing_spot_location = imsearch.search_img_in_rect(fishing_spot_icon, self.win.control_panel)
        #If the color recognition bot fails it will run the command again    
        try:
            self.mouse.move_to(fishing_spot_location.random_point(), mouseSpeed=self.mouse_speed)
            click_result = self.mouse.click(check_red_click=True)
        
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying click_angler_spot...")
            time.sleep(1)
            return self.depo_angler()  

    def deposit_raw_angler(self):       
        raw_angler_img = imsearch.BOT_IMAGES.joinpath("angler_images", "angler_icon.png")
        raw_angler = imsearch.search_img_in_rect(raw_angler_img, self.win.game_view)
        #If the color recognition bot fails it will run the command again    
        try:
            self.mouse.move_to(raw_angler.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()
            
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying click_angler_spot...")
            time.sleep(1)
            return self.deposit_raw_angler()

    def deposit_open_barrel(self):       
        open_barrel_img = imsearch.BOT_IMAGES.joinpath("angler_images", "open_fishing_barrel.png")
        open_barrel = imsearch.search_img_in_rect(open_barrel_img, self.win.game_view)
        #If the color recognition bot fails it will run the command again    
        try:
            self.mouse.move_to(open_barrel.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()
            
        except AttributeError:
            self.log_msg("AttributeError occurred. Retrying click_angler_spot...")
            time.sleep(1)
            return self.deposit_open_barrel()




        