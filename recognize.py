import os
import subprocess as sp
import signal
from subprocess import STDOUT
import face_recognition
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from datetime import datetime, date, time
from threading import Thread
from threading import local
import threading
from queue import Queue
import time

#Resolution here
width = 1280
height = 720
save_interval=5

res=width*height*3
was_load1 = False
was_load2 = False
counter = 0
cld=4

rec_d = [datetime(2018, 7, 11, 20, 0, 0), datetime(2018, 7, 11, 20, 0, 0)]
known_face_names = []
known_face_encoding = []

face_locations = []
face_encodings = []
matches = []
process_this_frame = True

url = 'http://some.vps.myjino.ru/index.php'

opts = FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(firefox_options=opts)
driver.implicitly_wait(200)
addon_path = '/var/pyscript/requests.xpi'
driver.install_addon(addon_path,temporary=True)
driver.get(url)

pipe = []
fmpq = Queue(maxsize=8)
thse = threading.Event()
#iframe = driver.find_elements_by_tag_name('iframe')[0]
#driver.switch_to.frame(iframe)
#btn_play = driver.find_element_by_class_name('iv-splash-screen__content')
#btn_play.click()
ppimg=""
class FFmpeg_th(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        global url
        global ppimg
        global cld
        global thse
        counter=0
        pipe = sp.Popen([ "ffmpeg", "-i", "","-loglevel", "quiet", "-an","-f", "image2pipe","-vcodec", "rawvideo","-r","1", "-"],stdin = sp.PIPE, stdout = sp.PIPE,stderr=STDOUT,preexec_fn=os.setsid)
        while True:
            print("FT:"+str(fmpq.qsize()))
            thse.set()
            pimg = pipe.stdout.read(res)
            if pimg:
                if not fmpq.full():
                    fmpq.put(pimg)
                    '''
                    frame = np.fromstring(pimg, dtype='uint8').reshape((height,width,3))
                    cv2.imwrite("/var/www/html/find_faces/"+str(counter)+"test.jpg",frame)
                    counter+=1
                    '''
                continue
            else:
                cld=4
                if os.path.isfile('/var/www/html/plchng.txt'): 
                    f = open('/var/www/html/plchng.txt','r')
                    urlf = f.readline()
                    f.close()
                    if url != urlf:
                        print(urlf)
                        url = urlf
                        
                        pipe = sp.Popen([ "ffmpeg", "-i", url,"-loglevel", "quiet", "-an","-f", "image2pipe","-pix_fmt", "bgr24","-vcodec", "rawvideo","-r","2", "-"],stdin = sp.PIPE, stdout = sp.PIPE,stderr=STDOUT,preexec_fn=os.setsid)
                        
            time.sleep(1)
thr = FFmpeg_th()
#thr.daemon = True
thr.start()

while True:
    print("MT")
    if os.path.isfile("/var/www/html/phchange.txt"):
        was_load1 = False
        was_load2 = False
        known_face_encoding = []
        known_face_names = []
        os.remove("/var/www/html/phchange.txt")
    if os.path.isfile("/var/www/html/file1.jpg") and was_load1 == False:
        was_load1 = True
        file1 = face_recognition.load_image_file("/var/www/html/file1.jpg")
        #file1 = file1[:, :, ::-1]
        file1_encoding = face_recognition.face_encodings(file1)[0]
        known_face_names.append("1")
        known_face_encoding.append(file1_encoding)
    if os.path.isfile("/var/www/html/file2.jpg") and was_load2 == False:
        was_load2 = True
        file2 = face_recognition.load_image_file("/var/www/html/file2.jpg")
        #file2 = file2[:, :, ::-1]
        file2_encoding = face_recognition.face_encodings(file2)[0]
        known_face_names.append("2")
        known_face_encoding.append(file2_encoding)
    if not was_load1 and not was_load2:
        counter = 0
    if fmpq.empty():
        time.sleep(1)
        if cld==0:
            cld=4
            f = open('/var/www/html/plchng.txt','r')
            urlf = f.readline()
            f.close()
            if url!=urlf:
                processes = map(int,sp.check_output(["pidof","ffmpeg"]).split())
                if processes:
                    for i in range(1):
                        for i in processes:
                            os.kill(int(i),signal.SIGKILL)
        else:
            cld-=1
    else:
        if known_face_names:
            frame = np.fromstring(fmpq.get(), dtype='uint8').reshape((height,width,3))    
            #bgr_frame = frame[:, :, ::-1] #RGB -> BGR
            if process_this_frame:
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)
                if len(known_face_names)==1:
                    for face_encoding in face_encodings:
                        print("1 - find face ")
                        #cv2.imwrite("/var/www/html/find_faces/"+str(counter)+"_fl1.jpg",frame)
                        #counter+=1
                        matches = face_recognition.compare_faces(known_face_encoding, face_encoding)
                        if matches[0] == True:
                            if not os.listdir("/var/www/html/find_faces"):
                                counter = 0
                            if (known_face_names[0]=="1"):
                                if ((datetime.now()-rec_d[0]).seconds > save_interval):
                                    cv2.imwrite("/var/www/html/find_faces/"+str(counter)+"_fl1.jpg",frame)
                                    counter+=1
                                    rec_d[0]=datetime.now();
                            else:
                                if ((datetime.now()-rec_d[1]).seconds > save_interval):
                                    cv2.imwrite("/var/www/html/find_faces/"+str(counter)+".jpg",frame)
                                    counter+=1
                                    rec_d[1]=datetime.now();
                            break
                else:
                    matches = [False, False]
                    for face_encoding in face_encodings:
                        print("2 - find face ")
                        matches = np.logical_or(matches,face_recognition.compare_faces(known_face_encoding, face_encoding))
                        if not (False in matches):
                            break
                    if not os.listdir("/var/www/html/find_faces"):
                        counter = 0
                    if (known_face_names[0]=="1"):
                        if matches[0]:
                            if ((datetime.now()-rec_d[0]).seconds > save_interval):
                                cv2.imwrite("/var/www/html/find_faces/"+str(counter)+"_fl1.jpg",frame)
                                counter+=1
                                rec_d[0]=datetime.now();
                        if matches[1]:
                            if ((datetime.now()-rec_d[1]).seconds > save_interval):
                                cv2.imwrite("/var/www/html/find_faces/"+str(counter)+".jpg",frame)
                                counter+=1
                                rec_d[1]=datetime.now();
                    else:
                        if matches[1]:
                            if ((datetime.now()-rec_d[1]).seconds > save_interval):
                                cv2.imwrite("/var/www/html/find_faces/"+str(counter)+"_fl1.jpg",frame)
                                counter+=1
                                rec_d[1]=datetime.now();
                        if matches[0]:
                            if ((datetime.now()-rec_d[0]).seconds > save_interval):
                                cv2.imwrite("/var/www/html/find_faces/"+str(counter)+".jpg",frame)
                                counter+=1
                                rec_d[0]=datetime.now();
        else:
            fmpq.get()
            time.sleep(1)
        process_this_frame = not process_this_frame
        thse.clear()
        thse.wait(timeout=0.1)