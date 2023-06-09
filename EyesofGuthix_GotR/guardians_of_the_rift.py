import time
import random
import pyautogui
import utilities.game_launcher as launcher    # |Allows for custom profile launch
import pathlib                                # |
import utilities.api.item_ids as ids
import utilities.color as clr
import utilities.ocr as ocr
import utilities.random_util as rd
import model.osrs.EyesofGuthix_GotR.BotSpecImageSearch as imsearch
from model.osrs.osrs_bot import OSRSBot
from utilities.api.morg_http_client import MorgHTTPSocket
from utilities.api.status_socket import StatusSocket

# TEXT_RED = Color([239,16,32])


class Gotr(OSRSBot, launcher.Launchable):
    def __init__(self):
        bot_title = "Eyes of Guthix - GotR"
        description = "This bot runs Guardians of the Rift"
        super().__init__(bot_title=bot_title, description=description)
        # Set option variables below (initial value is only used during headless testing)
        self.running_time = 10
        self.take_breaks = False
        self.game_focus = "Even Points"
        self.repair_now = False
        self.repair_rounds = "0 - Small/Cape/Lantern"
        self.mouse_speed = "fast"

    def create_options(self):
        self.options_builder.add_slider_option("running_time", "How long to run (minutes)?", 1, 360)
        self.options_builder.add_checkbox_option("repair_now", "Repair at start?", ["Yes"])
        self.options_builder.add_dropdown_option("game_focus", "How do you want your game focused?", ["Even Points", "Chaos", "Elemental", "GP"])
        self.options_builder.add_dropdown_option("repair_rounds", "Repair after how many rounds(C:8/G:10/L:29/M:45)", ["8 - Colossal", "10 - Giant", "29 - Large", "45 - Medium", "0 - Small/Cape/Lantern"])

    def save_options(self, options: dict):
        for option in options:
            if option == "running_time":
                self.running_time = options[option]
            elif option == "game_focus":
                self.game_focus = options[option]
            elif option == "repair_now":
                self.repair_now = options[option] != []
            elif option == "repair_rounds":
                self.repair_rounds = options[option]
            else:
                self.log_msg(f"Unknown option: {option}")
                print("Developer: ensure that the option keys are correct, and that options are being unpacked correctly.")
                self.options_set = False
                return
            
        self.log_msg(f"Running time: {self.running_time} minutes.")
        self.log_msg(f"You have chosen a {self.game_focus} game focus.")
        self.log_msg(f"Yot will{'' if self.repair_now else ' not'} repair at before the first game.")
        self.log_msg(f"You will repair after {self.repair_rounds[0]} rounds.") #Prints the first character'[0]' in the options
        self.log_msg("Options set successfully.")
        self.options_set = True
    
    def launch_game(self):
        settings = pathlib.Path(__file__).parent.joinpath("custom_settings.properties")
        launcher.launch_runelite(
            properties_path=settings,
            game_title=self.game_title,
            use_profile_manager=True,
            profile_name="Guardians of the Rift",  # Supply a name if you'd like to save it to PM permanently
            callback=self.log_msg,
        )

    def main_loop(self):
      
        # Setup and APIs
        api_m = MorgHTTPSocket()
        api_s = StatusSocket()
        elemental_energy = 0
        catalytic_energy = 0

        # Main loop
        start_time = time.time()
        end_time = self.running_time * 60
        while time.time() - start_time < end_time:
            # ------ Perform bot actions here ------
            alter = self.get_nearest_tag(clr.RED)
            self.mouse.move_to(alter.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()
            # self.camera_setup()
            # self.chatbox_text("active!", clr.TEXT_RED)
            # self.mine_guardians()
            # self.wait_for_portal()
            # self.climb_rubble()
            



            time.sleep(100)  #so no infinate loops for testing
            self.update_progress((time.time() - start_time) / end_time)
        
        

        self.update_progress(1)
        self.log_msg("Finished.")
        self.stop()


    def open_inv(self):
        #Clicks the inv icon
        self.log_msg("Opening Inventory...")
        self.mouse.move_to(self.win.cp_tabs[3].random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()
    
    def open_magic_book(self):
        #Clicks the magic book icon
        self.log_msg("Opening Magic Book...")
        self.mouse.move_to(self.win.cp_tabs[6].random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()

    def repair_pouches(self):
        #TODO add a way that wont break when called but pouches are full repaired
        self.open_magic_book()

        #Looks in control panel for a lit up NPC contact in Spellbook and clicks
        npc_contact_on_img = imsearch.BOT_IMAGES.joinpath("gotr_images", "npc_contact_on.png")
        if npc_contact := imsearch.search_img_in_rect(npc_contact_on_img, self.win.control_panel):
            self.log_msg("Clicking on NPC Contact...")
            self.mouse.move_to(npc_contact.random_point(), mouseSpeed=self.mouse_speed)
            self.mouse.click()
        else:
            self.log_msg("You are out of Runes or on the wrong spell book...")

        #Looks in game view for a Dark Mage Portrait and clicks
        dark_mage_portrait = imsearch.BOT_IMAGES.joinpath("gotr_images", "npc_contact_darkmage.png")
        dark_mage = imsearch.search_img_in_rect(dark_mage_portrait, self.win.game_view)
        while not dark_mage:
            time.sleep(random.randint(400,600)/1000)
            dark_mage = imsearch.search_img_in_rect(dark_mage_portrait, self.win.game_view)
        self.log_msg("Clicking on Dark Mage...")
        self.mouse.move_to(dark_mage.random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()

        #Looks in Chat for NPC Contact dialoge and press space to continue
        first_dialogue = imsearch.BOT_IMAGES.joinpath("gotr_images", "npc_contact_firstmessage.png")
        first_message = imsearch.search_img_in_rect(first_dialogue, self.win.chat)
        while not first_message:
            time.sleep(random.randint(400,600)/1000)
            first_message = imsearch.search_img_in_rect(first_dialogue, self.win.chat)
        self.log_msg("Pressing Space Bar through first dialogue...")
        pyautogui.keyDown('space')
        time.sleep(random.randint(400,600)/1000)
        pyautogui.keyUp('space')

        #Looks in Chat for repair option then clicks "1"
        click_option = imsearch.BOT_IMAGES.joinpath("gotr_images", "npc_contact_clickoption.png")
        repair_option = imsearch.search_img_in_rect(click_option, self.win.chat)
        while not repair_option:
            time.sleep(random.randint(400,600)/1000)
            repair_option = imsearch.search_img_in_rect(click_option, self.win.chat)
        self.log_msg(f"Pressing '1' to repair pouches...")
        pyautogui.keyDown('1')
        time.sleep(random.randint(400,600)/1000)
        pyautogui.keyUp('1')              
        
        #Looks in Chat for last NPC Contact dialoge and press space to continue
        last_dialogue = imsearch.BOT_IMAGES.joinpath("gotr_images", "npc_contact_lastmessage.png")
        last_message = imsearch.search_img_in_rect(last_dialogue, self.win.chat)
        while not last_message:
            time.sleep(random.randint(400,600)/1000)
            last_message = imsearch.search_img_in_rect(last_dialogue, self.win.chat)
        self.log_msg("Pressing 'space' to finish repair...")
        pyautogui.keyDown('space')
        time.sleep(random.randint(400,600)/1000)
        pyautogui.keyUp('space')
        self.open_inv() #Opens inv at the end to reset

    def mine_guardians(self):
        guardians = self.get_nearest_tag(clr.PINK)
        self.mouse.move_to(guardians.random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()        

    def climb_rubble(self):
        rubble = self.get_nearest_tag(clr.BLUE)
        self.mouse.move_to(rubble.random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()

    def work_at_bench(self):
        bench = self.get_nearest_tag(clr.WHITE)
        self.mouse.move_to(bench.random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()

    def deposit_runes(self):
        bench = self.get_nearest_tag(clr.PURPLE)
        self.mouse.move_to(bench.random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()

    def click_portal(self):
        #Clicks the Guardian portal, and exit portal at alters
        portal = self.get_nearest_tag(clr.CYAN)
        self.mouse.move_to(portal.random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()

    def click_alter(self):
        #Clicks the Guardian portal, and exit portal at alters
        alter = self.get_nearest_tag(clr.YELLOW)
        self.mouse.move_to(alter.random_point(), mouseSpeed=self.mouse_speed)
        self.mouse.click()

    def wait_for_portal(self):
        #Searches the screen waiting for a portal to appear
        portal_image = imsearch.BOT_IMAGES.joinpath("gotr_images", "gotr_portal.png")
        portal = imsearch.search_img_in_rect(portal_image, self.win.game_view)
        check_counter = 0
        while not portal:
            check_counter += 1    #Adds an internal counter to check for portal
            if check_counter % 10 == 0:    #After 10 checks it'll log a message checking for portal 
                self.log_msg("Checking for portal x " + str(check_counter // 5))
            time.sleep(random.randint(1000,2000)/1000)    #Wait 1-2 seconds to retry looking for portal
            portal = imsearch.search_img_in_rect(portal_image, self.win.game_view)
        self.log_msg("Portal Apeared...")
    
    def is_rift_active(self):
        #checks to see if rift active and will return True or False
        self.chatbox_textself.chatbox_text("active!", clr.TEXT_RED)
    
    def is_guardian_defeated(self):
        #checks to see if guardian defeated and will return True or False
        self.chatbox_textself.chatbox_text("defeated!", clr.TEXT_RED)

    def camera_setup(self):
        #Sets camera facing east, then move to a bird eyes view
        self.set_compass_east()
        pyautogui.keyDown('up')
        time.sleep(random.randint(1010,1300)/1000)
        pyautogui.keyUp('up')
    #games starts 
        #mine mine_guardians()
        #wait portal wait_for_portal()
        #climb climb_rubble()
        #navagate to portal
        #portal
            #mine ess mine_guardians()
            #runes
            #craft #click alter #TODO needs a click rune pouch sytem
            #runes
        #repeat




#make sure alters are all tagged
#look into async for active alters

#changed chatbox_text() in bot.py
#changed COLORS in color.py to add TEXT colors
#check modules before distribution
#make sure plugins work
#Colors work with atleast a 30pt difference possible movement