import cv2
import numpy as np
from scipy.spatial import distance as dist
from imutils import face_utils
import numpy as np
import imutils
import dlib
import cv2
import playsound
import requests


# calculating eye aspect ratio
def eye_aspect_ratio(eye):
    # compute the euclidean distances between the vertical
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # compute the euclidean distance between the horizontal
    C = dist.euclidean(eye[0], eye[3])
    # compute the eye aspect ratio
    ear = (A + B) / (2.0 * C)
    return ear


# calculating mouth aspect ratio
def mouth_aspect_ratio(mou):
    # compute the euclidean distances between the horizontal
    X = dist.euclidean(mou[0], mou[6])
    # compute the euclidean distances between the vertical
    Y1 = dist.euclidean(mou[2], mou[10])
    Y2 = dist.euclidean(mou[4], mou[8])
    # taking average
    Y = (Y1 + Y2) / 2.0
    # compute mouth aspect ratio
    mar = Y / X
    return mar


#Setup classifier

face_cascade=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

eye_cascade=cv2.CascadeClassifier('haarcascade_eye.xml')

phone_cascade=cv2.CascadeClassifier('Phone_Cascade.xml')
phone_usage = 0
                                    
cap=cv2.VideoCapture(0)

#Drowsiness

EYE_AR_THRESH = 0.25
EYE_AR_CONSEC_FRAMES = 50
MOU_AR_THRESH = 0.75

COUNTER = 0
yawnStatus = False
yawns = 0

# the facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("D:\\shape_predictor_68_face_landmarks.dat")

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]
(mStart, mEnd) = face_utils.FACIAL_LANDMARKS_IDXS["mouth"]

while True:
    ret, img=cap.read()
    ret, frame = cap.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    prev_yawn_status = yawnStatus
    rects = detector(gray, 0)

    # loop over the face detections
    for rect in rects:

        shape = predictor(gray, rect)
        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        mouth = shape[mStart:mEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)
        mouEAR = mouth_aspect_ratio(mouth)
        # average the eye aspect ratio together for both eyes
        ear = (leftEAR + rightEAR) / 2.0

        leftEyeHull = cv2.convexHull(leftEye)
        rightEyeHull = cv2.convexHull(rightEye)
        mouthHull = cv2.convexHull(mouth)

        if ear < EYE_AR_THRESH:
            COUNTER += 1
            cv2.putText(img, "Eyes Closed ", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            # if the eyes were closed for a sufficient number of
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                cv2.putText(img, "DROWSINESS ALERT!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                #playsound.playsound('./' + 'alarm1.mp3')



        else:
            COUNTER = 0
            cv2.putText(img, "Eyes Open ", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        # yawning detections

        if mouEAR > MOU_AR_THRESH:
            cv2.putText(img, "Yawning ", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            yawnStatus = True
        # output_text = "Yawn Count: " + str(yawns + 1)
        # cv2.putText(frame, output_text, (10,100),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,0,0),2)
        else:
            yawnStatus = False

        if prev_yawn_status == True and yawnStatus == False:
            yawns += 1
    #cv2.imshow("Frame", frame)
    #key = cv2.waitKey(1) & 0xFF

    #if key == ord("q"):
     #   break

    gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    #Use classifier to detect faces
    faces=face_cascade.detectMultiScale(gray, 1.3, 5)

    phones=phone_cascade.detectMultiScale(gray, 3, 9)
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break


    for (x,y,w,h) in phones:
        cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,255), 2)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img,'Phone',(x-w,y-h), font, 0.5, (11,255,255), 2, cv2.LINE_AA)
        #base_url = "https://api.thingspeak.com/update"

        # Your ThingSpeak API key
        #api_key = "MMAHXEBLUT3RPPTZ"

        # Data value you want to send
        #data_value = 42.0
        phone_usage+=1
        #playsound.playsound('./' + 'beep-09.mp3')


        # Send GET request to ThingSpeak
        #response = requests.get(base_url, params={'api_key': api_key, 'field1': phone_usage})

        # Check if the request was successful
        #if response.status_code == 200:
            #print("Data sent successfully to ThingSpeak!")
            #print(phone_usage)
        #else:
            #print("Failed to send data to ThingSpeak.")

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x,y), (x+w, y+h), (255,0,0), 3)
        roi=img[y:y+h, x:x+w]
        roi_gray=gray[y:y+h, x:x+w]
        eyes=eye_cascade.detectMultiScale(roi_gray)
        #for (ex, ey, ew, eh) in eyes:
            #cv2.rectangle(roi, (ex,ey), (ex+ew, ey+eh), (0,255,0), 2)

    #url = 'https://irdai-server.onrender.com/api/distraction'

    #r = requests.post(url, json={"count":phone_usage})

    #print(r.json())
    cv2.imshow('img', img)
    if (cv2.waitKey(30) & 0xff)==27:
        break


cap.release()
cv2.destroyAllWindows()
