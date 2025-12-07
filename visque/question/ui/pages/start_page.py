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
        super().__init__(parent)
        print("StartPage initialized")
        self.setObjectName("startPage")
        
        BASE_DIR = Path(__file__).resolve().parent.parent
        IMG_DIR  = BASE_DIR / "img"
            
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

        #Glabel = QLabel(self)   # veya bir layout içine koyacaksan sadece QLabel()
        #pix = QPixmap("ui/img/1.png")   # resim yolu
        #
        #Glabel.setPixmap(pix)
        #pix = QPixmap("ui/img/1.png")
        #Glabel.setPixmap(pix.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))


        layout = QVBoxLayout(self)

        self.img = QLabel()
        self.img.setAlignment(Qt.AlignCenter)
        self.img.setMinimumWidth(100)   # test için
        self.img.setMinimumHeight(100)


        # GÖRSELİ YÜKLE - STATİK DOSYA YOLU
        # Gerekli import (Eğer ekli değilse ekle)

        # 1. Görseli Yükle
        resim_yolu = str(IMG_DIR / "6.png")
        pix = QPixmap(resim_yolu)

        # Resim başarıyla yüklendi mi kontrol et
        if not pix.isNull():
            
            # 2. Resmi Boyutlandır (Örn: Genişlik 800px olsun, yükseklik otomatik)
            # Qt.SmoothTransformation: Resim küçülürken tırtıklı olmasını engeller, pürüzsüz yapar.
            yeni_pix = pix.scaledToWidth(320, Qt.SmoothTransformation)
            
            # 3. Label'a Boyutlanmış Resmi Ata
            self.img.setPixmap(yeni_pix)
            
            # 4. Tıklama Özelliğini Ekle
            self.img.mousePressEvent = self.on_image_clicked
            
            # 5. Arayüze Ekle
            root.addWidget(self.img)

        else:
            print(f"HATA: Resim yüklenemedi! Yol: {resim_yolu}")


        logos = QHBoxLayout()
        logos.setSpacing(80)
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
    def on_image_clicked(self, event):
        print("Resim tıklandı!")
        self.cardClicked.emit()

    def _logo(self, path: str) -> QLabel:
        lbl = QLabel()
        lbl.setObjectName("logo")
        lbl.setAlignment(Qt.AlignCenter)
        pix = QPixmap(path)
        if not pix.isNull():
            pix = pix.scaledToHeight(100, Qt.SmoothTransformation)
            lbl.setPixmap(pix)
        lbl.setMinimumSize(600, 300)
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