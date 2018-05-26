from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QPushButton
from PyQt5.QtGui import QLinearGradient, QPixmap, QBrush, QImage
from PyQt5.QtCore import Qt, QRectF, QRect, QTimer
from PIL.ImageQt import ImageQt
import sys, random
import numpy
from numpy.random import random_integers as rand
import time
import xml.dom.minidom as xm
import cmath

map_height = 24
map_width = 24

class Player:

    def __init__(self, X, Y, ind):
        self.index = ind
        self.X = X
        self.Y = Y
        self.alive = True
        self.prev_x = X
        self.prev_y = Y
    def reset(self):
        self.X = 1
        self.Y = 1
        self.alive = True

class Bomb:
    def __init__(self, X, Y, tura, start, owner):
        self.X = X
        self.Y = Y
        self.triggered = False
        self.start = start
        self.owner = owner
    def trigger(self):
        self.triggered = True

class Bot:
    def __init__(self, X, Y, ind):

        self.index = ind
        self.X = X
        self.Y = Y
        self.alive = True
        self.prev_x = X
        self.prev_y = Y
        self.left_bomb = False
        self.players = []
        self.board = []
        self.left_bomb = False


    def set_board(self, board):
        self.board = board

    def set_player_position(self, players):
        self.players = players

    def set_bombs(self, bombs):
        self.bombs = bombs

    #Sprawdzic przed zmiana wsp
    def is_bomb_or_un_dst_obst_there(self, dir):

        if dir == "r":
            if self.X + 2 < map_width and self.Y + 1 < map_width and self.X > 0 and self.Y > 0:
                if self.board[self.X+1][self.Y+1] == "XX" or self.board[self.X+2][self.Y] == "XX" or self.board[self.X+1][self.Y-1] == "XX" or \
                    self.board[self.X+1][self.Y] == "XX" or self.board[self.X+1][self.Y] == "##" or self.board[self.X][self.Y] == "XX":
                    return True
        if dir == "l":
            if self.X - 2 < map_width and self.Y + 1 < map_width and self.X > 0 and self.Y > 0:
                if self.board[self.X-1][self.Y+1] == "XX" or self.board[self.X-2][self.Y] == "XX" or self.board[self.X-1][self.Y-1] == "XX" or \
                        self.board[self.X - 1][self.Y] == "XX" or self.board[self.X-1][self.Y] == "##" or self.board[self.X][self.Y] == "XX":
                    return True
        if dir == "u":
            if self.Y - 2 < map_width and self.X + 1 < map_width and self.X > 0 and self.Y > 0:
                if self.board[self.X][self.Y-2] == "XX" or self.board[self.X+1][self.Y-1] == "XX" or self.board[self.X-1][self.Y-1] == "XX" or \
                    self.board[self.X][self.Y - 1]== "XX" or self.board[self.X][self.Y-1] == "##" or self.board[self.X][self.Y] == "XX":
                    return True
        if dir == "d":
            if self.Y + 2 < map_width and self.X + 1 < map_width and self.X > 0 and self.Y > 0:
                if self.board[self.X+1][self.Y+1] == "XX" or self.board[self.X][self.Y+2] == "XX" or self.board[self.X-1][self.Y+1] == "XX" or \
                    self.board[self.X][self.Y+1]== "XX" or self.board[self.X][self.Y+1] == "##" or self.board[self.X][self.Y] == "XX":
                    return True

        return False

    def where_is_player(self):
        ret_val = []

        if self.players[0].X < self.X:
            ret_val.append("l")
            ret_val.append("r")
        if self.players[0].X > self.X:
            ret_val.append("r")
            ret_val.append("l")
        if self.players[0].X == self.X:
            ret_val.append("e")
            if self.players[0].Y > self.Y:
                ret_val.append("d")
            if self.players[0].Y < self.Y:
                ret_val.append("u")
        if self.players[0].Y > self.Y:
            ret_val.append("d")
            ret_val.append("u")
        if self.players[0].Y < self.Y:
            ret_val.append("u")
            ret_val.append("d")
        if self.players[0].Y == self.Y:
            if self.players[0].X > self.X:
                ret_val.append("r")
            if self.players[0].X < self.X:
                ret_val.append("l")
            ret_val.append("e")

        return ret_val

    def is_obstacle_there(self, dir):
        if dir == "r":
            if self.board[self.X + 1][self.Y] == "**":
                return True
        if dir == "l":
            if self.board[self.X - 1][self.Y] == "**":
                return True
        if dir =="u":
            if self.board[self.X][self.Y - 1] == "**":
                return True
        if dir == "d":
            if self.board[self.X][self.Y + 1] == "**":
                return True
        return False

    def leave_bomb(self):
        self.left_bomb = True

    def is_bomb_left(self):
        return self.left_bomb

    def change_cords(self, move, move2):
        if move == "r":
            self.X +=1
        if move  == "l":
            self.X -= 1
        if move == "u":
            self.Y -= 1
        if move == "d":
            self.Y += 1
        if move == "e":
            if move2 == "u":
                self.Y -= 1
            if move2 == "d":
                self.Y += 1
        if move2 == "e":
            if move == "l":
                self.X -= 1
            if move == "r":
                self.X += 1



    def change_cords_by_value(self, X, Y):
        self.X = X
        self.Y = Y

    def move(self):
        if self.left_bomb:
            self.left_bomb = False

        #lista najpierw prawo/lewo potem gora/dol "e" jesli rowne
        player_positions = self.where_is_player()

        if not self.is_bomb_or_un_dst_obst_there(player_positions[0]):
            if self.is_obstacle_there(player_positions[0]):
                self.leave_bomb()
                self.change_cords_by_value(self.prev_x, self.prev_y)
            else:
                self.prev_x = self.X
                self.prev_y = self.Y
                self.change_cords(player_positions[0], player_positions[1])

        elif not self.is_bomb_or_un_dst_obst_there(player_positions[2]):
            if self.is_obstacle_there(player_positions[2]):
                self.leave_bomb()
                self.change_cords_by_value(self.prev_x, self.prev_y)
            else:
                self.prev_x = self.X
                self.prev_y = self.Y
                self.change_cords(player_positions[2], player_positions[1])

        elif not self.is_bomb_or_un_dst_obst_there(player_positions[1]):
            if self.is_obstacle_there(player_positions[1]):
                self.leave_bomb()
                self.change_cords_by_value(self.prev_x, self.prev_y)
            else:
                self.prev_x = self.X
                self.prev_y = self.Y
                self.change_cords(player_positions[1], player_positions[0])

        elif not self.is_bomb_or_un_dst_obst_there(player_positions[3]):
            if self.is_obstacle_there(player_positions[3]):
                self.leave_bomb()
                self.change_cords_by_value(self.prev_x, self.prev_y)
            else:
                self.prev_x = self.X
                self.prev_y = self.Y
                self.change_cords(player_positions[3], player_positions[0])



class MyRect(QtWidgets.QGraphicsRectItem):

    rect_height = 28
    rect_width = 28

    map_height = 24
    map_width = 24

    def __init__(self, x, y, path):
        super().__init__(self.rect_width + x * self.rect_width,\
                                                self.rect_height + (self.map_width - y - 1) *\
                                                self.rect_height, self.rect_height, self.rect_height)
        self.x = x
        self.y = y

        image = QImage(path)
        image = image.scaled(self.rect_height, self.rect_width, Qt.IgnoreAspectRatio)
        brush = QBrush(image)
        self.setBrush(brush)

    def mouseReleaseEvent(self, event):
        # Do your stuff here.
        print('Jestem sobie tutaj: ', end='')
        print(self.x, end='')
        print(", ", end="")
        print(self.y)
        return QtWidgets.QGraphicsRectItem.mouseReleaseEvent(self, event)



class MyView(QGraphicsView):
    map_height = 24
    map_width = 24

    WYSOKOSC_OKNA = 900
    SZEROKOSC_OKNA = 720

    rect_height = 28
    rect_width = 28

    bomb_path = 'images/honeyPot.jpg'
    bomberman_path = 'images/winnieThePooh.jpg'
    bot_path = 'images/tigger.jpg'
    destructable_path = 'images/bush.jpg'
    undestructable_path = 'images/tree.jpg'
    road_path = 'C:/Projekty/droga.jpg'

    
    players = []
    bots = []
    current_round = 0
    bombs = []
    key = '1'
    current_player_index = 0
    number_of_players = 1
    number_of_bots = 1

    bombs = []

    timer = QTimer()

    def __init__(self):
        QGraphicsView.__init__(self)
        self.scene = QGraphicsScene(0, 0, self.WYSOKOSC_OKNA, self.SZEROKOSC_OKNA)
        for i in range(self.number_of_players):
            self.players.append(Player(1 + i*10, 1 + i*10, i))

        for i in range(self.number_of_bots):
            self.bots.append(Bot(10 + (i+1)*6, 10 + (i+1)*6, i + 1))

        self.score = 0
        self.view = QGraphicsView(self.scene)
        self.getBoard()
        for bot in self.bots:
            bot.set_board(self.boar)
            bot.set_player_position(self.players)
            bot.set_bombs(self.bombs)

        #self.intro()
        self.drawBoard()

        self.setScene(self.scene)
        # self.timer.timeout.connect(self.draw_intro)
        # self.timer.start(10)
        self.timer.timeout.connect(self.update)
        self.timer.start(10)
        self.timer_boty = QTimer()
        self.timer_boty.timeout.connect(self.move_bot)
        self.timer_boty.start(500)
        self.textbox = QtWidgets.QGraphicsTextItem()
        self.textbox.setPos(
            QtCore.QPointF(self.rect_width * (self.map_height + 1.5), self.rect_width * 3))
        self.textbox.setPlainText("Score = " + str(self.score))

        self.scene.addItem(self.textbox)

   


    def initBoard(self):
        '''initiates board'''

        self.maz = self.maze(self.map_width, self.map_height)
        self.getBoard()
        for i in range(self.number_of_players):
            self.players.append(Player(1, 1, i))

        self.curX = 0
        self.curY = 0
        self.numLinesRemoved = 0
        self.board = []

    def get_obj_ind(self, x, y):
        for i in range(len(self.itemy)):
            if self.itemy[i].x == x and self.itemy[i].y == y:
                return i

    def get_label_from_scene(self):
        ret = -1
        for i in range(len(self.itemy)):
            if type(self.itemy[i]) == type(QtWidgets.QGraphicsTextItem()):
                ret = i
        return ret


    def update(self):
        self.textbox.setPlainText("Score = " + str(self.score))

        for bomba in self.bombs:
            self.boar[bomba.X][bomba.Y] = 'XX'  # wstawiamy bomby w plansze
            self.drawImage(bomba.X, bomba.Y, self.bomb_path)
        for gracz in self.players:
            if gracz.alive:
                self.boar[gracz.X][gracz.Y] = 'OO'  # wstawiamy gracza w plansze (usuwanie starego pionka gracza w linijce 57)
                self.drawImage(gracz.prev_x, gracz.prev_y, self.road_path)
                self.drawImage(gracz.X, gracz.Y, self.bomberman_path)

        for bot in self.bots:
            self.boar[bot.X][bot.Y] = 'BB'
            self.drawImage(bot.prev_x, bot.prev_y, self.road_path)
            self.drawImage(bot.X,bot.Y, self.bot_path)

        self.trigger_bombs()
        # self.write_board_xml()
        # self.read_board_xml()

    def read_board_xml(self):
        xmldoc = xm.parse('somefile.xml')

        rowslist = xmldoc.getElementsByTagName('row')

        for i in range(len(rowslist)):
            obj = rowslist[i].getElementsByTagName('obj')
            for j in range(len(obj)):
                self.boar[i][j] = obj[j].firstChild.data
        print(self.boar)


    def write_board_xml(self):
        doc = xm.Document()
        map_elem = doc.createElement("mapa")
        for i in range(len(self.boar)):
            row_elem = doc.createElement("row")

            for j in range(len(self.boar[0])):
                obj_elem = doc.createElement("obj")
                row_elem.appendChild(obj_elem)
                obj_elem.appendChild(doc.createTextNode(self.boar[i][j]))
            map_elem.appendChild(row_elem)
        doc.appendChild(map_elem)
        # doc.writexml(sys.stdout)
        #print(doc.toprettyxml())

        with open('somefile.xml', 'w') as the_file:
            the_file.write(doc.toprettyxml())

    def drawBoard(self):  # rysowanie planszy
        self.scene.clear()
        for bomba in self.bombs:
            self.boar[bomba.X][bomba.Y] = 'XX'  # wstawiamy bomby w plansze
        for gracz in self.players:
            if gracz.alive:
                self.boar[gracz.X][gracz.Y] = 'OO'  # wstawiamy gracza w plansze (usuwanie starego pionka gracza w linijce 57)

        for bot in self.bots:
            self.boar[bot.X][bot.Y] = 'BB'

        for i in range(len(self.boar)):
            for j in range(len(self.boar[i])):
                if self.boar[i][j] == '##':
                    self.drawImage( i,(j),self.undestructable_path)
                elif self.boar[i][j] == '**':
                    self.drawImage( i,(j), self.destructable_path)
                elif self.boar[i][j] == '  ':
                    self.drawImage( i,(j),self.road_path)

                elif self.boar[i][j] == 'OO':
                    path = self.bomberman_path
                    self.drawImage( i,  + (j), path)

                elif self.boar[i][j] == 'XX':
                    path = self.bomb_path
                    self.drawImage(i, (j, path))

                elif self.boar[i][j] == 'BB':
                    path = self.bot_path
                    self.drawImage(i, (j), path)

    def getBoard(self):  # tworzenie planszy stringow z tablicy true/false wygenerowanej przez funkcje maze

        temp = numpy.zeros((self.map_width, self.map_height), dtype=bool)
        temp = temp.astype(str)
        for x in range(self.map_width):
            for y in range(self.map_height):
                if x == 0 or y == 0 or x == self.map_width - 1 or y == self.map_height - 1:
                    temp[x][y] = "##"
                elif x%2 == 0 and y%2 == 0:
                    temp[x][y] = "##"
                else:
                    temp[x][y] = "**"
                for i in range(len(self.players)):
                    if temp[self.players[i].X + 1][self.players[i].Y] != "##":
                        temp[self.players[i].X + 1][self.players[i].Y] = "  "
                    if temp[self.players[i].X][self.players[i].Y + 1] != "##":
                        temp[self.players[i].X][self.players[i].Y + 1] = "  "
                    if temp[self.players[i].X + 2][self.players[i].Y] != "##":
                        temp[self.players[i].X + 2][self.players[i].Y] = "  "
                    if temp[self.players[i].X][self.players[i].Y + 2] != "##":
                        temp[self.players[i].X][self.players[i].Y + 2] = "  "
                for i in range(len(self.bots)):
                    if temp[self.bots[i].X - 1][self.bots[i].Y] != "##":
                        temp[self.bots[i].X - 1][self.bots[i].Y] = "  "
                    if temp[self.bots[i].X][self.bots[i].Y - 1] != "##":
                        temp[self.bots[i].X][self.bots[i].Y - 1] = "  "
                    if temp[self.bots[i].X - 2][self.bots[i].Y] != "##":
                        temp[self.bots[i].X - 2][self.bots[i].Y] = "  "
                    if temp[self.bots[i].X][self.bots[i].Y - 2] != "##":
                        temp[self.bots[i].X][self.bots[i].Y - 2] = "  "

                temp[14][16] = "  "
                temp[16][14] = "  "
                temp[14][15] = "  "
                temp[15][17] = "  "
                temp[15][15] = "  "
        self.boar = temp
    #Za kolor podajemy Qt.red na przyklad
    def drawRect(self, x, y, color):
        self.item = MyRect(x, y, color)
        self.item.setAcceptHoverEvents(True)
        self.item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.scene.addItem(self.item)


    def drawImage(self, x, y, path):
        #Usuwanie itemow ze sceny
        self.itemy = self.scene.items()
        if len(self.itemy) > self.map_height * self.map_width:
            ind = self.get_obj_ind(x, y)
            self.scene.removeItem(self.itemy[ind])
        self.item = MyRect(x, y, path)
        self.item.setAcceptHoverEvents(True)
        self.item.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable)
        self.scene.addItem(self.item)


    def keyPressEvent(self, event):
        '''processes key press events'''

        key = event.key()

        if key == Qt.Key_P:
            self.pause()
            return

        elif key == Qt.Key_Left:
            if self.players:
                self.move_left(self.players[self.current_player_index])
                self.current_round += 1

        elif key == Qt.Key_Right:
            if self.players:
                self.move_right(self.players[self.current_player_index])
                self.current_round += 1

        elif key == Qt.Key_Down:
            if self.players:
                self.move_down(self.players[self.current_player_index])
                self.current_round += 1

        elif key == Qt.Key_Up:
            if self.players:
                self.move_up(self.players[self.current_player_index])
                self.current_round += 1

        elif key == Qt.Key_Space:
            if self.players:
                if self.players[self.current_player_index].alive:
                    self.current_round += 1
                    self.add_bomb(self.players[self.current_player_index])

        elif key == Qt.Key_D:
            self.oneLineDown()

        #self.drawBoard()


    def move_up(self, gracz):
        if gracz.Y < self.map_height - 1 and self.boar[gracz.X][gracz.Y + 1] != '**' and self.boar[gracz.X][gracz.Y + 1] != '##':
            self.boar[gracz.X][gracz.Y] = '  '  # zastapienie starej pozycji gracza pustym polem
            gracz.prev_x = gracz.X
            gracz.prev_y = gracz.Y
            gracz.Y += 1

    def move_down(self, gracz):
        if gracz.Y > 1 and self.boar[gracz.X][gracz.Y - 1] != '**' and self.boar[gracz.X][gracz.Y - 1] != '##':
            self.boar[gracz.X][gracz.Y] = '  '  # zastapienie starej pozycji gracza pustym polem
            gracz.prev_x = gracz.X
            gracz.prev_y = gracz.Y
            gracz.Y -= 1

    def move_left(self, gracz):
        if gracz.X > 1 and self.boar[gracz.X - 1][gracz.Y] != '**' and self.boar[gracz.X - 1][gracz.Y] != '##':
            self.boar[gracz.X][gracz.Y] = '  '  # zastapienie starej pozycji gracza pustym polem
            gracz.prev_x = gracz.X
            gracz.prev_y = gracz.Y
            gracz.X -= 1

    def move_right(self, gracz):
        if gracz.X < self.map_height - 1 and self.boar[gracz.X + 1][gracz.Y] != '**' and self.boar[gracz.X + 1][gracz.Y] != '##':
            self.boar[gracz.X][gracz.Y] = '  '  # zastapienie starej pozycji gracza pustym polem
            gracz.prev_x = gracz.X
            gracz.prev_y = gracz.Y
            gracz.X += 1

    def add_bomb(self, gracz):  # poruszanie sie
        self.bombs.append(Bomb(gracz.X, gracz.Y, self.current_round, time.time(), gracz.index))
        # do listy bomb dodajemy w ktorej turze została postawiona i jej koordynaty

    #Obsluga wybuchania bomba
    def trigger_bombs(self):
        for bomba in self.bombs:
            if time.time() - bomba.start > 3:
            #if bomba.triggered:
                self.bomb_clear_surroundings(bomba)
                self.kill_players(bomba)
                self.bombs.remove(bomba)
                if bomba.owner == self.players[self.current_player_index].index:
                    self.score += 1

    #Czyszczenie pol naokolo bomby
    def bomb_clear_surroundings(self, bomba):
        if self.boar[bomba.X][bomba.Y + 1] != "##":
            self.boar[bomba.X][bomba.Y + 1] = "  "
            self.drawImage(bomba.X, bomba.Y + 1, self.road_path)

        if self.boar[bomba.X][bomba.Y - 1] != "##":
            self.boar[bomba.X][bomba.Y - 1] = "  "
            self.drawImage(bomba.X, bomba.Y - 1, self.road_path)

        if self.boar[bomba.X + 1][bomba.Y] != "##":
            self.boar[bomba.X + 1][bomba.Y] = "  "
            self.drawImage(bomba.X + 1, bomba.Y, self.road_path)

        if self.boar[bomba.X - 1][bomba.Y] != "##":
            self.boar[bomba.X - 1][bomba.Y] = "  "
            self.drawImage(bomba.X - 1, bomba.Y, self.road_path)

        self.boar[bomba.X][bomba.Y] = "  "
        self.drawImage(bomba.X, bomba.Y, self.road_path)

    def kill_players(self, bomba):
        for gracz in self.players:
            if gracz.X == bomba.X + 1 and gracz.Y == bomba.Y:
                gracz.alive = False
            if gracz.X == bomba.X - 1 and gracz.Y == bomba.Y:
                gracz.alive = False
            if gracz.X == bomba.X and gracz.Y == bomba.Y + 1:
                gracz.alive = False
            if gracz.X == bomba.X and gracz.Y == bomba.Y - 1:
                gracz.alive = False



    def move_bot(self):
        for bot in self.bots:
            stare_x = bot.X
            stare_y = bot.Y
            bot.move()
            if bot.is_bomb_left():
                self.bombs.append(Bomb(stare_x, stare_y, self.current_round, time.time(), 1))
                self.boar[stare_x][stare_y] = "XX"
            else:
                self.boar[stare_x][stare_y] = "  "
            self.boar[bot.X][bot.Y] = "BB"
            bot.set_player_position(self.players)
            bot.set_board(self.boar)
            bot.set_bombs(self.bombs)



class window(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(window, self).__init__()
        self.view = MyView()
        self.setCentralWidget(self.view)

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    view = window()
    view.show()
    sys.exit(app.exec_())

