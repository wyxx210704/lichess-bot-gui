import sys
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QPushButton,
    QTextEdit
)
from PyQt6.QtCore import Qt


class LichessCurlTool(QMainWindow):
    def __init__(self,window:QWidget|None=None):
        super().__init__(window)
        self.resize(900, 700)

        # 主容器与垂直布局（从上到下排列组件）
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        # 1. 列表框：预设命令模板
        self.cmd_list = QListWidget()
        # 预设命令映射：显示名称 -> curl命令模板
        self.cmd_templates = {
            "1. 获取个人账号信息 /user/me":
                'TOKEN="你的token"\ncurl -s -H "Authorization: Bearer $TOKEN" https://lichess.org/api/user/me | jq .',
            "2. 导出自己全部对局PGN":
                'TOKEN="你的token"\ncurl -H "Authorization: Bearer $TOKEN" https://lichess.org/api/games/user/你的用户名 > all_games.pgn',
            "3. 获取单局PGN":
                'GAME_ID="对局ID"\ncurl https://lichess.org/api/game/$GAME_ID/pgn > game_$GAME_ID.pgn',
            "4. 实时监听对局流（SSE）":
                'TOKEN="你的token"\ncurl -N -H "Authorization: Bearer $TOKEN" https://lichess.org/api/stream/user',
            "5. 查询玩家基础信息":
                'USER="目标用户名"\ncurl -s https://lichess.org/api/user/$USER | jq .',
            "6. 向用户发送站内消息":
                'TOKEN="你的token"\ncurl -X POST -H "Authorization: Bearer $TOKEN" -d "text=你好" https://lichess.org/api/message/目标用户',
            "7. 创建对局挑战":
                'TOKEN="你的token"\ncurl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d \'{"clock":{"limit":300,"increment":0},"variant":"standard"}\' https://lichess.org/api/challenge/对手名称'
        }
        # 填充列表
        for display_name in self.cmd_templates.keys():
            QListWidgetItem(display_name, self.cmd_list)
        # 列表点击事件
        self.cmd_list.itemClicked.connect(self.on_list_item_click)
        layout.addWidget(self.cmd_list, stretch=3)

        # 2. 单行输入框：编辑curl命令
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("修改curl命令模板，完成后点击执行...")
        layout.addWidget(self.cmd_input, stretch=1)

        # 3. 执行按钮
        self.run_btn = QPushButton("运行当前命令")
        self.run_btn.clicked.connect(self.run_command)
        layout.addWidget(self.run_btn)

        # 4. 只读多行输出框
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setPlaceholderText("命令输出会展示在这里...")
        layout.addWidget(self.output_text, stretch=4)

    def on_list_item_click(self, item: QListWidgetItem):
        """点击列表项，填充对应模板到输入框"""
        display_text = item.text()
        template_cmd = self.cmd_templates[display_text]
        self.cmd_input.setText(template_cmd)

    def run_command(self):
        """执行输入框中的shell命令，捕获输出写入文本框"""
        cmd_str = self.cmd_input.text().strip()
        if not cmd_str:
            self.output_text.setText("错误：输入框不能为空！")
            return

        # 执行前清空输出框
        self.output_text.clear()
        self.output_text.append(f"===== 开始执行命令 =====\n{cmd_str}\n")

        try:
            # shell=True 支持管道、变量、多行命令
            result = subprocess.run(
                cmd_str,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            # 拼接标准输出与错误输出
            out = result.stdout
            err = result.stderr
            self.output_text.append("===== 标准输出 =====")
            self.output_text.append(out if out else "(无输出)")
            if err:
                self.output_text.append("\n===== 错误输出 =====")
                self.output_text.append(err)
            self.output_text.append(f"\n执行完成，返回码：{result.returncode}")
        except subprocess.TimeoutExpired:
            self.output_text.append("错误：命令执行超时（30秒）")
        except Exception as e:
            self.output_text.append(f"执行异常：{str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LichessCurlTool()
    window.show()
    sys.exit(app.exec())