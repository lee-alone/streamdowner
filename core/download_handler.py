import os
from core.history_manager import HistoryManager

def handle_existing_download(url: str, save_path: str, filename: str, history_manager: HistoryManager):
    """
    处理已经下载过的文件。

    Args:
        url: 下载的 URL。
        save_path: 保存路径。
        filename: 文件名。
        history_manager: HistoryManager 对象。
    """
    # 从历史记录中删除该条记录
    history_entries = history_manager.search_history(url)
    for entry in history_entries:
        history_manager.history.remove(entry)
    history_manager.save_history()

    # 删除硬盘上已存在的文件
    file_path = os.path.join(save_path, filename)
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")