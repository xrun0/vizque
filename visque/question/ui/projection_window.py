# ui/projection_window.py
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QMovie
from pathlib import Path


class ProjectionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Projeksiyon")
        self.setObjectName("projectionWindow")

        # Tam ekran gösterilecek, main tarafında showFullScreen ile açacağız
        grid = QGridLayout(self)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(0)

        self.cells = {}          # (row, col) -> QLabel
        self.cell_movies = {}    # (row, col) -> QMovie (animasyon için)
        self.active = None

        # Görsel/GIF dosya yolu (örnek)
        base_dir = Path(__file__).resolve().parent
        img_dir = base_dir / "img"

        # Statik görsel (PNG) – istersen sadece bunu da kullanabilirsin
        self.static_pix = QPixmap(str(img_dir / "correct_answer.png"))
        # Aktif animasyon (GIF) – seçilen hücrede oynatılacak
        self.active_gif_path = str(img_dir / "celebratefinal.gif")

        for r in range(2):
            for c in range(2):
                lbl = QLabel()
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setStyleSheet("background-color: black;")
                lbl.setMinimumSize(400, 400)  # projeksiyon boyutuna göre büyütülür

                # Hücreye varsayılan statik görsel koy (varsa)
                if not self.static_pix.isNull():
                    lbl.setPixmap(self.static_pix.scaled(
                        960, 540, Qt.KeepAspectRatio, Qt.SmoothTransformation
                    ))

                grid.addWidget(lbl, r, c)
                self.cells[(r, c)] = lbl

                # Her hücre için QMovie (GIF) oluşturalım (aynı dosyadan)
                movie = QMovie(self.active_gif_path)
                self.cell_movies[(r, c)] = movie

        # Aktif hücre yanıp sönsün mü diye istersen timer da ekleyebilirsin
        # şimdilik sadece GIF yeterli, ekstra timer kullanmıyoruz.

    def setActiveCell(self, row, col):
        """
        Kameradan gelen (row, col) bilgisini alır.
        - Tüm hücrelerde animasyonu durdurur
        - Sadece seçilen hücrede GIF animasyonunu oynatır
        - Eğer row/col None ise her şeyi temizler
        """
        # Önce tüm hücrelerde animasyonu durdur + statik haline al
        for (r, c), lbl in self.cells.items():
            movie = self.cell_movies[(r, c)]
            movie.stop()
            if not self.static_pix.isNull():
                lbl.setPixmap(self.static_pix.scaled(
                    960, 540, Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
            else:
                lbl.setStyleSheet("background-color: black;")

        # Aktif yoksa tamamen temizledik, çık
        if row is None or col is None:
            self.active = None
            return

        self.active = (row, col)

        # Seçilen hücrede GIF başlat
        movie = self.cell_movies[(row, col)]
        lbl = self.cells[(row, col)]

        # Movie'yi label'a bağla ve oynat
        lbl.setMovie(movie)
        movie.start()

    def showFullResultGif(self):
        base_dir = Path(__file__).resolve().parent
        img_dir = base_dir / "img"

        # 1) Grid hücrelerini gizle
        for lbl in self.cells.values():
            lbl.hide()

        # 2) Result label yoksa oluştur
        if not hasattr(self, "resultGifLabel") or self.resultGifLabel is None:
            self.resultGifLabel = QLabel(self)
            self.resultGifLabel.setGeometry(self.rect())
            self.resultGifLabel.setScaledContents(True)

        # 3) Movie nesnesini attribute olarak sakla (GC olmasın)
        if not hasattr(self, "resultMovie") or self.resultMovie is None:
            self.resultMovie = QMovie(str(img_dir / "celebratefinal.gif"))
        else:
            # Aynı gif'i tekrar kullanacağız, istersen dosya adını burada da güncelleyebilirsin
            self.resultMovie.setFileName(str(img_dir / "celebratefinal.gif"))

        self.resultGifLabel.setMovie(self.resultMovie)
        self.resultGifLabel.show()   # 🔴 HER SEFERİNDE SHOW!
        self.resultMovie.start()

    def clearResultGif(self):
        """Result GIF'ini gizle ve 4'lü grid görünümüne geri dön."""
        # 1) GIF'i durdur ve label'ı gizle
        if hasattr(self, "resultMovie") and self.resultMovie:
            self.resultMovie.stop()

        if hasattr(self, "resultGifLabel") and self.resultGifLabel:
            self.resultGifLabel.hide()
            # self.resultGifLabel.clear()  # şart değil, istersen bırak

        # 2) Hücreleri tekrar görünür yap ve temel görsel / rengi geri yükle
        for (r, c), lbl in self.cells.items():
            lbl.show()
            if hasattr(self, "static_pix") and getattr(self, "static_pix", None) and not self.static_pix.isNull():
                lbl.setPixmap(
                    self.static_pix.scaled(
                        960, 540,
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
            else:
                lbl.setStyleSheet("background-color: black;")
