# -*- coding: utf-8 -*-

import machine
import network
import time
import os

#- check ap config file
AP_SSID = 'upy'
AP_PWD = 'pypypypy'
ap_config = None
ap_config_fn = 'ap.txt'
if ap_config_fn in os.listdir():
    print('ap config here!')
    f = open(ap_config_fn)
    ap_config = f.read()
    f.close()
if ap_config:
    print( ('ap_config:', ap_config))
    ap_config = ap_config.split('\n')
    AP_SSID = ap_config[0].strip()
    AP_PWD = ap_config[1].strip()
print('line to: ', (AP_SSID, AP_PWD))

#-- 連到AP 為Station
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect(AP_SSID, AP_PWD)
sta_if.isconnected()
for i in range(20):
    time.sleep(0.5)
    if sta_if.isconnected():
        break
sta_ip = ''
if sta_if.isconnected():
    print('connected!  --> ', sta_if.ifconfig())
    sta_ip = sta_if.ifconfig()[0]
else:
    print('not connected!  --> ', sta_if.ifconfig())

#-- 當AP，並指定
uid = machine.unique_id()
#ap_if.ifconfig()
# ('192.168.4.1', '255.255.255.0', '192.168.4.1', '192.168.43.1')
# (ip, mask, gateway, dns)
my_sn = '%02X%02X' %(uid[0], uid[1])

#- Change name/password/ip of ESP8266's AP:
ap_if = network.WLAN(network.AP_IF)
#ap_if.ifconfig([my_ip, my_mask, my_gw, my_dns])

my_ssid = 'upy_%s_%s' %(my_sn, sta_ip)
#ap_if.config(essid = my_ssid)#改ssid，馬上生效
ap_if.config(essid=my_ssid, authmode=network.AUTH_WPA_WPA2_PSK, password="12345678")
#DHCP 功能micropython預設就有，不用設定
#AP的IP，每次重開都會回到預設值，因此需要開機時就設定
#一般是配給AP ip的下一號ip


import socket
from machine import Pin
from machine import PWM
import dht

# PIN Define:
D0 = 16
D1 = 5  #PWM
D2 = 4  #PWM
D3 = 0  #PWM
D4 = 2  #PWM, #Led on board
D5 = 14 #PWM
D6 = 12 #PWM
D7 = 13 #PWM
D8 = 15 #PWM

#Setup PINS
led = Pin(D4, Pin.OUT)
led.value(0)
for i in range(6):
    led.value(not led.value())
    time.sleep(0.2)
    
# ir
IrR = Pin(D5, Pin.IN) #Right
IrL = Pin(D6, Pin.IN) #Left
#IrM = Pin(D7, Pin.IN) #Middle

# for motor sheilf
motor_a1 = machine.Pin(D1, machine.Pin.OUT) #A-, speed
motor_a2 = machine.Pin(D3, machine.Pin.OUT) #A+, dir
motor_b1 = machine.Pin(D2, machine.Pin.OUT) #B-, speed
motor_b2 = machine.Pin(D4, machine.Pin.OUT) #B+, dir
FWD = 0
REV = 1
    
def car_fwd():
    motor_a1.value(1)    #l
    motor_a2.value(FWD)
    motor_b1.value(1)    #r
    motor_b2.value(FWD)

def car_rev():
    motor_a1.value(1)    #l
    motor_a2.value(REV)
    motor_b1.value(1)    #r
    motor_b2.value(REV)

def car_stop():
    motor_a1.value(0)    #l
    motor_a2.value(FWD)
    motor_b1.value(0)    #r
    motor_b2.value(FWD)

def car_right():
    motor_a1.value(1)     #l
    motor_a2.value(FWD)
    motor_b1.value(0)     #r
    motor_b2.value(FWD)

def car_left():
    motor_a1.value(0)     #l
    motor_a2.value(FWD)
    motor_b1.value(1)     #r
    motor_b2.value(FWD)

# 快速右轉
def car_right2():
    motor_a1.value(1)    #l
    motor_a2.value(FWD)
    motor_b1.value(1)    #r
    motor_b2.value(REV)    

# 快速左轉
def car_left2():
    motor_a1.value(1)    #l
    motor_a2.value(REV)
    motor_b1.value(1)    #r
    motor_b2.value(FWD)


#Setup Socket WebServer
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 80))
s.listen(5)
while True:
    conn, addr = s.accept()
    print("Got a connection from %s" % str(addr))
    request = conn.recv(1024)
    print("Content = %s" % str(request))

    request = str(request)
    led_on = request.find('GET /?LED=ON')
    led_off = request.find('GET /?LED=OFF')
    car_fwd_action = request.find('GET /?car=FWD')
    car_rev_action = request.find('GET /?car=REV')
    car_left_action = request.find('GET /?car=LEFT')
    car_right_action = request.find('GET /?car=RIGHT')


    if led_on >= 0:
        print('TURN Led ON')
        led.value(0)
    if led_off >= 0:
        print('TURN Led OFF')
        led.value(1)

    if car_fwd_action >= 0:
        print('Car Forward')
        car_fwd()
        time.sleep(1)
        car_stop()
    if car_rev_action >= 0:
        print('Car Back')
        car_rev()
        time.sleep(1)
        car_stop()
    if car_left_action >= 0:
        print('Car Left')
        car_left()
        time.sleep(1)
        car_stop()
    if car_right_action >= 0:
        print('Car Right')
        car_right()
        time.sleep(1)
        car_stop()

    f = open('webtool.html')

    while(1):
        html = f.read(1024)

        conn.sendall(html) #改用send all就不會有資料傳一半的問題
        if(len(html)<=0):
            break
    f.close()
    conn.close()
