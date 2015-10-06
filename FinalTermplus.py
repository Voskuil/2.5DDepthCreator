# IMPORTS #
import cv2
import numpy as np
from Tkinter import *
import Tkconstants, tkFileDialog
from random import *
import time
import winsound
import tkMessageBox
import tkSimpleDialog

drawing = False
mode = True
ix, iy = -1, -1
edges = None
nuedges = None

def draw(event,x,y,flags,param):
    global drawing, mode, ix, iy, edges, nuedges
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        ix,iy = x,y
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing == True:
            if mode == True:
                cv2.line(edges,(ix,iy),(x,y),(0,0,0),2)
                cv2.line(nuedges,(ix,iy),(x,y),(0,0,0),2)
            else:
                cv2.circle(edges,(x,y),5,(255,255,255),-1)
                cv2.circle(nuedges,(x,y),5,(255,255,255),-1)
            ix, iy = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        if mode == True:
            cv2.line(edges,(ix,iy),(x,y),(0,0,0),2)
            cv2.line(nuedges,(ix,iy),(x,y),(0,0,0),2)

def circleCheck(contours, hierarchy,circleX,circleY):
    for h,cnt in enumerate(contours):
        if cv2.pointPolygonTest(cnt,(circleX,circleY), False) == 1:
            if hierarchy[0,h][2] == -1:
                return h
            else:
                nuH = hierarchy[0,h][2]
                kinderList = []
                passed = True
                if cv2.pointPolygonTest(contours[nuH],(circleX,circleY), False) != 1:
                    kinderList = recursiveNeighborCheck(kinderList,hierarchy,nuH,0)
                    kinderList = recursiveNeighborCheck(kinderList,hierarchy,nuH,1)
                    for kind in kinderList:
                        if cv2.pointPolygonTest(contours[kind],(circleX,circleY), False) == 1:
                            passed = False
                    if passed:
                        return h
    return False
                    
def recursiveNeighborCheck(neighborList,hierarchy,h,step):
    while hierarchy[0,h][step] != -1:
        neighborList += [hierarchy[0,h][step]]
        h = hierarchy[0,h][step]
    return neighborList

class DimensionalEditor(object):
    def __init__(self, width, height, data):
        self.opacity = 0.4
        self.loop = True
        self.width = width
        self.height = height
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.root = Tk()
        self.root.withdraw()

    def timerFired(self, cap, data):
        self.cap = cap
        self.nuData = self.working[0]
        
    def timerFiredWrapper(self,cap, data):
        while self.loop:
            self.key = cv2.waitKey(30)
            self.timerFired(cap, data)
            if not self.working[1]:
                self.nuData = self.working[0]
                self.loop = False
        cv2.destroyAllWindows()
        return self.nuData

    def run(self, cap, data):
        data = self.timerFiredWrapper(cap, data)
        return data
        

class Calibration(DimensionalEditor):
    def __init__(self, width, height, data):
        super(Calibration, self).__init__(width, height,data)
        self.working = [data, True]
        self.timeCount = 1
        self.countdown = False
        self.calibrateCount = 0
        self.isCalibrated = False
        self.cursorRadius = 10
        self.minBlue = 255
        self.maxBlue = 0
        self.minGreen = 255
        self.maxGreen = 0
        self.minRed = 255
        self.maxRed = 0

    def initCalScreen(self):
        if self.calibrateCount == 0:
            cv2.circle(self.oframe, (250,250), self.cursorRadius,
                       (0, 0, 255), thickness=-1)
            self.centX, self.centY = 250, 250
        elif self.calibrateCount == 1:
            cv2.circle(self.oframe, (100,100), self.cursorRadius,
                       (0, 0, 255), thickness=-1)
            self.centX, self.centY = 100, 100
        elif self.calibrateCount == 2:
            cv2.circle(self.oframe, (100,400), self.cursorRadius,
                       (0, 0, 255), thickness=-1)
            self.centX, self.centY = 100, 400
        elif self.calibrateCount == 3:
            cv2.circle(self.oframe, (400,100), self.cursorRadius,
                       (0, 0, 255), thickness=-1)
            self.centX, self.centY = 400, 100
        elif self.calibrateCount == 4:
            cv2.circle(self.oframe, (400,400),self.cursorRadius,
                       (0, 0, 255), thickness=-1)
            self.centX, self.centY = 400, 400
        cv2.addWeighted(self.oframe, self.opacity, self.frame,
                        1 - self.opacity, 0, self.frame)
        cv2.putText(self.frame,'Hello, Welcome to 2.5D Editor',
                    (self.width/16, self.height/16), self.font, 2.25,(255,255,255))
        cv2.putText(self.frame,"Use your webcam and line up an item to use as your cursor within the circle",
                    (self.width/16, (self.height*14)/16), self.font, 0.9,(255,255,255))
        cv2.putText(self.frame,"Press the spacebar to begin calibrating your cursor, and use 'w' and 's' to adjust the cursor size",
                    (self.width/16, (self.height*15)/16), self.font, 0.7,(255,255,255))

    def countdownScreen(self):
        self.currentTime = time.time()
        if self.timeCount - int(round(self.currentTime - self.startTime)) <= 0:
            self.countdown = False
            self.isCalibrated = True
        else:
            cv2.putText(self.frame,
                        str(self.timeCount -
                            int(round(self.currentTime - self.startTime))),
                (250,250), self.font, 1.5,(255,255,255))

    def calibrateCursor(self):
        _, aframe = cap.read()
        (rows, cols, _) = self.oframe[self.centY-self.cursorRadius:self.centY+self.cursorRadius,
                                      self.centX-self.cursorRadius:self.centX+self.cursorRadius].shape
        startY = self.centY-self.cursorRadius
        startX = self.centX-self.cursorRadius
        for row in xrange(startY, startY + rows):
            for col in xrange(startX, startX + cols):
                if (self.oframe[row,col][0] == 0 and
                   self.oframe[row,col][1] == 0 and
                   self.oframe[row,col][2] == 255):
                    if aframe[row,col][2] >= self.maxBlue:
                        self.maxBlue = aframe[row,col][2]
                    if aframe[row,col][2] <= self.minBlue:
                        self.minBlue = aframe[row,col][2]
                    if aframe[row,col][1] >= self.maxGreen:
                        self.maxGreen = aframe[row,col][1]
                    if aframe[row,col][1] <= self.minGreen:
                        self.minGreen = aframe[row,col][1]
                    if aframe[row,col][2] >= self.maxRed:
                        self.maxRed = aframe[row,col][0]
                    if aframe[row,col][2] <= self.minRed:
                        self.minRed = aframe[row,col][0]
        self.low = np.array([min(self.minRed,self.maxRed),
                        min(self.minGreen,self.maxGreen),
                        min(self.minBlue,self.maxBlue)])
        self.high = np.array([max(self.minRed,self.maxRed),
                         max(self.minGreen,self.maxGreen),
                         max(self.minBlue,self.maxBlue)])
        self.isCalibrated = False
        self.calibrateCount += 1

    def finlCalScreen(self):
        _, nuframe = cap.read()
        cv2.putText(self.frame,"Good, you're ready to begin!",
                    (self.width/16, self.height/16), self.font, 2.25,(255,255,255))
        cv2.putText(self.frame,"When you're ready move your cursor to the start button and press the spacebar",
                        (self.width/16, (self.height*15)/16), self.font, 0.8,(255,255,255))
        cv2.rectangle(self.frame,((self.width*3)/8, (self.height*7)/16),
                      ((self.width*5)/8, (self.height*9)/16),(0,0,255),-1)
        cv2.putText(self.frame, "START", ((self.width*3)/8, (self.height*9)/16),
                    self.font,2.5,(255,255,255))
        mask = cv2.bitwise_not(cv2.inRange(nuframe, self.low, self.high))
        kernel = np.ones((5,5),np.uint8)
        opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        nuopening = np.copy(opening)
        contours,hierarchy = cv2.findContours(nuopening,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        max_area = 0
        sizeDict = dict()
        for cnt in contours:
            area = cv2.contourArea(cnt)
            sizeDict[area] = cnt
        try:
            best_cnt = sizeDict[sorted(sizeDict)[-2]]
            # finding centroids of best_cnt and draw a circle there
            M = cv2.moments(best_cnt)
            self.cx,self.cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            cv2.circle(self.frame,(self.cx,self.cy),11,(255,0,0),-1)
        except:
           pass

    def isIn(self,cx,cy,left,top,right,bottom):
        if cx >= left and cx <= right and cy >= top and cy <= bottom:
            self.inside = True
        else:
            self.inside = False

    def timerFired(self,cap, data):
        super(Calibration,self).timerFired(cap,data)
        _,self.frame = self.cap.read()
        _,self.oframe = self.cap.read()
        if not (self.calibrateCount == 5):
            self.initCalScreen()
        else:
            self.finlCalScreen()
        if self.countdown:
            self.countdownScreen()
        if self.isCalibrated:
            self.calibrateCursor()
            
        if self.key == ord('d'):
            self.debugMode = not self.debugMode
        if not (self.calibrateCount == 5) and not self.isCalibrated:
            if self.key == ord(' '):
                self.countdown = True
                self.startTime = time.time()
        elif self.calibrateCount == 5:
            if self.key == ord(' '):
                self.isIn(self.cx,self.cy,200,200,400,400)
                print self.inside
                if self.inside:
                    print "Here"
                    self.working[0] = [self.low, self.high, self.cursorRadius]
                    print self.working
                    self.working[1] = False
        if self.key == ord('w') and self.cursorRadius <= min(self.width/8, self.height/8):
            self.cursorRadius += 1
        if self.key == ord('s')and self.cursorRadius >= 5:
            self.cursorRadius -= 1
        cv2.imshow("video", self.frame)

class Backdrop(DimensionalEditor):
    def __init__(self, width, height, data):
        super(Backdrop, self).__init__(width, height, data)
        self.working = [data, True]
        self.oimg = cv2.imread('c:\Python27\loadingScreen.jpg',1)
        self.opacity = 0.4
        self.uploadTrigd = False
        self.scShotTrigd = False
        self.bckdrpFound = False
        self.oimg = cv2.resize(self.oimg,(self.height, self.width))

    def initCursor(self, image):
        for cnt in self.cursorContours:
            area = cv2.contourArea(cnt)
            self.sizeDict[area] = cnt
        try:
            best_cnt = self.sizeDict[sorted(self.sizeDict)[-2]]
            # finding centroids of best_cnt and draw a circle there
            M = cv2.moments(best_cnt)
            self.cx,self.cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            cv2.circle(image,(self.cx,self.cy),11,(255,0,0),-1)
        except:
            print "woops"

    def isIn(self,cx,cy,left,top,right,bottom):
        if cx >= left and cx <= right and cy >= top and cy <= bottom:
            self.inside = True
        else:
            self.inside = False

    def initWindow(self):
        cv2.putText(self.oimg,'Great! Now to setup a backdrop!',
                    (self.width/32, self.height/16), self.font, 2,(0,0,255))
        cv2.putText(self.oimg,"Either upload an image or take one with your webcam",
                    (self.width/32, (self.height*30)/32), self.font, 1.25,(0,0,255))
        cv2.rectangle(self.oimg,(self.width/8, (self.height*7)/16),
                      ((self.width*3)/8, (self.height*9)/16),(255,0,0),-1)
        cv2.rectangle(self.oimg,((self.width*6)/8, (self.height*7)/16),
                      (self.width,(self.height*9)/16),(0,255,0),-1)
        cv2.putText(self.oimg,'Take Photo',(self.width/8, self.height/2), self.font,
                    1.25,(0,0,255))
        cv2.putText(self.oimg,"Upload",((self.width*6)/8, self.height/2), self.font, 2,
                    (0,0,255))
        self.img = np.copy(self.oimg)
        cv2.imshow('Backdrop Setup', self.img)

    def initbckdrpFired(self):
        _, self.frame = self.cap.read()
        self.mask = cv2.bitwise_not(cv2.inRange(self.frame, self.low, self.high))
        #self.frame = cv2.bitwise_and(self.frame,self.frame, mask= self.mask)
        (self.rows,self.cols) = self.mask.shape
        self.kernel = np.ones((5,5),np.uint8)
        self.opening = cv2.morphologyEx(self.mask, cv2.MORPH_OPEN, self.kernel)
        self.nuopening = np.copy(self.opening)
        self.cursorContours,self.cursorHierarchy = cv2.findContours(
            self.nuopening,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        self.sizeDict = dict()
        self.initCursor(self.oimg)
        if not self.uploadTrigd and not self.scShotTrigd:
            self.initWindow()
        if self.scShotTrigd:
            self.tempFrame = np.copy(self.frame)
            cv2.putText(self.frame,'Press "p" to take a screen shot!',
                        (self.width/32, self.height/16), self.font, 2,(255,255,255))
            cv2.imshow('Screen Shot Setup', self.frame)
        elif self.uploadTrigd:
            filename = tkFileDialog.askopenfilename(parent=self.root, filetypes = [('JPEG', '.jpg')])
            self.oimg = cv2.imread(str(filename),1)
            self.oimg = cv2.resize(self.oimg, (self.cols, self.rows))
            self.bckdrpFound = True
            self.uploadTrigd = False

    def finlbckdrpFired(self):
        self.img = np.copy(self.oimg)
        _, self.frame = self.cap.read()
        self.mask = cv2.bitwise_not(cv2.inRange(self.frame, self.low, self.high))
        self.kernel = np.ones((5,5),np.uint8)
        self.opening = cv2.morphologyEx(self.mask, cv2.MORPH_OPEN, self.kernel)
        self.nuopening = np.copy(self.opening)
        (self.rows, self.cols) = self.mask.shape
        self.img = cv2.resize(self.img, (self.cols,self.rows))
        # find contours in the threshold image
        self.cursorContours,self.cursorHierarchy = cv2.findContours(
            self.nuopening,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        self.sizeDict = dict()
        self.initCursor(self.img)
        cv2.putText(self.img,'Happy with your backdrop? Press the button to continue',
                    (self.width/32, self.height/16), self.font, 1.25,(255,255,255))
        cv2.putText(self.img,"Or press 'u' to undo",
                (self.width/4, (self.height*30)/32), self.font, 2,(255,255,255))
        cv2.rectangle(self.img,((self.width*3)/8, (self.height*7)/16),
                      ((self.width*5)/8, (self.height*9)/16),(0,0,255),-1)
        cv2.putText(self.img, "START", ((self.width*3)/8, (self.height*9)/16),self.font,
                    2.5,(255,255,255))
        cv2.imshow('Backdrop Setup', self.img)
            
    def timerFired(self,cap, clData):
        super(Backdrop,self).timerFired(cap,clData)
        self.low, self.high, self.cursorRadius = clData
        if not self.bckdrpFound:
            self.oimg = cv2.imread('c:\Python27\loadingScreen.jpg',1)
            self.oimg = cv2.resize(self.oimg,(self.height, self.width))
            self.initbckdrpFired()
        else:
            self.finlbckdrpFired()
        
        if self.key == ord(' '):
            self.isIn(self.cx,self.cy,self.width/8,
                         (self.height*7)/16,(self.width*3)/8, (self.height*9)/16)
            if self.inside:
                self.scShotTrigd = True
                self.inside = False
            self.isIn(self.cx,self.cy,(self.width*6)/8,
                        (self.height*7)/16,self.width,(self.height*9)/16)
            if self.inside and not self.scShotTrigd:
                self.uploadTrigd = True
                self.inside = False
        if self.scShotTrigd and self.key == ord('p'):
            self.oimg = self.tempFrame
            self.bckdrpFound = True
            self.scShotTrigd = False
            cv2.destroyWindow('Screen Shot Setup')
        if self.bckdrpFound:
            self.isIn(self.cx,self.cy,(self.width*3)/8,
                    (self.height*7)/16,(self.width*5)/8,
                    (self.height*9)/16)
            if self.key == ord('u'):
                self.bckdrpFound = False
            elif self.key == ord(' ') and self.inside:
                self.working[0] = (self.low, self.high,self.cursorRadius, self.oimg)
                self.working[1] = False
        
class DepthCreator(DimensionalEditor):
    def __init__(self, width, height, data):
        super(DepthCreator, self).__init__(width, height, data)
        global drawing, edges, nuedges, mode, ix, iy
        (self.low, self.high, self.cursorRadius, self.oimg) = data
        self.working = [data, True]
        self.depthDict = dict()
        self.hasContours = False
        self.contourExtremesDict = dict()
        self.colorDict = dict()
        ix, iy = -1, -1
        self.fill = False
        mode = True
        drawing = False
        self.toggle = 1
        self.img = np.copy(self.oimg)
        self.big = cv2.resize(self.img, (500,500))
        self.img = cv2.resize(self.img, (500,400))
        self.floor =  np.array([np.uint8(255),np.uint8(255),np.uint8(255)])
        self.ceiling = np.array([np.uint8(255),np.uint8(255),np.uint8(255)])
        self.white = cv2.bitwise_not(cv2.inRange(self.big, self.floor, self.ceiling))
        self.white = cv2.cvtColor(self.white, cv2.COLOR_GRAY2BGR)
        self.white[0:400,0:500] = self.img
        self.img = self.white
        edges = cv2.Canny(self.img,100,200)
        self.kernel = np.ones((5,5),np.uint8)
        edges = cv2.dilate(edges,self.kernel,iterations = 1)
        edges = cv2.bitwise_not(edges)
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        cv2.rectangle(self.img, (0,400), (125, 500), (0,0,255), -1)
        cv2.rectangle(self.img, (125,400), (250, 500), (255,0,0), -1)
        cv2.rectangle(self.img, (250,400), (375, 500), (0,255,0), -1)
        cv2.rectangle(self.img, (375,400), (500, 500), (255,0,255), -1)
        cv2.putText(self.img,'Toggle Image',(0, 450), self.font, 1,(255,255,255))
        cv2.putText(self.img,'Draw / Erase',(125, 450), self.font, 1,(255,255,255))
        cv2.putText(self.img,'(Click with cursor draw with Mouse)',(125, 470),
                    self.font, 0.4,(255,255,255))
        cv2.putText(self.img,'Create Depth',(250, 450), self.font, 1,(255,255,255))
        cv2.putText(self.img,'   Finish   ',(375, 450), self.font, 1,(255,255,255))
        cv2.rectangle(edges, (0,400), (125, 500), (0,0,255), -1)
        cv2.rectangle(edges, (125,400), (250, 500), (255,0,0), -1)
        cv2.rectangle(edges, (250,400), (375, 500), (0,255,0), -1)
        cv2.rectangle(edges, (375,400), (500, 500), (255,0,255), -1)
        cv2.putText(edges,'Toggle Image',(0, 450), self.font, 1,(255,255,255))
        cv2.putText(edges,'Draw / Erase',(125, 450), self.font, 1,(255,255,255))
        cv2.putText(edges,'(Click with cursor draw with Mouse)',(125, 470),
                    self.font, 0.4,(255,255,255))
        cv2.putText(edges,'Create Depth',(250, 450), self.font, 1,(255,255,255))
        cv2.putText(edges,'   Finish   ',(375, 450), self.font, 1,(255,255,255))
        
        opacity = 0.6
        self.erase = False
        self.draw = False
        self.hasContours = False
        self.cx, self.cy = 0, 0
        self.finished = False
        self.done = False
        tkMessageBox.showinfo("Welcome to 2.5 Editor!",
"""Here we will add depth to your photo!

Use the Toggle Button to toggle between
different images to help you create depth.
(can only edit outline picture)

Press the Draw/Erase Button to draw
or erase edges with your mouse.

Press the Depth Creator Button to
allow yourself to fill in different
regions with a specified depth

And finally when you're finished pressed
the Finish Key to get your Final product""")

    #def draw(self,event,x,y,flags,param):
    #  if event == cv2.EVENT_LBUTTONDOWN:
      #      self.drawing = True
       #     self.ix,self.iy = x,y
        #elif event == cv2.EVENT_MOUSEMOVE:
         #   if self.drawing == True:
          #      if self.mode == True:
           #         cv2.line(self.edges,(self.ix,self.iy),(x,y),(0,0,0),2)
            #        cv2.line(self.nuedges,(self.ix,self.iy),(x,y),(0,0,0),2)
             #   else:
              #      cv2.circle(self.edges,(x,y),5,(255,255,255),-1)
               #     cv2.circle(self.nuedges,(x,y),5,(255,255,255),-1)
                #self.ix, self.iy = x, y
 #       elif event == cv2.EVENT_LBUTTONUP:
  #          self.drawing = False
   #         if mode == True:
    #            cv2.line(self.edges,(self.ix,self.iy),(x,y),(0,0,0),2)
     #           cv2.line(self.nuedges,(self.ix,self.iy),(x,y),(0,0,0),2)
                
    def initCursor(self):
        for cnt in self.cursorContours:
            area = cv2.contourArea(cnt)
            self.sizeDict[area] = cnt
        try:
            best_cnt = self.sizeDict[sorted(self.sizeDict)[-2]]
            # finding centroids of best_cnt and draw a circle there
            M = cv2.moments(best_cnt)
            self.cx,self.cy = int(M['m10']/M['m00']), int(M['m01']/M['m00'])
            cv2.circle(self.nuimg,(self.cx,self.cy),self.cursorRadius,(100,100,100),-1)
            cv2.circle(self.nupeimg,(self.cx,self.cy),self.cursorRadius,(100,100,100),-1)
            cv2.circle(self.flingedges,(self.cx,self.cy),self.cursorRadius,(100,100,100),-1)
        except:
            print "woops"

    def recursiveChildChecker(self,hierarchy, contours, h, x, y):
        if cv2.pointPolygonTest(contours[h],(x,y), False) == 1:
            if hierarchy[0,h][2] == -1:
                return 1
            else:
                return 1 + self.recursiveChildChecker(hierarchy, contours, hierarchy[0,h][2], x, y)
        else:
            if hierarchy[0,h][0] == -1:
                return 0
            else:
                return self.recursiveChildChecker(hierarchy, contours, hierarchy[0,h][0], x, y)

    def finishButton(self):
        reply = tkMessageBox.askyesno("Ready?", "Are you finished with depth creation?")
        if reply:
            self.ROI = edges[0:400, 0:500]
            self.ROI = cv2.cvtColor(self.ROI, cv2.COLOR_BGR2GRAY)
            self.ROI = cv2.resize(self.ROI,(500,500))
            num = 0
            self.ret,self.thresh = cv2.threshold(self.ROI,127,255,0)
            self.contours, self.hierarchy = cv2.findContours(self.thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            for h,cnt in enumerate(self.contours):
                if cv2.contourArea(cnt) >= 20:
                    hasColor = False
                    self.leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
                    self.rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
                    self.topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
                    self.bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])
                    num += 1
                    self.contourExtremesDict[h] = True
                    for x,y in self.depthDict:
                        if cv2.pointPolygonTest(cnt,(x,y), False) == 1:
                            if self.hierarchy[0,h][2] != -1:
                                inside = self.recursiveChildChecker(self.hierarchy,
                                                                    self.contours,h,x,y)
                                if inside == 1:
                                    self.colorDict[h] = self.depthDict[(x,y)]
                                    hasColor = True
                            else:
                                self.colorDict[h] = self.depthDict[(x,y)]
                                hasColor = True
                                                
                    if not hasColor:
                        self.colorDict[h] = False
                else:
                    self.contourExtremesDict[h] = False
            self.hasContours = True
            cv2.destroyAllWindows()

    def initScreen(self):
        if self.toggle % 3 == 1:
            cv2.imshow('Original', self.nupeimg)
            try:
                cv2.destroyWindow("Edge Trace")
            except:
                pass
            try:
                cv2.destroyWindow("Outline")
            except:
                pass
        elif self.toggle % 3 == 2:
            cv2.imshow('Edge Trace', self.flingedges)
            try:
                cv2.destroyWindow("Original")
            except:
                pass
            try:
                cv2.destroyWindow("Outline")
            except:
                pass
        elif self.toggle % 3 == 0:
            cv2.imshow('Outline',self.nuimg)
            try:
                cv2.destroyWindow("Edge Trace")
            except:
                pass
            try:
                cv2.destroyWindow("Original")
            except:
                pass
        cv2.setMouseCallback("Outline",draw)

    def finlScreen(self):
        global drawing, edges, nuedges, mode, ix, iy
        self.eROI = np.copy(self.ROI)
        self.eROI = cv2.cvtColor(self.eROI, cv2.COLOR_GRAY2BGR)
        cv2.putText(self.eROI,"Great! Press the button to edit your 2.5D image!",(0, 50), self.font, 1.5,(255,255,255))
        cv2.rectangle(self.eROI, (200,200), (300, 300), (0,0,255), -1)
        cv2.putText(self.eROI, "Customize", (200,250), self.font, 1, (255,255,255))
        cv2.circle(self.eROI,(self.cx,self.cy),self.cursorRadius,(255,0,0),-1)
        cv2.imshow('edge', self.eROI)
        self.done = True
        self.finished = True

    def fillButton(self):
        isNumber = False
        while not isNumber:
            tempx, tempy = self.cx, self.cy
            distance = tkSimpleDialog.askstring("Depth",
                        "How far is the object? 254 being close, 1 being far away. ")
            try:
                color = int(distance)
                assert(color > 0 and color < 255)
                isNumber = True
            except:
                isNumber = False
                print "Write a number between 1 and 254"
        cv2.circle(self.img,(tempx,tempy),5,(color,color,color),-1)
        self.depthDict[(tempx,tempy)] = color

    def isIn(self,cx,cy,left,top,right,bottom):
        if cx >= left and cx <= right and cy >= top and cy <= bottom:
            return True
        else:
            return False

    def timerFired(self,cap, data):
        global drawing, edges, nuedges, mode, ix, iy
        super(DepthCreator,self).timerFired(cap, data)
        (self.low, self.high, self.cursorRadius, self.oimg) = data
        self.nupeimg = np.copy(self.img)
        self.nuimg = np.copy(self.img)
        self.flingedges = np.copy(edges)
        nuedges = np.copy(edges)
        self.nuimg = cv2.addWeighted(self.nuimg, self.opacity, nuedges,
                                     1 - self.opacity, 0, nuedges)
        _, self.frame = cap.read()
        self.mask = cv2.bitwise_not(cv2.inRange(self.frame, self.low, self.high))
        self.kernel = np.ones((5,5),np.uint8)
        self.opening = cv2.morphologyEx(self.mask, cv2.MORPH_OPEN, self.kernel)
        self.nuopening = np.copy(self.opening)
        self.cursorContours,self.cursorHierarchy = cv2.findContours(
            self.nuopening,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        self.sizeDict = dict()
        self.initCursor()
        
        if self.key == ord(' '):
            if not self.finished:
                if self.isIn(self.cx, self.cy, 125, 400, 250, 500):
                    mode = not mode
                elif self.isIn(self.cx,self.cy,0,400,125,500):
                    self.toggle += 1
                elif self.isIn(self.cx, self.cy, 250, 400, 375, 500):
                    self.fill = not self.fill
                elif self.isIn(self.cx, self.cy, 375, 400, 500, 500):
                    self.finishButton()
                elif self.fill and self.isIn(self.cx,self.cy, 0,0,400,500):
                    self.fillButton()
            if self.done:
                    if self.isIn(self.cx,self.cy, 0,0,400,500):
                        self.working[0] = (self.colorDict, edges, self.depthDict,self.ret,
                                    self.contours, self.hierarchy, self.oimg)
                        self.working[1] = False

        if self.erase:
            if self.isIn(self.cx,self.cy,0,0,500,400):
                cv2.circle(edges,(self.cx,self.cy),5,(255,255,255),-1)
        if self.draw:
            if self.isIn(self.cx,self.cy,0,0,500,400):
                cv2.line(edges,(ix,iy),(self.cx,self.cy),(0,0,0), 2)
        if self.hasContours:
            for h,cnt in enumerate(self.contours):
                if self.contourExtremesDict[h]:
                    conColor = self.colorDict[h]
                    if conColor != False:
                        cv2.drawContours(self.ROI,[cnt],0,(conColor,conColor,conColor),-1)
                        self.hasContours = False
                        self.finished = True
        if self.finished:
            self.finlScreen()
            
        else:
            self.initScreen()
            
def createBlank(fimg):
    ceiling = np.array([255,255,255])
    floor = np.array([255,255,255])
    return cv2.bitwise_not(cv2.inRange(fimg, floor,ceiling))

cap = cv2.VideoCapture(0)
cap.set(3, 500)
cap.set(4, 500)
winsound.PlaySound('C:/Users/Alex/Desktop/18 Besaid 1.wav',
                           winsound.SND_ASYNC)
clData = Calibration(500,500, None).run(cap, None)
bkData = Backdrop(500,500, clData).run(cap, clData)
dpData = DepthCreator(500,500, bkData).run(cap,bkData)

colorDict, edges, depthDict,ret,contours, hierarchy, oimg = dpData

drawing = False
pickedUp = False
aimg = cv2.resize(oimg, (500,500))
fimg = np.copy(aimg)
blank = createBlank(fimg)
(centerLeft,centerRight,centerTop,centerBottom) = (0,0,0,0)
initialDepth = 0
isDrawing = False
pointPicked = False
blankROI =  None
fimgROI = None
cntOI = None
ax = None
ay = None
tkMessageBox.showinfo("Customize Mode",
"""Good! Now You may move images and have it adjust to the image!

Press the 'd' button to toggle between Grab and Draw Mode.

In Draw Mode simply draw around an object and when finished
toggle to Grab Mode to pick up and move your object to the
designated location

If the size is too big an error will pop up explaining the
depth difference will cause the image to be encompassed by
your object.

When You're finished simply press the 's' key to save your new
edited image!
   """)

def draws2(event,x,y,flags,param):
    global ix, iy, isDrawing, eimg, fimg
    if event == cv2.EVENT_LBUTTONDOWN:
        isDrawing = True
        ix,iy = x,y
    elif event == cv2.EVENT_MOUSEMOVE:
        if isDrawing == True:
            cv2.line(fimg,(ix,iy),(x,y),(255,0,0), 2)
            cv2.line(blank,(ix,iy),(x,y),(0,0,0), 2)
            ix, iy = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        cv2.line(fimg,(ix,iy),(x,y),(255,0,0), 2)
        isDrawing = False

def findDepth(x,y):
    for h,cnt in enumerate(contours):
        if cv2.pointPolygonTest(cnt,(x,y), False) == 1 and hierarchy[0,h][2] == -1:
            print "B. No Child"
            return colorDict[h]
        elif cv2.pointPolygonTest(cnt,(x,y), False) == 1 and hierarchy[0,hierarchy[0,h][2]][2] == -1:
            print "C. Found Contour"
            previousList = []
            nextList = []
            previousList = recursiveNeighborCheck(previousList,hierarchy,hierarchy[0,hierarchy[0,h][2]][2],0)
            nextList = recursiveNeighborCheck(nextList,hierarchy,hierarchy[0,hierarchy[0,h][2]][2],1)
            childList = previousList + nextList
            found = h
            print "D.", childList
            for child in childList:
                print "E. Checking chil'n..."
                if cv2.pointPolygonTest(contours[child],(x,y), False) == 1:
                    print "F. Found Child"
                    found = child
            if found == h:
                return colorDict[h]
    print "G. I've made a huge mistake..."
    return None

def pickSpace(event,x,y,flags,param):
    global centerLeft,centerRight,centerTop,centerBottom,initialDepth, pointPicked, blankROI, fimgROI, blank, cntOI, fimg, leftmost, rightmost, topmost, bottommost
    if event == cv2.EVENT_LBUTTONDOWN:
        initialDepth = findDepth(x,y)
        print "A.", initialDepth
        bcontours, bhierarchy = cv2.findContours(blank,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        for h,cnt in enumerate(bcontours):
            if cv2.contourArea(cnt) <= (fimg.size / 2):
                if bhierarchy[0,h][2] == -1:
                    if cv2.pointPolygonTest(cnt,(x,y), False) == 1:
                        pickedUp = True
                        leftmost = tuple(cnt[cnt[:,:,0].argmin()][0])
                        rightmost = tuple(cnt[cnt[:,:,0].argmax()][0])
                        topmost = tuple(cnt[cnt[:,:,1].argmin()][0])
                        bottommost = tuple(cnt[cnt[:,:,1].argmax()][0])
                        print "4.", type(x), type(y), type(int(leftmost[0])), type(int(rightmost[0])), type(int(topmost[1])), type(int(bottommost[1]))
                        print "4.5", x, topmost[1], bottommost[1], y, leftmost[0], rightmost[0]
                        blankROI = blank[topmost[1]:bottommost[1], leftmost[0]:rightmost[0]]
                        fimgOROI = np.copy(fimg[topmost[1]:bottommost[1], leftmost[0]:rightmost[0]])
                        (rows, cols, whatever) = fimg.shape
                        print "6.", cv2.pointPolygonTest(cnt,(x,y), False) != 1
                        for row in xrange(int(topmost[1]), int(bottommost[1]+1)):
                            for col in xrange(int(leftmost[0]), int(rightmost[0]+1)):
                                if cv2.pointPolygonTest(cnt,(col,row), False) != 1:
                                    if row == x and col == y:
                                        print type(x), type(row), cv2.pointPolygonTest(cnt,(x,y), False), cv2.pointPolygonTest(cnt,(row,col), False)
                                    fimg[row,col][0] = 255
                                    fimg[row,col][1] = 255
                                    fimg[row,col][2] = 255
                        fimgROI = np.copy(fimg[topmost[1]:bottommost[1], leftmost[0]:rightmost[0]])
                        fimg[topmost[1]-4:bottommost[1]+4, leftmost[0]-4:rightmost[0]+4] = aimg[topmost[1]-4:bottommost[1]+4, leftmost[0]-4:rightmost[0]+4]
                        centerLeft = x - leftmost[0]
                        centerRight = rightmost[0] - x
                        centerTop = y - topmost[1]
                        centerBottom = bottommost[1] - y
                        print "5.", centerLeft, centerRight, centerTop, centerBottom
                        pointPicked = True
                        cntOI = cnt
                        ax, ay = x, y
    elif event == cv2.EVENT_LBUTTONUP:
        if pointPicked:
            finalDepth = findDepth(x,y)
            zoomFactor = (float(finalDepth) / initialDepth)
            (rows1, cols1, blah) = fimgROI.shape
            (rows2, cols2) = blankROI.shape
            centerLeft = int(zoomFactor*centerLeft)
            centerRight = int(zoomFactor*centerRight)
            centerTop = int(zoomFactor*centerTop)
            centerBottom = int(zoomFactor*centerBottom)
            print "Usefuls", finalDepth, zoomFactor, centerLeft, centerRight, centerBottom, centerTop, x, y
            width = centerLeft + centerRight
            height = centerTop + centerBottom
            fimgROI = cv2.resize(fimgROI, (width, height))
            if y - centerTop < 0:
                top = topmost[1]+abs(y-centerTop)
                fimgROI = fimgROI[top: height, 0: width]
            if x - centerLeft < 0:
                left = leftmost[0]+abs(x-centerLeft)
                fimgROI = fimgROI[0: height, left: width]
            if y + centerBottom > 500:
                bottom = bottommost[1]-((y+centerBottom)-500)
                fimgROI = fimgROI[0: bottom, 0: width]
            if x + centerRight > 500:
                right = rightmost[0]-((x+centerRight)-500)
                fimgROI = fimgROI[0: height, 0: right]
            try:
                fimg[y-centerTop:y+centerBottom, x-centerLeft:x+centerRight] = fimgROI
            except:
                tkMessageBox.showinfo("Error!","Could not move that image!")
            for row in xrange(500):
                for col in xrange(500):
                    if edges[row, col] > finalDepth and edges[row, col] != 255:
                        fimg[row, col][0] = aimg[row,col][0]
                        fimg[row, col][1] = aimg[row,col][1]
                        fimg[row, col][2] = aimg[row,col][2]
                    elif fimg[row, col][0] == 0 and fimg[row, col][1] == 0 and fimg[row, col][2] == 0:
                        fimg[row, col][0] = aimg[row,col][0]
                        fimg[row, col][1] = aimg[row,col][1]
                        fimg[row, col][2] = aimg[row,col][2]
            blank = cv2.bitwise_not(blank)
            pointPicked = False
        else:
            print "Error"
        

drawMode = True
while True:
    key = cv2.waitKey(30) & 0xFF
    cv2.imshow('2.5D Photo', fimg)
    if key == ord('d'):
        drawMode = not drawMode
    elif key == ord('s'):
        reply = tkMessageBox.askyesno("2.5D Message", "Are you done customizing your image?")
        if reply:
            cv2.imswrite("Edited Photo.jpg", fimg)
            tkMessageBox.showinfo("Goodbye!",
"""Your Message has been saved! Come Again!""")
            break
    if drawMode:
        cv2.setMouseCallback('2.5D Photo', draws2)
    else:
        cv2.setMouseCallback('2.5D Photo',pickSpace)

cv2.destroyAllWindows()
