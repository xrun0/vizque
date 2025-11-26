import cv2

# Görüntü oku ve griye çevir
img = cv2.imread('../medya/resim5.png')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

cv2.imshow("gray", gray)
# Binary mask oluştur
_, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
cv2.imshow("thresh", thresh)
contours, hierarchy = cv2.findContours(thresh,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 5. Konturları çiz (kırmızı renk, kalınlık 2)
cv2.drawContours(img, contours, -1, (0, 255, 0), 4)
for i, h in enumerate(hierarchy[0]):
    print(f"Kontur {i}: next={h[0]}, prev={h[1]}, child={h[2]}, parent={h[3]}")

print(f"Bulunan kontur sayısı: {len(contours)}")

cv2.imshow("resim", img)
cv2.waitKey(0)
cv2.destroyAllWindows()
