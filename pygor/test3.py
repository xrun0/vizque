import cv2
import numpy as np

def bul_kagit_kosesi(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    # Konturları bul
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)

        if len(approx) == 4:  # Kağıt dikdörtgense 4 köşesi olur
            return np.float32([pt[0] for pt in approx])

    return None

def perspektif_duzelt(frame, corners):
    # Kağıt köşelerini sırala: sol üst, sağ üst, sağ alt, sol alt
    def sirala_noktalar(pts):
        pts = sorted(pts, key=lambda x: x[0] + x[1])  # sol üst, sağ alt
        top_left = min(pts, key=lambda x: x[0] + x[1])
        bottom_right = max(pts, key=lambda x: x[0] + x[1])
        top_right = min(pts, key=lambda x: x[0] - x[1])
        bottom_left = max(pts, key=lambda x: x[0] - x[1])
        return np.array([top_left, top_right, bottom_right, bottom_left], dtype='float32')

    ordered = sirala_noktalar(corners)
    width, height = 400, 600  # A4 oranına uygun varsayımsal boyut

    target = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
    matrix = cv2.getPerspectiveTransform(ordered, target)
    warp = cv2.warpPerspective(frame, matrix, (width, height))

    return warp

def bul_kirmizi_nokta(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    lower1 = np.array([0, 100, 100])
    upper1 = np.array([10, 255, 255])
    lower2 = np.array([160, 100, 100])
    upper2 = np.array([180, 255, 255])

    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    mask = cv2.bitwise_or(mask1, mask2)

    mask = cv2.medianBlur(mask, 5)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        if area > 100:
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cx = int(M["m10"] / M["m00"])
                cy = int(M["m01"] / M["m00"])
                return (cx, cy)
    return None

def hangi_karede(cx, cy, w, h, satir=4, sutun=2):
    hucre_genislik = w // sutun
    hucre_yukseklik = h // satir

    col = cx // hucre_genislik
    row = cy // hucre_yukseklik

    return int(row), int(col)

# Ana kamera döngüsü
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    kose = bul_kagit_kosesi(frame)

    if kose is not None:
        duz = perspektif_duzelt(frame, kose)
        cxcy = bul_kirmizi_nokta(duz)

        if cxcy:
            cx, cy = cxcy
            satir, sutun = hangi_karede(cx, cy, duz.shape[1], duz.shape[0])
            print(f"Kırmızı nokta: {satir}. satır, {sutun}. sütun")
            cv2.circle(duz, (cx, cy), 10, (0, 255, 0), -1)

        # 4x2 ızgara çiz
        for r in range(1, 4):
            y = (duz.shape[0] // 4) * r
            cv2.line(duz, (0, y), (duz.shape[1], y), (200, 200, 200), 1)
        for c in range(1, 2):
            x = (duz.shape[1] // 2) * c
            cv2.line(duz, (x, 0), (x, duz.shape[0]), (200, 200, 200), 1)

        cv2.imshow("Izgara", duz)

    cv2.imshow("Kamera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
