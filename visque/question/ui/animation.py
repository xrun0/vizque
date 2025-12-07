from PyQt5.QtWidgets import QLabel, QGraphicsOpacityEffect
from PyQt5.QtCore import QPropertyAnimation, QRect, Qt, QEasingCurve, pyqtSignal

class GeriSayimLabel(QLabel):
    # Geri sayım bittiğinde bu sinyali tetikleyeceğiz
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Tasarım Ayarları
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("color: red; font-weight: bold; font-size: 100px;")
        
        # Arka plan şeffaf olsun (Kamera görünsün diye)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide() # Başlangıçta gizli

        # Animasyon Nesnesi
        self.animasyon = QPropertyAnimation(self, b"geometry")
        self.animasyon.setDuration(900) # Her sayı 0.9 saniye sürsün
        self.animasyon.setEasingCurve(QEasingCurve.OutBounce) # "Zıplama" efekti verir
        
        # Animasyon her bittiğinde bu fonksiyonu çağır
        self.animasyon.finished.connect(self._sonraki_sayi)
        
        self.simdiki_sayi = 3
        self.parent_widget = parent

    def baslat(self):
        """Geri sayımı başlatır"""
        self.simdiki_sayi = 3
        self.show()
        self.raise_() # En öne getir
        self._animasyonu_oynat()

    def _animasyonu_oynat(self):
        # Yazıyı güncelle
        self.setText(str(self.simdiki_sayi))
        
        # Parent (Pencere) boyutlarını al
        if self.parent_widget:
            p_w = self.parent_widget.width()
            p_h = self.parent_widget.height()
        else:
            p_w, p_h = 800, 600

        # Başlangıç (Küçük) ve Bitiş (Büyük) karelerini hesapla
        # Merkezden dışa doğru büyümesi için matematik:
        
        # Bitiş Boyutu (Büyük)
        end_size = 300
        end_rect = QRect(int(p_w/2 - end_size/2), int(p_h/2 - end_size/2), end_size, end_size)
        
        # Başlangıç Boyutu (Küçük)
        start_size = 10
        start_rect = QRect(int(p_w/2 - start_size/2), int(p_h/2 - start_size/2), start_size, start_size)

        # Animasyonu Kur
        self.animasyon.setStartValue(start_rect)
        self.animasyon.setEndValue(end_rect)
        
        # Yazı boyutunu dinamik ayarlamak zor olduğu için
        # büyük font verip geometri ile oynuyoruz.
        self.animasyon.start()

    def _sonraki_sayi(self):
        self.simdiki_sayi -= 1
        
        if self.simdiki_sayi > 0:
            # 2 ve 1 için tekrar oynat
            self._animasyonu_oynat()
        else:
            # 0 olduysa bitir
            self.hide()
            self.finished.emit() # Bitti sinyali gönder