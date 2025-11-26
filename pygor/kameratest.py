import cv2

INDEX = 0  # harici kamera genelde 1
cap = cv2.VideoCapture(INDEX, cv2.CAP_AVFOUNDATION)

if not cap.isOpened():
    raise RuntimeError(f"Kamera {INDEX} açılamadı. Sistem izinleri veya bağlantıyı kontrol et.")

# (isteğe bağlı) çözünürlük
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# küçük ısınma (bazı kameralar ilk kareleri siyah verebilir)
for _ in range(5):
    cap.read()

while True:
    ok, frame = cap.read()
    if not ok:
        print("Kare alınamadı!")
        break

    cv2.imshow("Harici Kamera (1)", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
