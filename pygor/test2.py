import cv2
import numpy as np

# Kamerayı başlat
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    height, width, _ = frame.shape

    # HSV renk uzayına çevir
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Kırmızı için iki ayrı HSV aralığı tanımlanmalı (çünkü HSV'de kırmızı 0-10 ve 160-180 arasında olur)
    lower_red1 = np.array([0, 100, 100])
    upper_red1 = np.array([10, 255, 255])

    lower_red2 = np.array([160, 100, 100])
    upper_red2 = np.array([180, 255, 255])

    # Maskeleri oluştur
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = cv2.bitwise_or(mask1, mask2)

    # Gürültü temizleme (opsiyonel ama önerilir)
    red_mask = cv2.medianBlur(red_mask, 5)

    # Konturları bul
    contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # En büyük kırmızı alanı al
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        if area > 100:  # Çok küçük noktaları eleyelim
            # Kırmızı noktanın merkezini bul
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])

                # Noktayı göster
                cv2.circle(frame, (cx, cy), 8, (0, 255, 0), -1)

                # 4x2 kare hesaplama
                rows = 4
                cols = 2

                cell_width = width // cols
                cell_height = height // rows

                col_index = cx // cell_width
                row_index = cy // cell_height

                print(f"Kırmızı nokta {row_index}. satır, {col_index}. sütun karesinde.")

                # Hücre çizgilerini çiz
                for r in range(1, rows):
                    cv2.line(frame, (0, r * cell_height), (width, r * cell_height), (255, 255, 255), 1)
                for c in range(1, cols):
                    cv2.line(frame, (c * cell_width, 0), (c * cell_width, height), (255, 255, 255), 1)

    # Görüntüyü göster
    cv2.imshow('Kırmızı Takibi', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
