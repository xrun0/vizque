import cv2

for i in range(5):
    cap = cv2.VideoCapture(i)
    if cap.isOpened():
        print(f"Kamera {i} kullanılabilir.")
        cap.release()
    else:
        print(f"Kamera {i} bulunamadı.")