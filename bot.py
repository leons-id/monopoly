# Класс и модуль для бота
import model, controller, inter3, util


class BotMaster(model.Player):
    def __init__(self, master, name, playerType, ident, cash):
        super().__init__(master, name, playerType, ident, cash)
        
    def processing(self):
        pass