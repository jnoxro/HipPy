import os
import cv2
import pytesseract
import string
import time
#preocr = cv2.resize(preocr, (250, 80))
path = r'ramdrive/'
ocrcount = 0

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
    
    preocr = cv2.imread(os.path.join(path,name))
    print("OCR NOWWWWWWWWW",preocr)
    
    try:
        ocr = pytesseract.image_to_data(preocr, lang=None, config="--oem 1 --psm 5", nice=-12,
                                    output_type=pytesseract.Output.DATAFRAME)
    except Exception as e:
        print(e)

    print("OCR FINISHED")
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
            file.write(ocrres[0]+"\n")# ocrres[1]))
            file.close()
            print(ocrres[0])
            ocrcount += 1

    os.remove(os.path.join(path,name))
    if ocrcount >= 3:
        print("OCR SLEEPPPPING")
        file = open("log.txt","a")
        file.write("SLEEP")       
        time.sleep(30)
        print("AWOKE")
        ocrcount = 0
        files = os.listdir(path)
        for file in files:
            if file.endswith(".png"):
                os.remove(os.path.join(path,file))
        print("LMAO I DIDNT CRASH YOURE JUST RETARDED")
