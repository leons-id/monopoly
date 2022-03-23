from inter3 import View
from util import *
import rsrc


class Controller:
    def __init__(self, model):
        self.model = model
        self.model.add_controller(self)
        self.view = View(self)
        self.model.add_view(self.view)
        self.view.show()
        self.model.init_game()

    def start_game_2_part(self):
        self.model.game_2_part()

    def model_ask(self, player_type, word):
        if player_type == PlayerType.HUMAN:
            return self.view.ui.show_message_box(word)
        
    def cube_pressed(self):
        self.model.get_view_cube()
        
    def gif_cube_pressed(self):
        self.model.get_view_cube()
        
    def card_pressed(self, index):
        self.model.sendInfo(index)
        
    def get_card_info(self, key):
        info = self.model.get_card_info(key)
        return info
    
    def get_player_info(self, key):
        info = self.model.get_player_info(key)
        return info
    
    def sell_house_pressed(self, player_name, city_name):
        self.model.sell_house(player_name, city_name)
        
    def add_house_pressed(self, player_name, city_name):
        self.model.add_house(player_name, city_name)
        
    def start_game_pressed(self):
        self.model.game_with_timers()
        
    def player_ready_pressed(self):
        # self.model.set_player_ready(player_name)
        # self.model.game_with_timers()
        self.model.game_1_part()
