import random as rd
from util import *
from PyQt5.QtCore import *
import rsrc


class Cube:
    _value: int = 0

    @property
    def value(self) -> int:
        return self._value

    def randomize(self) -> int:
        self._value = rd.randint(1, 6)
        # self._master.set_view_cube(self.Value())
        return self._value


class Card:

    def __init__(self, master, obj_name, name, proc=0):
        self._master: Model = master
        self._name: str = name
        self._obj_name: str = obj_name
        self._proc: float = proc

    @property
    def proc(self) -> float:
        return self._proc

    @property
    def master(self):
        return self._master

    @property
    def obj_name(self) -> str:
        return self._obj_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def info(self) -> dict:
        items = {'name': self.name,
                 'obj_name': self.obj_name}
        return items

    def process(self, player) -> None:
        pass


class City(Card):
    def __init__(self, master, obj_name, name, group, proc):
        super().__init__(master, obj_name, name, proc)
        self._group: int = group
        self._owner = None
        self._level: int = 0

    @property
    def group(self) -> int:
        return self._group

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, item) -> None:
        if isinstance(item, Player):
            self._owner = item
            self.master.notify_view()

    @owner.deleter
    def owner(self) -> None:
        del self._owner
        self.master.notify_view()

    @property
    def level(self) -> int:
        return self._level

    def inc_level(self) -> None:
        if self._level < DEF_MAX_HOUSE_COUNT:
            self._level += 1
            self._master.notify_view()

    def dec_level(self) -> None:
        if self._level > 0:
            self._level -= 1
            self._master.notify_view()

    def res_level(self) -> None:
        self._level = 0
        self._master.notify_view()

    @property
    def full_cash(self) -> int:
        return self.cost * (1 + self.level)

    @property
    def owner_name(self) -> str:
        if self.owner is not None:
            return self.owner.name
        else:
            return 'Отсутствует'

    @property
    def owner_ident(self) -> int:
        if self.owner is not None:
            return self.owner.ident
        else:
            return -1

    @property
    def info(self) -> dict:
        items = {'group': self.group,
                 'owner_name': self.owner_name,
                 'owner_ident': self.owner_ident,
                 'cost': self.cost,
                 'rent0': self.rent_param(0),
                 'rent1': self.rent_param(1),
                 'rent2': self.rent_param(2),
                 'rent3': self.rent_param(3),
                 'cur_rent': self.rent,
                 'level': self.level}
        items.update(super().info)
        return items

    @property
    def group_rent(self) -> bool:
        if self.owner is not None or self.owner.check_on_group_city(self):
            return True
        else:
            return False

    @property
    def cost(self) -> int:
        return int(DEF_CASH * self.proc * DEF_CITY_COST_PROC)

    @property
    def rent(self) -> int:
        return int(self.cost * DEF_RENT_PERCENT * (1 + self.level) *
                   (1 + int(self.group_rent) * DEF_GROUP_COST))

    def rent_param(self, level) -> int:
        return int(self.cost * DEF_RENT_PERCENT * (1 + level) * (1 + int(self.group_rent) * DEF_GROUP_COST))

    def process(self, player) -> None:
        player.show_message(f'попадает на {self._name}.')
        if self.owner is None:
            player.show_message(f'{self._name} никому не принадлежит.')
            if player.cash >= self.cost:
                player.show_message(f'думает о покупке...')
                answer = player.get_answer(
                    f'{player.name}, хотите приобрести {self.name} за {get_format_value(self.cost)}')
                if answer is True:
                    player.city = self
                    self.owner = player
                    player.capital = self.cost
                    player.del_cash(self.cost)
                    player.show_message(f'приобретает {self.name}')
                else:
                    player.show_message(f'отказался о покупки.')
            else:
                player.show_message(f'слишком дорого...')
        elif self.owner == player:
            player.show_message(f'попадает на свою территорию.')
        else:
            player.show_message(f'попал на территорию {self.owner.name}.')
            player.show_message(f'платит аренду {get_format_value(self.rent)} игроку {self.owner.name}')
            self.owner.add_cash(self.rent)
            player.del_cash(self.rent)
        self.master.notify_view()


class Start(Card):

    def info(self) -> dict:
        items = {'desc': 'Получите награду за прохождение круга!',
                 'value': get_format_value(DEF_LAP_CASH, 'За круг + ')}
        items.update(super().info)
        return items


class Bonus(Card):
    def __init__(self, master, obj_name, name, proc):
        super().__init__(master, obj_name, name, proc)

    @property
    def value(self) -> int:
        return int(DEF_CASH * self.proc)

    def process(self, player) -> None:
        player.add_cash(self.value)
        player.show_message(f'получил бонус {get_format_value(self.value)}')
        # self._master.show_message(f'0')
        self.master.notify_view()

    def info(self) -> dict:
        items = {'info': 'Ооо, повезло. Получите награду.',
                 'value': f'+ {get_format_value(self.value)}'}
        items.update(super().info)
        return items


class Penalty(Card):
    def __init__(self, master, obj_name, name, proc):
        super().__init__(master, obj_name, name, proc)
        self._proc: float = proc

    @property
    def proc(self) -> float:
        return self._proc

    @property
    def value(self) -> int:
        return int(DEF_CASH * self.proc)

    def process(self, player) -> None:
        player.del_cash(self.value)
        player.show_message(f'заплатил штраф {get_format_value(self.value)}')
        self.master.notify_view()

    def info(self):
        items = {'info': 'Попались...  Заплатите  штраф',
                 'value': f'- {get_format_value(self.value)}'}
        items.update(super().info)
        return items


class Prisoner:
    def __init__(self, player, moves):
        self._player: Player = player
        self._moves: int = moves - 1

    @property
    def player(self):
        return self._player

    @property
    def moves(self) -> int:
        return self._moves

    def dec_moves(self) -> None:
        self._moves -= 1

    def check(self, item) -> bool:
        if item == self.player:
            return True
        else:
            return False


class Container(Card):
    def __init__(self, master, obj_name, name, moves):
        super().__init__(master, obj_name, name)
        self._moves: int = moves
        self._prisoners: list = []

    @property
    def moves(self):
        return self._moves

    @property
    def prisoners(self):
        return self._prisoners

    def add_prisoner(self, item) -> None:
        if

    def del_prisoner(self, item) -> None:
        pass

    def is_prisoner(self, item) -> bool:
        if self.prisoners:
            for el in self.prisoners:
                if el.check(item):
                    return True
            return False
        else:
            return False

    def info(self):
        string: str
        if self.get_moves() == 1:
            string = 'хода'
        else:
            string = 'ходов'
        items = {'info': 'Ооо, не повезло. Ну что ж, бывает. Отправляйтесь прямиком в тюрьму.',
                 'value': f'Пропуск {self.get_moves()} {string}'}
        items.update(super().info)
        return items


class Prison(Container):
    def process(self, player):
        if player not in self._prisoners:
            self._prisoners.append(player)
            self._prisoners.append(self._moves - 1)
            player.set_moved(False)
            if self._moves == 1:
                string = 'ход'
            else:
                string = 'хода'
            player.show_message(f'пропустит {self._moves} {string}')
        else:
            ind = self._prisoners.index(player)
            if self._prisoners[ind + 1] <= 0:
                del self._prisoners[ind:ind + 2]
                player.set_moved(True)
                # player.show_message(f'продолжил игру.')
            else:
                self._prisoners[ind + 1] -= 1
        # self._master.show_message(f'0')
        self._master.notify_view()


class Hotel(Container):

    def info(self):
        return {'_name': self._name,
                'type': 'container',
                'info': 'Не торопитесь, можете остановиться тут и отдохнуть немного...',
                '_value': f'Макс. ходов {self._moves}'}

    def process(self, player):
        if player not in self._prisoners:
            answer = player.get_answer('Хотите здесь остановиться?')
            if answer is True:
                self._prisoners.append(player)
                self._prisoners.append(self._moves)
                player.set_moved(False)
                player.show_message(f'пропустит 1 ход.')
            else:
                pass
        else:
            ind = self._prisoners.index(player)
            if ind + 1 <= 0:
                del self._prisoners[ind:ind + 2]
                player.set_moved(True)
                player.show_message(f'продолжил игру.')
            else:
                answer = player.get_answer('Хотите остаться здесь?')
                if answer is True:
                    self._prisoners[ind + 1] -= 1
                    player.show_message(f'пропустит 1 ход.')
                else:
                    del self._prisoners[ind:ind + 2]
                    player.set_moved(True)
                    player.show_message(f'продолжил игру.')
        # self._master.show_message(f'0')
        self._master.notify_view()


class Player:
    def __init__(self, master, name, player_type, ident, cash=DEF_CASH):
        self.answer = None
        self._master = master
        self._player_type = player_type
        self._name = name
        self._cash = cash
        self._capital = 0
        self._ident = ident
        self._lap = 0
        self._moved = True
        self._cities = []
        # self.place = None
        self._ready = True
        self._can_sell = True

    def get_moved(self):
        return self._moved

    def get_player_type(self):
        return self._player_type

    def get_city_by_index(self, index):
        for x in self._cities:
            if x.index == index:
                return x

    def get_ident(self):
        return self._ident

    def get_name(self):
        return self._name

    def get_info(self):
        return {'_name': self.get_name(),
                '_ready': self.get_ready(),
                'index': self.get_ident(),
                '_cash': self.get_cash(),
                '_capital': self.get_capital(),
                'laps': self.get_laps(),
                '_moved': self.get_moved(),
                '_cities': self.get_cities_name(),
                # 'canAddHouse':self.get_can_add_house(),
                '_can_sell': self.get_can_sell(),
                'player_type': self.get_player_type()}

    def add_city(self, city):
        if city not in self._cities:
            self._cities.append(city)
            city.add_owner(self)
            self._master.notify_view()

    def del_city(self, city):
        if city in self._cities:
            self.add_cash(city.Cost())
            self.del_capital(city.Cost())
            self._cities.remove(city)
            city.reset_houses()
            city.del_owner(self)
            self._master.notify_view()

    def add_house(self, city):
        if city in self._cities:
            city.add_house()
            self.del_cash(city.Cost())
            self.add_capital(city.Cost())
            self._master.notify_view()

    def del_house(self, city):
        if city in self._cities:
            if city.get_house_count() > 0:
                self.add_cash(city.Cost())
                self.del_capital(city.Cost())
                city.del_house()
            else:
                self.del_city(city)
            self._master.notify_view()

    def get_cities_name(self):
        item_names = []
        if len(self._cities) > 0:
            for item in self._cities:
                item_names.append(item.get_obj_name())
        return item_names

    def check_cities_group_state(self):
        temp = []
        for x in self._cities:
            temp.append(x.get_group())
        temp1 = [i for i, x in enumerate(temp) if temp.count(x) == 2]
        for ind in temp:
            self._cities[ind].setGroupCostState(state=False)
        for ind1 in temp1:
            self._cities[ind1].set_group_cost_state(state=True)
        self._master.notify_view()

    def check_on_group_city(self, city):
        temp = []
        for x in self._cities:
            if x.get_group() == city.get_group():
                temp.append(x)
        if len(temp) == DEF_GROUP_CITY_COUNT:
            city.set_group_cost_state(True)
        else:
            city.set_group_cost_state(False)

    def show_message(self, text):
        self._master.show_message(f'{self._ident}{self._name} {text}')
        # self._master.notify_view()

    def set_answer(self, state):
        self.answer = bool(state)

    def get_answer(self, word):
        answer = self._master.notify_controller(self._player_type, word)
        return answer

    def set_moved(self, state):
        self._moved = state
        self._master.notify_view()

    def check_pos_cash(self):
        if self._cash >= 0:
            return True
        else:
            self.set_can_sell(True)
            return False

    def check_pay(self):
        if self._cash + self._capital <= 0:
            return True
        else:
            return False

    def add_cash(self, value):
        self._cash += value
        self._master.notify_view()

    def del_cash(self, value):
        self._cash -= value
        self.check_pos_cash()
        self._master.notify_view()

    def get_cash(self):
        return self._cash

    def add_capital(self, value):
        self._capital += value
        self._master.notify_view()

    def del_capital(self, value):
        self._capital -= value
        self._master.notify_view()

    def get_capital(self):
        return self._capital

    def add_lap(self):
        self._lap += 1
        self.add_cash(DEF_LAP_CASH)
        self.show_message(f'прошел круг и получает {get_format_value(DEF_LAP_CASH)}')
        self._master.notify_view()

    def get_laps(self):
        return self._lap

    def get_ready(self):
        return self._ready

    def set_ready(self, state):
        self._ready = state
        self._master.notify_view()

    def get_can_add_house(self, cost):
        if cost > self._cash:
            return False
        else:
            return True

    def set_can_sell(self, value):
        self._can_sell = value

    def get_can_sell(self):
        return self._can_sell


class CardList:
    def __init__(self, master):
        self.items = [Start(master, 'start', 'Старт'),
                      City(master, 'piter', 'С.-Петербург', 0, 0.3),
                      City(master, 'yar', 'Ярославль', 0, 0.4),
                      Penalty(master, 'straf1', 'Штраф', 0.1),
                      City(master, 'samara', 'Самара', 2, 0.5),
                      City(master, 'penza', 'Пенза', 2, 0.6),
                      Prison(master, 'turma1', 'Тюрьма', 1),
                      City(master, 'ryzan', 'Рязань', 2, 0.7),
                      City(master, 'pskov', 'Псков', 2, 0.8),
                      Bonus(master, 'bonus1', 'Бонус', 0.075),
                      City(master, 'krasn', 'Красноярск', 3, 0.9),
                      City(master, 'novosib', 'Новосибирск', 3, 1),
                      Hotel(master, 'hotel', 'Отель', 5),
                      City(master, 'chelyb', 'Челябинск', 3, 1.1),
                      City(master, 'syktyv', 'Сыктывкар', 3, 1.2),
                      Penalty(master, 'straf2', 'Штраф', 0.1),
                      City(master, 'vladik', 'Владивосток', 4, 1.3),
                      City(master, 'moskva', 'Москва', 4, 1.4),
                      Prison(master, 'turma2', 'Тюрьма', 2),
                      City(master, 'kazan', 'Казань', 4, 1.5),
                      City(master, 'bel', 'Белгород', 4, 1.6),
                      Bonus(master, 'bonus2', 'Бонус', 0.1),
                      City(master, 'perm', 'Пермь', 0, 1.7),
                      City(master, 'ekat', 'Екатеринбург', 0, 2)]

    def get(self, name):
        for item in self.items:
            if item.get_obj_name() == name:
                return item


class PlayerList:

    def __init__(self, master):
        self.items = [Player(master, 'Игрок 1', PlayerType.HUMAN, 1),
                      Player(master, 'Игрок 2', PlayerType.HUMAN, 2)]

    def addItem(self, item: Player):
        self.items.append(item)

    def get(self, name):
        for item in self.items:
            if item.get_name() == name:
                return item


class Model(QObject):
    endSignal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._cur_player = None
        self._lap = None
        self._repeat = None
        self._next_place_index = None
        self._view = None
        self._controller = None
        self._message = ''
        self._cube = Cube(self)
        self._card_list = CardList(self)
        self._player_list = PlayerList(self)
        self._selector = 0
        self._condition = 0  # 0 игра на банкротство, 1 игра на количество кругов
        self._laps_count = 6
        self._cur_place_index = [0, 0]
        self._running = True
        self.endSignal.connect(self.game_3_part)

    def set_running(self, state):
        self._running = state

    def init_game(self):
        self._player_list.items[0].set_ready(False)

    @staticmethod
    def check_players(player):
        if player.check_pay() is True:
            return 2
        else:
            if player.check_pos_cash() is False:
                return 1
            else:
                return 0

    def game_with_timers(self):
        plr1_rez = self.check_players(self._player_list.items[0])
        plr2_rez = self.check_players(self._player_list.items[1])
        if plr1_rez == 0 and plr2_rez == 0:
            selector = self.get_selector()
            cur_player = self._player_list.items[selector]
            cur_player.set_ready(True)
            cur_player.set_can_sell(False)
            self._player_list.items[1 - selector].set_can_sell(False)
            ready_timing = 5500
            lap = False

            if cur_player.get_moved():
                cube_value = self.get_view_cube()
                timing = cube_value * (500 - 40 * (cube_value - 1)) + 3600
                ready_timing = timing
                next_place_index = self._cur_place_index[selector] + cube_value
                self._view.ui.drive_player(selector, cube_value)
                if next_place_index >= len(self._card_list.items):
                    self._cur_place_index[selector] = next_place_index - len(self._card_list.items)
                    lap = True
                else:
                    self._cur_place_index[selector] = next_place_index

                if lap:
                    QTimer().singleShot(timing + 400, cur_player.add_lap)
                QTimer().singleShot(timing + 500,
                                    lambda: self._card_list.items[self._cur_place_index[selector]].process(cur_player))
            else:
                prison_1 = self._card_list.get('turma1')
                prison_2 = self._card_list.get('turma2')
                hotel = self._card_list.get('hotel')
                if prison_1.is_prisoner(cur_player):
                    prison_1.process(cur_player)
                elif prison_2.is_prisoner(cur_player):
                    prison_2.process(cur_player)
                elif hotel.is_prisoner(cur_player):
                    hotel.process(cur_player)

            if self._player_list.items[1 - selector].get_moved():
                QTimer().singleShot(ready_timing + 500, lambda: self._player_list.items[1 - selector].set_ready(False))
                self._player_list.items[1 - selector].set_can_sell(True)
                repeat = False
            else:
                self._player_list.items[selector].set_can_sell(True)
                repeat = True
                # QTimer().singleShot(ready_timing+500, lambda: self.player_list.items[selector].set_ready(False))

            self.set_selector(1 - selector)

            if repeat:
                self.game_with_timers()
            else:
                pass

        else:
            if plr1_rez == 2:
                self._player_list.items[0].show_message('банкрот! Игра окончена!')
                self._player_list.items[0].set_ready(True)
                self._player_list.items[1].set_ready(True)
            elif plr2_rez == 2:
                self._player_list.items[1].show_message('банкрот! Игра окончена!')
                self._player_list.items[0].set_ready(True)
                self._player_list.items[1].set_ready(True)
            elif plr1_rez == 1:
                self._player_list.items[0].show_message('погасите задолженность!')
                self._player_list.items[0].set_can_sell(True)
            elif plr2_rez == 1:
                self._player_list.items[1].show_message('погасите задолженность!')
                self._player_list.items[1].set_can_sell(True)

    def game_1_part(self):
        plr1_rez = self.check_players(self._player_list.items[0])
        plr2_rez = self.check_players(self._player_list.items[1])
        if plr1_rez == 0 and plr2_rez == 0:
            self._cur_player = self._player_list.items[self._selector]
            self._cur_player.set_ready(True)
            self._cur_player.set_can_sell(False)
            self._player_list.items[1 - self._selector].set_can_sell(False)
            self._repeat = False
            self._lap = False

            if self._cur_player.get_moved():
                cube_value = self.get_view_cube()
                self._next_place_index = self._cur_place_index[self._selector] + cube_value
                self._view.ui.drive_player(self._selector, cube_value)

            else:
                prison_1 = self._card_list.get('turma1')
                prison_2 = self._card_list.get('turma2')
                hotel = self._card_list.get('hotel')
                if prison_1.get_prisoners(self._cur_player):
                    prison_1.process(self._cur_player)
                elif prison_2.get_prisoners(self._cur_player):
                    prison_2.process(self._cur_player)
                elif hotel.get_prisoners(self._cur_player):
                    hotel.process(self._cur_player)
                self.endSignal.emit()

        else:
            if plr1_rez == 2:
                self._player_list.items[0].show_message('банкрот! Игра окончена!')
                self._player_list.items[0].set_ready(True)
                self._player_list.items[1].set_ready(True)
            elif plr2_rez == 2:
                self._player_list.items[1].show_message('банкрот! Игра окончена!')
                self._player_list.items[0].set_ready(True)
                self._player_list.items[1].set_ready(True)
            elif plr1_rez == 1:
                self._player_list.items[0].show_message('погасите задолженность!')
                self._player_list.items[0].set_can_sell(True)
            elif plr2_rez == 1:
                self._player_list.items[1].show_message('погасите задолженность!')

    def game_2_part(self):
        if self._next_place_index >= len(self._card_list.items):
            self._cur_place_index[self._selector] = self._next_place_index - len(self._card_list.items)
            self._lap = True
        else:
            self._cur_place_index[self._selector] = self._next_place_index

        if self._lap:
            self._cur_player.add_lap()
        print('я тут')
        self._card_list.items[self._cur_place_index[self._selector]].process(self._cur_player)
        self.endSignal.emit()

    def game_3_part(self):
        if self._player_list.items[1 - self._selector].get_moved():
            self._player_list.items[1 - self._selector].set_ready(False)
            self._player_list.items[1 - self._selector].set_can_sell(True)
            self._repeat = False
        else:
            # self.player_list.items[self.selector].set_can_sell(True)
            self._repeat = True

        self._selector = 1 - self._selector

        if self._repeat:
            self.game_1_part()

    def sell_house(self, player_name, city_name):
        player = self._player_list.get(player_name)
        city = self._card_list.get(city_name)
        player.del_house(city)
        player.show_message(f'продает имущество в {city.get_name()}')

    def add_house(self, player_name, city_name):
        player = self._player_list.get(player_name)
        city = self._card_list.get(city_name)
        player.add_house(city)
        player.show_message(f'улучшает город {city.get_name()}')

    def get_card_list(self):
        return self._card_list

    def add_controller(self, controller):
        self._controller = controller

    def notify_controller(self, player_type, word):
        return self._controller.model_ask(player_type, word)

    def add_view(self, view):
        self._view = view

    def notify_view(self):
        self._view.ui.update_all()

    def show_message(self, text):
        self._view.ui.show_message(text)

    def get_view_cube(self):
        return self._cube.randomize()

    def set_view_cube(self, value):
        self._view.ui.draw_cube_image(value)

    def get_card_info(self, key):
        return self._card_list.get(key).info()

    def get_player_info(self, key):
        return self._player_list.get(key).get_info()

    def set_player_ready(self, player_name):
        self._player_list.get(player_name).set_ready(True)

    def get_selector(self):
        return self._selector

    def set_selector(self, value):
        self._selector = value
