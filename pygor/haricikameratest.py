import cv2

cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)  # 1 = harici kamera
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

while True:
    ok, frame = cap.read()
    if not ok:
        break

    cv2.imshow("Creality Kamera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()