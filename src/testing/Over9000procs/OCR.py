import os
import cv2
import pytesseract
import string
import time
#preocr = cv2.resize(preocr, (250, 80))
path = r'ramdrive/'
ocrcount = 0
gpscoords = 0.00,0.00

import pigpio


def getgps():
    pi.wave_clear()
    pi.wave_add_serial(TX, 9600, 'tar')
    tarwave = pi.wave_create()
    print("---------------sending GPS request")
    pi.wave_send_once(tarwave)
    rec = 0
    data = ''
    #time.sleep(1)
    pi.bb_serial_read_open(RX, 9600, 8)
    time.sleep(1)
    reqtime = time.time()
    while 1:
        print("---------------waiting for GPS response")
        (rec, data) = pi.bb_serial_read(RX)    
        if rec:
            print("---------------GPS data received")
            pi.bb_serial_read_close(RX)
            return data
        time.sleep(0.5)






while True:
    found = False
    num = 0
    while not found:
        name = r'ocrimg' + str(num) + r'.png'
        found = os.path.exists(os.path.join(path,name))
        #print(os.path.join(path,name))
        num += 1
        if num > 500:
            num = 0

     
    try:
        gpscoords = getgps.decode()
    except:
        gpscoords = 5.00,5.00
                    
    if not gpscoords == (5.00,5.00):
        #print("gps received :)")
        print("---------------GPS: ", gpscoords)
        long,lat = [float(x) for x in gpscoords.split(",")]
    else:
        print("---------------DEFAULTED GPS TO 5.00,5.00")
        long,lat = 5.00,5.00

    preocr = cv2.imread(os.path.join(path,name))
    print("---------------OCR NOW")
    
    try:
        ocr = pytesseract.image_to_data(preocr, lang=None, config="--oem 1 --psm 5", nice=-12,
                                    output_type=pytesseract.Output.DATAFRAME)
    except Exception as e:
        print(e)

    print("---------------OCR FINISHED")
    #    try:
    #        print(ocr)
    #    except Exception as e:
    #        print(e)

    if len(ocr["text"]) == 11:  # only perform OCR if all 4 orientations had an outcome (fix out of range error)

        ocrres = [0, 0, 0, 0]
        ocrres[0] = (ocr["text"][4], ocr["conf"][4])
        ocrres[1] = (ocr["text"][6], ocr["conf"][6])
        ocrres[2] = (ocr["text"][8], ocr["conf"][8])
        ocrres[3] = (ocr["text"][10], ocr["conf"][10])

        textg = ocr["text"][:]
        confg = ocr["conf"][:]
        ocrres.sort(key=lambda tup: tup[1])

    #       try:
    #           print(textg, confg)
    #       except Exception as e:
    #           print(e)

        ocrres = ocrres[3]

        if ocrres[0] in string.ascii_uppercase:
            #letter = ocrres[0]
            #confidence = ocrres[1]
            file = open("log.txt","a")
            file.write(ocrres[0]+","+lat+","+long+"\n")# ocrres[1]))
            file.close()
            print("---------------", ocrres[0])
            ocrcount += 1

    os.remove(os.path.join(path,name))
    if ocrcount >= 3:
        print("---------------OCR SLEEPING")
        file = open("log.txt","a")
        file.write("SLEEP")       
        time.sleep(30)
        print("---------------OCR RESTARTING")
        ocrcount = 0
        files = os.listdir(path)
        for file in files:
            if file.endswith(".png"):
                os.remove(os.path.join(path,file))
        print("---------------OCR READY")
        
