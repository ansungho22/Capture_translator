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



def current_index(): ##변역하고자하는 TEXT 값을 가져오는 함수
    return textbox.index(tk.INSERT) ##Textbox 값 리턴

def fontSizeFunc(*new_var): ##폰트,사이즈 및 텍스트 창 설정 함수
    
    theFont = "Arial %d" % new_var ##theFont 라는 변수에 사용하고자 하는 글씨체 및 크기 설정
    textbox.configure(font=theFont) ## textbox 텍스트창 글씨체는 theFont
    textbox2.configure(font=theFont) ## textbox2 텍스트창 글씨체는 theFont


class ResizingCanvas(Canvas): 
    def __init__(self,parent,**kwargs):
        Canvas.__init__(self,parent,**kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self,event):
        wscale = float(event.width)/self.width
        hscale = float(event.height)/self.height
        self.width = event.width
        self.height = event.height
        self.config(width=self.width, height=self.height)
        self.scale("all",0,0,wscale,hscale)
        fontSizeFunc(self.width/60)


def loadText():  ##텍스트 추가
    global text ##text = 전역변수
    global label ##label = 전역변수
    filename = filedialog.askopenfilename(initialdir="./", title="Select File", filetypes=(("png files", "*.png"), ("all files", "*.*"))) 
    ##이미지 파일을 선택하여 filename에 저장
    text = pytesseract.image_to_string(Image.open(filename)) ##filename에 저장된 이미지 파일 속 텍스트 인식
    textbox.insert("end-1c", text)## textbox에 이미지에서 추출된 문자열 추가
    ##end-1c은 끝에서 한글자 앞을 의미 즉 문자열 끝의 /n을 제거하기 위한것
    translate() ## 번역 함수 실행


def translate(event=""): ## 번역
    global translated_text ##translated_text =  전역변수
    global text
    text = textbox.get(1.0, 'end-1c') ##textbox안에 있는 텍스트 추출하여 text에 저장 
    client_id = "RdBrKuhpxmIinSG4r64S" ##파파고 ID
    client_secret = "KmSlI89ee6" ##파파고 secret key

    input_text = urllib.parse.quote(text) ## papago API를 통해서 번역할 내용
    data = "source=en&target=ko&text=" + input_text ##영어 에서 한국어로 + 번역할 내용
    url = "https://openapi.naver.com/v1/papago/n2mt" ##파파고 관련 함수 및 모듈이 있는 url이라고 예상
    request = urllib.request.Request(url) ## 해당 url request라고 지정
    request.add_header("X-Naver-Client-Id", client_id) ## 파파고 ID 입력
    request.add_header("X-Naver-Client-Secret", client_secret) ## 파파고 secret키 입력
    response = urllib.request.urlopen(request, data=data.encode("utf-8")) ##URL을 열기위한 함수 
    ##데이터를 유니코드 방식으로
    rescode = response.getcode() ## url열기 성공시 response.status = 200 이되는데
    ## 이때의 status의 값을 가져오는 함수
    

    if rescode == 200:#번역 성공시
        response_body = response.read() ## 번역한 내용
        response_body = response_body.decode('utf-8') ## 해독 방식
        data = json.loads(response_body) ## response_body의 내용을 json을통해 data에 저장
        translated_text = data['message']['result']['translatedText'] ## 메세지 >> result >> translatedText 내용

        textbox2.delete(1.0, "end") ## textbox2 초기화
        textbox2.insert("end-1c", translated_text) ## 번역내용을 출력
    else:##에러가 났다면
        print("Error Code:" + rescode) ##에러코드 출력


def mouse_callback(event, x, y, flags, param): ##마우스드래그 함수
    global start_x, start_y,mouse_is_pressing
    global text
    global label
    img_result = param.copy()

    if event == cv2.EVENT_LBUTTONDOWN: ## 마우스 왼쪽 버튼을 눌렀을 때

        mouse_is_pressing = True ##눌려진상태
        start_x, start_y = x, y ##왼쪽 버튼 클릭 위치의 x,y

        cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)  ## 캡쳐 영역 보여주기
        cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
        cv2.imshow("window", img_result)

    elif event == cv2.EVENT_MOUSEMOVE: ## 마우스 움직일 때

        if mouse_is_pressing: ##눌려진상태라면
            cv2.rectangle(img_result, (start_x, start_y), (x, y), (0, 255, 0), 1) ## 마우스가 움직이는만큼 네모를 출력
            cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN)
            cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
            cv2.imshow("window", img_result)

    elif event == cv2.EVENT_LBUTTONUP: ## 마우스 왼쪽 버튼을 눌렀다 땠을때
        
        mouse_is_pressing = False ## 안눌린 상태
        img_capture = param[start_y:y, start_x:x] ## 이미지 속의 선택영역
        cv2.destroyAllWindows() 
        IMG = img_capture.copy()
        img = cv2.cvtColor(IMG, cv2.COLOR_BGR2GRAY) ##이미지를 회색으로 저장
        text = pytesseract.image_to_string(img) ## 이미지속 문자열 추출
        textbox.insert("end-1c", text) ## textbox에 문자열 추가
        translate() ## 번역


def capture(event=""): ##캡처를 위한 함수
    imgGrab = ImageGrab.grab(bbox=(0, 0, 1920, 1080)) ##캡쳐범위를 설정
     ##                        시작x,y  끝x,y
    cv_img = cv2.cvtColor(numpy.array(imgGrab), cv2.COLOR_RGB2BGR) ## cv_img = 바탕화면
   
    cv2.namedWindow("window", cv2.WND_PROP_FULLSCREEN) ## 윈도우의 풀스크린을 window로 저장
    cv2.setWindowProperty("window",cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    ##                     창의이름,    편집할 창 속성,     창 속성의 새로운 값
    cv2.imshow("window", cv_img) ##window라는 이름이으로 cv_img 출력
    cv2.setMouseCallback('window',mouse_callback,param=cv_img) ##지정된 창에 대한 마우스 핸들러를 설정
    ##                    창이름,  마우스함수,    매개변수
    cv2.waitKey(0)  ## 딜레이 0
    cv2.destroyAllWindows() ## 열려있는 모든 highGUI창을 삭제


def refresh(event=""): ##새로고침
    global text
    global translated_text

    textbox.delete("1.0",tk.END) ## textbox 전부 지우기
    textbox2.delete("1.0",tk.END) ## textbox2 전부 지우기
   
    del text ##변수 제거
    del translated_text ##변수 제거
   
root = tk.Tk() ##GUI생성
root.title("번역 프로그램") ##GUI 제목

text = "" ## text = string
translated_text = "" ## translated_text = string

mouse_is_pressing = False ## 마우스 클릭상태
start_x, start_y = -1, -1 ## 변수 초기화

menu = Menu(root) ## 메뉴바

new_item = Menu(menu) ## 메뉴바의 메뉴칸

new_item.add_command(label='이미지 읽기', command=loadText) ## 이름 이미지 읽기 / 클릭시 loadText함수 실행

new_item.add_separator() ## 실선 생성

#---------------------------------------------------------------

new_item.add_command(label='번역', command=translate, accelerator="Ctrl+S") ## 설명 

root.bind_all("<Control - s>", translate) ##단축키 누를시 번역 함수 실행

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
frame = tk.Frame(root, bg="white") ## 프레임생성
frame.place(relwidth=0.9, relheight=0.35, relx=0.05, rely=0.1) ## 프레임크기,위치

textbox = Text(frame) ##프레임 위에 TEXT덮어쓰우기
textbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True) ## side = 정렬방향 / fill = 할당된 공간에 대한 크기 맞춤 /expand = 미사용 공간 확보

#번역된 text창 설정
frame2 = tk.Frame(root, bg="black")
frame2.place(relwidth=0.9, relheight=0.35, relx=0.05, rely=0.5)

textbox2 = Text(frame2)
textbox2.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

#<초기설정>
font_size = tk.IntVar() ##tk에서 사용할 변수타입을 int로 미리 생성
font_size.set(20)
start_index = tk.StringVar() ##tk에서 사용할 변수타입을 string로 미리 생성
current_tag = tk.StringVar() ##tk에서 사용할 변수타입을 string로 미리 생성
start_index.set(current_index()) ##start_index 값을 current_index()값으로 set
current_tag.set("Arial %d" % font_size.get()) ##current_tag에 대한 폰트 설정
root.config(menu=menu) ##GUI에 메뉴 추가
root.mainloop() ##윈도우 내부에서 수행되는 마우스 클릭 같은 이벤트들이 발생하게끔 유지해주는 함수


