import cv2
import numpy as np
import matplotlib.pyplot as plt

# --- 0) GÖRSELİ YÜKLE ---
img_path = "../medya/resim6.png"   # <-- kendi yolunu yaz
bgr = cv2.imread(img_path)
if bgr is None:
    raise FileNotFoundError("Görüntü bulunamadı. Yol/isim doğru mu?")

hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)

# --- 1) RENK MASKELEMELERİ (HSV) ---
# Not: Işığa göre alt/üst sınırlar ayarlanabilir.
# KIRMIZI iki aralık ister (0/tur ve 180/tur)
lower_red1, upper_red1 = (0, 80, 80), (10, 255, 255)
lower_red2, upper_red2 = (170, 80, 80), (180, 255, 255)
mask_red = cv2.inRange(hsv, np.array(lower_red1), np.array(upper_red1)) | \
           cv2.inRange(hsv, np.array(lower_red2), np.array(upper_red2))

# MAVİ (yaklaşık 100–130 Hue)
lower_blue, upper_blue = (100, 80, 80), (130, 255, 255)
mask_blue = cv2.inRange(hsv, np.array(lower_blue), np.array(upper_blue))

# İnce çizgileri toparlamak için hafif genleştirme (opsiyonel, gerekirse 1→2 yap)
kernel = np.ones((3,3), np.uint8)
mask_red  = cv2.dilate(mask_red, kernel, iterations=1)
mask_blue = cv2.dilate(mask_blue, kernel, iterations=1)

def find_main_contour(mask):
    # Dış konturları bul
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not cnts:
        return None
    # En büyük alanlı kontur kareyi temsil eder
    cnt = max(cnts, key=cv2.contourArea)
    # İsteğe bağlı: 4 köşeye yaklaştır
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.02 * peri, True)
    return approx if len(approx) >= 4 else cnt

def draw_and_label(canvas, cnt, label):
    # Konturu yeşil çiz
    cv2.drawContours(canvas, [cnt], -1, (0, 255, 0), 2)
    # Etiket konumu: kontur merkezine koy
    M = cv2.moments(cnt)
    if M["m00"] != 0:
        cx, cy = int(M["m10"]/M["m00"]), int(M["m01"]/M["m00"])
    else:
        # m00=0 olursa (çok ince/boş), basitçe bounding box merkezini al
        x, y, w, h = cv2.boundingRect(cnt)
        cx, cy = x + w//2, y + h//2
    cv2.putText(canvas, label, (cx-20, cy-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2, cv2.LINE_AA)

# --- 2) KONTURLARI BUL ---
cnt_red  = find_main_contour(mask_red)
cnt_blue = find_main_contour(mask_blue)

# --- 3) ÇİZ VE ETİKETLE ---
out = bgr.copy()
if cnt_red is not None:
    draw_and_label(out, cnt_red, "a karesi")
else:
    print("Uyarı: Kırmızı kare bulunamadı. HSV aralıklarını ayarla.")

if cnt_blue is not None:
    draw_and_label(out, cnt_blue, "b karesi")
else:
    print("Uyarı: Mavi kare bulunamadı. HSV aralıklarını ayarla.")

# --- 4) GÖSTER ---
plt.figure(figsize=(10,5))
plt.subplot(1,3,1); plt.title("Mask - Kırmızı"); plt.imshow(mask_red, cmap="gray"); plt.axis("off")
plt.subplot(1,3,2); plt.title("Mask - Mavi");    plt.imshow(mask_blue, cmap="gray"); plt.axis("off")
plt.subplot(1,3,3); plt.title("Sonuç"); 
plt.imshow(cv2.cvtColor(out, cv2.COLOR_BGR2RGB)); plt.axis("off")
plt.tight_layout(); plt.show()