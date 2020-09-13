from PIL import Image
from pytesseract import*
import re
import cv2
text = image_to_string('C:\\Users\\O_o\\ansel\\gaga.png')
#원문 페이지에서는 주석 부분을 실행하면 되는데 저는 오류가떠서 현재처럼 실행했습니다
#혹시 괜찮으시다면 주석부분을 해제하시고 위에 text를 주석하고 실행한번 해보셔도 
#좋을꺼같아요
#img = Image.open('C:\\Users\\O_o\\ansel\\gaga.png')
#text = pytesseract.image_to_string(img,lang='euc')
print(text)
