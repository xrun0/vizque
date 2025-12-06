from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QMovie
from pathlib import Path


class ProjectionWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Varsayılan değerler (senin kodundan) ---
        self.cells = {}          # (r,c) -> QLabel
        self.resultGifLabel = None
        self.resultMovie = None

        # ---- Görsel yükleme ----
        base_dir = Path(__file__).resolve().parent
        img_dir = base_dir / "img"

        # Idle, seçili, doğru, yanlış PNG'leri
        self.idle_pix     = self._load_pix(img_dir / "bos.png")
        self.selected_pix = self._load_pix(img_dir / "secili.png")
        self.correct_pix  = self._load_pix(img_dir / "dogru.png")
        self.wrong_pix    = self._load_pix(img_dir / "yanlis.png")

        # ---- 2x2 kare oluşturma ----
        letters = {
            (0, 0): "A",
            (0, 1): "B",
            (1, 0): "C",
            (1, 1): "D",
        }

        # Arka plan kareleri
        for r in range(2):
            for c in range(2):
                lbl = QLabel(self)
                lbl.setAlignment(Qt.AlignCenter)
                lbl.setScaledContents(True)
                self.cells[(r, c)] = lbl

        # --- Harf label'ları (EN ÜSTE GELECEK) ---
        self.letter_labels = {}
        for (r, c), text in letters.items():
            lbl = QLabel(self)
            lbl.setText(text)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("""
                color: black;
                font-size: 72px;
                font-weight: bold;
                background: transparent;
            """)
            self.letter_labels[(r, c)] = lbl

        self._relayout()

    # ---------------------------------------------------------
    #   YARDIMCI FONKSİYON
    # ---------------------------------------------------------
    def _load_pix(self, path: Path):
        if path.exists():
            return QPixmap(str(path))
        return None

    # ---------------------------------------------------------
    #   GRID YERLEŞTİRME
    # ---------------------------------------------------------
    def _relayout(self):
        """Tam ekranı 2x2 böl ve kareleri doğru şekilde yerleştir."""
        w = self.width()
        h = self.height()

        cell_w = w // 2
        cell_h = h // 2

        for (r, c), lbl in self.cells.items():
            x = c * cell_w
            y = r * cell_h
            lbl.setGeometry(x, y, cell_w, cell_h)

            # Idle görsel uygula
            if self.idle_pix:
                lbl.setPixmap(
                    self.idle_pix.scaled(
                        cell_w, cell_h,
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                )
            else:
                lbl.setStyleSheet("background-color: black;")

        # HARF LABEL’LARINI TAM ÜSTE ORTALA
        for (r, c), letter_lbl in self.letter_labels.items():
            x = c * cell_w
            y = r * cell_h
            letter_lbl.setGeometry(x, y, cell_w, cell_h)

    def resizeEvent(self, event):
        """Pencere tam ekran değişince grid'i yeniden boyutla."""
        super().resizeEvent(event)
        self._relayout()

    # ---------------------------------------------------------
    #   SORU ESNASINDA SEÇİM
    # ---------------------------------------------------------
    def setSelectedCell(self, row, col):
        """
        Soru sırasında seçilen kare: (row, col)
        Diğer kareler idle olur.
        """

        # Tüm kareleri idle yap
        for (r, c), lbl in self.cells.items():
            if self.idle_pix:
                lbl.setPixmap(self.idle_pix.scaled(
                    lbl.width(), lbl.height(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                ))
            else:
                lbl.setStyleSheet("background-color: black;")

        if row is None or col is None:
            return

        lbl = self.cells.get((row, col))
        if lbl and self.selected_pix:
            lbl.setPixmap(
                self.selected_pix.scaled(
                    lbl.width(), lbl.height(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )

    # ---------------------------------------------------------
    #   DOĞRU / YANLIŞ GÖSTERİMİ
    # ---------------------------------------------------------
    def showResultCell(self, row, col, is_correct=True):
        """
        Süre bitince sadece seçilen kare doğru/yanlış görseli alır.
        Diğerleri idle olur.
        """
        # Tüm kareleri idle yap
        for (r, c), lbl in self.cells.items():
            if self.idle_pix:
                lbl.setPixmap(self.idle_pix.scaled(
                    lbl.width(), lbl.height(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                ))

        lbl = self.cells.get((row, col))
        if not lbl:
            return

        pix = self.correct_pix if is_correct else self.wrong_pix
        if pix:
            lbl.setPixmap(
                pix.scaled(
                    lbl.width(), lbl.height(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                )
            )

    # ---------------------------------------------------------
    #   RESULT TAM EKRAN GIF
    # ---------------------------------------------------------
    def showFullResultGif(self):
        """Result ekranında tam ekran GIF."""
        base_dir = Path(__file__).resolve().parent
        gif_path = base_dir / "img" / "celebratefinal.gif"

        # Grid’i gizle
        for lbl in self.cells.values():
            lbl.hide()
        for lbl in self.letter_labels.values():
            lbl.hide()

        # GIF
        if not self.resultGifLabel:
            self.resultGifLabel = QLabel(self)
            self.resultGifLabel.setScaledContents(True)

        if not self.resultMovie:
            self.resultMovie = QMovie(str(gif_path))
            self.resultGifLabel.setMovie(self.resultMovie)

        self.resultGifLabel.setGeometry(self.rect())
        self.resultGifLabel.show()
        self.resultMovie.start()

    def clearResultGif(self):
        """Başa dönünce GIF'i gizle, grid’i geri getir."""
        if self.resultMovie:
            self.resultMovie.stop()

        if self.resultGifLabel:
            self.resultGifLabel.hide()

        # Grid'i geri getir
        for lbl in self.cells.values():
            lbl.show()
        for lbl in self.letter_labels.values():
            lbl.show()

        self._relayout()
        
    def showWrongAndCorrect(self, wrong_row, wrong_col, correct_row, correct_col):
        """
        Yanlış cevap durumunda:
          - Seçilen kareye wrong.png
          - Doğru kareye correct.png
          - Diğer kareler idle.png (varsa)
        """
        # Önce tüm kareleri idle yap
        for (r, c), lbl in self.cells.items():
            if self.idle_pix:
                lbl.setPixmap(
                    self.idle_pix.scaled(
                        lbl.width(), lbl.height(),
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                )
            else:
                lbl.setStyleSheet("background-color: black;")

        # Yanlış seçilen kare
        if wrong_row is not None and wrong_col is not None:
            wrong_lbl = self.cells.get((wrong_row, wrong_col))
            if wrong_lbl and self.wrong_pix:
                wrong_lbl.setPixmap(
                    self.wrong_pix.scaled(
                        wrong_lbl.width(), wrong_lbl.height(),
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                )

        # Doğru kare
        if correct_row is not None and correct_col is not None:
            correct_lbl = self.cells.get((correct_row, correct_col))
            if correct_lbl and self.correct_pix:
                correct_lbl.setPixmap(
                    self.correct_pix.scaled(
                        correct_lbl.width(), correct_lbl.height(),
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                )

