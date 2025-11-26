import cv2

# Varsayılan kamerayı başlat (genellikle 0 numaralı kamera)
kamera = cv2.VideoCapture(0)

# Kamera açılamazsa hata ver
if not kamera.isOpened():
    print("Kamera açılamadı!")
    exit()

while True:
    # Kameradan bir kare (frame) oku
    ret, frame = kamera.read()

    if not ret:
        print("Görüntü alınamadı!")
        break

    # Görüntüyü ekranda göster
    cv2.imshow('Kamera Görüntüsü', frame)

    # 'q' tuşuna basılınca çık
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Kaynakları serbest bırak
kamera.release()
cv2.destroyAllWindows()
