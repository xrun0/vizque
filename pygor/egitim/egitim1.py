import cv2

cap = cv2.VideoCapture(0)  # Kamerayı başlat

while True:
    ret, frame = cap.read()  # 1 kare oku
    
    if not ret:
        break  # Okuma başarısızsa döngüden çık
    
    cv2.imshow("Kamera", frame)  # Kareyi göster
    
    if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q' ya basınca çık
        break

cap.release()
cv2.destroyAllWindows()