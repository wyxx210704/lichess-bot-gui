modification_instructions = '''
# gui_config.json配置修改说明

## chess.svg.board()尺寸与样式
- **`size`**
    棋盘像素大小（正方形），例如 `400` → 400×400，默认 `None`（无限制）。

- **`coordinates`**
    是否显示棋盘坐标（a-h / 1-8），默认 `True`，设 `False` 关闭。

- **`colors`**
    自定义棋盘颜色（覆盖默认配色）。
    可用键：
    - `square light` / `square dark`：浅色/深色格子
    - `square light lastmove` / `square dark lastmove`：最后一步高亮
    - `margin` / `coord`：边距、坐标颜色
    - `arrow green/blue/red/yellow`：箭头颜色
    颜色格式：`#ffce9e`（不透明）、`#15781B80`（带透明通道）

- **`flipped`**
    翻转棋盘（黑方在下），设 `True` 开启。

- **`borders`**
    显示棋盘外边框，默认 `False`，设 `True` 开启。

## game_viewer要观看的账号
修改`game_viewer_user_name`项目为将要观战的账号
'''

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

class GuiConfig(QMainWindow):
    def __init__(self,window:QWidget|None = None):
        super().__init__(window)

        widget = QWidget(self)
        self.setCentralWidget(widget)
        self.layout_ = QVBoxLayout(widget)

        self.text_broswer = QTextBrowser(widget)
        self.text_broswer.setMarkdown(modification_instructions)
        self.text_broswer.setFrameShape(QFrame.Shape.NoFrame)
        self.layout_.addWidget(self.text_broswer)
            
        self.text_edit = QTextEdit(widget)
        self.text_edit.setLineWrapMode(self.text_edit.LineWrapMode.NoWrap)
        self.text_edit.setFrameShape(QFrame.Shape.NoFrame)
        self.layout_.addWidget(self.text_edit)

        self.text_edit.setFont(QFont(
            'Consolas',
            15,
        ))

        self.text_edit.setText(open(
            "./gui_config.json",
            'r',
            encoding='utf-8',
            errors='ignore',
        ).read())

        self.button_1 = QPushButton(
            '保存更改',
            widget,
        )

        self.label = QLabel(
            '保存更改后将在重启该程序时生效',
            widget,
        )

        self.button_1.clicked.connect(self.save)
        self.layout_.addWidget(self.button_1)
        self.layout_.addWidget(self.label)

    def save(self):open(
        "./gui_config.json",
        'w',
        encoding='utf-8',
        errors='ignore',
    ).write(self.text_edit.toPlainText())
        
if __name__ == '__main__':
    app = QApplication([])
    window = GuiConfig()
    window.show()
    app.exec()