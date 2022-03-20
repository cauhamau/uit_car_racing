import numpy as np
import darknet
import Lane.util as util
import time

class Rule():
    def __init__(self, SetStatusObjs = [], StatusLines = [], StatusBoxes = [], objs_disappear = []):

        self.StatusObjs = SetStatusObjs
        self.StatusLines = StatusLines
        self.objs_disappear = objs_disappear
        self.StatusBoxes = StatusBoxes
        self.tweakAngle = None
        self.speed = None
        self.flag = False
        self.time = 0
        self.point_in_lane = 0
        self.fits = None




    def update(self, SetStatusObjs, StatusLines, StatusBoxes, objs_disappear, point_in_lane, fits):
        self.StatusObjs = SetStatusObjs
        self.StatusLines = StatusLines
        self.StatusBoxes = StatusBoxes
        self.objs_disappear = objs_disappear
        self.point_in_lane = point_in_lane
        self.fits = fits

        

    def get_result(self):
        # print(f'Angel: {self.tweakAngle}')
        # print(f'Speed: {self.speed}')
        return self.tweakAngle, self.speed

    def handle(self):
        
        if self.flag is not False:
            print(self.StatusObjs, self.StatusLines, self.objs_disappear)
            if (all(np.array(self.StatusLines[-3:]) >= 2) and self.time < 10) or self.time <= 0:
                print("stoped flag handle")
                self.flag = False
                self.tweakAngle = None
                self.speed = None

            if self.flag == 'i12':
                if 'i5' in self.StatusObjs[-1]:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    index = list(self.StatusObjs[-1]).index('i5')
                    bbox_i5 = self.StatusBoxes[-1][index]
                    left, top, right, bottom = darknet.bbox2points(bbox_i5)
                    # x_center = int(( left + right ) / 2 / 416 * 512)
                    x_center = int(( left + right ) / 2)
                    # y_center = int(( top + bottom ) / 2 / 416 * 256)
                    if x_center < 150:
                        self.tweakAngle = util.errorAngle((x_center + 100, 128))
                        self.speed = 5
            #self.time -= 1
        
            # if self.flag == 'i10':
            #     if 'i5' in self.StatusObjs[-1]:
            #         print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            #         index = list(self.StatusObjs[-1]).index('i5')
            #         bbox_i5 = self.StatusBoxes[-1][index]
            #         left, top, right, bottom = darknet.bbox2points(bbox_i5)
            #         # x_center = int(( left + right ) / 2 / 416 * 512)
            #         x_center = int(( left + right ) / 2)
            #         # y_center = int(( top + bottom ) / 2 / 416 * 256)
            #         if x_center > 350:
            #             self.tweakAngle = util.errorAngle((x_center + 35, 128))
            #             self.speed = 30
            # self.time -= 1

            if self.flag == 'i13':
                if 'i5' in self.StatusObjs[-1]:
                    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                    index = list(self.StatusObjs[-1]).index('i5')
                    bbox_i5 = self.StatusBoxes[-1][index]
                    left, top, right, bottom = darknet.bbox2points(bbox_i5)
                    # x_center = int(( left + right ) / 2 / 416 * 512)
                    x_center = int(( left + right ) / 2)
                    # y_center = int(( top + bottom ) / 2 / 416 * 256)
                    self.tweakAngle = util.errorAngle((x_center + 80, 128))
                    self.speed = 20
            self.time -= 1
            print("self,time:",self.time)
        else:

            if 'i10' in self.objs_disappear:
                self.handle_i10()
                self.flag = 'i10'
                # if 'i5' in self.StatusObjs[-1]:
                #     index = list(self.StatusObjs[-1]).index('i5')
                #     bbox_i5 = self.StatusBoxes[-1][index]
                #     left, top, right, bottom = darknet.bbox2points(bbox_i5)
                #     x_center = int(( left + right ) / 2 / 416 * 512)
                #     # x_center = int(( left + right ) / 2)
                #     if x_center > 300 and x_center < 512:
                #         self.tweakAngle = util.errorAngle((x_center + 40, 128))
                #         self.speed = 30
                #         self.time = 15
                # else:

                self.tweakAngle = 25
                self.speed = -6
                self.time = 55
                # if 'i5' in self.StatusObjs[-1] or 'pne' in self.StatusObjs[-1]:
                #     self.speed = -10
                #     self.time = 45         
            if 'i12' in self.objs_disappear:
                time.sleep(0.4)
                self.handle_i12()
                self.flag = 'i12'
                print("None")
                # if 'i5' in self.StatusObjs[-1]:
                #     index = list(self.StatusObjs[-1]).index('i5')
                #     bbox_i5 = self.StatusBoxes[-1][index]
                #     left, top, right, bottom = darknet.bbox2points(bbox_i5)
                #     x_center = int(( left + right ) / 2 / 416 * 512)
                #     # x_center = int(( left + right ) / 2)
                #     if x_center > 0 and x_center < 100:
                #         self.tweakAngle = util.errorAngle((x_center + 40, 128))
                #         self.speed = 30
                #         self.time = 15
                #     else:
                #         print('ok')
                #         self.tweakAngle = -25
                #         self.speed = -2
                #         self.time = 15ds
                # else:
                #     self.tweakAngle = -25
                #     self.speed = -2
                #     self.time = 15
                self.tweakAngle = -15
                self.speed = -1
                self.time = 25
                # if 'i5' in self.StatusObjs[-1] or 'pne' in self.StatusObjs[-1]:
                #     print("------pne,i5----")
                #     self.tweakAngle = -20
                #     self.speed = -5
                #     self.time = 30   
            if 'i13' in self.objs_disappear:
                self.handle_i13()
                self.flag = 'i13'
                if 'i5' in self.StatusObjs[-1]:
                    index = list(self.StatusObjs[-1]).index('i5')
                    bbox_i5 = self.StatusBoxes[-1][index]
                    left, top, right, bottom = darknet.bbox2points(bbox_i5)
                    # x_center = int(( left + right ) / 2 / 416 * 512)
                    x_center = int(( left + right ) / 2)
                    if x_center > 200 and x_center < 412:
                        print(x_center)
                        self.tweakAngle = util.errorAngle((x_center + 135, 128))
                        self.speed = -50
                        self.time = 12

                else:
                    self.tweakAngle = 0
                    self.speed = 12
                    self.time = 28



            if 'p19' in self.objs_disappear:
                self.handle_p19()
                self.flag = 'p19'

                if 'i5' in self.StatusObjs[-1]:
                    print("Co i5 2**************")
                    index = list(self.StatusObjs[-1]).index('i5')
                    bbox_i5 = self.StatusBoxes[-1][index]
                    left, top, right, bottom = darknet.bbox2points(bbox_i5)
                    # x_center = int(( left + right ) / 2 / 416 * 512)
                    x_center = int(( left + right ) / 2)
                    if x_center > 400 and x_center < 512:
                        self.tweakAngle = -25
                        self.speed = 30
                        self.time = 20
                    if x_center > 200 and x_center < 400:
                        self.tweakAngle = util.errorAngle((x_center + 35, 128))
                        self.speed = 30
                        self.time = 15
                else:
                    if all(np.array(self.StatusLines[-3:]) < 3):
                        y = 20
                        avaiable_fit =  np.poly1d(self.fits[0])
                        # check where do line?
                        point_x = self.point_in_lane[0]
                        point_y = self.point_in_lane[1]
                        val = point_x - avaiable_fit(point_y)
                        # print(avaiable_fit(point_y))
                        # print(val)
                        
                        print("val:", val)
                        if val <= 225.0: #val < 225 
                            # self.tweakAngle += 10
                            print('---loss left----')
                            self.tweakAngle = -25
                            self.speed = 0
                            self.time = 40
                        else:
                            # self.tweakAngle -= 10
                            print('----Go straight--- ')
                            self.tweakAngle = 0
                            self.speed = 30
                            self.time = 60
                # elif all(np.array(self.StatusLines[-2:]) < 1):
                #     print("TH1----------")
                #     self.tweakAngle = -20
                #     self.speed = -1
                #     self.time = 33
                # else:
                #     print("TH2----------")
                #     self.tweakAngle = -18
                #     self.speed = -5
                #     self.time = 20


                # elif all(np.array(self.StatusLines[-2:]) < 1):
                #     print("TH1----------")
                #     self.tweakAngle = -20
                #     self.speed = -1
                #     self.time = 22
                # else:
                #     print("TH2----------")
                #     self.tweakAngle = -18
                #     self.speed = -5
                #     self.time = 20


            # if 'p14' in self.objs_disappear:
            #     self.handle_p14()
            #     self.flag = 'p14'
            #     if 'i5' in self.StatusObjs[-1]:
            #         index = list(self.StatusObjs[-1]).index('i5')
            #         bbox_i5 = self.StatusBoxes[-1][index]
            #         left, top, right, bottom = darknet.bbox2points(bbox_i5)
            #         # x_center = int(( left + right ) / 2 / 416 * 512)
            #         x_center = int(( left + right ) / 2)
            #         if x_center > 400 and x_center < 512:
            #             print("p14 1-----------")
            #             self.tweakAngle = util.errorAngle((x_center + 30, 128))
            #             self.speed = 30
            #             self.time = 15
            #         elif x_center > 200 and x_center < 300:
            #             print("p14 2-----------")
            #             self.tweakAngle = -20
            #             self.speed = 30
            #             self.time = 40
            #     else:
            #         if all(np.array(self.StatusLines[-3:]) < 3):
            #             y = 20
            #             avaiable_fit =  np.poly1d(self.fits[0])
            #             # check where do line?
            #             point_x = self.point_in_lane[0]
            #             point_y = self.point_in_lane[1]
            #             val = point_x - avaiable_fit(point_y)
            #             # print(avaiable_fit(point_y))
            #             # print(val)

            #             if val < 225.0 :
            #                 print("p14 3-----------")
            #                 self.tweakAngle = 25
            #                 self.speed = -2
            #                 self.time = 20
            #             else:
            #                 print("p14 4-----------")
            #                 self.tweakAngle = -20
            #                 self.speed = -2
            #                 self.time = 40
            #         else:
            #             self.tweakAngle = -20
            #             self.speed = -2
            #             self.time = 40


            if 'p23' in self.objs_disappear:
                self.handle_p23()
                self.flag = 'p23'
                #time.sleep(1)
                if 'i5' in self.StatusObjs[-1]:
                    print('p23 + i5')
                    index = list(self.StatusObjs[-1]).index('i5')
                    bbox_i5 = self.StatusBoxes[-1][index]
                    left, top, right, bottom = darknet.bbox2points(bbox_i5)
                    # x_center = int(( left + right ) / 2 / 416 * 512)
                    x_center = int(( left + right ) / 2)
                    if x_center > 150 and x_center < 462:
                        self.tweakAngle = util.errorAngle((x_center + 100, 128))
                        self.speed = 30
                        self.time = 25
                else:
                    if all(np.array(self.StatusLines[-3:]) < 3):
                        y = 20
                        avaiable_fit =  np.poly1d(self.fits[0])
                        # check where do line?
                        point_x = self.point_in_lane[0]
                        point_y = self.point_in_lane[1]
                        val = point_x - avaiable_fit(point_y)
                        # print(avaiable_fit(point_y))
                        # print(val)
                        
                        print("val:", val)
                        if val >= 225.0: #val < 225 
                            # self.tweakAngle += 10
                            print('---loss right----')
                            self.tweakAngle = 25
                            self.speed = 0
                            self.time = 33
                        else:
                            # self.tweakAngle -= 10
                            print('----Go straight--- ')
                            self.tweakAngle = 0
                            self.speed = 60
                            self.time = 45
                # else:
                #     self.tweakAngle = 25
                #     self.speed = 10
                #     self.time = 25

            if 'p14' in self.objs_disappear:
                # self.handle_p14()
                # self.flag = 'p14'
                # self.speed = 25
                # if 'i5' in self.StatusObjs[-1] or 'pne' in self.StatusObjs[-1]:
                #     print('i5 and pne')
                #     self.tweakAngle = -23
                #     self.speed = 2
                #     self.time = 20
                
                # else :
                #     print('None')
                #     self.tweakAngle = -23
                #     self.speed = 2
                #     self.time = 20
                self.speed = 100
                self.handle_p14()
                self.flag = 'p14'
                # self.time = 5
                #time.sleep(0.5)
                if 'i5' in self.StatusObjs[-1]:
                    print('--i5--')
                    index = list(self.StatusObjs[-1]).index('i5')
                    bbox_i5 = self.StatusBoxes[-1][index]
                    left, top, right, bottom = darknet.bbox2points(bbox_i5)
                    # x_center = int(( left + right ) / 2 / 416 * 512)
                    x_center = int(( left + right ) / 2)
                    if x_center > 400 and x_center < 512:
                        # print('tinhhh')
                        self.tweakAngle = util.errorAngle((x_center + 30, 128))
                        self.speed = 100
                        self.time = 20
                    elif x_center > 200 and x_center < 300:
                        print('i5 and pne')
                        self.tweakAngle = -25
                        self.speed = 100
                        self.time = 20

                elif 'pne' in self.StatusObjs[-1]:
                    print('--pne--')
                    index = list(self.StatusObjs[-1]).index('pne')
                    bbox_i5 = self.StatusBoxes[-1][index]
                    left, top, right, bottom = darknet.bbox2points(bbox_i5)
                    # x_center = int(( left + right ) / 2 / 416 * 512)
                    x_center = int(( left + right ) / 2)
                    if x_center > 400 and x_center < 512:
                        print("Loss right")
                        self.tweakAngle = 25
                        self.speed = 5
                        self.time = 25
                    elif x_center > 200 and x_center < 300:
                        print('loss left')
                        self.tweakAngle = -20
                        self.speed = 30
                        self.time = 20

                else:
                    print('***********')
                    if all(np.array(self.StatusLines[-3:]) < 3):
                        y = 20
                        avaiable_fit =  np.poly1d(self.fits[0])
                        # check where do line?
                        point_x = self.point_in_lane[0]
                        point_y = self.point_in_lane[1]
                        val = point_x - avaiable_fit(point_y)
                        # print(avaiable_fit(point_y))
                        # print(val)
                        
                        print("val:", val)
                        if val > 250.0: #val < 225 
                            # self.tweakAngle += 10
                            print('---loss right----')
                            self.tweakAngle = 25
                            self.speed = 10
                            self.time = 36
                        else:
                            # self.tweakAngle -= 10
                            time.sleep(0.3)
                            print('----loss left--- ')
                            self.tweakAngle = -18
                            self.speed = 50
                            self.time = 35
                    else:
                        print('there')
                        self.tweakAngle = -25
                        self.speed = 10
                        self.time = 20
            if 'other' in self.objs_disappear:
                self.handle_other()
                self.flag = 'other'
                self.speed = 5
                self.tweakAngle = 0
                self.time = 1

            if 'car' in self.objs_disappear:
                print("handle_car")
                self.flag = 'car'
                self.speed = 5
                self.tweakAngle = 0
                self.time = 1
    def handle_i10(self):
        print("handle_i10")
        self.flag = False
        self.tweakAngle = None
        self.speed = None
    
    def handle_i12(self):
        print("handle_i12")
        self.flag = False
        self.tweakAngle = None
        self.speed = None

    def handle_i13(self):
        print("handle_i13")
        self.flag = False
        self.tweakAngle = None
        self.speed = None

    def handle_p19(self):
        print("handle_p19")
        self.flag = False
        self.tweakAngle = None
        self.speed = None

    def handle_p23(self):
        print("handle_p23")
        self.flag = False
        self.tweakAngle = None
        self.speed = None        

    def handle_p14(self):
        print("handle_p14")
        self.flag = False
        self.tweakAngle = None
        self.speed = None
    
    def handle_other(self):
        print("handle_other")
        self.flag = False
        self.tweakAngle = None
        self.speed = None