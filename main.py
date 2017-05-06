from PyQt5.QtWidgets import QApplication
import sys
import game

if __name__ == '__main__':
    # Hack to run this interactively
    try:
        if app:
            pass
    except NameError:
        app = QApplication(sys.argv)

    game = game.Game()
    game.show()

    app.exec_()
