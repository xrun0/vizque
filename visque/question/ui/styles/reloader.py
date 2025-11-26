# styles/reloader.py
from pathlib import Path
from PyQt5.QtCore import QObject, QFileSystemWatcher, QTimer

class QssReloader(QObject):
    def __init__(self, app, paths, parent=None):
        super().__init__(parent)
        self.app = app
        self.paths = [str(p) for p in paths]
        self.watcher = QFileSystemWatcher(self.paths)
        self._timer = QTimer(self, interval=150)  # küçük debounce
        self._timer.setSingleShot(True)
        self.watcher.fileChanged.connect(lambda _p: self._timer.start())
        self._timer.timeout.connect(self.reload)
        self.reload()  # ilk yükleme

    def reload(self):
        text = ""
        for p in self.paths:
            try:
                text += Path(p).read_text(encoding="utf-8") + "\n"
            except FileNotFoundError:
                pass
        self.app.setStyleSheet(text)
        print("🔄 QSS yeniden yüklendi.")
