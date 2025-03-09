import json
import os
from datetime import datetime
from typing import List, Dict

class HistoryManager:
    def __init__(self, history_file: str = "download_history.json"):
        self.history_file = history_file
        self.history: List[Dict] = self.load_history()
    
    def load_history(self) -> List[Dict]:
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading history: {e}")
        return []
    
    def save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    def add_entry(self, url: str, filename: str, save_path: str, options: Dict):
        entry = {
            'url': url,
            'filename': filename,
            'save_path': save_path,
            'options': options,
            'timestamp': datetime.now().isoformat(),
            'status': 'completed'
        }
        self.history.insert(0, entry)  # 添加到列表开头
        if len(self.history) > 1000:  # 限制历史记录数量
            self.history = self.history[:1000]
        self.save_history()
    
    def get_recent_entries(self, limit: int = 100) -> List[Dict]:
        return self.history[:limit]
    
    def clear_history(self):
        self.history.clear()
        self.save_history()
    
    def search_history(self, keyword: str) -> List[Dict]:
        keyword = keyword.lower()
        return [
            entry for entry in self.history
            if keyword in entry['url'].lower() or
               keyword in entry['filename'].lower()
        ]