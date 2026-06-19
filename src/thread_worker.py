from lichess_bot import start_program
from PyQt6.QtCore import QObject, pyqtSignal

# 全局 Worker 实例引用
_worker_instance = None

class Worker(QObject):
    text_signal = pyqtSignal(str)
    list_signal = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        global _worker_instance
        _worker_instance = self
    
    def send_text(self, text: str):
        self.text_signal.emit(text)

    def run_event(self):
        
        start_program()

def get_worker():
    """获取 Worker 实例的全局访问点"""
    return _worker_instance