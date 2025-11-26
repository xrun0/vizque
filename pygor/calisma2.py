import cv2
import numpy as np
import traceback


def funcKontur(contours,hierarchy):
  try:
    if len(contours) < 9 :
      return 0
    else:
      anakareler = []
      elemanlar = []
      elemankontur = []
      newHierarchy = list(hierarchy)
      for i, h in enumerate(newHierarchy[0]):
        #print(f"Kontur {i}: next={h[0]}, prev={h[1]}, child={h[2]}, parent={h[3]}---------")#{contours[i]}
        data = [i,int(h[0]),int(h[1]),int(h[2]),int(h[3])]
        anakareler.append(data)
        if h[3] > 0:
          data = [i,int(h[0]),int(h[1]),int(h[2]),int(h[3])]
          elemanlar.append(data)
          elemankontur.append(contours[i])
      return anakareler,elemanlar,elemankontur
  except:
    print("Bir hata oluştu FuncKontur")
      
def funcBuyuklukolc(elemanlar,elemankontur):
  #print(elemankontur)
  buyukalan=0
  enbuyukkontur = 0
  sayac = 0
  for i in elemankontur:
    alan = cv2.contourArea(i)
    if buyukalan < alan:
      buyukalan = alan
      enbuyukkontur = elemanlar[sayac]
    sayac+=1
  return buyukalan, enbuyukkontur

def funcFindParent(parentKontur,anakareler):
  matris = 0
  for i in anakareler:
    if i[0] == parentKontur:
      #print(parentKontur)
      matris = 8-i[2]
  return matris

      
try:
  orjimg = cv2.imread('medya/w5.jpeg')
  height, width = orjimg.shape[:2]

  scale = 3
  new_width  = int(width * scale)
  new_height = int(height * scale)

  img = cv2.resize(orjimg, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

  gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

  cv2.imshow("gray", gray)
  blur = cv2.GaussianBlur(gray, (5,5), 0) # ortalama
  blur2 = cv2.medianBlur(blur, 7) # tuz biber ortanca
  blur3 = cv2.bilateralFilter(blur2, d=7, sigmaColor=75, sigmaSpace=75)
  #blur = gray
  _, thresh = cv2.threshold(blur3, 185, 255, cv2.THRESH_BINARY_INV)
  cv2.imshow("thresh", thresh)
  thresh_color = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
  contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
  for cnt in contours:
    area = cv2.contourArea(cnt)  # konturun alanı (piksel cinsinden)

    if 10000 < area < 1000000:  # 500 pikselden büyük olanları çiz
        print("ciz")
        cv2.drawContours(thresh_color, [cnt], -1, (0, 255, 0), 8)

  #cv2.drawContours(thresh_color, contours, -1, (0, 255, 0), 8)

  kareler,nesneler,nesnelerkontur = funcKontur(contours,hierarchy)
  buyukalan, enbuyukkontur =funcBuyuklukolc(nesneler,nesnelerkontur)
  if enbuyukkontur == 0:
    sendData = 0
  else:
    sendData = funcFindParent(enbuyukkontur[4],kareler)

  print(sendData)
  cv2.imshow("thresh_color", thresh_color)
  cv2.waitKey(0)
  cv2.destroyAllWindows()
except Exception as e:
    print("=== Hata Detayı ===")
    print(f"Tip: {type(e).__name__}")
    print(f"Mesaj: {e}")
    print("Traceback:")
    traceback.print_exc()
    with open("error_log.txt", "a") as f:
      f.write("Hata:" + "\n")
