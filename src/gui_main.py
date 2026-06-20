#导入的是库
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

#导入的是自定义文件
from thread_worker import Worker
from game_viewer import GameViewer
from edit_bot_config import BotConfig
from edit_gui_config import GuiConfig
from edit_style import EditStyle
from lichess_api_custom_call import LichessCurlTool

class StartupDialog(QDialog):
    """启动选项对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout_ = QVBoxLayout(self)

        self.setWindowTitle("启动设置")
        self.setModal(True)
        
        self.check_box_1 = QCheckBox(
            '启动lichess-bot',
            self,
        )

        self.check_box_2 = QCheckBox(
            '启动组件：对局查看器',
            self,
        )

        self.check_box_3 = QCheckBox(
            '启动组件：修改机器人配置',
            self,
        )

        self.check_box_4 = QCheckBox(
            '启动组件：修改gui配置',
            self,
        )

        self.check_box_5 = QCheckBox(
            '启动组件：修改gui样式',
            self,
        )

        self.check_box_6 = QCheckBox(
            '启动组件：lichess api自定义调用',
            self,
        )

        self.layout_.addWidget(self.check_box_1)
        self.layout_.addWidget(self.check_box_2)
        self.layout_.addWidget(self.check_box_3)
        self.layout_.addWidget(self.check_box_4)
        self.layout_.addWidget(self.check_box_5)
        self.layout_.addWidget(self.check_box_6)

        self.button = QPushButton(
            '以该配置启动程序',
            self,
        )

        self.button.clicked.connect(self.accept)
        self.layout_.addWidget(self.button)

        self.layout_.addWidget(QLabel(
            'lichess-bot-gui版本1.4\n基于lichess-bot版本2026.5.21.1开发',
            self
        ))
    
    def get_config(self):
        """返回用户配置"""
        return [
            self.check_box_1.isChecked(),
            self.check_box_2.isChecked(),
            self.check_box_3.isChecked(),
            self.check_box_4.isChecked(),
            self.check_box_5.isChecked(),
            self.check_box_6.isChecked(),
        ]

def main():
    app = QApplication([])
    dialog = StartupDialog()
    
    if dialog.exec() == QDialog.DialogCode.Accepted:
        config = dialog.get_config()

        window = QMainWindow()
        window.setStyleSheet(open(
            './style.txt',
            'r',
            encoding='utf-8',
            errors='ignore',
        ).read())

        window.setWindowTitle('lichess机器人')
        window.setWindowIcon(QIcon("./lichess_icon.ico"))
        
        tool_box = QToolBox(window)
        window.setCentralWidget(tool_box)

        if config[0]:
            text_broswer = QTextBrowser(window)
            text_broswer.setFont(QFont('Consolas',15))
            text_broswer.setFrameShape(QFrame.Shape.NoFrame)
            tool_box.addItem(
                text_broswer,
                '输出'
            )

            worker_thread = QThread()
            worker = Worker()

            worker.moveToThread(worker_thread)
            worker.text_signal.connect(text_broswer.append)

            worker_thread.started.connect(worker.run_event)
            worker_thread.finished.connect(worker_thread.deleteLater)
            worker_thread.start()

        if config[1]:
            game_viewer = GameViewer(tool_box)
            tool_box.addItem(
                game_viewer,
                '查看对局',
            )

        if config[2]:
            bot_config = BotConfig(tool_box)
            tool_box.addItem(
                bot_config,
                '修改机器人配置',
            )

        if config[3]:
            gui_config = GuiConfig(tool_box)
            tool_box.addItem(
                gui_config,
                '修改gui配置',
            )

        if config[4]:
            gui_config = EditStyle(tool_box)
            tool_box.addItem(
                gui_config,
                '修改gui样式',
            )

        if config[5]:
            api_custom_call = LichessCurlTool(window)
            tool_box.addItem(
                api_custom_call,
                'lichess api自定义调用',
            )

        window.show()
        app.exec()

if __name__ == '__main__':main()