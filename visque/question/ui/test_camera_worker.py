# ui/test_camera_worker.py

import cv2
from camera_worker import process_frame  # aynı klasörde olduğu için doğrudan import

def main():
    cap = cv2.VideoCapture(0)  # Gerekirse 1,2 diye değiştir

    if not cap.isOpened():
        print("Kamera acilamadi")
        return

    print("Test başlıyor. 'q' tuşu ile çıkabilirsiniz.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kare okunamadi, kamera kapandi mi?")
            break

        # Her kare için sendData üret
        processed,sendData,thresed_frame = process_frame(frame)
        cv2.imshow("processed",processed)
        cv2.imshow("thresed_frame",thresed_frame)

        # Terminale yaz
        print("sendData:", sendData)

        # Kamerayı ekranda göster (ANA THREAD, o yüzden sorun yok)
        
        # 'q' ile çıkış
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
