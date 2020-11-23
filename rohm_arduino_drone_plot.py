# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt
import pygame
from pygame.locals import *
import serial
import sys
import math

def main():
    dataReadSouceFlag = False # True:csv File Read False:Serial Rcv
    xscale = 400             # Graph X scale
    
    if(dataReadSouceFlag == False) :
        ser = serial.Serial("COM7", 115200)  # COMポート(Arduino接続)
        ser.flush()


    temps = np.array([0]*xscale)         # 温度格納
    luxs= np.array([0]*xscale)         # 照度センサ
    presss= np.array([0]*xscale)
    magxys= np.array([0]*xscale)
    accxs= np.array([0]*xscale)
    accys= np.array([0]*xscale)
    acczs= np.array([0]*xscale)
    colorRs= np.array([0]*xscale)   
    colorGs= np.array([0]*xscale)
    colorBs= np.array([0]*xscale)
    colorIRs= np.array([0]*xscale)
    
    
    t = np.arange(0,xscale,1)
    plt.ion()
    pygame.init()                # Pygameを初期化

    # print("[*] temps:", temps)
    # print("[*] t:", t)


    """
    rpr0521rs.get_psalsval(&ps_val, &als_val); // 照度センサ ps_val:近接  als_val:照度 Lx
    rc = bh1749nuc.get_val(rgbc);              // カラーセンサ (RED)(GREEN)(BLUE)(IR)(GREEN2)
    bm1383aglv.get_val(&press, &press_temp);   // 気圧センサ
    bd1020.get_val(&temp);	// 温度センサ
    bm1422agmv.get_val(mag);// 地磁気センサ
    kx224.get_val(acc);		// 加速度センサ
    sprintf(str,"%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%d,%d,%d,%d\n", alsvalbuf, ps_val, tempbuf, mag0buf, mag1buf, mag2buf, pressbuf, presstempbuf, acc0buf, acc1buf, acc2buf, rgbc[0], rgbc[1], rgbc[2], rgbc[3], rgbc[4]);
    sprintf(str,"%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%d,%d,%d,%d\n", als_val  , ps_val, tempbuf, mag[x] , mag[y] , mag[z] , pressbuf, presstempbuf, acc[x] , acc[y] , acc[z] , (RED)  , (GREEN), (BLUE) , (IR)   ,(GREEN2));
    """

    # log write csv file
    path = './rohm_sensor_001.csv'
    if(dataReadSouceFlag == False) :
      f = open(path, mode='w')
    else:
      f = open(path, mode='r')

    # 描画領域を取得
    # fig, ax = plt.subplots(1, 1)
    # fig, (ax, circle) = plt.subplots(ncols=2, figsize=(10,4))
    fig, (ax, circle) = plt.subplots(nrows=2, figsize=(80,8))
    
    # 描画領域を取得
    colors = ["red", "green", "blue"]
    if(dataReadSouceFlag == False) :
      f.write("als_val  , ps_val, tempbuf, mag[x] , mag[y] , mag[z] , pressbuf, presstempbuf, acc[x] , acc[y] , acc[z] , (RED)  , (GREEN), (BLUE) , (IR)   ,(GREEN2)\n")
    else:
      stemp = f.readline().rstrip().replace(' ','') # 1行読み飛ばし
      
    while True:
      if(dataReadSouceFlag == False) :
        stemp = ser.readline().rstrip().decode(encoding='utf-8').replace(' ','') # \nまで読み込む
      else:
        stemp = f.readline().rstrip().replace(' ','') # \nまで読み込む
        
      temp = stemp.split(",") #.decode(encoding='utf-8')
      # print("[*] len(temp):",len(temp))
      
      if(len(temp) == 16) :
          print("[*1] temp:", temp)
      else:
          print("[*1] temp:+")
          continue
      
      if(dataReadSouceFlag == False) :
        f.write(stemp)
        f.write("\n")

      #text = font.render(str(float(temp[2])/10) + "[C]", False, (255,255,255))    # 表示する文字の設定
      # センサデータのリスト更新
      luxs   = np.append(float(temp[0])/120*100, luxs)    # 照度
      luxs   = np.delete(luxs, len(luxs) - 1)        
      temps  = np.append(float(temp[7]), temps)           # 気温
      temps  = np.delete(temps, len(temps) - 1)
      presss = np.append((float(temp[6])-1020.63)*100, presss)  # 気圧
      presss = np.delete(presss, len(presss) - 1)
      # magxys = np.append(math.degrees(math.atan2((float(temp[3])+30), (float(temp[4])+20))), magxys)  # 
      magxys = np.append((math.degrees(math.atan2((float(temp[3])+30), (float(temp[4])+20)))/2), magxys)  # 
      magxys = np.delete(magxys, len(magxys) - 1)
      accxs  = np.append(float(temp[8])*50, accxs)
      accxs  = np.delete(accxs, len(accxs) - 1)
      accys  = np.append(float(temp[9])*50, accys)
      accys  = np.delete(accys, len(accys) - 1)
      acczs  = np.append(float(temp[10])*50, acczs)
      acczs  = np.delete(acczs, len(acczs) - 1)
      print("[*1] temp:", temp)

      # グラフ表示設定
      ax.set_title("Temperature")
      ax.set_xlabel("Time [s]")
      ax.set_ylabel("Temperature [C]")
      ax.grid(True)
      ax.set_xlim([1,xscale])
      ax.set_ylim([0,100])

      line1, = ax.plot(t, temps, color='blue')   # 温度更新
      line2, = ax.plot(t, luxs, color='red')   # 照度更新
      line3, = ax.plot(t, presss, color='green') # 気圧更新
      #line4,= ax.plot(t, accxs, color='yellow') # ACC X軸更新
      line5, = ax.plot(t, acczs, color='purple') # ACC Z軸更新
      line6, = ax.plot(t, magxys, color='black') # MAG XYRotate軸更新
      #plt.draw()
      #plt.pause(0.001)

      # 円グラフを描画
      # circle.set_title("Color")
      circle.set_xlabel("Color[RGB Ratio]")

      xData = np.array([int(temp[11]), int(temp[12]), int(temp[13])])
      # circles = circle.pie(xData, labels=colors, autopct='%1.1f%%', shadow=True, colors=colors, startangle=90)
      circles = circle.pie(xData, labels=[" "," "," "], autopct='%1.1f%%', shadow=True, colors=colors, startangle=90)
      circle.axis('equal')  # Equal aspect ratio
      plt.show()

      circles = circle.pie(xData, labels=colors, autopct='%1.1f%%', shadow=True, colors=colors, startangle=90)
      plt.show()
      plt.pause(0.001)

      # グラフをクリア
      line1.remove()
      line2.remove()
      line3.remove()
      #line4.remove()
      line5.remove()
      line6.remove()
      # circles.remove()
      
      for event in pygame.event.get():
      # 終了ボタンが押されたら終了処理
          if event.type == QUIT:
              pygame.quit()
              if(dataReadSouceFlag == False) :
                ser.close()
              plt.close()
              sys.exit()


if __name__ == '__main__':
    main()
