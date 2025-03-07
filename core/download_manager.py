import yt_dlp
from PySide6.QtCore import QObject, Signal
import os
from .queue_manager import QueueManager, DownloadTask

class DownloadProgress:
    def __init__(self):
        self.filename = ""
        self.percent = 0
        self.speed = ""
        self.status = "等待中"

class DownloadManager(QObject):
    progress_updated = Signal(str, DownloadProgress)
    download_completed = Signal(str)
    download_error = Signal(str, str)
    queue_updated = Signal(int, int)  # 队列大小, 活动下载数

    def __init__(self):
        super().__init__()
        self.active_downloads = {}
        self.queue_manager = QueueManager(max_concurrent=3)
        
    def add_download(self, url: str, save_path: str, options: dict):
        task = DownloadTask(url, save_path, options)
        self.queue_manager.add_task(task)
        self._process_queue()
        self._emit_queue_status()

    def _emit_queue_status(self):
        self.queue_updated.emit(
            self.queue_manager.get_queue_size(),
            self.queue_manager.get_active_count()
        )

    def _process_queue(self):
        while task := self.queue_manager.get_next_task():
            self.download(task.url, task.save_path, task.options)

    def create_ydl_opts(self, url, save_path, options):
        progress_handler = self.create_progress_handler(url)
        
        ydl_opts = {
            'format': self._get_format_string(options),
            'paths': {'home': save_path},
            'progress_hooks': [progress_handler],
            'ignoreerrors': True,
            'noplaylist': options.get('download_type') != '播放列表'
        }

        if options.get('download_type') == '音频':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': options.get('format', 'mp3'),
                }],
            })

        if options.get('subtitle_enabled'):
            ydl_opts.update({
                'writesubtitles': True,
                'subtitleslangs': ['all'],
            })

        return ydl_opts

    def _get_format_string(self, options):
        quality_map = {
            '最佳质量': 'bestvideo+bestaudio/best',
            '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
            '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
            '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]'
        }
        
        quality = options.get('quality', '最佳质量')
        include_audio = options.get('include_audio', True)
        
        if include_audio:
            format_str = quality_map.get(quality, 'bestvideo+bestaudio/best')
        else:
            format_str = quality_map.get(quality, 'bestvideo/best').replace('+bestaudio', '')
        
        if options.get('format') in ['mp4', 'mkv']:
            format_str += f'[ext={options["format"]}]'
            
        return format_str

    def create_progress_handler(self, url):
        progress = DownloadProgress()
        self.active_downloads[url] = progress

        def progress_hook(d):
            if d['status'] == 'downloading':
                progress.filename = os.path.basename(d.get('filename', '未知文件'))
                progress.percent = d.get('downloaded_bytes', 0) / d.get('total_bytes', 1) * 100
                progress.speed = d.get('speed', 0)
                if progress.speed:
                    progress.speed = f"{progress.speed / 1024 / 1024:.1f} MB/s"
                progress.status = '下载中'
                self.progress_updated.emit(url, progress)
            elif d['status'] == 'finished':
                progress.percent = 100
                progress.status = '完成'
                self.progress_updated.emit(url, progress)
                self.download_completed.emit(url)
                self.queue_manager.task_completed(url)
                self._process_queue()
                self._emit_queue_status()
            elif d['status'] == 'error':
                progress.status = '错误'
                self.progress_updated.emit(url, progress)
                self.download_error.emit(url, str(d.get('error', '未知错误')))
                self.queue_manager.task_completed(url)
                self._process_queue()
                self._emit_queue_status()

        return progress_hook

    def download(self, url, save_path, options):
        try:
            ydl_opts = self.create_ydl_opts(url, save_path, options)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            self.download_error.emit(url, str(e))
            self.queue_manager.task_completed(url)
            self._process_queue()
            self._emit_queue_status()