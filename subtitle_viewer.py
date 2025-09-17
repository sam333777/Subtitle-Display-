import sys
import pysrt
import time
from PyQt5.QtWidgets import (
    QApplication, QLabel, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QSizePolicy
)
from PyQt5.QtCore import QTimer, Qt


class SubtitleViewer(QWidget):
    def __init__(self, subtitles, offset=0):
        super().__init__()
        self.subtitles = subtitles
        self.offset = offset
        self.start_time = time.time()
        self.paused = False
        self.pause_time = 0

     
        self.setWindowTitle("Subtitle Viewer")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)  
        self.setGeometry(300, 100, 1000, 180)
        self.setStyleSheet("background-color: black;")

        
        self.subtitle_label = QLabel("", self)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet("color: white; font-size: 32pt;")
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.time_label = QLabel("00:00", self)
        self.time_label.setAlignment(Qt.AlignRight)
        self.time_label.setStyleSheet("color: grey; font-size: 14pt; padding-right: 10px;")

        self.pause_button = QPushButton("⏸ Pause")
        self.pause_button.clicked.connect(self.toggle_pause)

        self.rewind_button = QPushButton("⏪ -30s")
        self.rewind_button.clicked.connect(self.rewind)

        self.forward_button = QPushButton("⏩ +30s")
        self.forward_button.clicked.connect(self.forward)

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.pause_button)
        button_layout.addWidget(self.rewind_button)
        button_layout.addWidget(self.forward_button)
        button_layout.addStretch()

      
        subtitle_layout = QVBoxLayout()
        subtitle_layout.addWidget(self.subtitle_label)
        subtitle_layout.addWidget(self.time_label)

       
        main_layout = QHBoxLayout()
        main_layout.addLayout(subtitle_layout, stretch=4)
        main_layout.addLayout(button_layout, stretch=1)

        self.setLayout(main_layout)

       
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)

    def toggle_pause(self):
        if self.paused:
            self.start_time += time.time() - self.pause_time
            self.pause_button.setText("⏸ Pause")
        else:
            self.pause_time = time.time()
            self.pause_button.setText("▶️ Play")
        self.paused = not self.paused

    def rewind(self):
        self.offset -= 30

    def forward(self):
        self.offset += 30

    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02}:{secs:02}"

    def update_display(self):
        if self.paused:
            return

        elapsed = time.time() - self.start_time + self.offset
        self.time_label.setText(f"⏱ {self.format_time(elapsed)}")

        text = ""
        for sub in self.subtitles:
            start = sub.start.ordinal / 1000
            end = sub.end.ordinal / 1000
            if start <= elapsed <= end:
                text = sub.text
                break

        self.subtitle_label.setText(text)

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Space:
            self.toggle_pause()
        elif key == Qt.Key_Left:
            self.rewind()
        elif key == Qt.Key_Right:
            self.forward()


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("srt_file", help="Path to .srt file")
    parser.add_argument("--offset", type=float, default=0, help="Start time offset in sec")
    args = parser.parse_args()

    subs = pysrt.open(args.srt_file)

    app = QApplication(sys.argv)
    viewer = SubtitleViewer(subs, offset=args.offset)
    viewer.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
