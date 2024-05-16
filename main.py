from PyQt6.QtWidgets import QApplication

from window import Window


def run():
    try:
        app = QApplication([])
        window = Window()
        window.show()
        app.exec()
    except Exception as e:
        print("Wystąpił błąd w metodzie run():", e)


if __name__ == "__main__":
    run()
