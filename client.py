import base64
import numpy as np
import socketio
from PIL import Image
from flask import Flask
from io import BytesIO

# Import socket module
import socket
import cv2
import numpy as np

import copy

import torch
import time

# My import 
from Lane.net import Net
from Lane.parameters import Parameters
from Lane import util
import darknet
from rules import Rule
import copy

import torch
import time

# My setup

net = Net()
p = Parameters()
warning = []
SetStatusObjs = []
StatusLines = []
StatusBoxes = []

#Global variable
MAX_SPEED = 40
MAX_ANGLE = 25
#Tốc độ thời điểm ban đầu
speed_limit = MAX_SPEED
MIN_SPEED = 10



prevTime = time.time()


global sendBack_angle, sendBack_Speed, current_speed, current_angle
sendBack_angle = 0
sendBack_Speed = 0
current_speed = 0
current_angle = 0

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the port on which you want to connect
PORT = 54321
# connect to the server on local computer
config_file = "./cfg/tiny-traffic-sign.cfg"
weights = "./models/tiny-traffic-sign_best.weights"
data_file = "./cfg/tiny-traffic-sign.data"
    
#-----------------------------------  Setup  ------------------------------------------#
print('I am loading model right now, pls wait a minute')
net.load_model(40,"tensor(0.2030)")

yolov4, class_names, class_colors = darknet.load_network(config_file, data_file, weights, 1)
width = darknet.network_width(yolov4)
height = darknet.network_height(yolov4)
darknet_image =  darknet.make_image(width, height, 3)
thresh = 0.9 #0.88
ru = Rule()

print('Hey Your computer has GPU, right?')
s.connect(('127.0.0.1', PORT))

flag_stop = False
def Control(angle, speed):
    global sendBack_angle, sendBack_Speed
    sendBack_angle = angle
    sendBack_Speed = speed


if __name__ == "__main__":     

    try:
        while True:
            message = bytes(f"1 {sendBack_angle} {sendBack_Speed}", "utf-8")
            s.sendall(message)
            data = s.recv(100000)

            try:
                image = cv2.imdecode(
                    np.frombuffer(
                        data,
                        np.uint8
                        ), -1
                    )

                #print(current_speed, current_angle)
                #print(image.shape)

                # your process here
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                image = cv2.resize(image,(512,256))
                #pro_img = cv2.inRange(image, (190,190,190), (255,255,255))
                #cv2.imshow('processed image',image)
                # your process here
                if flag_stop:
                    if speed <= 2:
                        send_control(0,0)
                    else:
                        send_control(0,-150)
                    print("STOP")
                    # if speed == 0:
                        
                else:
                    prevTime = time.time()
                    ###Traffic
                    image_resized = cv2.resize(image, (width, height),
                                            interpolation=cv2.INTER_LINEAR)
                    darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
                    
                    detections = np.array(darknet.detect_image(yolov4, class_names, darknet_image, thresh=thresh), dtype=object)
                    
                    
                    ###Lane 
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    image = cv2.resize(image,(512,256))
                
                    x, y = net.predict(image)
                    # fits = np.array([np.polyfit(_y, _x, 1) if len(_x) < 5  else  np.polyfit(_y, _x, 2) for _x, _y in zip(x, y)])
                    fits = np.array([np.polyfit(_y, _x, 1) for _x, _y in zip(x, y)])
                    
                    fits = util.adjust_fits(fits)
                    
                    StatusLines.append(len(fits))
                    if len(StatusLines) > 8:
                        StatusLines = StatusLines[-8:]
                    

                    mask = net.get_mask_lane(fits)
                    curTime = time.time()
                    # image_lane = net.get_image_points()
                    sendBack_angle = util.get_steer_angle(fits)
                    
                    

                    labels = confidences = bboxes = np.array([])

                    if len(detections) != 0:
                        sendBack_Speed = 0
                        labels, confidences, bboxes =  detections[:,0], detections[:,1], detections[:,2]
                        if 'car' in labels:
                            bbox = bboxes[list(labels).index('car')]
                            left, top, right, bottom = darknet.bbox2points(bbox)
                            center = [int((left + right) // 2 / 224 * image.shape[1]), int(((top + bottom) // 2 + 30) / 224 * image.shape[0])]
                            if center[0] > 511:
                                center[0] = 511
                            if center[1] > 255:
                                center[1] = 255

                            #### continue here
                            index = [i for i in range(len(net.colours)) if all(net.colours[i] == mask[center[1], center[0]])]

                            if index == [1]:
                                fits = fits[:-1]
                                sendBack_angle = util.get_steer_angle(fits)
                            else:
                                pass
                        if 'i10' in labels:
                            sendBack_Speed = -3

                        SetStatusObjs.append(set(labels))
                        StatusBoxes.append(bboxes)
                        
                    else:
                        SetStatusObjs.append(set())
                        StatusBoxes.append([])
                        sendBack_Speed = util.calcul_speed(sendBack_angle)
                    if len(SetStatusObjs) > 6:
                        SetStatusObjs = SetStatusObjs[-6:]
                        StatusBoxes =  StatusBoxes[-6:]
                        # print(SetStatusObjs)

                    t = np.array([ 1 if 'stop' in sobjs else 0 for sobjs in SetStatusObjs ])
                    if len(np.where(t == 1)[0]) > 3:
                        flag_stop = True


                    #get object disappear
                    objs_disappear = []
                    # print(SetStatusObjs)
                    if len(SetStatusObjs) >= 5:
                        temp = [obj.copy() for obj in SetStatusObjs]
                        cleared_StatusObjs = util.clear_StatusObjs(temp)
                        first_labels = cleared_StatusObjs[0]
                        first_sub = first_labels - cleared_StatusObjs[1]
                        # print(first_sub)
                        if len(first_sub) == 0:
                            pass
                        elif all([ first_sub == (first_labels - set_detection) for set_detection in cleared_StatusObjs[2:]]):
                            objs_disappear = first_sub
                            print(objs_disappear)    


                    # include SetStatusObjs, StatusLines, objs_disappear

                    ru.update(SetStatusObjs, StatusLines, StatusBoxes, objs_disappear)
                    ru.handle()
                    ruAngle, ruSpeed = ru.get_result()
                    
                    if ruAngle != None:
                        sendBack_angle = ruAngle
                        sendBack_Speed = ruSpeed


                    sec = curTime - prevTime
                    fps = 1/(sec)
                    s = "FPS : "+ str(fps)
                    # print(s)
                    #image_lane = net.get_image_lane()
                    #image_lane = darknet.draw_boxes(detections, image_lane, class_colors)
                    # cv2.putText(image_lane, s, (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0))
                    #cv2.imshow("image", image_lane)
                    #cv2.waitKey(1)

                    
                    #------------------------------------------------------------------------------------------------------#
                    # print('{} : {}'.format(sendBack_angle, sendBack_Speed))
                    if speed > MAX_SPEED:
                        sendBack_Speed = 5
                    if speed < 10:
                        sendBack_Speed = 100
                cv2.waitKey(1)

            except Exception as er:
                print(er)
                pass

    finally:
        print('closing socket')
        s.close()