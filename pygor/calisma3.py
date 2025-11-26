import cv2
import numpy as np

def funcKontur(contours,hierarchy):
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
    #print(f"{i} konturun noktası:")
    #print(f"{contours[i]}")
      #if h[3] == 0:
        #kare = newHierarchy[0][i]
        #anakareler.append(kare)
      if h[3] > 0:
        data = [i,int(h[0]),int(h[1]),int(h[2]),int(h[3])]
        elemankontur.append(contours[i])
        elemanlar.append(data)
    #print(kareler)
    #print(elemanlar)
    #print(elemankontur)
    return anakareler,elemanlar,elemankontur
      
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
  print("nerden gelin nere giden gara kız")
  lenkareler = len(anakareler)
  for i in range(lenkareler):
    if i == parentKontur:
      print(anakareler[i])

      
orjimg = cv2.imread('medya/bozuk.png')
height, width = orjimg.shape[:2]

scale = .4  # resmi 2 kat büyüt
new_width  = int(width * scale)
new_height = int(height * scale)

img = cv2.resize(orjimg, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

cv2.imshow("gray", gray)

_, thresh = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY_INV)
cv2.imshow("thresh", thresh)
thresh_color = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(thresh_color, contours, -1, (0, 255, 0), 1)
kareler,nesneler,nesnelerkontur = funcKontur(contours,hierarchy)
print(nesneler)
#buyukalan, enbuyukkontur =funcBuyuklukolc(nesneler,nesnelerkontur)
#print(enbuyukkontur)
#funcFindParent(enbuyukkontur[3],kareler)
cv2.imshow("thresh_color", thresh_color)
cv2.waitKey(0)
cv2.destroyAllWindows()