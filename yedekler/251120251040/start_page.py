from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QSizePolicy, QApplication
)
from PyQt5.QtCore import Qt, QSize, QEvent, pyqtSignal
from PyQt5.QtGui import QPixmap
from pathlib import Path


class StartPage(QWidget):
    cardClicked = pyqtSignal()
    def __init__(self, parent=None):
        BASE_DIR = Path(__file__).resolve().parent.parent
        print(BASE_DIR)
        IMG_DIR  = BASE_DIR / "img"
        print(IMG_DIR) 

        super().__init__(parent)
        self.setObjectName("startPage")

            
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(20)

        self.title = QLabel("Merhaba !")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignHCenter)

        self.subtitle = QLabel(
            "Genç KOMEK tarafından hazırlanan Etkileşimli Zemin uygulamasına hoş geldiniz.\n\n"
        )
        self.subtitle.setObjectName("subtitle")
        self.subtitle.setAlignment(Qt.AlignHCenter)
        self.subtitle.setWordWrap(True)

        header_box = QVBoxLayout()
        header_box.setSpacing(8)
        header_box.addWidget(self.title, 0, Qt.AlignHCenter)
        header_box.addWidget(self.subtitle, 0, Qt.AlignHCenter)

        header = QWidget()
        header.setLayout(header_box)
        root.addWidget(header)



        # Card yapısı
        grid_wrap = QWidget()
        grid = QGridLayout(grid_wrap)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(40)
        grid.setVerticalSpacing(8)

        # Görsel Yolları
        assets = {
            "religion": str(IMG_DIR / "6.png"),
        }

        card1 = self._make_card(
            image_path=assets["religion"],
            title="Hazırsanız Başlayalım",
            number=None
        )
        #number=1
        self._make_clickable(card1, "religion")

        grid.addWidget(card1, 0, 0)
        root.addWidget(grid_wrap, 0, Qt.AlignHCenter)

        logos = QHBoxLayout()
        logos.setSpacing(18)
        self.logo1 = self._logo(str(IMG_DIR / "7.png"))
        logos.addStretch(1)
        logos.addWidget(self.logo1)
        logos.addStretch(1)
        logos_wrap = QWidget()
        logos_wrap.setObjectName("logosWrap")
        logos_wrap.setLayout(logos)
        root.addStretch(1)
        root.addWidget(logos_wrap)

    # ---------- helpers ----------

    def _make_card(self, image_path: str, title: str, number: int|None) -> QWidget:
        card = QWidget()
        card.setObjectName("card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)
        lay.setAlignment(Qt.AlignHCenter)

        # Resim çerçevesi
        frame = QFrame()
        frame.setObjectName("imageFrame")
        frame.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        frame_lay = QVBoxLayout(frame)
        frame_lay.setContentsMargins(8, 8, 8, 8)

        img = QLabel()
        img.setObjectName("cardImage")
        img.setAlignment(Qt.AlignCenter)
        pix = QPixmap(image_path)
        if not pix.isNull():
            pix = pix.scaled(QSize(260, 260), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img.setPixmap(pix)
        img.setMinimumSize(240, 240)  # çizim yoksa boşluğu koru
        frame_lay.addWidget(img)
        lay.addWidget(frame, 0, Qt.AlignHCenter)

        # Başlık
        lbl_title = QLabel(title)
        lbl_title.setObjectName("cardTitle")
        lbl_title.setAlignment(Qt.AlignHCenter)
        lay.addWidget(lbl_title)

        # "1 Numaralı Kare" satırı (kırmızı sayı + siyah metin)
        if number is not None:
            row = QHBoxLayout()
            row.setSpacing(6)
            num = QLabel(str(number))
            num.setObjectName("cardNumber")
            txt = QLabel("Numaralı Kare")
            txt.setObjectName("cardNumberText")
            row.addWidget(num, 0, Qt.AlignVCenter)
            row.addWidget(txt, 0, Qt.AlignVCenter)

            row_wrap = QWidget()
            row_wrap.setLayout(row)
            row_wrap.setObjectName("cardNumberRow")
            lay.addWidget(row_wrap, 0, Qt.AlignHCenter)

        return card

    def _logo(self, path: str) -> QLabel:
        lbl = QLabel()
        lbl.setObjectName("logo")
        lbl.setAlignment(Qt.AlignCenter)
        pix = QPixmap(path)
        if not pix.isNull():
            pix = pix.scaledToHeight(50, Qt.SmoothTransformation)
            lbl.setPixmap(pix)
        lbl.setMinimumSize(100, 50)
        return lbl
    
    def _make_clickable(self, widget: QWidget, category_key: str):
        """Kartı ve içindeki tüm çocukları tıklanabilir yap."""
        def mark(w):
            w.setProperty("category", category_key)
            w.setCursor(Qt.PointingHandCursor)
            w.installEventFilter(self)

        mark(widget)
        for child in widget.findChildren(QWidget):
            mark(child)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:

            self.cardClicked.emit()
            # Tıklanan elemanın ait olduğu kartı bul (objectName="card")
            w = obj
            while w and w.objectName() != "card":
                w = w.parentWidget()

            if w:
                # Kart içindeki resim label'ını bul (objectName="cardImage")
                img_lbl = w.findChild(QLabel, "cardImage")
                if img_lbl:
                    self._make_image_black(img_lbl)
                    return True
        return super().eventFilter(obj, event)
    
    def _make_image_black(self, img_lbl: QLabel):
        """Verilen resim QLabel'ını aynı boyutta siyaha çevir."""
        pm = img_lbl.pixmap()
        size = pm.size() if pm and not pm.isNull() else img_lbl.size()
        black = QPixmap(size)
        black.fill(Qt.black)
        img_lbl.setPixmap(black)