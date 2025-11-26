import cv2
import numpy as np
import time
prev_time = time.time()  # döngü dışında tanımla


# Kamerayı başlat
cap = cv2.VideoCapture(0)

# Turuncu için HSV renk aralığı
lower_orange = np.array([15, 150, 150])
upper_orange = np.array([25, 255, 255])

while True:
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
    time.sleep(0.199)

    ret, frame = cap.read()
    if not ret:
        break
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
    

    # Renk uzayını BGR'den HSV'ye çevir
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Turuncu alanları maskele
    mask = cv2.inRange(hsv, lower_orange, upper_orange)

    # Gürültüyü azaltmak için filtre uygula
    mask = cv2.medianBlur(mask, 3)

    # Konturları bul
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 1000:  # küçük parazitleri ele
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            print("Turuncu nesne bulundu")
            cv2.putText(frame, "Turuncu nesne", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        

    # Görüntüyü göster
    cv2.imshow("Turuncu Tespiti", frame)
    cv2.imshow("Maske", mask)
    

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

# Temizlik
cap.release()
cv2.destroyAllWindows()
