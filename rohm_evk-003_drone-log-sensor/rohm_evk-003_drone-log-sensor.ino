/*****************************************************************************
  RPR-0521RS.ino

 Copyright (c) 2016 ROHM Co.,Ltd.

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 THE SOFTWARE.
******************************************************************************/
/*
 * rohm_evk-003_drone-log-sensor.ino
 * Copyright (c) 2016 ROHM Co.,Ltd.
 * Copyright:K.Nakajima 2020.11.02 
 * License：MIT License
 * Ref:https://www.rohm.co.jp/sensor-shield-support
 */

#include <Wire.h>       //I2C用
#include <FlexiTimer2.h>//タイマ用
#include <stdio.h>      //テキストI/O処理

volatile bool timer_flg;
char str[100];
void timer_isr(void);

// 照度センサ
#include <RPR-0521RS.h>
RPR0521RS rpr0521rs;

// カラーセンサ
#include <BH1749NUC.h>
BH1749NUC bh1749nuc(BH1749NUC_DEVICE_ADDRESS_39);

// 温度センサ
#include <BD1020.h>
int tempout_pin = A0;
BD1020 bd1020;

// 地磁気センサ
#include <BM1422AGMV.h>
BM1422AGMV bm1422agmv(BM1422AGMV_DEVICE_ADDRESS_0E);
void bm1422agmv_isr(void);

// 気圧センサ
#include <BM1383AGLV.h>
BM1383AGLV bm1383aglv;

// 加速度センサ
#include <KX224_I2C.h>
KX224 kx224(KX224_DEVICE_ADDRESS_1E);

void setup() {
  byte rc;
  float acc[3];
  
  timer_flg = false;
  Serial.begin(115200);
  while (!Serial);

  Wire.begin();
  Wire.setClock(400000L);

  rc = bm1383aglv.init();
  bd1020.init(tempout_pin);
  rc = bm1422agmv.init();
  if (rc != 0) {
    Serial.println("bm1422agmv initialize failed");
  } else {
    Serial.flush();
    bm1422agmv.isr_func(0, bm1422agmv_isr);
  }

  rc = kx224.init();
  if (rc != 0) {
    Serial.println(F("KX224 initialization failed"));
    Serial.flush();
  }

  rc = bh1749nuc.init();// カラーセンサ
  rc = rpr0521rs.init();// 照度センサ
  if (rc != 0) {
    //Serial.println("BH1790 initialize failed");
  } else {
    FlexiTimer2::stop();
    FlexiTimer2::set(250, 1.0/8000, timer_isr);  // 32Hz timer
    FlexiTimer2::start();
  }
}

void loop() {
  byte rc;
  unsigned short ps_val;
  float als_val;
  unsigned short rgbc[5];
  float temp;
  float mag[3];
  float acc[3];
  float press = 0, press_temp = 0;
  char alsvalbuf[16];
  char tempbuf[16];
  char mag0buf[16];
  char mag1buf[16];
  char mag2buf[16];
  char pressbuf[16];
  char acc0buf[16];
  char acc1buf[16];
  char acc2buf[16];

  if (timer_flg) {
    rc = rpr0521rs.get_psalsval(&ps_val, &als_val); // 照度センサ
    rc = bh1749nuc.get_val(rgbc); // カラーセンサ (RED)(GREEN)(BLUE)(IR)(GREEN2)
    rc = bm1383aglv.get_val(&press, &press_temp);   // 気圧センサ
    rc = kx224.get_val(acc);      //加速度センサ
    bd1020.get_val(&temp);        // 温度センサ
    rc = bm1422agmv.get_val(mag); // 地磁気センサ
    if (rc == 0) {
      dtostrf(als_val,5,1,alsvalbuf);
      dtostrf(temp,5,1,tempbuf);
      dtostrf(mag[0],5,1,mag0buf);
      dtostrf(mag[1],5,1,mag1buf);
      dtostrf(mag[2],5,1,mag2buf);
      dtostrf(press,5,3 ,pressbuf);
      dtostrf(acc[0],5,1,acc0buf);
      dtostrf(acc[1],5,1,acc1buf);
      dtostrf(acc[2],5,1,acc2buf);
      sprintf(str, "%s,%d,%s,%s,%s,%s,%s,%s,%s,%s,%s,%d,%d,%d,%d,%d\n", alsvalbuf, ps_val, tempbuf, mag0buf, mag1buf, mag2buf, pressbuf, acc0buf, acc1buf, acc2buf, rgbc[0], rgbc[1], rgbc[2], rgbc[3], rgbc[4]);
      Serial.print(str);
    }
    timer_flg = false;
  }
  delay(30);
}

void timer_isr(void) {
  timer_flg = true;
}

void bm1422agmv_isr(void)
{
  bm1422agmv.set_drdy_flg();
}
