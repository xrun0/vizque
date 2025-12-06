# ui/pages/result_page.py

from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QSizePolicy,QPushButton
)
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtGui import QPixmap
from pathlib import Path


class ResultPage(QWidget):
    goHome = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("resultPage")

        root = QVBoxLayout(self)
        root.setContentsMargins(60, 40, 60, 40)
        root.setSpacing(40)
        root.setAlignment(Qt.AlignTop)

        # === ÜST KARTLAR (Doğru / Yanlış) ===
        topRow = QHBoxLayout()
        topRow.setSpacing(40)

        self.correctCard = self._createResultCard("Doğru Cevap")
        self.wrongCard = self._createResultCard("Yanlış Cevap")

        topRow.addWidget(self.correctCard)
        topRow.addWidget(self.wrongCard)

        root.addLayout(topRow)

        # === ORTA MESAJ KUTUSU (TEBRİKLER!) ===
        self.messageFrame = QFrame()
        self.messageFrame.setObjectName("resultMessageCard")
        self.messageFrame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        msgLayout = QVBoxLayout(self.messageFrame)
        msgLayout.setContentsMargins(40, 24, 40, 24)

        self.messageLabel = QLabel("TEBRİKLER!")
        self.messageLabel.setObjectName("resultMessageLabel")
        self.messageLabel.setAlignment(Qt.AlignCenter)

        msgLayout.addWidget(self.messageLabel)
        root.addWidget(self.messageFrame)

                # === BUTON: BAŞA DÖN ===
        self.homeButton = QPushButton("Başa Dön")
        self.homeButton.setObjectName("homeButton")
        self.homeButton.setFixedHeight(60)
        self.homeButton.clicked.connect(self.goHome.emit)

        root.addWidget(self.homeButton, alignment=Qt.AlignCenter)

        BASE_DIR = Path(__file__).resolve().parent.parent
        IMG_DIR  = BASE_DIR / "img"

        logos = QHBoxLayout()
        logos.setSpacing(18)
        self.logo1 = self._logo(str(IMG_DIR / "5.png"))
        logos.addStretch(1)
        logos.addWidget(self.logo1)
        logos.addStretch(1)
        logos_wrap = QWidget()
        logos_wrap.setObjectName("logosWrap")
        logos_wrap.setLayout(logos)
        root.addStretch(1)
        root.addWidget(logos_wrap)

    # ----------------- yardımcılar -----------------
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
    
    def _createResultCard(self, title: str) -> QFrame:
        card = QFrame()
        card.setObjectName("resultCard")
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(40, 32, 40, 32)
        layout.setSpacing(16)

        titleLabel = QLabel(title)
        titleLabel.setObjectName("resultCardTitle")
        titleLabel.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        titleLabel.setWordWrap(True)

        valueLabel = QLabel("0")
        valueLabel.setObjectName("resultCardValue")
        valueLabel.setAlignment(Qt.AlignCenter)

        layout.addWidget(titleLabel)
        layout.addWidget(valueLabel, 1, Qt.AlignCenter)

        # referans için saklayalım
        card.titleLabel = titleLabel
        card.valueLabel = valueLabel

        return card

    def _createLogoLabel(self, path: str) -> QLabel:
        lbl = QLabel()
        lbl.setObjectName("resultLogo")
        lbl.setAlignment(Qt.AlignCenter)
        pix = QPixmap(path)
        if not pix.isNull():
            lbl.setPixmap(pix.scaledToHeight(60, Qt.SmoothTransformation))
        return lbl

    # ----------------- dışarıdan kullanacağın API -----------------

    def setResults(self, correct: int, wrong: int):
        """Soru sayfası işini bitirince buradan sonuçları güncelle."""
        self.correctCard.valueLabel.setText(str(correct))
        self.wrongCard.valueLabel.setText(str(wrong))

    def setMessage(self, text: str):
        self.messageLabel.setText(text)
