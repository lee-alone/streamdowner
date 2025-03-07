import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow
import shutil
import os  # 导入 os 模块

def check_ffmpeg():
    if not shutil.which('ffmpeg'):
        # 检查根目录下是否存在 ffmpeg 程序
        ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg.exe')  # 假设 ffmpeg 程序名为 ffmpeg.exe
        if os.path.exists(ffmpeg_path):
            os.environ['PATH'] += os.pathsep + os.getcwd()  # 将根目录添加到 PATH 环境变量
        else:
            QMessageBox.warning(
                None,
                "缺少依赖",
                "未检测到FFmpeg。为了确保视频和音频能正确合并，请先安装FFmpeg。\n"
                "Windows用户可以从 https://www.gyan.dev/ffmpeg/builds/ 下载安装。"
            )

def main():
    app = QApplication(sys.argv)
    check_ffmpeg()  # 添加FFmpeg检查
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()