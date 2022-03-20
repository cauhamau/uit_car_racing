"""
- Chương trình đưa cho bạn 1 giá trị đầu vào:
    * image: hình ảnh trả về từ xe

- Bạn phải dựa vào giá trị đầu vào này để tính toán và gán lại góc lái và tốc độ xe vào 2 biến:
    * Biến điều khiển: sendBack_angle, sendBack_Speed
    Trong đó:
        + sendBack_angle (góc điều khiển): [-25, 25]  NOTE: ( âm là góc trái, dương là góc phải)
        + sendBack_Speed (tốc độ điều khiển): [-150, 150] NOTE: (âm là lùi, dương là tiến)
"""

import numpy as np
import socket
import sys   
import cv2
import time
import math

# My import 
from Lane.net import Net
from Lane.parameters import Parameters
from Lane import util
import darknet
from rules import Rule
import copy

import torch

# My setup

net = Net()
p = Parameters()
warning = []
SetStatusObjs = []
StatusLines = []
StatusBoxes = []


#Global variable
MAX_SPEED = 26
MAX_ANGLE = 25
#Tốc độ thời điểm ban đầu
speed_limit = MAX_SPEED
MIN_SPEED = 10

global sendBack_angle, sendBack_Speed, current_speed, current_angle
sendBack_angle = 0
sendBack_Speed = 0
current_speed = 0
current_angle = 0

# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

prevTime = time.time()

def send_control(angle, speed):
    global sendBack_angle, sendBack_Speed
    sendBack_angle = angle
    sendBack_Speed = speed

def control_car():
    global SetStatusObjs
    global StatusLines
    global StatusBoxes
    global flag_stop
    sendBack_angle = 0
    sendBack_Speed = 70
    ru = Rule()
    # try:
    while True:
        message_getState = bytes("0", "utf-8")
        s.sendall(message_getState)
        state_date = s.recv(100)

        try:
            current_speed, current_angle = state_date.decode(
                "utf-8"
                ).split(' ')
        except Exception as er:
            print(er)
            pass    
        current_angle = float(current_angle)
        current_speed = float(current_speed)

        message = bytes(f"1 {sendBack_angle} {sendBack_Speed}", "utf-8")
        s.sendall(message)
        data = s.recv(100000)
        
        # try:
        image = cv2.imdecode(
            np.frombuffer(
                data,
                np.uint8
                ), -1
            )

        # print(current_speed, current_angle)
        # # your process here
        if image is None:
            sendBack_angle = 0
            sendBack_Speed = 50
            continue

        image_resized = cv2.resize(image, (width, height),
                                        interpolation=cv2.INTER_LINEAR)
        darknet.copy_image_from_bytes(darknet_image, image_resized.tobytes())
                
        detections = np.array(darknet.detect_image(yolov4, class_names, darknet_image, thresh=thresh), dtype=object)
            
        image = cv2.resize(image,(512,256))
        x, y = net.predict(image)
        fits = np.array([np.polyfit(_y, _x, 1) for _x, _y in zip(x, y)])
        fits = util.adjust_fits(fits)
        sendBack_angle, checklane = util.get_steer_angle(fits, current_speed)
        sendBack_Speed = util.calcul_speed(sendBack_angle)
        
        try:
                labels = confidences = bboxes = np.array([])
                mask = net.get_mask_lane(fits)
                if len(detections) != 0:
                    sendBack_Speed = -10
                    labels, confidences, bboxes =  detections[:,0], detections[:,1], detections[:,2]
                    print(labels)
                    if 'car' in labels:
                        bbox = bboxes[list(labels).index('car')]
                        left, top, right, bottom = darknet.bbox2points(bbox)
                        center = [int((left + right) // 2), int(((top + bottom) // 2 + 30))]
                        if center[0] > 511:
                            center[0] = 511
                        if center[1] > 255:
                            center[1] = 255

                        #### continue here
                        index = [i for i in range(len(net.colours)) if all(net.colours[i] == mask[center[1], center[0]])]
                        print("index:",index)
                        if index == [1]:
                            fits = fits[:-1]
                            sendBack_angle, checklane = util.get_steer_angle(fits, current_speed)
                            print("car\nangle: ", sendBack_angle)
                        else:
                            pass
                    # if 'p19' in labels and current_angle > 0:
                        
                    #     if sendBack_angle != -25:
                    #         sendBack_angle = -10
                    #     if 'i5' in labels:
                    #         print("Co i5-----------")
                    #         sendBack_angle += 25
                    #         sendBack_Speed = 100
                    #         time.sleep(1)
                    #         continue
                    # if 'p23' in labels and current_angle < 0:
                    #     time.sleep(0.8)
                    #     sendBack_Speed = 25
                    #     if sendBack_angle != 25:
                    #         sendBack_angle = 10
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
                        #print(objs_disappear)    


                # include SetStatusObjs, StatusLines, objs_disappear

                ru.update(SetStatusObjs, StatusLines, StatusBoxes, objs_disappear,p.point_in_lane,fits)
                ru.handle()
                ruAngle, ruSpeed = ru.get_result()
                if ruAngle != None:
                    sendBack_angle = ruAngle
                    sendBack_Speed = ruSpeed
                if 'p19' in labels and current_angle > 0:   
                    if sendBack_angle != -25:
                        sendBack_angle = -10
                    if 'i5' in labels:
                        print("Co i5-----------")
                        sendBack_angle = 0
                        sendBack_Speed = 35
                if 'other' in labels:
                    sendBack_Speed = current_speed
                    sendBack_angle = current_angle
                # if 'p23' in labels and current_angle < 0:
                #     time.sleep(0.8)
                #     sendBack_Speed = 25
                #     if sendBack_angle != 25:
                #         sendBack_angle = 10
        except Exception as error:
            print(error)


        image_point = net.get_image_points()
        cv2.imshow('image point', image_point)
        # print(string)
        net.get_mask_lane(fits)
        image_lane = net.get_image_lane()
        image_lane = darknet.draw_boxes(detections, image_lane, class_colors)
        cv2.imshow("image_lane", image_lane)
        #cv2.imwrite('demo.png', image)
        cv2.waitKey(1)


        print(current_angle,current_speed)
        #print(labels)
        if current_speed > MAX_SPEED:
            sendBack_Speed = 4
        if current_speed <= 10:
            sendBack_Speed = 35
        if current_angle >= 10 and current_speed > 12:
            sendBack_Speed = -2
        if current_angle >= 20 and current_speed > 12:
            sendBack_Speed = -6
        if checklane == -1 and -4 <= current_angle <= 4:
            # time.sleep(0.2)
            if 'i5' in labels:
                time.sleep(0.4)
            else:
                print("checklane==-1 currentangle")
                time.sleep(0.2)
        if checklane == -1 and 'p23' in labels and current_angle <= -5:
            print("checklane==-1 p23 cg <= -5")
            sendBack_angle = 25
            sendBack_Speed = 3
        if checklane == -1 and 'p14' in labels:
            sendBack_angle = -10
        # if (current_angle >= 23 or current_angle <= -23) and labels is None:            
        #     print("90 do")
        #     sendBack_Speed = -20
        #     if current_angle >= 20:
        #         sendBack_angle = 25
        #     else:
        #         sendBack_angle = -25
        # except Exception as er:
        #     print(er)
        #     pass
    # except:
    #     print('Closing socket')
    #     s.close()

if __name__ == '__main__':

    config_file = "./cfg/yolo-tiny-v4-custom.cfg"
    weights = "./models/yolo-tiny-v4-custom_last.weights"
    data_file = "./cfg/tiny-traffic-sign.data"
    
    #-----------------------------------  Setup  ------------------------------------------#
    print('I am loading model right now, pls wait a minute')
    net.load_model(49,"tensor(0.2270)")

    yolov4, class_names, class_colors = darknet.load_network(config_file, data_file, weights, 1)
    width = darknet.network_width(yolov4)
    height = darknet.network_height(yolov4)
    darknet_image =  darknet.make_image(width, height, 3)
    # print(darknet_image)
    thresh = 0.86
    ru = Rule()

    print('Hey Your computer has GPU, right?')

    # Define the port on which you want to connect
    PORT = 54321
    # connect to the server on local computer
    s.connect(('127.0.0.1', PORT))

    control_car()
