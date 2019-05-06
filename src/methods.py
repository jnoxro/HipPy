"""
ALL THE METHODS
"""

import cv2
import os

if os.uname()[4][:3] == 'arm':
    from picamera.array import PiRGBArray
    from picamera import PiCamera

import time
import string
import numpy as np
import pytesseract

#pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract"  # My computer needs this ;_;


def setup():
    """ Initial setup """
    camera = PiCamera()
    rawCapture = PiRGBArray(camera)
    time.sleep(0.1)

    grey = np.empty([480, 640])
    image = np.empty([480, 640])
    edged = np.empty([480, 640])


def getimg(camera, rawCapture):
    """ Method to get image size and properties """

    camera.capture(rawCapture, format="bgr", use_video_port=True)

    return rawCapture.array


def getimgwin(camera):
    """ Windows version of getimg """
    return camera.read()




def procimg(image):
    """ procimg does all the image processing required (filters, edges and rotations) """

    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grey scale
    grey = cv2.GaussianBlur(grey, (5, 5), 1)  # Blur image to get rid of some noise (adjust this for less noise)

    edged = cv2.Canny(grey, 0, 150)
    im2, cnts, hierarchy = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:5]

    screenCnt = []
    for c in cnts:
        # approximate the contour
        # Perimeter of the contour, True specifies whether shape is a closed contour (or curve)
        peri = cv2.arcLength(c, True)

        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # print(approx)

        # Compute the bounding box of the contour and use the
        # bounding box to compute the aspect ratio
        # Basically selects the area in question
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h

        area = cv2.contourArea(c)
        hull = cv2.convexHull(c)
        hull_area = cv2.contourArea(hull)

        if hull_area != 0:
            solidity = float(area) / hull_area

            # solidity = float(area) / hull_area

        # print("Solidity:", solidity)
        # print("Area:", area)
        # If there are 4 points, that means that approx detected a quadrilateral
        if len(approx) == 4 and 0.7 <= aspect_ratio <= 1.3 and solidity > 0.8:
            screenCnt = approx

            box2d = cv2.minAreaRect(screenCnt)  # alternative bounding box command, also returns angle
            angle = box2d[2]
            # print(angle)

            rotateRequired = 90 + angle
            break

    preocr = np.zeros((170, 770, 3), np.uint8)  # merge all 4 orientations onto this 1 image for ocr

    if screenCnt != []:
        rop = image[y:y + h, x:x + w]
        cv2.drawContours(image,[screenCnt],-1,(0,255,0),10)
        rop = cv2.resize(rop, (250, 250))
        M = cv2.getRotationMatrix2D((250 / 2, 250 / 2), rotateRequired, 1)
        M2 = cv2.getRotationMatrix2D((250 / 2, 250 / 2), rotateRequired + 90, 1)
        M3 = cv2.getRotationMatrix2D((250 / 2, 250 / 2), rotateRequired + 180, 1)
        M4 = cv2.getRotationMatrix2D((250 / 2, 250 / 2), rotateRequired + 270, 1)
        dst = cv2.warpAffine(rop, M, (250, 250))[40:210, 40:210]
        dst2 = cv2.warpAffine(rop, M2, (250, 250))[40:210, 40:210]
        dst3 = cv2.warpAffine(rop, M3, (250, 250))[40:210, 40:210]
        dst4 = cv2.warpAffine(rop, M4, (250, 250))[40:210, 40:210]

        preocr[0:170, 0:170] = dst
        preocr[0:170, 170:200] = (255, 255, 255)
        preocr[0:170, 200:370] = dst2
        preocr[0:170, 370:400] = (255, 255, 255)
        preocr[0:170, 400:570] = dst3
        preocr[0:170, 570:600] = (255, 255, 255)
        preocr[0:170, 600:770] = dst4

        preocr = cv2.cvtColor(preocr, cv2.COLOR_BGR2GRAY)
        # cv2.imshow("A",preocr)
        ret, preocr = cv2.threshold(preocr, 130, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        return preocr, True, [screenCnt]

    return 0, False, 0


def doocr(preocr):
    """doocr handles the OCR"""

    preocr = cv2.resize(preocr, (68, 15))
    ocr = pytesseract.image_to_data(preocr, lang=None, config="--oem 1 --psm 5", nice=0,
                                    output_type=pytesseract.Output.DATAFRAME)

    try:
        print(ocr)
    except Exception as e:
        print(e)

    if len(ocr["text"]) == 11:  # only perform OCR if all 4 orientations had an outcome (fix out of range error)

        ocrres = [0, 0, 0, 0]
        ocrres[0] = (ocr["text"][4], ocr["conf"][4])
        ocrres[1] = (ocr["text"][6], ocr["conf"][6])
        ocrres[2] = (ocr["text"][8], ocr["conf"][8])
        ocrres[3] = (ocr["text"][10], ocr["conf"][10])

        textg = ocr["text"][:]
        confg = ocr["conf"][:]
        ocrres.sort(key=lambda tup: tup[1])

        try:
            print(textg, confg)
        except Exception as e:
            print(e)

        ocrres = ocrres[3]

        if ocrres[0] in string.ascii_uppercase:
            #letter = ocrres[0]
            #confidence = ocrres[1]

            return  (ocrres[0], ocrres[1])    # todo: actually fix this
        else:
            return (' ',' ')


def outimg(image, preocr, letter=' ', confidence=0):
    """outimg prepares the final output image"""

    composit = np.zeros((1000, 1250, 3), np.uint8)  # final output feed
    preocr = np.expand_dims(preocr,3)
    try:
        composit[0:170, 1080:1250] = preocr[0:170, 0:170]
        composit[170:340, 1080:1250] = preocr[0:170, 200:370]
        composit[340:510, 1080:1250] = preocr[0:170, 400:570]
        composit[510:680, 1080:1250] = preocr[0:170, 600:770]
    except Exception as e:
        # print("Error",e)
        pass
    composit[0:1000, 0:1000] = cv2.resize(image, (1000, 1000))

    composit2 = cv2.resize(composit, (1200, 700))
    cv2.putText(composit2, "Detected:", (970, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(composit2, "Confidence:", (1100, 550), cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)

    cv2.putText(composit2, letter, (975, 630), cv2.FONT_HERSHEY_COMPLEX, 3, (255, 255, 255), 1)
    cv2.putText(composit2, str(confidence), (1100, 610), cv2.FONT_HERSHEY_COMPLEX, 1.5, (255, 255, 255), 1)
    cv2.putText(composit2, "%", (1160, 600), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

    return composit2


def confidence_sort(arr):
    """ Sort array by confidence, remove duplicates and return new array  """

    data = sorted(arr, key = lambda x: x[1], reverse=True)  # Sort by confidence
    
    dupe = set()

    log = []  # array to be returned
    
    for i,j,k,l in data:
        # remove duplicates
        if i not in dupe:
            dupe.add(i)
            log.append((i,j,k,l))

    return log
