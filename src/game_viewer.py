import sys
import json
import requests
import logging
from typing import Literal
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QHBoxLayout, 
                             QVBoxLayout, QLabel, QTextEdit, QGroupBox, 
                             QFormLayout, QGridLayout, QFrame, QPushButton)
from PyQt6.QtCore import QTimer, Qt, pyqtSignal, QThread, QMutex
from PyQt6.QtGui import QFont, QPalette, QColor

import chess
import chess.svg
from PyQt6.QtSvgWidgets import QSvgWidget

logger = logging.getLogger(__name__)
CHESS_AVAILABLE = True
DEFAULT_REFRESH_INTERVAL = 5000  # 默认5秒刷新一次

# 根据时间模式定义刷新间隔（毫秒）
SPEED_INTERVALS = {
    'bullet': 1000,      # 每秒更新
    'blitz': 2000,       # 每2秒更新
    'rapid': 5000,       # 每5秒更新
    'classical': 10000,  # 每10秒更新
}

class Config:
    '''
    json期望格式（拿默认值举例）
    {
        "game_viewer_user_name":"default",
        "chess_board_color":{
            "square light":"#A6A6A6",
            "square dark":"#8B8B8B"
        },
        "chess_board":{
            "size":500,
            "coordinates":true,
            "flipped":false,
            "borders":false
        }
    }
    '''

    def __init__(self):
        self.more_dict = {}
        DEFAULT = {
            "game_viewer_user_name":"default",
            "chess_board_color":{
                "square light":"#A6A6A6",
                "square dark":"#8B8B8B"
            },
            "chess_board":{
                "size":500,
                "coordinates":True,
                "flipped":False,
                "borders":False
            }
        }

        try:
            config = json.load(open(
                "./gui_config.json",
                'r',
                encoding='utf-8',
                errors='ignore',
            ))
        except json.JSONDecodeError:
            logger.info('json格式不对，接下来将会使用默认值')
            color_use_default = True
            size_use_default = True
            coordinates_use_default = True
            flipped_use_default = True
            borders_use_default = True
            user_name_use_default = True
        else:
            if type(config) != dict:
                logger.info('json格式不对，接下来将会使用默认值')
                color_use_default = True
                size_use_default = True
                coordinates_use_default = True
                flipped_use_default = True
                borders_use_default = True
                user_name_use_default = True
            else:
                try:
                    config['game_viewer_user_name']
                except KeyError:
                    user_name_use_default = True
                else:user_name_use_default = False

                try:
                    config['chess_board_color']
                except KeyError:
                    logger.info('没有chess_board_color这个键，接下来将会使用默认值')
                    color_use_default = True
                else:
                    if type(config['chess_board_color']) != dict:
                        logger.info('json格式不对，接下来将会使用默认值')
                        color_use_default = True
                    else:color_use_default = False

                try:
                    config['chess_board']
                except KeyError:
                    logger.info('没有chess_board这个键，接下来将会使用默认值')
                    size_use_default = True
                    coordinates_use_default = True
                    flipped_use_default = True
                    borders_use_default = True
                else:
                    if type(config['chess_board']) != dict:
                        logger.info('json格式不对，接下来将会使用默认值')
                        size_use_default = True
                        coordinates_use_default = True
                        flipped_use_default = True
                        borders_use_default = True
                    else:
                        chess_board_config = config['chess_board']

                        try:
                            chess_board_config['size']
                        except KeyError:
                            logger.info('没有size这个键，接下来将会使用默认值')
                            size_use_default = True
                        else:size_use_default = False

                        try:
                            chess_board_config['coordinates']
                        except KeyError:
                            logger.info('没有coordinates这个键，接下来将会使用默认值')
                            coordinates_use_default = True
                        else:coordinates_use_default = False

                        try:
                            chess_board_config['flipped']
                        except KeyError:
                            logger.info('没有flipped这个键，接下来将会使用默认值')
                            flipped_use_default = True
                        else:flipped_use_default = False

                        try:
                            chess_board_config['borders']
                        except KeyError:
                            logger.info('没有borders这个键，接下来将会使用默认值')
                            borders_use_default = True
                        else:borders_use_default = False

        if user_name_use_default:
            self.user_name = DEFAULT['game_viewer_user_name']
        else:
            self.user_name = config['game_viewer_user_name']

        if color_use_default:
            self.color = DEFAULT['chess_board_color']
        else:
            self.color = config['chess_board_color']

        if size_use_default:
            self.more_dict['size'] = DEFAULT['chess_board']['size']
        else:
            self.more_dict['size'] = config['chess_board']['size']

        if coordinates_use_default:
            self.more_dict['coordinates'] = DEFAULT['chess_board']['coordinates']
        else:
            self.more_dict['coordinates'] = config['chess_board']['coordinates']

        if flipped_use_default:
            self.more_dict['flipped'] = DEFAULT['chess_board']['flipped']
        else:
            self.more_dict['flipped'] = config['chess_board']['flipped']

        if borders_use_default:
            self.more_dict['borders'] = DEFAULT['chess_board']['borders']
        else:
            self.more_dict['borders'] = config['chess_board']['borders']

    def get_color(self):
        return self.color
    
    def get_user_name(self):
        return self.user_name
    
    def get_config(self,config:Literal['size','coordinates','flipped','borders']):
        return self.more_dict[config]
        
def get_refresh_interval_from_speed(speed):
    """根据时间模式获取刷新间隔（毫秒）"""
    return SPEED_INTERVALS.get(speed, DEFAULT_REFRESH_INTERVAL)

class GameFetcher(QThread):
    """在后台线程中获取游戏数据"""
    game_data_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    interval_changed = pyqtSignal(int)  # 刷新间隔改变信号
    
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.running = True
        self.current_interval = DEFAULT_REFRESH_INTERVAL
        self.mutex = QMutex()
        
    def update_interval(self, new_interval):
        """更新刷新间隔"""
        self.mutex.lock()
        try:
            if self.current_interval != new_interval:
                self.current_interval = new_interval
                self.interval_changed.emit(new_interval)
                # print(f"刷新间隔已更新为: {new_interval}ms")
        finally:
            self.mutex.unlock()
        
    def run(self):
        while self.running:
            try:
                data = self.fetch_current_game()
                self.game_data_received.emit(data if data else {})
            except Exception as e:
                self.error_occurred.emit(str(e))
            self.msleep(self.current_interval)
    
    def fetch_current_game(self):
        """获取当前对局数据"""
        url = f"https://lichess.org/api/user/{self.username}/current-game"
        headers = {
            "User-Agent": "my-lichess-bot/1.0",
            "Accept": "application/json"
        }
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            elif resp.status_code == 204:
                return None
            else:
                return None
        except Exception as e:
            raise e
    
    def stop(self):
        self.running = False


class ChessBoardWidget(QWidget):
    """棋盘显示组件"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        if CHESS_AVAILABLE:
            self.board_svg = QSvgWidget()
            self.layout.addWidget(self.board_svg)
        else:
            self.label = QLabel("请安装 python-chess 库:\npip install python-chess")
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.label.setStyleSheet("font-size: 14px; color: red;")
            self.layout.addWidget(self.label)
        
        self.board = None
        self.current_fen = None
        
    def update_position(self, initial_fen, moves_str):
        """根据初始FEN和走子序列更新棋盘"""
        if not CHESS_AVAILABLE:
            return
            
        try:
            # 从初始FEN创建棋盘
            self.board = chess.Board(initial_fen if initial_fen else chess.STARTING_FEN)
            
            # 应用所有走子 (moves是SAN格式，如 "d4 d5 e3 Ng6")
            moves = moves_str.split()
            for san_move in moves:
                if not san_move:
                    continue
                try:
                    # 使用 parse_san 解析代数记谱法
                    move = self.board.parse_san(san_move)
                    self.board.push(move)
                except ValueError as e:
                    #print(f"解析走法失败: {san_move}, 错误: {e}")
                    continue
            
            '''
            def board(
                board: BaseBoard | None = None,
                *,
                orientation: Color = chess.WHITE,
                lastmove: Move | None = None,
                check: Square | None = None,
                arrows: Iterable[Arrow | Tuple[Square, Square]] = [],
                fill: Dict[Square, str] = {},
                squares: IntoSquareSet | None = None,
                size: int | None = None,
                coordinates: bool = True,
                colors: Dict[str, str] = {},
                flipped: bool = False,
                borders: bool = False,
                style: str | None = None
            ) -> str
            '''

            config = Config()
            # 生成SVG并显示
            svg_data = chess.svg.board(
                self.board,
                size=config.get_config('size'),
                coordinates=config.get_config('coordinates'),
                lastmove=self.board.move_stack[-1] if self.board.move_stack else None,
                colors=config.get_color(),
                flipped=config.get_config('flipped'),
                borders=config.get_config('borders')
            )
            self.board_svg.load(svg_data.encode('utf-8'))
            self.current_fen = self.board.fen()
            
        except Exception as e:
            logger.info(f"棋盘更新错误: {e}")
            
    def get_current_fen(self):
        """获取当前局面的FEN字符串"""
        return self.current_fen if self.current_fen else ""


class InfoPanel(QWidget):
    """右侧信息面板"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 游戏状态组
        self.game_group = QGroupBox("游戏状态")
        game_layout = QFormLayout(self.game_group)
        self.status_label = QLabel("无对局")
        #self.status_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        self.rated_label = QLabel("-")
        self.variant_label = QLabel("-")
        self.speed_label = QLabel("-")
        self.time_control_label = QLabel("-")
        self.refresh_interval_label = QLabel("-")  # 新增：显示当前刷新间隔
        
        game_layout.addRow("状态:", self.status_label)
        game_layout.addRow("是否计分:", self.rated_label)
        game_layout.addRow("变体:", self.variant_label)
        game_layout.addRow("速度:", self.speed_label)
        game_layout.addRow("时间控制:", self.time_control_label)
        game_layout.addRow("刷新频率:", self.refresh_interval_label)
        layout.addWidget(self.game_group)
        
        # 玩家信息组
        self.players_group = QGroupBox("玩家信息")
        players_layout = QGridLayout(self.players_group)
        
        # 白方信息
        self.white_name = QLabel("-")
        self.white_rating = QLabel("-")
        self.white_title = QLabel("-")
        
        # 黑方信息
        self.black_name = QLabel("-")
        self.black_rating = QLabel("-")
        self.black_title = QLabel("-")
        
        players_layout.addWidget(QLabel("白方:"), 0, 0)
        players_layout.addWidget(self.white_name, 0, 1)
        players_layout.addWidget(QLabel("等级分:"), 0, 2)
        players_layout.addWidget(self.white_rating, 0, 3)
        players_layout.addWidget(QLabel("称号:"), 0, 4)
        players_layout.addWidget(self.white_title, 0, 5)
        
        players_layout.addWidget(QLabel("黑方:"), 1, 0)
        players_layout.addWidget(self.black_name, 1, 1)
        players_layout.addWidget(QLabel("等级分:"), 1, 2)
        players_layout.addWidget(self.black_rating, 1, 3)
        players_layout.addWidget(QLabel("称号:"), 1, 4)
        players_layout.addWidget(self.black_title, 1, 5)
        
        layout.addWidget(self.players_group)
        
        # 时钟信息组
        self.clock_group = QGroupBox("时钟信息")
        clock_layout = QFormLayout(self.clock_group)
        self.white_clock = QLabel("-")
        self.black_clock = QLabel("-")
        self.initial_time = QLabel("-")
        self.increment = QLabel("-")
        
        clock_layout.addRow("白方剩余:", self.white_clock)
        clock_layout.addRow("黑方剩余:", self.black_clock)
        clock_layout.addRow("初始时间:", self.initial_time)
        clock_layout.addRow("每步加时:", self.increment)
        layout.addWidget(self.clock_group)
        
        # 走子记录组
        self.moves_group = QGroupBox("走子记录")
        moves_layout = QVBoxLayout(self.moves_group)
        self.moves_text = QTextEdit()
        self.moves_text.setFrameShape(QFrame.Shape.NoFrame)
        self.moves_text.setReadOnly(True)
        self.moves_text.setMaximumHeight(200)
        self.moves_text.setFont(QFont("Courier New", 10))
        moves_layout.addWidget(self.moves_text)
        layout.addWidget(self.moves_group)
        
        # 游戏ID
        self.game_id_label = QLabel("游戏ID: -")
        #self.game_id_label.setStyleSheet("font-size: 10px; color: gray;")
        layout.addWidget(self.game_id_label)
        
        layout.addStretch()
        
    def update_info(self, game_data, refresh_interval=None):
        """更新所有信息"""
        if not game_data:
            self.status_label.setText("无对局")
            self.refresh_interval_label.setText("-")
            #self.status_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
            return
            
        # 游戏状态
        status = game_data.get('status', 'unknown')
        status_text = {
            'started': '进行中',
            'mate': '将死',
            'resign': '认输',
            'outoftime': '超时',
            'aborted': '已取消',
            'draw': '和棋',
            'created': '等待开始'
        }.get(status, status)
        self.status_label.setText(status_text)
        #self.status_label.setStyleSheet("font-weight: bold; color: #27ae60;" if status == 'started' else "font-weight: bold; color: #e74c3c;")
        
        self.rated_label.setText("是" if game_data.get('rated') else "否")
        self.variant_label.setText(game_data.get('variant', '-'))
        speed = game_data.get('speed', '-')
        self.speed_label.setText(speed)
        
        # 显示当前刷新间隔
        if refresh_interval is not None:
            interval_sec = refresh_interval / 1000
            self.refresh_interval_label.setText(f"每 {interval_sec:.1f} 秒")
        
        # 时间控制
        clock_info = game_data.get('clock', {})
        initial_sec = clock_info.get('initial', 0)
        increment_sec = clock_info.get('increment', 0)
        self.time_control_label.setText(f"{initial_sec // 60}+{increment_sec}")
        self.initial_time.setText(f"{initial_sec // 60} 分钟" if initial_sec > 60 else f"{initial_sec} 秒")
        self.increment.setText(f"{increment_sec} 秒")
        
        # 玩家信息
        players = game_data.get('players', {})
        white = players.get('white', {})
        black = players.get('black', {})
        
        white_user = white.get('user', {})
        black_user = black.get('user', {})
        
        self.white_name.setText(white_user.get('name', '-'))
        self.white_rating.setText(str(white.get('rating', '-')))
        self.white_title.setText(white_user.get('title', '-') or '-')
        
        self.black_name.setText(black_user.get('name', '-'))
        self.black_rating.setText(str(black.get('rating', '-')))
        self.black_title.setText(black_user.get('title', '-') or '-')
        
        # 时钟显示
        clocks = game_data.get('clocks', [])
        if len(clocks) >= 2:
            # 最新的时钟值
            white_time = clocks[-2] if len(clocks) % 2 == 0 else clocks[-1]
            black_time = clocks[-1] if len(clocks) % 2 == 0 else clocks[-2]
            self.white_clock.setText(self.format_time(white_time))
            self.black_clock.setText(self.format_time(black_time))
        else:
            self.white_clock.setText("-")
            self.black_clock.setText("-")
        
        # 走子记录 - 格式化为对局记录
        moves = game_data.get('moves', '').split()
        if moves:
            formatted_moves = []
            for i in range(0, len(moves), 2):
                move_num = i // 2 + 1
                white_move = moves[i]
                black_move = moves[i+1] if i+1 < len(moves) else ""
                formatted_moves.append(f"{move_num}. {white_move} {black_move}")
            self.moves_text.setText("\n".join(formatted_moves))
            scrollbar = self.moves_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        else:
            self.moves_text.setText("无走子记录")
        
        # 游戏ID
        game_id = game_data.get('id', '-')
        self.game_id_label.setText(f"游戏ID: {game_id}")
        
    def format_time(self, centiseconds):
        """将百分秒格式化为 mm:ss 或 HH:MM:SS"""
        seconds = centiseconds / 100
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{minutes:02d}:{secs:02d}"


class GameViewer(QMainWindow):
    def __init__(self,window:QWidget|None=None):
        super().__init__(window)
        self.setFixedSize(
            1281,
            805,
        )

        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 左侧棋盘区域
        self.board_widget = ChessBoardWidget()
        main_layout.addWidget(self.board_widget, 60)
        
        # 右侧信息面板
        self.info_panel = InfoPanel()
        main_layout.addWidget(self.info_panel, 40)
        
        # 状态栏
        self.statusBar().showMessage("正在获取对局数据...")
        status_bar = self.statusBar()
        
        # 后台获取线程
        self.fetcher = GameFetcher(Config().get_user_name())
        self.fetcher.game_data_received.connect(self.on_game_data_received)
        self.fetcher.error_occurred.connect(self.on_error)
        self.fetcher.interval_changed.connect(self.on_interval_changed)
        self.fetcher.start()
        
        # 当前游戏数据
        self.current_game_data = None
        
    def on_game_data_received(self, game_data):
        """接收到游戏数据时的处理"""
        if game_data:
            self.current_game_data = game_data
            
            # 根据时间模式动态调整刷新间隔
            speed = game_data.get('speed', '')
            new_interval = get_refresh_interval_from_speed(speed)
            self.fetcher.update_interval(new_interval)
            
            self.statusBar().showMessage(f"最后更新: {self.get_current_time()} - 对局进行中 ({speed})")
            
            # 更新信息面板（传递当前刷新间隔）
            current_interval = self.fetcher.current_interval
            self.info_panel.update_info(game_data, current_interval)
            
            # 更新棋盘
            initial_fen = game_data.get('initialFen', chess.STARTING_FEN)
            moves = game_data.get('moves', '')
            self.board_widget.update_position(initial_fen, moves)
        else:
            self.statusBar().showMessage(f"最后更新: {self.get_current_time()} - 无对局")
            self.info_panel.update_info(None)
            
    def on_error(self, error_msg):
        """错误处理"""
        self.statusBar().showMessage(f"错误: {error_msg}")
        print(f"获取数据错误: {error_msg}")
    
    def on_interval_changed(self, new_interval):
        """刷新间隔改变时的处理"""
        interval_sec = new_interval / 1000
        self.statusBar().showMessage(f"刷新间隔已调整为: {interval_sec:.1f} 秒")
        
    def get_current_time(self):
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
        
    def closeEvent(self, event):
        """关闭窗口时停止后台线程"""
        self.fetcher.stop()
        self.fetcher.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    window = GameViewer()
    window.setWindowTitle("Lichess 对局观看器")
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()