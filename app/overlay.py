import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, QMetaObject, Q_ARG, pyqtSlot
from multiprocessing import Process, Queue
from PyQt5 import QtCore, QtGui, QtWidgets

def get_display_center(desktop):
    screen_geometry = desktop.availableGeometry() # Get the screen geometry
    center_point = screen_geometry.center() # Get the center point
    return center_point

class Overlay(QWidget):
    def __init__(self):
        super().__init__()

        # Frameless, transparent, always-on-top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()

        # Load images
        self.images = {
            "idle": QPixmap("resources/idle.png"),
            "speaking": QPixmap("resources/speaking.png")
        }

        # Two stacked labels
        self.label_idle = QLabel(self)
        self.label_idle.setPixmap(self.images["idle"])
        self.label_idle.setAlignment(Qt.AlignCenter)

        self.label_speaking = QLabel(self)
        self.label_speaking.setPixmap(self.images["speaking"])
        self.label_speaking.setAlignment(Qt.AlignCenter)

        # Same size and position
        self.label_idle.resize(self.images["idle"].size())
        self.label_speaking.resize(self.images["idle"].size())

        # Apply opacity effects
        self.effect_idle = QGraphicsOpacityEffect()
        self.effect_speaking = QGraphicsOpacityEffect()
        self.label_idle.setGraphicsEffect(self.effect_idle)
        self.label_speaking.setGraphicsEffect(self.effect_speaking)
        self.effect_idle.setOpacity(1.0)
        self.effect_speaking.setOpacity(0.0)

        # Initial size and position
        self.resize(self.images["idle"].size())
        self.move(-41, 629)

        self.state = "idle"

    @pyqtSlot(str)
    def set_state(self, new_state):
        if new_state == self.state:
            return
        self.state = new_state

        # Opacity animation
        fade_out = self.effect_idle if new_state == "speaking" else self.effect_speaking
        fade_in = self.effect_speaking if new_state == "speaking" else self.effect_idle

        anim_out = QPropertyAnimation(fade_out, b"opacity")
        anim_out.setDuration(300)
        anim_out.setStartValue(1.0)
        anim_out.setEndValue(0.0)

        anim_in = QPropertyAnimation(fade_in, b"opacity")
        anim_in.setDuration(300)
        anim_in.setStartValue(0.0)
        anim_in.setEndValue(1.0)

        anim_out.start()
        anim_in.start()

        self.anim_out = anim_out  # Keep references
        self.anim_in = anim_in

        # Move up/down animation
        current_pos = self.pos()
        offset = QPoint(0, -20) if new_state == "speaking" else QPoint(0, 20)

        move_anim = QPropertyAnimation(self, b"pos")
        move_anim.setDuration(300)
        move_anim.setStartValue(current_pos)
        move_anim.setEndValue(current_pos + offset)
        move_anim.start()

        self.move_anim = move_anim

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print(self.pos())
            self.drag_pos = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_pos)
            event.accept()

    def keyPressEvent(self, event):
        modifiers = event.modifiers()
        key = event.key()

        if (modifiers & Qt.ControlModifier and
            modifiers & Qt.AltModifier and
            key == Qt.Key_Q):
            self.close()


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(236, 224)

        self.overlay = Overlay()
        self.overlay.show()

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.button1 = QtWidgets.QPushButton(self.centralwidget)
        self.button1.setGeometry(QtCore.QRect(70, 60, 93, 28))
        self.button1.setObjectName("button1")
        self.button1.clicked.connect(lambda:self.overlay.set_state("speaking"))
        self.button2 = QtWidgets.QPushButton(self.centralwidget)
        self.button2.setGeometry(QtCore.QRect(70, 100, 93, 28))
        self.button2.setObjectName("button2")
        self.button2.clicked.connect(lambda:self.overlay.set_state("idle"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 236, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.button1.setText(_translate("MainWindow", "Up"))
        self.button2.setText(_translate("MainWindow", "Down"))

def run_overlay(queue: Queue):
    app = QApplication(sys.argv)
    character = Overlay()
    character.show()
    character.set_state("idle")

    # Check for queue messages
    def poll_queue():
        while not queue.empty():
            msg = queue.get()
            #print(f"[Overlay] received: {msg}")
            QMetaObject.invokeMethod(
                        character,
                        "set_state",
                        Qt.QueuedConnection,
                        Q_ARG(str, msg)
                    )

    # Poll every 100ms
    timer = QTimer()
    timer.timeout.connect(poll_queue)
    timer.start(100)

    sys.exit(app.exec())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    overlay = Overlay()
    overlay.show()
    # print(get_display_center(app.desktop()))
    # MainWindow = QtWidgets.QMainWindow()
    # ui = Ui_MainWindow()
    # ui.setupUi(MainWindow)
    # MainWindow.show()

    # # 🔁 Example usage
    # from PyQt5.QtCore import QTimer
    # QTimer.singleShot(1000, lambda: overlay.set_state("speaking"))
    # QTimer.singleShot(3000, lambda: overlay.set_state("idle"))

    sys.exit(app.exec_())
