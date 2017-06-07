from enum import Enum
import pytmx
from PySide2.QtCore import (Qt, QTimer, QAbstractTransition)
from PySide2.QtGui import QPixmap, QVector2D
from PySide2.QtWidgets import (QGraphicsPixmapItem, QGraphicsView,
                               QGraphicsScene, QGraphicsItem)


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


class State():
    pass


class StateMachine():
    def __init__(self, initialState):
        self.currentState = initialState
        self.currentState.run()

    def runAll(self, states):
        for i in states:
            print(i)
            self.currentState = self.currentState.next(i)
            self.currentState.run()


class Standing(State):
    def execute(self):
        print("I am standing")


class Movement(State):
    def execute(self):
        print("I am moving")


class Jumping(State):
    def execute(self):
        print("I am jumping")


class Transition():
    def __init__(self, toState):
        self.toState = toState

    def execute(self):
        print("transitioning...")


class MovementTransition(Transition):
    def __init__(self, toState, player):
        super().__init__(toState)
        self.player = player

    def execute(self, key):
        pass

class FSM():
    def __init__(self, char):
        self.char = char
        self.states = {}
        self.transitions = {}
        self.curState = None
        self.curTransition = None

    def setInitialState(self, name):
        self.curState = self.states[name]

    def setTransition(self, name):
        self.curTransition = self.transitions[name]

    def execute(self):
        if self.curTransition:
            self.curTransition.execute()
            self.curState = self.states[self.curTransition.toState]
            self.curTransition = None
        self.curState.execute()


class Player(Character):
    class EventType(Enum):
        Release = 1
        Press = 2

    def __init__(self, fileName, world, rect=None, parent=None):
        super().__init__(fileName, parent)
        self.world = world
        self.initialise()
        self.buildInputStateMachine()
        self.setPixmap(self.srcImage.copy(0, 0, 24, 32))
        self.velocity = QVector2D(0, 0)
        self.updateTimer = QTimer()
        self.updateTimer.timeout.connect(self.update)
        self.updateTimer.start(50)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFocus()

    def buildInputStateMachine(self):
        pass

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return

    def initialise(self):
        for object_ in self.world.objects:
            if object_.name == 'Player':
                self.setPos(object_.x, object_.y)

    def update(self):
        self.setPos(self.x(),
                    self.y() + 5)


class QtTileMap(pytmx.TiledMap):
    def __init__(self, fileName, scene):
        super().__init__(fileName, image_loader=self.qtImageLoader)
        self.scene = scene

    def createPixmapItems(self):
        for layer in self.layers:
            try:
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
