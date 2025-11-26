import cv2
import numpy as np
import time
prev_time = time.time()  
cap = cv2.VideoCapture(0)

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


while True:
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time
    time.sleep(1)

    ret, frame = cap.read()
    if not ret:
        break
    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
                        
    _, thresh = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY_INV)
    thresh_color = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
    contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(thresh, contours, -1, (0, 255, 0), 1)
    kareler,nesneler,nesnelerkontur = funcKontur(contours,hierarchy)
    buyukalan, enbuyukkontur =funcBuyuklukolc(nesneler,nesnelerkontur)
    if enbuyukkontur == 0:
      sendData = 0
    else:
      sendData = funcFindParent(enbuyukkontur[4],kareler)
    # Görüntüyü göster
    cv2.imshow("Turuncu Tespiti", frame)
    print(sendData)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    cv2.putText(frame, f"FPS: {int(fps)}", (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

# Temizlik
cap.release()
cv2.destroyAllWindows()
