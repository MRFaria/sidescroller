from PyQt5.QtWidgets import (QGraphicsPixmapItem, QGraphicsView,
                             QGraphicsScene, QGraphicsRectItem,
                             QGraphicsItem)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QTimer
import pytmx


class Game(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__()
        self.window_width = 800
        self.window_height = 600

        self.scene = QGraphicsScene()
        self.scale(5, 5)
        self.setScene(self.scene)
        self.map1 = QtTileMap("./res/images/Map/sample_map.tmx",
                              scene=self.scene)
        self.map1.createPixmapItems()

        player = Player("./res/images/Spritesheet/characters.png")
        self.scene.addItem(player)
        player.setFlag(QGraphicsItem.ItemIsFocusable, True)
        player.setFocus()

        self.setSceneRect(0, 0, self.window_width, self.window_height)
        self.setFixedSize(self.window_width, self.window_height)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


class Character(QGraphicsPixmapItem):
    def __init__(self, fileName, parent):
        super().__init__(parent)
        print(fileName)
        self.srcImage = QPixmap(fileName)


class Player(Character):
    def __init__(self, fileName, parent=None):
        super().__init__(fileName, parent)
        self.setPixmap(self.srcImage.copy(0, 0, 16, 16))
        self.hmotion = 0
        self.vmotion = 0
        self.speed = 5
        self.moveTimer = QTimer()
        self.moveTimer.timeout.connect(self.move)
        self.moveTimer.start(50)

    def move(self):
        self.setPos(self.x() + self.speed*self.hmotion,
                    self.y() + self.speed*self.vmotion)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Left:
            self.hmotion = -1
        elif e.key() == Qt.Key_Right:
            self.hmotion = 1
        elif e.key() == Qt.Key_Up:
            self.vmotion = -1
        elif e.key() == Qt.Key_Down:
            self.vmotion = 1

    def keyReleaseEvent(self, e):
        if e.key() == Qt.Key_Left:
                self.hmotion = 0
        elif e.key() == Qt.Key_Right:
                self.hmotion = 0
        elif e.key() == Qt.Key_Up:
            self.vmotion = 0
        elif e.key() == Qt.Key_Down:
            self.vmotion = 0


class QtTileMap(pytmx.TiledMap):
    def __init__(self, fileName, scene):
        super().__init__(fileName, image_loader=self.qtImageLoader)
        self.scene = scene

    def createPixmapItems(self):
        for layer in self.layers:
            for x, y, image in layer.tiles():
                tileItem = QGraphicsPixmapItem()
                tileItem.setPixmap(image)
                tileItem.setPos(x * tileItem.pixmap().width(),
                                y * tileItem.pixmap().height())
                props = self.get_tile_properties(x, y,
                                                 self.layers.index(layer))
                try:
                    props['item'] = tileItem
                except TypeError:
                    props = {'sceneItem': tileItem}

                gid = layer.data[y][x]
                self.set_tile_properties(gid, props)
                self.scene.addItem(tileItem)

    def qtImageLoader(self, filename, colorkey=False, **kwargs):
        srcImage = QPixmap(filename)

        def extract_image(rect, flags):
            x, y = rect[0], rect[1]
            width, height = rect[2], rect[3]
            tileImg = srcImage.copy(x, y, width, height)
            return tileImg

        return extract_image