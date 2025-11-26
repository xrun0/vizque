import cv2
import numpy as np
import traceback


def funcKontur(contours, hierarchy):
    try:
        # Hiyerarşi hiç bulunamadıysa
        if hierarchy is None or len(contours) < 9:
            return [], [], []

        anakareler = []
        elemanlar = []
        elemankontur = []

        newHierarchy = list(hierarchy)
        for i, h in enumerate(newHierarchy[0]):
            # h: [next, prev, child, parent]
            data = [i, int(h[0]), int(h[1]), int(h[2]), int(h[3])]
            anakareler.append(data)

            # Parent'ı olanlar (içteki elemanlar)
            if h[3] > 0:
                elemanlar.append(data)
                elemankontur.append(contours[i])

        return anakareler, elemanlar, elemankontur
    except Exception as e:
        print("Bir hata oluştu funcKontur:", e)
        return [], [], []


def funcBuyuklukolc(elemanlar, elemankontur):
    buyukalan = 0
    enbuyukkontur = None
    sayac = 0

    for cnt in elemankontur:
        alan = cv2.contourArea(cnt)
        if buyukalan < alan:
            buyukalan = alan
            if sayac < len(elemanlar):
                enbuyukkontur = elemanlar[sayac]
        sayac += 1

    return buyukalan, enbuyukkontur


def funcFindParent(parentKontur, anakareler):
    matris = 0
    for i in anakareler:
        if i[0] == parentKontur:
            # 8 - childIndex mantığını korudum
            matris = 8 - i[2]
    return matris


def process_frame(frame):
    """
    Tek bir kareyi (frame) işle:
    - yeniden boyutlandır
    - griye çevir
    - blur + threshold
    - kontur bul
    - alan filtresi
    - hiyerarşiden sendData üret
    """
    # İstersen buradaki scale ile oynayabilirsin
    scale = 1
    height, width = frame.shape[:2]
    new_width = int(width * scale)
    new_height = int(height * scale)
    img = cv2.resize(frame, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Gürültü azaltma
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    blur2 = cv2.medianBlur(blur, 7)
    blur3 = cv2.bilateralFilter(blur2, d=7, sigmaColor=75, sigmaSpace=75)

    # Threshold
    _, thresh = cv2.threshold(blur3, 14, 255, cv2.THRESH_BINARY_INV)

    # Konturları çizmek için renkli kopya
    thresh_color = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

    # Kontur bul
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Alan filtresi ile bazı konturları çiz
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 10000 < area < 1000000:
            cv2.drawContours(thresh_color, [cnt], -1, (0, 255, 0), 3)

    # Hiyerarşi analizi
    kareler, nesneler, nesnelerkontur = funcKontur(contours, hierarchy)

    sendData = 0
    if len(nesneler) > 0 and len(nesnelerkontur) > 0:
        buyukalan, enbuyukkontur = funcBuyuklukolc(nesneler, nesnelerkontur)

        if enbuyukkontur is not None:
            sendData = funcFindParent(enbuyukkontur[4], kareler)

    # Ekranda görmek için sendData'yı yazdır
    cv2.putText(thresh_color,
                f"sendData: {sendData}",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                2,
                cv2.LINE_AA)

    return thresh_color, sendData


def main():
    try:
        # 1) Kameradan görüntü almak için:
        cap = cv2.VideoCapture(0)  # 0 = varsayılan kamera

        # 1b) Eğer video dosyasından okuyacaksan:
        # cap = cv2.VideoCapture('medya/video.mp4')

        if not cap.isOpened():
            print("Video kaynağı açılamadı!")
            return

        while True:
            ret, frame = cap.read()
            if not ret:
                print("Kare okunamadı, video bitti veya kamera yok.")
                break

            # Her kareyi işle
            processed_frame, sendData = process_frame(frame)

            # Ekrana göster
            cv2.imshow("Islenmis Video (thresh_color)", processed_frame)

            # Çıkış için 'q' ya da ESC
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break

        cap.release()
        cv2.destroyAllWindows()

    except Exception as e:
        print("=== Hata Detayı ===")
        print(f"Tip: {type(e).__name__}")
        print(f"Mesaj: {e}")
        print("Traceback:")
        traceback.print_exc()
        with open("error_log.txt", "a") as f:
            f.write("Hata:\n")
            traceback.print_exc(file=f)


if __name__ == "__main__":
    main()
