import util
from controller import *
import random
from PyQt5.QtGui import (QIcon, QPixmap, QFont, QPainter, QPalette, QPaintEvent, QMovie, QColor, QBrush, QPen,
                         QLinearGradient)
from PyQt5.QtCore import (QPoint, QPointF, QSize, QPropertyAnimation, QObject, Qt, QTimer)
from PyQt5.QtWidgets import (QWidget, QMainWindow, QGridLayout, QPushButton, QMessageBox, QGraphicsView,
                             QGraphicsScene, QGraphicsTextItem, QGraphicsRectItem, QGraphicsGridLayout,
                             QLabel, QGraphicsPixmapItem, QFrame, QSizePolicy, QListWidget)
import rsrc


class View(QMainWindow):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.setWindowIcon(QIcon(LOGO_IMAGE))
        # self.setWindowTitle('Ситиполия')
        self.ui = MonoUi(self.controller)
        self.setCentralWidget(self.ui)
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)
        self.resize(1200, 800)


class MonoUi(QWidget):
    def __init__(self, controller, parent=None):
        super().__init__(parent)
        self.controller = controller
        self.win_grid = QGridLayout()
        self.win_grid.setSpacing(10)
        self.gif_cube = GifCube(self.controller)
        # win_grid.addWidget(cards, 0, 1)
        self.win_grid.addWidget(self.gif_cube, 3, 1)
        self.game = CardGridContainer(self.controller)
        self.win_grid.addWidget(self.game, 0, 0, 4, 1)
        # startBtn = QPushButton(text='Старт')
        # startBtn.resize(QSize(100, 50))
        # startBtn.clicked.connect(lambda event: self.game.drive(1))
        # win_grid.addWidget(startBtn, 0, 2)
        self.setLayout(self.win_grid)
        self.player_view1 = PlayerView(self.controller, 'Игрок 1', 30, self.game)
        self.player_view2 = PlayerView(self.controller, 'Игрок 2', -30, self.game)
        self.players = [self.player_view1, self.player_view2]
        self.win_grid.addWidget(self.player_view1, 0, 1)
        self.win_grid.addWidget(self.player_view2, 1, 1)
        self.startGameBtn = QPushButton(text='Начать игру')
        self.startGameBtn.setStyleSheet("background: rgba(0,0,0,40%)")
        self.startGameBtn.setFont(QFont('Arial', 20))
        self.startGameBtn.clicked.connect(self.controller.start_game_pressed)
        # self.win_grid.addWidget(self.startGameBtn, 2, 1)
        self.game.add_message('Игра началась')

    def drive_player(self, player_index, value):
        self.players[player_index].drive(value)

    def show_message(self, text):
        self.game.add_message(text)

    def paintEvent(self, a0: QPaintEvent):
        painter = QPainter(self)
        pixmap = QPixmap(BACK_IMAGE).scaled(1200, 800)
        painter.drawPixmap(self.rect(), pixmap)

    def draw_cube_image(self, value):
        # self._cube.draw_cube_image(_value)

        self.gif_cube.draw_gif(value)

    def update_all(self):
        self.game.update_items()
        self.player_view1.update_values()
        self.player_view2.update_values()

    def show_message_box(self, word):
        ret = False
        msg = QMessageBox(self)
        msg.setWindowOpacity(0.9)

        msg.setStyleSheet(f"background: #CFDFCB")
        msg.setFont(QFont('Arial', 12))
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle('Подтверждение')
        msg.setText(word)
        yes = msg.addButton('Да', QMessageBox.AcceptRole)
        no = msg.addButton('Нет', QMessageBox.AcceptRole)
        no.setFont(QFont('Arial', 12))
        yes.setFont(QFont('Arial', 12))
        msg.exec_()
        msg.deleteLater()
        if msg.clickedButton() is yes:
            ret = True
        elif msg.clickedButton() is no:
            ret = False
        return ret


class GifCube(QLabel):

    def __init__(self, controller):
        super().__init__()
        # self.mouseReleaseEvent = _controller.gif_cube_pressed
        self.frame_count = 0
        self.movie = None
        self.value = None
        self.controller = controller
        # self.mouseReleaseEvent = lambda event: _controller.gif_cube_pressed(10)
        # self.show()
        self.draw_gif(0)
        self.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)

    def draw_gif(self, value: int):
        gif = CUBE_GIFTS.get(value)
        self.value = value
        self.movie = QMovie(gif)
        self.movie.setScaledSize(QSize(200, 200))
        self.setMovie(self.movie)
        self.frame_count = self.movie.frameCount()
        self.movie.frameChanged.connect(self.frame_Changed)
        self.movie.start()

    def frame_Changed(self, v):
        if self.frame_count == v + 1:
            self.movie.stop()


class GraphicsScene(QGraphicsScene):
    def __init__(self, controller, parent=None):
        QGraphicsScene.__init__(self, parent)
        self.controller = controller

    def mousePressEvent(self, event):
        # x = event.scenePos().x()
        # y = event.scenePos().y()
        pass


class MesView(QListWidget):
    def __init__(self, controller):
        super().__init__()
        # self.setBackgroundVisible(False)
        # self.setReadOnly(True)
        self.controller = controller
        self.setMinimumSize(HORIZONTAL_WIDTH * 5 - 10, HORIZONTAL_WIDTH * 5 - 10)
        self.setMaximumSize(HORIZONTAL_WIDTH * 5 - 10, HORIZONTAL_WIDTH * 5 - 10)
        self.setStyleSheet("background: rgba(0,0,0,10%)")
        self.setFont(QFont('Arial', 14, QFont.Bold, italic=True))
        self.setSelectionMode(QListWidget.NoSelection)
        # self.setWordWrapMode(3)
        # self.document().setMaximumBlockCount(50)
        # self.setAutoFillBackground(False)
        # self.setTextBackgroundColor(QColor(255, 255, 0))

    def add_message(self, mes: str):
        # color_index = mes[0]
        msg = mes[1:]
        self.addItem(msg)
        if self.count() >= 50:
            self.takeItem(0)
        self.scrollToItem(self.item(self.count() - 1))


class CardGridContainer(QGraphicsView):
    def __init__(self, controller):
        super().__init__()
        # self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # self.setFrameStyle(QFrame.NoFrame)
        # self.setBackgroundBrush(QBrush(QColor(BACKGROUND_COLOR)))
        self.setStyleSheet("background:transparent;")
        self.controller = controller
        self.setFrameShape(QFrame.NoFrame)
        # self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.scene = GraphicsScene(self.controller)
        self.scene.setSceneRect(0, 0, 960, 960)
        self.setScene(self.scene)
        self.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        pen = QPen(QColor(MAIN_COLOR))
        pen.setWidth(20)
        rect = QGraphicsRectItem(0, 0, 954, 954)
        rect.setOpacity(0.5)
        rect.setPen(pen)
        rect.setPos(16, 16)
        self.scene.addItem(rect)

        self.items = [SquaCardView(self.scene, 'start', controller, 6, 6, CardOrient.SQUADE_BOTTOM),
                      CityCardView(self.scene, 'piter', controller, 6, 5, CardOrient.HORIZONTAL_BOTTOM),
                      CityCardView(self.scene, 'yar', controller, 6, 4, CardOrient.HORIZONTAL_BOTTOM),
                      BnPrCardView(self.scene, 'straf1', controller, 6, 3, CardOrient.HORIZONTAL_BOTTOM),
                      CityCardView(self.scene, 'samara', controller, 6, 2, CardOrient.HORIZONTAL_BOTTOM),
                      CityCardView(self.scene, 'penza', controller, 6, 1, CardOrient.HORIZONTAL_BOTTOM),
                      SquaCardView(self.scene, 'turma1', controller, 6, 0, CardOrient.SQUADE_BOTTOM),
                      CityCardView(self.scene, 'ryzan', controller, 5, 0, CardOrient.VERTICAL_LEFT),
                      CityCardView(self.scene, 'pskov', controller, 4, 0, CardOrient.VERTICAL_LEFT),
                      BnPrCardView(self.scene, 'bonus1', controller, 3, 0, CardOrient.VERTICAL_LEFT),
                      CityCardView(self.scene, 'krasn', controller, 2, 0, CardOrient.VERTICAL_LEFT),
                      CityCardView(self.scene, 'novosib', controller, 1, 0, CardOrient.VERTICAL_LEFT),
                      SquaCardView(self.scene, 'hotel', controller, 0, 0, CardOrient.SQUADE_TOP),
                      CityCardView(self.scene, 'chelyb', controller, 0, 1, CardOrient.HORIZONTAL_TOP),
                      CityCardView(self.scene, 'syktyv', controller, 0, 2, CardOrient.HORIZONTAL_TOP),
                      BnPrCardView(self.scene, 'straf2', controller, 0, 3, CardOrient.HORIZONTAL_TOP),
                      CityCardView(self.scene, 'vladik', controller, 0, 4, CardOrient.HORIZONTAL_TOP),
                      CityCardView(self.scene, 'moskva', controller, 0, 5, CardOrient.HORIZONTAL_TOP),
                      SquaCardView(self.scene, 'turma2', controller, 0, 6, CardOrient.SQUADE_TOP),
                      CityCardView(self.scene, 'kazan', controller, 1, 6, CardOrient.VERTICAL_RIGHT),
                      CityCardView(self.scene, 'bel', controller, 2, 6, CardOrient.VERTICAL_RIGHT),
                      BnPrCardView(self.scene, 'bonus2', controller, 3, 6, CardOrient.VERTICAL_RIGHT),
                      CityCardView(self.scene, 'perm', controller, 4, 6, CardOrient.VERTICAL_RIGHT),
                      CityCardView(self.scene, 'ekat', controller, 5, 6, CardOrient.VERTICAL_RIGHT)]

        self.mesView = MesView(self.contr)
        mes = self.scene.addWidget(self.mesView)
        mes.setPos(HORIZONTAL_HEIGHT + 25, HORIZONTAL_HEIGHT + 25)

        self.posList = [LPoint(6, 6), LPoint(6, 5), LPoint(6, 4), LPoint(6, 3),
                        LPoint(6, 2), LPoint(6, 1), LPoint(6, 0), LPoint(5, 0),
                        LPoint(4, 0), LPoint(3, 0), LPoint(2, 0), LPoint(1, 0),
                        LPoint(0, 0), LPoint(0, 1), LPoint(0, 2), LPoint(0, 3),
                        LPoint(0, 4), LPoint(0, 5), LPoint(0, 6), LPoint(1, 6),
                        LPoint(2, 6), LPoint(3, 6), LPoint(4, 6), LPoint(5, 6)]

    def add_message(self, mes):
        self.mesView.add_message(mes)

    def update_items(self):
        for item in self.items:
            item.update_values()


class PlayerAnimationItem(QObject):

    def __init__(self, image_number):
        super().__init__()

        self.image = QGraphicsPixmapItem(QPixmap(PLAYER_MARKER_IMAGES.get(image_number)).scaled(60, 60))

    def _set_pos(self, pos):
        self.image.setPos(pos)

    pos = pyqtProperty(QPointF, fset=_set_pos)


class PlayerAnimation():
    def __init__(self, master, image_number: int, offset: int = 0):
        self.count = 0
        self.scene = master.scene
        self.master = master
        self.offset = offset
        self.pl = PlayerAnimationItem(image_number)
        self.anim = QPropertyAnimation(self.pl, b'pos')
        self.scene.addItem(self.pl.image)
        coord_x, coord_y = self.getCoord(0)
        self.anim.setStartValue(QPoint(coord_x, coord_y))
        self.anim.setEndValue(QPoint(coord_x, coord_y))
        self.anim.start()
        self.anim.stop()
        self.last_player_pos = LPoint(6, 6)
        self.anim.finished.connect(self.spec)

    def init_player_pos(self, row: int, col: int):
        self.last_player_pos = LPoint(row, col)

    def drive_player(self, value):
        self.drive(value)
        QTimer().singleShot(4000, self.anim.start)

    def drive(self, steps: int):
        start = self.last_player_pos
        st_index = self.master.posList.index(start)
        self.anim.setDuration(steps * (500 - 40 * (steps - 1)))
        pos_len = len(self.master.posList)
        coord_x, coord_y = self.getCoord(st_index)
        self.anim.setStartValue(QPoint(coord_x, coord_y))
        rng = st_index + steps
        if rng >= pos_len:
            end_index = rng - pos_len
        else:
            end_index = rng
        count = 1
        while count <= steps:
            key = float(0.8 / steps * count)
            index = count + st_index
            if index >= pos_len:
                index = index - pos_len
            coord_x, coord_y = self.getCoord(index)
            self.anim.setKeyValueAt(key, QPoint(coord_x, coord_y))
            count += 1
        coord_x, coord_y = self.getCoord(end_index)
        self.anim.setEndValue(QPoint(coord_x, coord_y))
        self.last_player_pos = self.master.posList[end_index]
        # self.anim.finished.connect(lambda: self.anim.setKeyValues({}))
        self.anim.finished.connect(self.spec)

    def spec(self):
        self.anim.setKeyValues({})
        print(self.count)
        self.count += 1
        self.master.controller.start_game_2_part()

    def getCoord(self, index: int):
        offset_x = 0
        offset_y = 0
        if self.master.items[index].row == 0:
            offset_y = -self.offset
        elif self.master.items[index].row == 6:
            offset_y = self.offset
        if self.master.items[index].col == 0:
            offset_x = -self.offset
        elif self.master.items[index].col == 6:
            offset_x = self.offset
        ret_x = self.master.items[index].center.x() + offset_x
        ret_y = self.master.items[index].center.y() + offset_y
        return [ret_x, ret_y]


class PlayerView(QFrame):
    def __init__(self, controller, name: str, offset: int, anim_container):
        super().__init__()
        self.name = name
        self.controller = controller
        self.setFrameShape(QFrame.Panel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(3)
        self.player_type = self.get_info('player_type')
        self.w = 300
        self.h = 200
        # self.resize(self.w, self.h)
        self.grid = QGridLayout(self)
        self.image_size = 120
        self.setFont(QFont('Arial', 14))
        self.setMinimumSize(280, 200)
        self.setMaximumSize(380, 260)

        self.image_pixmap = QPixmap(self.get_image()).scaled(self.image_size, self.image_size)
        self.pic_image = QLabel()
        self.pic_image.setPixmap(self.image_pixmap)
        self.pic_image.setFrameShape(QFrame.Box)
        self.pic_image.setFrameShadow(QFrame.Raised)
        self.pic_image.setLineWidth(3)
        self.pic_image.setMaximumSize(self.image_size + 10, self.image_size + 10)
        self.pic_image.setMinimumSize(self.image_size + 10, self.image_size + 10)

        self.name_label = QLabel(text=name)
        self.name_label.setFont(QFont('Arial', 16))
        pl = self.name_label.palette()
        pl.setColor(QPalette.Window, QColor(PLAYER_COLORS.get(self.get_info('index'))))
        self.name_label.setAutoFillBackground(True)
        self.name_label.setPalette(pl)
        self.name_label.setFrameShape(QFrame.Panel)
        self.name_label.setFrameShadow(QFrame.Raised)
        self.name_label.setLineWidth(3)
        # self.name_label.setMinimumWidth(100)
        self.name_label.setMaximumHeight(50)
        self.name_label.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)

        # self.cash_label_name = QLabel(text='Наличные')
        self.cash_label_name = QLabel()
        cash_image = QPixmap(CASH_IMAGE).scaled(30, 30)
        self.cash_label_name.setPixmap(cash_image)

        self.cash_label_value = QLabel(get_format_value(self.get_info('cash')))
        self.cash_label_value.setFrameShape(QFrame.Panel)
        self.cash_label_value.setFrameShadow(QFrame.Sunken)
        self.cash_label_value.setMinimumSize(80, 50)
        self.cash_label_value.setMaximumSize(80, 50)
        # self.cash_label_value.setAlignment(Qt.AlignLeft|Qt.AlignHCenter)

        # self.capital_label_name = QLabel(text='Капитал')
        self.capital_label_name = QLabel()
        capital_image = QPixmap(CAPITAL_IMAGE).scaled(30, 30)
        self.capital_label_name.setPixmap(capital_image)

        self.capital_label_value = QLabel(get_format_value(self.get_info('capital')))
        self.capital_label_value.setFrameShape(QFrame.Panel)
        self.capital_label_value.setFrameShadow(QFrame.Sunken)
        self.capital_label_value.setMinimumSize(80, 50)
        self.capital_label_value.setMaximumSize(80, 50)
        # self.capital_label_value.setAlignment(Qt.AlignLeft|Qt.AlignHCenter)

        self.grid.addWidget(self.name_label, 0, 0, 1, 3)
        self.grid.addWidget(self.pic_image, 1, 0, 2, 1)
        self.grid.addWidget(self.cash_label_name, 1, 1)
        self.grid.addWidget(self.cash_label_value, 1, 2)
        self.grid.addWidget(self.capital_label_name, 2, 1)
        self.grid.addWidget(self.capital_label_value, 2, 2)
        self.mouseReleaseEvent = lambda event: self.show_info()

        self.anim = PlayerAnimation(anim_container, self.get_info('index'), offset)

        self.ready_btn = QPushButton(text='Бросить кубик')
        self.ready_btn.setVisible(False)
        self.ready_btn.clicked.connect(lambda: self.controller.player_ready_pressed(self.name))
        self.grid.addWidget(self.ready_btn, 3, 0)
        self.ready_btn.setStyleSheet("background: rgba(0,0,0,20%)")
        self.ready_btn.setFont(QFont('Arial', 12))

    def drive(self, value):
        self.anim.drive_player(value)

    def update_values(self):
        self.cash_label_value.setText(get_format_value(self.get_info('cash')))
        self.capital_label_value.setText(get_format_value(self.get_info('capital')))
        ready = self.get_info('ready')
        self.ready_btn.setVisible(not ready)

    def show_info(self):
        pass

    def get_image(self):
        if self.player_type == PlayerType.HUMAN:
            x = random.randint(0, 3)
            image = PLAYER_AVATOR_IMAGES.get(x)
        elif self.player_type == PlayerType.BOT:
            x = random.randint(4, 7)
            image = PLAYER_AVATOR_IMAGES.get(x)
        else:
            x = random.randint(0, 7)
            image = PLAYER_AVATOR_IMAGES.get(x)
        return image

    def get_info(self, info_item: str):
        info = self.controller.get_player_info(self.name)
        value = info.get(info_item)
        return value

    def get_all_info(self):
        info = self.controller.get_player_info(self.name)
        return info

    def get_name(self):
        value = self.get_info('name')
        return value


class CardView(QGraphicsView):
    def __init__(self, master, name: str, controller, row: int, col: int, orient: CardOrient):
        super().__init__()

        self.name = name

        self.rect_off_set = 2
        self.rect_off_size = 4
        self.rect_width = 4

        self.controller = controller
        self.simple_color = QColor(MAIN_COLOR)
        self.middle_main_color = QColor(MIDDLE_COLOR)
        self.text_color = QColor(TEXT_COLOR)
        self.border_color = QColor(BORDER_COLOR)

        self.font_size = 11

        self.verticalScrollBarPolicy = Qt.ScrollBarAlwaysOff
        self.horizontalScrollBarPolicy = Qt.ScrollBarAlwaysOff
        self.setFrameStyle(QFrame.NoFrame)
        # self.setBackgroundBrush(QBrush(QColor('#271D72')))
        self.setStyleSheet("background:transparent;")

        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.orient = orient
        self.master = master
        self.row = row
        self.col = col

        if self.orient == CardOrient.SQUADE_TOP or self.orient == CardOrient.SQUADE_BOTTOM:
            self.w = VERTICAL_WIDTH
            self.h = HORIZONTAL_HEIGHT

        elif self.orient == CardOrient.HORIZONTAL_BOTTOM or self.orient == CardOrient.HORIZONTAL_TOP:
            self.w = HORIZONTAL_WIDTH
            self.h = HORIZONTAL_HEIGHT

        elif self.orient == CardOrient.VERTICAL_LEFT or self.orient == CardOrient.VERTICAL_RIGHT:
            self.w = VERTICAL_WIDTH
            self.h = VERTICAL_HEIGHT

        self.resize(self.w, self.h)
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, self.w, self.h)

        self.my_font = QFont('Arial', self.font_size)
        # self.my_font.setItalic(True)
        self.my_font.setBold(True)

        self.pen = QPen(self.border_color)
        self.pen.setWidth(5)

        self.setScene(self.scene)
        main_border = 20

        proxy = self.master.addWidget(self)
        # proxy.setPos(10, 10)
        if self.row == 0:
            offset_y = 0
        else:
            offset_y = (self.row - 1) * VERTICAL_HEIGHT + HORIZONTAL_HEIGHT

        if self.col == 0:
            offset_x = 0
        else:
            offset_x = (self.col - 1) * HORIZONTAL_WIDTH + VERTICAL_WIDTH

        proxy.setPos(offset_x + main_border, offset_y + main_border)
        proxy.setOpacity(0.75)

        self.center = QPoint(offset_x + int(self.w / 2) - 11, offset_y + (self.h / 2) - 11)

        self.mouseReleaseEvent = lambda event: self.show_info_window()

    def get_info(self, info_item: str):
        info = self.controller.get_card_info(self.name)
        value = info.get(info_item)
        return value

    def get_all_info(self):
        info = self.controller.get_card_info(self.name)
        return info

    def get_image(self):
        image = CARD_IMAGES.get(self.name)
        return image

    def get_name(self):
        value = self.get_info('_name')
        return value

    def show_info_window(self):
        window1 = self.controller.view
        modal_window = InfoWindow(window1, Qt.Window)
        modal_window.setMinimumSize(320, 400)
        modal_window.setMaximumSize(320, 400)
        modal_window.move(window1.geometry().center() - modal_window.rect().center() - QPoint(40, 30))
        modal_window.setWindowTitle('Карточка')
        # modal_window.setWindowFlags( Qt.CustomizeWindowHint | Qt.WindowMaximizeButtonHint)
        # modal_window.setWindowFlags( Qt.WindowMaximizeButtonHint)
        # modal_window.setAttribute(Qt.WA_TranslucentBackground)
        # modal_window.setWindowFlags(Qt.FramelessWindowHint)

        info = self.get_all_info()

        label = QLabel()
        image_pixmap = QPixmap(self.get_image()).scaled(200, 200)
        label.setPixmap(image_pixmap)
        label.setFrameShape(QFrame.Panel)
        label.setFrameShadow(QFrame.Sunken)
        label.setLineWidth(2)

        label1 = QLabel()
        pl = label1.palette()
        pl.setColor(QPalette.Window, QColor(MIDDLE_COLOR))
        label1.setAutoFillBackground(True)
        label1.setPalette(pl)
        label1.setText(info.get('_name'))
        label1.setFont(QFont('Arial', 16, QFont.Bold))
        label1.setMinimumSize(260, 50)
        label1.setAlignment(Qt.AlignCenter)
        label1.setFrameShape(QFrame.Panel)
        label1.setFrameShadow(QFrame.Raised)
        label1.setLineWidth(6)

        label3 = QLabel(text=info.get('value'))
        label3.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        label3.setFont(QFont('Arial', 14, italic=True))
        label3.setMargin(10)

        label2 = QLabel(text=info.get('info'))
        label2.setAlignment(Qt.AlignLeft)
        # label2.setMargin(10)
        label2.setFont(QFont('Arial', 11, italic=True))
        label2.setWordWrap(True)

        grid = QGridLayout(modal_window)
        grid.addWidget(label1, 0, 0, 1, 2, Qt.AlignCenter)
        grid.addWidget(label, 1, 0, 1, 2, Qt.AlignCenter)
        grid.addWidget(label2, 2, 0, 1, 2, Qt.AlignCenter)
        grid.addWidget(label3, 3, 0, 1, 2, Qt.AlignCenter)

        modal_window.show()


class SquaCardView(CardView):
    def __init__(self, master, name: str, controller, row: int, col: int, orient: CardOrient):
        super().__init__(master, name, controller, row, col, orient)

        self.image_size = int(self.w * 0.5)

        self.rect = QGraphicsRectItem(0, 0, self.w, self.h)

        self.pen.setWidth(5)
        self.rect.setPen(QPen(self.pen))
        self.rect.setPos(0, 0)

        self.title = QGraphicsTextItem(self.get_name())
        self.title.setFont(self.my_font)
        self.title.setDefaultTextColor(self.text_color)

        self.image_pixmap = QPixmap(self.get_image()).scaled(self.image_size, self.image_size)
        self.pic_image = QGraphicsPixmapItem()
        self.pic_image.setPixmap(self.image_pixmap)

        self.image_rect = QGraphicsRectItem(0, 0, self.image_size + self.rect_off_size,
                                            self.image_size + self.rect_off_size)
        self.pen.setWidth(self.rect_width)
        self.image_rect.setPen(self.pen)

        self.value_text = QGraphicsTextItem()
        self.value_text.setFont(self.my_font)
        self.value_text.setDefaultTextColor(self.text_color)

        self.scene.addItem(self.rect)
        self.scene.addItem(self.image_rect)
        self.scene.addItem(self.title)
        self.scene.addItem(self.pic_image)
        self.scene.addItem(self.value_text)

        self.update_values()
        self.config()

    def config(self):

        if self.orient == CardOrient.SQUADE_BOTTOM:

            grad = QLinearGradient(int(self.w / 2), int(self.h * 0.1), int(self.w / 2), self.h - int(self.h * 0.1))
            grad.setColorAt(0, self.simple_color)
            grad.setColorAt(0.2, self.middle_main_color)
            grad.setColorAt(0.8, self.middle_main_color)
            grad.setColorAt(1, self.simple_color)
            self.rect.setBrush(QBrush(grad))

            self.title.setPos(int((self.w - self.title.boundingRect().width()) / 2), int(self.h * 0.08))

            self.pic_image.setOffset(int((self.w - self.image_size) / 2), int(self.h * 0.25))

            self.image_rect.setPos(int((self.w - self.image_size) / 2) - self.rect_off_set,
                                   int(self.h * 0.25) - self.rect_off_set)

            self.value_text.setPos(int((self.w - self.value_text.boundingRect().width()) / 2), int(self.h * 0.82))

        elif self.orient == CardOrient.SQUADE_TOP:

            grad = QLinearGradient(int(self.w / 2), int(self.h * 0.1), int(self.w / 2), self.h - int(self.h * 0.1))
            grad.setColorAt(0, self.simple_color)
            grad.setColorAt(0.2, self.middle_main_color)
            grad.setColorAt(0.8, self.middle_main_color)
            grad.setColorAt(1, self.simple_color)
            self.rect.setBrush(QBrush(grad))

            self.title.setPos(int((self.w - self.title.boundingRect().width()) / 2), int(self.h * 0.8))

            self.pic_image.setOffset(int((self.w - self.image_size) / 2), int(self.h * 0.25))

            self.image_rect.setPos(int((self.w - self.image_size) / 2) - self.rect_off_set,
                                   int(self.h * 0.25) - self.rect_off_set)

            self.value_text.setPos(int((self.w - self.value_text.boundingRect().width()) / 2), int(self.h * 0.08))

    def update_values(self):
        self.value_text.setPlainText(self.get_info("value"))


class BnPrCardView(CardView):
    def __init__(self, master, name: str, controller, row: int, col: int, orient: CardOrient):
        super().__init__(master, name, controller, row, col, orient)

        if self.orient == CardOrient.HORIZONTAL_BOTTOM or self.orient == CardOrient.HORIZONTAL_TOP:
            self.image_size = int(self.w * 0.8)

        elif self.orient == CardOrient.VERTICAL_LEFT or self.orient == CardOrient.VERTICAL_RIGHT:
            self.image_size = int(self.h * 0.8)

        self.rect = QGraphicsRectItem(0, 0, self.w, self.h)

        self.pen.setWidth(5)
        self.rect.setPen(QPen(self.pen))
        self.rect.setPos(0, 0)

        self.title = QGraphicsTextItem(self.get_name())
        self.title.setFont(self.my_font)
        self.title.setDefaultTextColor(self.text_color)
        self.image_pixmap = QPixmap(self.get_image()).scaled(self.image_size, self.image_size)
        # self.image_pixmap.createMaskFromColor(QColor('#FFFFFF'), Qt.MaskInColor)
        self.pic_image = QGraphicsPixmapItem()
        self.pic_image.setPixmap(self.image_pixmap)

        self.image_rect = QGraphicsRectItem(0, 0, self.image_size + self.rect_off_size,
                                            self.image_size + self.rect_off_size)
        self.pen.setWidth(self.rect_width)
        self.image_rect.setPen(self.pen)

        self.value_text = QGraphicsTextItem()
        self.value_text.setFont(self.my_font)
        self.value_text.setDefaultTextColor(self.text_color)

        self.scene.addItem(self.rect)
        self.scene.addItem(self.image_rect)
        self.scene.addItem(self.title)
        self.scene.addItem(self.pic_image)
        self.scene.addItem(self.value_text)

        self.update_values()
        self.config()

    def config(self):
        if self.orient == CardOrient.HORIZONTAL_BOTTOM:

            grad = QLinearGradient(int(self.w / 2), int(self.h * 0.1), int(self.w / 2), self.h - int(self.h * 0.1))
            grad.setColorAt(0, self.simple_color)
            grad.setColorAt(0.2, self.middle_main_color)
            grad.setColorAt(0.8, self.middle_main_color)
            grad.setColorAt(1, self.simple_color)
            self.rect.setBrush(QBrush(grad))

            self.title.setPos(int((self.w - self.title.boundingRect().width()) / 2), int(self.h * 0.15))

            self.pic_image.setOffset(int((self.w - self.image_size) / 2), int(self.h * 0.35))

            self.image_rect.setPos(int((self.w - self.image_size) / 2) - self.rect_off_set,
                                   int(self.h * 0.35) - self.rect_off_set)

            self.value_text.setPos(int((self.w - self.value_text.boundingRect().width()) / 2), int(self.h * 0.82))

        elif self.orient == CardOrient.HORIZONTAL_TOP:

            grad = QLinearGradient(int(self.w / 2), int(self.h * 0.1), int(self.w / 2), self.h - int(self.h * 0.1))
            grad.setColorAt(0, self.simple_color)
            grad.setColorAt(0.2, self.middle_main_color)
            grad.setColorAt(0.8, self.middle_main_color)
            grad.setColorAt(1, self.simple_color)
            self.rect.setBrush(QBrush(grad))

            self.title.setPos(int((self.w - self.title.boundingRect().width()) / 2),
                              self.h - int(self.h * 0.25) - self.font_size)

            self.pic_image.setOffset(int((self.w - self.image_size) / 2), self.h - int(self.h * 0.35) - self.image_size)

            self.image_rect.setPos(int((self.w - self.image_size) / 2) - self.rect_off_set,
                                   self.h - int(self.h * 0.35) - self.image_size - self.rect_off_set)

            self.value_text.setPos(int((self.w - self.value_text.boundingRect().width()) / 2), self.h - int(
                self.h * 0.87) - self.font_size)  # x = x - text.boundingRect().width() / 2

        elif self.orient == CardOrient.VERTICAL_LEFT:

            grad = QLinearGradient(int(self.w * 0.1), int(self.h / 2), self.w - int(self.w * 0.1), int(self.h / 2))
            grad.setColorAt(0, self.simple_color)
            grad.setColorAt(0.2, self.middle_main_color)
            grad.setColorAt(0.8, self.middle_main_color)
            grad.setColorAt(1, self.simple_color)
            self.rect.setBrush(QBrush(grad))

            self.title.setRotation(90.0)
            self.title.setPos(int(self.w * 0.85), int((self.h - self.title.boundingRect().width()) / 2))

            self.pic_image.setOffset(int(self.w * 0.25), int((self.h - self.image_size) / 2))

            self.image_rect.setPos(int(self.w * 0.25) - self.rect_off_set,
                                   int((self.h - self.image_size) / 2) - self.rect_off_set)

            self.value_text.setRotation(90.0)
            self.value_text.setPos(int(self.w * 0.18), int((self.h - self.value_text.boundingRect().width()) / 2))

        elif self.orient == CardOrient.VERTICAL_RIGHT:

            grad = QLinearGradient(int(self.w * 0.1), int(self.h / 2), self.w - int(self.w * 0.1), int(self.h / 2))
            grad.setColorAt(0, self.simple_color)
            grad.setColorAt(0.2, self.middle_main_color)
            grad.setColorAt(0.8, self.middle_main_color)
            grad.setColorAt(1, self.simple_color)
            self.rect.setBrush(QBrush(grad))

            self.title.setRotation(270.0)
            self.title.setPos(int(self.w * 0.15), int((self.h + self.title.boundingRect().width()) / 2))

            self.pic_image.setOffset(int(self.w * 0.35), int((self.h - self.image_size) / 2))

            self.image_rect.setPos(int(self.w * 0.35) - self.rect_off_set,
                                   int((self.h - self.image_size) / 2) - self.rect_off_set)

            self.value_text.setRotation(270.0)
            self.value_text.setPos(int(self.w * 0.82), int((self.h + self.value_text.boundingRect().width()) / 2))

    def update_values(self):
        self.value_text.setPlainText(self.get_info("value"))


class CityCardView(CardView):
    def __init__(self, master, name: str, controller, row: int, col: int, orient: CardOrient):
        super().__init__(master, name, controller, row, col, orient)

        self.star_pixmap = None
        self.star_min = 0.6

        if self.orient == CardOrient.HORIZONTAL_BOTTOM or self.orient == CardOrient.HORIZONTAL_TOP:
            self.image_size = int(self.w * 0.8)
            self.star_width = int(self.w * self.star_min)
            self.star_height = int(self.w * 0.27 * self.star_min)

        elif self.orient == CardOrient.VERTICAL_LEFT or self.orient == CardOrient.VERTICAL_RIGHT:
            self.image_size = int(self.h * 0.8)
            self.star_width = int(self.h * self.star_min)
            self.star_height = int(self.h * 0.27 * self.star_min)

            # self.star_pixmap.createMaskFromColor(QColor('#FFFFFF'), Qt.MaskInColor)

        self.star_pic = QGraphicsPixmapItem()

        self.rect_owner = QGraphicsRectItem(0, 0, self.w, self.h)

        self.pen.setWidth(4)
        self.rect_owner.setPen(QPen(self.pen))
        self.rect_owner.setPos(0, 0)

        self.title = QGraphicsTextItem(self.get_name())
        self.title.setFont(self.my_font)
        self.title.setDefaultTextColor(self.text_color)

        self.image_pixmap = QPixmap(self.get_image()).scaled(self.image_size, self.image_size)
        # self.image_pixmap.createMaskFromColor(QColor('#FFFFFF'), Qt.MaskInColor)
        self.pic_image = QGraphicsPixmapItem()
        self.pic_image.setPixmap(self.image_pixmap)

        self.image_rect = QGraphicsRectItem(0, 0, self.image_size + self.rect_off_size,
                                            self.image_size + self.rect_off_size)
        self.pen.setWidth(self.rect_width)
        self.image_rect.setPen(self.pen)

        self.value_text = QGraphicsTextItem()
        self.value_text.setFont(self.my_font)
        self.value_text.setDefaultTextColor(self.text_color)

        self.scene.addItem(self.rect_owner)
        self.scene.addItem(self.star_pic)
        self.scene.addItem(self.image_rect)
        self.scene.addItem(self.title)
        self.scene.addItem(self.pic_image)
        self.scene.addItem(self.value_text)

        self.update_values()
        self.config()

    def get_star_image(self):
        houses = self.get_info('house_count')
        image = STAR_IMAGE.get(houses)
        return image

    def get_group_color(self):
        group = self.get_info('group')
        color = GROUP_COLORS.get(group)
        return QColor(color)

    def get_owner_color(self):
        owner = self.get_info('owner_number')
        if owner < 0:
            color = MAIN_COLOR
        else:
            color = PLAYER_COLORS.get(owner)
        return QColor(color)

    def get_value(self):
        owner = self.get_info("owner_number")
        if owner == -1:
            value = self.get_info("cur_cost")
        else:
            value = self.get_info('cur_rent')
        return value

    def config(self):
        if self.orient == CardOrient.HORIZONTAL_BOTTOM:

            self.star_pic.setOffset(int((self.w - self.star_width) / 2), int(self.star_height / 2))

            self.title.setPos(int((self.w - self.title.boundingRect().width()) / 2), int(self.h * 0.15))

            self.pic_image.setOffset(int((self.w - self.image_size) / 2), int(self.h * 0.35))

            self.image_rect.setPos(int((self.w - self.image_size) / 2) - self.rect_off_set,
                                   int(self.h * 0.35) - self.rect_off_set)

            self.value_text.setPos(int((self.w - self.value_text.boundingRect().width()) / 2), int(self.h * 0.82))

        elif self.orient == CardOrient.HORIZONTAL_TOP:

            self.star_pic.setOffset(int((self.w - self.star_width) / 2),
                                    self.h - int(self.star_height / 2) - self.star_height)

            self.title.setPos(int((self.w - self.title.boundingRect().width()) / 2),
                              self.h - int(self.h * 0.25) - self.font_size)

            self.pic_image.setOffset(int((self.w - self.image_size) / 2), self.h - int(self.h * 0.35) - self.image_size)

            self.image_rect.setPos(int((self.w - self.image_size) / 2) - self.rect_off_set,
                                   self.h - int(self.h * 0.35) - self.image_size - self.rect_off_set)

            self.value_text.setPos(int((self.w - self.value_text.boundingRect().width()) / 2), self.h - int(
                self.h * 0.87) - self.font_size)  # x = x - text.boundingRect().width() / 2

        elif self.orient == CardOrient.VERTICAL_LEFT:

            self.star_pic.setRotation(90.0)
            self.star_pic.setOffset(int((self.h - self.star_width) / 2), -(self.w - int(self.star_height / 2)))

            self.title.setRotation(90.0)
            self.title.setPos(int(self.w * 0.85), int((self.h - self.title.boundingRect().width()) / 2))

            self.pic_image.setOffset(int(self.w * 0.25), int((self.h - self.image_size) / 2))

            self.image_rect.setPos(int(self.w * 0.25) - self.rect_off_set,
                                   int((self.h - self.image_size) / 2) - self.rect_off_set)

            self.value_text.setRotation(90.0)
            self.value_text.setPos(int(self.w * 0.18), int((self.h - self.value_text.boundingRect().width()) / 2))

        elif self.orient == CardOrient.VERTICAL_RIGHT:

            self.star_pic.setRotation(270.0)
            self.star_pic.setOffset(-(self.star_width + int((self.h - self.star_width) / 2)), int(self.star_height / 2))

            self.title.setRotation(270.0)
            self.title.setPos(int(self.w * 0.15), int((self.h + self.title.boundingRect().width()) / 2))

            self.pic_image.setOffset(int(self.w * 0.35), int((self.h - self.image_size) / 2))

            self.image_rect.setPos(int(self.w * 0.35) - self.rect_off_set,
                                   int((self.h - self.image_size) / 2) - self.rect_off_set)

            self.value_text.setRotation(270.0)
            self.value_text.setPos(int(self.w * 0.82), int((self.h + self.value_text.boundingRect().width()) / 2))

    def update_values(self):
        self.star_pixmap = QPixmap(self.get_star_image()).scaled(self.star_width, self.star_height)
        self.star_pic.setPixmap(self.star_pixmap)

        self.value_text.setPlainText(get_format_value(self.get_value()))

        if self.orient == CardOrient.HORIZONTAL_BOTTOM:

            grad = QLinearGradient(int(self.w / 2), int(self.h * 0.1), int(self.w / 2), self.h - int(self.h * 0.1))
            grad.setColorAt(0, self.get_group_color())
            grad.setColorAt(0.2, self.middle_main_color)
            grad.setColorAt(0.6, self.middle_main_color)
            grad.setColorAt(1, self.get_owner_color())
            self.rect_owner.setBrush(QBrush(grad))

        elif self.orient == CardOrient.HORIZONTAL_TOP:

            grad = QLinearGradient(int(self.w / 2), int(self.h * 0.1), int(self.w / 2), self.h - int(self.h * 0.1))
            grad.setColorAt(0, self.get_owner_color())
            grad.setColorAt(0.4, self.middle_main_color)
            grad.setColorAt(0.8, self.middle_main_color)
            grad.setColorAt(1, self.get_group_color())
            self.rect_owner.setBrush(QBrush(grad))

        elif self.orient == CardOrient.VERTICAL_LEFT:

            grad = QLinearGradient(int(self.w * 0.1), int(self.h / 2), self.w - int(self.w * 0.1), int(self.h / 2))
            grad.setColorAt(0, self.get_owner_color())
            grad.setColorAt(0.4, self.middle_main_color)
            grad.setColorAt(0.8, self.middle_main_color)
            grad.setColorAt(1, self.get_group_color())
            self.rect_owner.setBrush(QBrush(grad))

        elif self.orient == CardOrient.VERTICAL_RIGHT:

            grad = QLinearGradient(int(self.w * 0.1), int(self.h / 2), self.w - int(self.w * 0.1), int(self.h / 2))
            grad.setColorAt(0, self.get_group_color())
            grad.setColorAt(0.2, self.middle_main_color)
            grad.setColorAt(0.6, self.middle_main_color)
            grad.setColorAt(1, self.get_owner_color())
            self.rect_owner.setBrush(QBrush(grad))

    def show_info_window(self):
        window1 = self.controller.view
        modal_window = InfoWindow(window1, Qt.Window)
        modal_window.setMinimumSize(520, 350)
        modal_window.setMaximumSize(520, 350)
        modal_window.move(window1.geometry().center() - modal_window.rect().center() - QPoint(40, 30))
        modal_window.setWindowTitle('Карточка города')
        # modal_window.setWindowFlags( Qt.CustomizeWindowHint | Qt.WindowMaximizeButtonHint)
        # modal_window.setWindowFlags( Qt.WindowMaximizeButtonHint)
        # modal_window.setAttribute(Qt.WA_TranslucentBackground)
        # modal_window.setWindowFlags(Qt.FramelessWindowHint)
        self.setFont(QFont('Arial', 13, QFont.Bold))
        info = self.get_all_info()

        label = QLabel()
        image_pixmap = QPixmap(self.get_image()).scaled(200, 200)
        label.setPixmap(image_pixmap)
        label.setFrameShape(QFrame.Panel)
        label.setFrameShadow(QFrame.Sunken)
        label.setLineWidth(2)

        label1 = QLabel()
        pl = label1.palette()
        pl.setColor(QPalette.Window, self.get_group_color())
        label1.setAutoFillBackground(True)
        label1.setPalette(pl)
        label1.setText(info.get('name'))
        label1.setFont(QFont('Arial', 16, QFont.Bold))
        label1.setMinimumSize(480, 50)
        label1.setAlignment(Qt.AlignCenter)
        label1.setFrameShape(QFrame.Panel)
        label1.setFrameShadow(QFrame.Raised)
        label1.setLineWidth(6)

        label2 = QLabel(text='Владелец')
        label2.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        label2.setMargin(10)
        label3 = QLabel(text=info.get('owner_name'))
        label3.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        label3.setMargin(10)
        p3 = label3.palette()
        color = self.get_owner_color()
        if color == QColor(MAIN_COLOR):
            color = QColor(TEXT_COLOR)
        p3.setColor(QPalette.WindowText, color)
        p3.setColor(QPalette.Window, QColor(MAIN_COLOR))
        label3.setAutoFillBackground(True)
        label3.setPalette(p3)

        label4 = QLabel(text='Рента')
        label4.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label13 = QLabel(text=get_format_value(info.get("rent0")))
        label13.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        label5 = QLabel(text='С 1 домом')
        label5.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label6 = QLabel(text=get_format_value(info.get('rent1')))
        label6.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        label5.setMargin(10)
        label6.setMargin(10)

        label7 = QLabel(text='С 2 домом')
        label7.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label8 = QLabel(text=get_format_value(info.get('rent2')))
        label8.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        label7.setMargin(10)
        label8.setMargin(10)

        label9 = QLabel(text='С 3 домом')
        label9.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label10 = QLabel(text=get_format_value(info.get('rent3')))
        label10.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        label9.setMargin(10)
        label10.setMargin(10)

        label11 = QLabel(text='Цена')
        label11.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        label12 = QLabel(text=get_format_value(info.get('cost')))
        label12.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        label11.setMargin(10)
        label12.setMargin(10)

        label2.setFont(QFont('Arial', 13, QFont.Bold))
        label3.setFont(QFont('Arial', 13, QFont.Bold))
        label4.setFont(QFont('Arial', 13, QFont.Bold))
        label13.setFont(QFont('Arial', 13, QFont.Bold))
        label5.setFont(QFont('Arial', 13, QFont.Bold))
        label6.setFont(QFont('Arial', 13, QFont.Bold))
        label7.setFont(QFont('Arial', 13, QFont.Bold))
        label8.setFont(QFont('Arial', 13, QFont.Bold))
        label9.setFont(QFont('Arial', 13, QFont.Bold))
        label10.setFont(QFont('Arial', 13, QFont.Bold))
        label11.setFont(QFont('Arial', 13, QFont.Bold))
        label12.setFont(QFont('Arial', 13, QFont.Bold))

        grid = QGridLayout(modal_window)
        grid.addWidget(label1, 0, 0, 1, 7, Qt.AlignCenter)
        grid.addWidget(label, 1, 0, 6, 1, Qt.AlignCenter)
        grid.addWidget(label2, 1, 1)
        grid.addWidget(label3, 1, 2)
        grid.addWidget(label4, 2, 1)
        grid.addWidget(label13, 2, 2)
        grid.addWidget(label5, 3, 1)
        grid.addWidget(label6, 3, 2)
        grid.addWidget(label7, 4, 1)
        grid.addWidget(label8, 4, 2)
        grid.addWidget(label9, 5, 1)
        grid.addWidget(label10, 5, 2)
        grid.addWidget(label11, 6, 1)
        grid.addWidget(label12, 6, 2)

        owner_name = self.get_info('owner_name')
        if owner_name != 'Отсутствует':
            owner_info = self.controller.get_player_info(owner_name)
            plt = owner_info.get('player_type')
            if plt == PlayerType.HUMAN:
                if not owner_info.get('ready'):
                    if self.get_info('house_count') < 3 and owner_info.get('cash') >= self.get_info('cost'):
                        add_house_btn = QPushButton(text='Купить дом')
                        add_house_btn.setFont(QFont('Arial', 13, QFont.Bold))
                        # add_house_btn.setStyleSheet("background:transparent;")
                        add_house_btn.setStyleSheet("background: rgba(0,0,0,20%)")
                        add_house_btn.clicked.connect(lambda: self.add_house(modal_window))
                        grid.addWidget(add_house_btn, 7, 0)
                        modal_window.setMinimumSize(520, 400)
                        modal_window.setMaximumSize(520, 400)

                if owner_info.get('can_sell'):
                    sell_btn = QPushButton()
                    sell_btn.setFont(QFont('Arial', 13, QFont.Bold))
                    sell_btn.setStyleSheet("background: rgba(0,0,0,20%)")
                    sell_btn.clicked.connect(lambda: self.sell_house(modal_window))
                    if self.get_info('house_count') > 0:
                        sell_btn.setText('Продать дом')
                    else:
                        sell_btn.setText('Продать участок')

                    grid.addWidget(sell_btn, 7, 2)
                    modal_window.setMinimumSize(520, 400)
                    modal_window.setMaximumSize(520, 400)

        modal_window.show()

    def sell_house(self, window):
        window.close()
        self.controller.sell_house_pressed(self.get_info('owner_name'), self.name)

    def add_house(self, window):
        window.close()
        self.controller.add_house_pressed(self.get_info('owner_name'), self.name)


class InfoWindow(QWidget):
    def __init__(self, parent, window_type):
        super().__init__(parent, window_type)
        self.setWindowOpacity(0.9)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFont(QFont('Arial', 13, QFont.Bold))
        self.setWindowModality(Qt.WindowModal)
        self.setAttribute(Qt.WA_DeleteOnClose, True)

    def paintEvent(self, a0: QPaintEvent):
        painter = QPainter(self)
        painter.setBrush(QBrush(QColor(MAIN_COLOR)))
        painter.drawRect(self.rect())
