from PySide2.QtWidgets import QApplication
import sys
import game

if __name__ == '__main__':
    # Hack to run this interactively
    try:
        if app:
            pass
    except NameError:
        try:
            app = QApplication(sys.argv)
        except RuntimeError:
            app = QApplication.instance()

    game = game.Game()
    game.show()

    app.exec_()
