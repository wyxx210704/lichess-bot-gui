from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

class BotConfig(QMainWindow):
    def __init__(self,window:QWidget|None = None):
        super().__init__(window)

        widget = QWidget(self)
        self.setCentralWidget(widget)
        self.layout_ = QVBoxLayout(widget)
            
        self.text_edit = QTextEdit(widget)
        self.text_edit.setFrameShape(QFrame.Shape.NoFrame)
        self.text_edit.setLineWrapMode(self.text_edit.LineWrapMode.NoWrap)
        self.layout_.addWidget(self.text_edit)

        self.text_edit.setFont(QFont(
            'Consolas',
            15,
        ))

        self.text_edit.setText(open(
            "./config.yml",
            'r',
            encoding='gbk',
            errors='ignore',
        ).read())

        self.button_1 = QPushButton(
            '保存更改',
            widget,
        )

        self.label = QLabel(
            '保存更改后将在重启lichess机器人时生效',
            widget,
        )

        self.button_1.clicked.connect(self.save)
        self.layout_.addWidget(self.button_1)
        self.layout_.addWidget(self.label)

    def save(self):open(
        "./config.yml",
        'w',
        encoding='gbk',
        errors='ignore',
    ).write(self.text_edit.toPlainText())
        
if __name__ == '__main__':
    app = QApplication([])
    window = BotConfig()
    window.show()
    app.exec()