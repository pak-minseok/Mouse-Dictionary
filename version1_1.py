#version 1.1
#2016 08 27

import sys
import PyQt4
from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4.QtCore import QPoint, QRect, QSize, Qt
from PyQt4.QtGui import *
import PIL.ImageGrab
import PIL.ImageTk

from pytesser import *
import urllib
import urllib2
from bs4 import BeautifulSoup
import PIL.Image
import PIL.ImageGrab

from Tkinter import *
import time

#Store position of mouse(x1, y1)
posDictionary1 = []
#Store position of mouse(x2, y2)
posDictionary2 = []

#capture the specific word and save it as jpg
def Capture(x1, y1, x2, y2):
        image = PIL.ImageGrab.grab()
        crop = image.crop((x1,y1,x2,y2))
        crop.save('mcapture.jpg', 'JPEG')

#Extract text from image
def OCR(capture_word):
    im = PIL.Image.open(capture_word)
    text = image_to_string(im)
    return text

#crawl meaning list of the word
def Parse_Naverendic_Section(card):
    resulttext=''
    head = card.find_all('a', attrs={'class': 'h_word'})
    body = card.find_all('ul', attrs={'class': 'desc_lst'})

    if len(head) >= 1:
        resulttext += head[0].get_text(' ', strip=True)
        resulttext += "\n"
    if len(body) >= 1:
        meaninglist = body[0].findAll('li')
        for item in meaninglist:
            resulttext += item.text.strip()
            resulttext += "\n"
    return resulttext

#Access Naver Dictionary
def Get_Result(word):
    url = 'http://m.endic.naver.com/search.nhn?searchOption=entryIdiom&query='+word.encode('utf-8')
    url = urllib.quote(url, '/:?=&')
    resp = urllib2.urlopen(url).read()
    soup = BeautifulSoup(resp, "html.parser")
    target = soup.find_all('div', attrs={'class':'section_card'})
    if len(target) >= 1:
        tmp = ''
        i = 0
        for item in target:
            tmp += Parse_Naverendic_Section(item)
            tmp += '\n'
            i += 1
            if i>=3:
                break
        #print(tmp)
        return tmp
    else:
        tmp = 'No result'
        return tmp
        #print('No result')

def Result_Window():
    word = OCR('mcapture.jpg')
    result = Get_Result(word)

    #The new window shows the result
    root = Tk()
    root.title("Simple Dictionary") 
    root.configure(background = 'white')
    label = Label(root, text = result, font = 'times 15 bold', justify= 'left')
    label.configure(background='white')
    label.pack()

    root.mainloop()
    
#This is First window that user can see.
class Window(QLabel):

    #First of all, user can watch the full screenshot
    def __init__(self, parent = None):
    
        QLabel.__init__(self, parent)
        self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
        self.origin = QPoint()
        
        img = QPixmap.grabWindow(QApplication.desktop().winId())
        self.setPixmap(img)

    #Using Mouse, user can select area of screenshot to choose word(english) for searching.
    # This version cannot support capture of area.
    
    def mousePressEvent(self, event):
    
        if event.button() == Qt.LeftButton:
            self.origin = QPoint(event.pos())
            posDictionary1.append(self.origin.x())
            posDictionary1.append(self.origin.y())
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
    
    def mouseMoveEvent(self, event):
    
        if not self.origin.isNull():
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
    
    def mouseReleaseEvent(self, event):
    
        if event.button() == Qt.LeftButton:
            x = (QPoint(event.pos())).x()
            y = (QPoint(event.pos())).y()

            posDictionary2.append(x)
            posDictionary2.append(y) 
            self.rubberBand.hide()
            self.close()

            Capture(posDictionary1[0],posDictionary1[1],posDictionary2[0],posDictionary2[1])
            Result_Window()
            

if __name__ == "__main__":
        app = QApplication(sys.argv)

        window = Window()
        window.showFullScreen()
        sys.exit(app.exec_())
    
