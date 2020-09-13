

import tkinter as tk
from tkinter import filedialog, Text, Menu, Canvas
import os
import sys
import json
import urllib.request
from PIL import Image ,ImageGrab
import pytesseract
import numpy
import cv2

root = tk.Tk()
root.title("번역 프로그램")

text = ""
translated_text = ""

mouse_is_pressing = False
start_x, starty = -1, -1

def current_index():
    return textbox.index(tk.INSERT)

def fontSizeFunc(*new_var):
    
    print(current_index())
    
    textbox.tag_add(current_tag.get(), start_index.get(), 1.0)
    textbox.tag_config(current_tag.get(), font=current_tag.get())
    
    textbox2.tag_add(current_tag.get(), start_index.get(), 1.0)
    textbox2.tag_config(current_tag.get(), font=current_tag.get())

    theFont = "Arial %d" % new_var
    textbox.configure(font=theFont)
    textbox2.configure(font=theFont)
    current_tag.set(theFont)

#기본 canvas 설정
class ResizingCanvas(Canvas):
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)
        # rescale all the objects tagged with the "all" tag
        self.scale("all",0,0,wscale,hscale)
        fontSizeFunc(self.width/60)

#이미지읽기
def loadText():
    global text
    global label
    filename = filedialog.askopenfilename(initialdir="./", title="Select File", filetypes=(("png files", "*.png"), ("all files", "*.*")))
    text = pytesseract.image_to_string(Image.open(filename))
    textbox.insert("end-1c", text)
    translate()

#번역
def translate(event=""):
    global text
    global translated_text

    text = textbox.get(1.0, 'end-1c')

    client_id = "RdBrKuhpxmIinSG4r64S"
    client_secret = "KmSlI89ee6"

    input_text = urllib.parse.quote(text)
    data = "source=en&target=ko&text=" + input_text
    url = "https://openapi.naver.com/v1/papago/n2mt"
    request = urllib.request.Request(url)
    request.add_header("X-Naver-Client-Id", client_id)
    request.add_header("X-Naver-Client-Secret", client_secret)
    response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    rescode = response.getcode()
    

    if rescode == 200:
        response_body = response.read()
        response_body = response_body.decode('utf-8')
        data = json.loads(response_body)
        translated_text = data['message']['result']['translatedText']

        textbox2.delete(1.0, "end")
        textbox2.insert("end-1c", translated_text)
    else:
        print("Error Code:" + rescode)

#마우스드래그
def mouse_callback(event, x, y, flags, param):
    global start_x, start_y,mouse_is_pressing
    global text
    global label
    img_result = param.copy()

    if event == cv2.EVENT_LBUTTONDOWN:

        mouse_is_pressing = True
        start_x, start_y = x, y

        cv2.circle(img_result, (x,y), 10, (0, 255, 0), -1)
        cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
        cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("window", img_result)

    elif event == cv2.EVENT_MOUSEMOVE:

        if mouse_is_pressing:
            cv2.rectangle(img_result, (start_x, start_y), (x, y), (0, 255, 0), 1)
            cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
            cv2.imshow("window", img_result)

    elif event == cv2.EVENT_LBUTTONUP:
        
        mouse_is_pressing = False
        img_capture = param[start_y:y, start_x:x]
        cv2.destroyAllWindows()
        IMG = img_capture.copy()
        img = cv2.cvtColor(IMG, cv2.COLOR_BGR2GRAY)
        cv2.imshow("capture", img)
        text = pytesseract.image_to_string(img)
        textbox.insert("end-1c", text)
        translate()

#캡쳐
def capture(event=""):
    imgGrab = ImageGrab.grab(bbox=(0, 0, 1920, 1080))##캡쳐범위 
     ##                        시작x,y  끝x,y
    cv_img = cv2.cvtColor(numpy.array(imgGrab), cv2.COLOR_RGB2BGR)
    
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow("window", cv_img)
    cv2.setMouseCallback('window',mouse_callback,param=cv_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#새로고침
def refresh(event=""):
    global text
    global translated_text

    textbox.delete("1.0",tk.END)
    textbox2.delete("1.0",tk.END)
    del text
    del translated_text
   
menu = Menu(root)

new_item = Menu(menu)

new_item.add_command(label='이미지 읽기', command=loadText)

new_item.add_separator()

#---------------------------------------------------------------

new_item.add_command(label='번역', command=translate, accelerator="Ctrl+S")

root.bind_all("<Control - s>", translate)

new_item.add_separator()

#---------------------------------------------------------------

new_item.add_command(label='이미지 찍기', command=capture, accelerator="Ctrl+Z")

root.bind_all("<Control - z>", capture)

new_item.add_separator()

#---------------------------------------------------------------

new_item.add_command(label='새로고침', command=refresh, accelerator="F5")

root.bind_all("<F5>", refresh)

#---------------------------------------------------------------

menu.add_cascade(label='실행', menu=new_item)

#---------------------------------------------------------------

canvas = ResizingCanvas(root, height=800, width=800, bg="#BAF7B3", highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=tk.YES)

#번역을위한 text창 설정
frame = tk.Frame(root, bg="white")
frame.place(relwidth=0.9, relheight=0.35, relx=0.05, rely=0.1)

textbox = Text(frame)
textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#번역된 text창 설정
frame2 = tk.Frame(root, bg="gray")
frame2.place(relwidth=0.9, relheight=0.35, relx=0.05, rely=0.5)

textbox2 = Text(frame2)
textbox2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#<초기설정>
font_size = tk.IntVar()
font_size.set(20)
start_index = tk.StringVar()
current_tag = tk.StringVar()
start_index.set(current_index())
current_tag.set("Arial %d" % font_size.get())
root.config(menu=menu)
root.mainloop()
