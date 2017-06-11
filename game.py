from enum import Enum
import pytmx
from PySide2.QtCore import (Qt, QTimer, QAbstractTransition)
from PySide2.QtGui import QPixmap, QVector2D
from PySide2.QtWidgets import (QGraphicsPixmapItem, QGraphicsView,
                               QGraphicsScene, QGraphicsItem,
                               QGraphicsItemGroup)


class Game(QGraphicsView):
    """ This is the main game class"""
    def __init__(self, parent=None):
        super().__init__()
        self.window_width = 630
        self.window_height = 600

        self.scene = QGraphicsScene()
        self.scale(1, 1)
        self.setScene(self.scene)
        self.world = QtTileMap("./res/images/Spritemaps/level1.tmx",
                               scene=self.scene)
        self.world.createPixmapItems()

        player = Player("./res/images/character.png", self.world)
        self.scene.addItem(player)

        self.setSceneRect(0, 0, self.window_width, self.window_height)
        self.setFixedSize(self.window_width, self.window_height)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


class Character(QGraphicsPixmapItem):
    def __init__(self, fileName, rect=None, parent=None):
        super().__init__(parent)
        self.srcImage = QPixmap(fileName)


class State:
    def __init__(self):
        self.transitions = None

    def next(self, msg):
        if msg in self.transitions:
            return self.transitions[msg]
        else:
            return self


class Falling(State):
    def __init__(self, character):
        super().__init__()
        self.character = character

    def run(self):
        self.character.velocity.x = 0
        self.character.velocity.y = 5
        self.character.acc = 0

    def next(self, msg):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
                'hitGround': self.character.standing
            }
        return State.next(self, msg)


class WalkingRight(State):
    def __init__(self, character):
        super().__init__()
        self.character = character

    def run(self):
        self.character.velocity.x = 5
        self.character.velocity.y = 0
        self.character.acc = 0

    def next(self, msg):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
                'hitGround': self.character.standing
            }
        return State.next(self, msg)


class Standing(State):
    def __init__(self, character):
        super().__init__()
        self.character = character

    def run(self):
        self.character.velocity.x = 0
        self.character.velocity.y = 0
        self.character.acc = 0

    def next(self, msg):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
                'fall': self.character.falling
            }
            self.transitions = {
                'jump': self.character.jumping
            }

        return State.next(self, msg)


class Jumping(State):
    def __init__(self, character):
        super().__init__()
        self.character = character

    def run(self):
        self.character.velocity.x = 0
        self.character.velocity.y = -10
        self.character.acc = 1

    def next(self, msg):
        # Lazy initialization:
        if not self.transitions:
            self.transitions = {
                'hitGround': self.character.standing
            }
        return State.next(self, msg)


class StateMachine:
    def __init__(self, initialState):
        self.currentState = initialState
        self.currentState.run()

    def next(self, msg):
        self.currentState = self.currentState.next(msg)
        self.currentState.run()


class Player(Character):
    def __init__(self, fileName, world, rect=None, parent=None):
        super().__init__(fileName, parent)
        self.world = world
        self.velocity = QVector2D(0, 0)
        self.acc = 0
        self.setPixmap(self.srcImage.copy(0, 0, 24, 32))

        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.update)
        self.updateTimer.start(10)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFocus()

        self.initialise()

    def startStateMachine(self):
        self.falling = Falling(self)
        self.standing = Standing(self)
        self.jumping = Jumping(self)
        self.sfm = StateMachine(self.falling)

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return
        if event.key() == Qt.Key_Space:
            self.sfm.next('jump')

    def getBbox(self):
        object_ = self.world.get_object_by_name("Player")
        self.setPos(object_.x, object_.y)
        bbox = [object_.width, object_.height]
        return bbox

    def initialise(self):
        self.bbox = self.getBbox()
        self.startStateMachine()

    def update(self):
        self.velocity.y += self.acc
        self.setPos(self.x() + self.velocity.x,
                    self.y() + self.velocity.y)

        collidingItems = self.collidingItems()

        for item in collidingItems:
            if self.world.groups['Tile Layer 1'].isAncestorOf(item):
                self.sfm.next('hitGround')


class QtTileMap(pytmx.TiledMap):
    def __init__(self, fileName, scene):
        super().__init__(fileName, image_loader=self.qtImageLoader)
        self.scene = scene
        self.groups = {}

    def createPixmapItems(self):
        for layer in self.layers:
            layerItem = QGraphicsPixmapItem()
            self.groups[layer.name] = layerItem
            self.scene.addItem(layerItem)
            try:
                for x, y, image in layer.tiles():
                    tileItem = QGraphicsPixmapItem(layerItem)
                    tileItem.setPixmap(image)
                    tileItem.setPos(x * tileItem.pixmap().width(),
                                    y * tileItem.pixmap().height())

            except AttributeError:
                pass

    def qtImageLoader(self, filename, colorkey=False, **kwargs):
        srcImage = QPixmap(filename)

        def extract_image(rect, flags):
            x, y = rect[0], rect[1]
            width, height = rect[2], rect[3]
            tileImg = srcImage.copy(x, y, width, height)
            return tileImg

        return extract_image
