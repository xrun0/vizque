import cv2
import numpy as np

def background_subtraction_demo():
    cap = cv2.VideoCapture(0) # 0: Laptop kamerası veya bağlı USB kamera
    
    # Arka planı saklayacağımız değişken
    background = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # 1. Görüntüyü Griye Çevir ve Yumuşat
        # Renklerle uğraşmamak ve gürültüyü azaltmak için şarttır.
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        # 2. Arka Plan Belirlenmiş mi?
        if background is None:
            background = gray.copy().astype("float")
            print("Arka plan kaydedildi! Nesneleri sahneye alabilirsiniz.")
            continue
            
        # 3. Matematiksel Çıkarma İşlemi (MUTLAK FARK)
        # cv2.absdiff: Absolute Difference (Mutlak Fark)
        # frame (anlık) - background (hafıza) işlemini yapar.
        # Bu aşamada arka planın float formatından uint8'e dönmesi gerekir.
        fark = cv2.absdiff(cv2.convertScaleAbs(background), gray)
        
        # 4. Eşikleme (Threshold)
        # Fark değeri 25'ten küçükse (küçük ışık oynamaları) yoksay (siyah yap),
        # 25'ten büyükse (gerçek nesne) beyaz yap.
        _, thresh = cv2.threshold(fark, 25, 255, cv2.THRESH_BINARY)
        
        # 5. Temizlik (Morfoloji)
        # Nesnenin içindeki küçük siyah delikleri kapat
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        # GÖRSELLEŞTİRME ---
        # Kontur bulup orijinal kareye çizelim ki sonucu görelim
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        display_frame = frame.copy()
        
        for cnt in contours:
            if cv2.contourArea(cnt) < 500: # Çok küçük hareketleri yoksay
                continue
                
            (x, y, w, h) = cv2.boundingRect(cnt)
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(display_frame, "Nesne Algilandi", (10, 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Pencereleri göster
        cv2.imshow("1. Orjinal Goruntu", display_frame)
        cv2.imshow("2. Fark Goruntusu (AbsDiff)", fark)
        cv2.imshow("3. Sonuc Maskesi (Threshold)", thresh)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            # 'r' tuşuna basarsan arka planı o anki görüntüyle yeniler
            background = gray.copy().astype("float")
            print("Arka plan yenilendi!")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    background_subtraction_demo()