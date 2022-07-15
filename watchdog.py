
#  IMPORTANT: READ BEFORE DOWNLOADING, COPYING, INSTALLING OR USING.
#
#  By downloading, copying, installing or using the software you agree to this license.
#  If you do not agree to this license, do not download, install,
#  copy or use the software.
#
#
#                           License Agreement
#                For Open Source Computer Vision Library
#
# Copyright (C) 2000-2008, Intel Corporation, all rights reserved.
# Copyright (C) 2009-2010, Willow Garage Inc., all rights reserved.
# Third party copyrights are property of their respective owners.
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
#   * Redistribution's of source code must retain the above copyright notice,
#     this list of conditions and the following disclaimer.
#
#   * Redistribution's in binary form must reproduce the above copyright notice,
#     this list of conditions and the following disclaimer in the documentation
#     and/or other materials provided with the distribution.
#
#   * The name of the copyright holders may not be used to endorse or promote products
#     derived from this software without specific prior written permission.
#
# This software is provided by the copyright holders and contributors "as is" and
# any express or implied warranties, including, but not limited to, the implied
# warranties of merchantability and fitness for a particular purpose are disclaimed.
# In no event shall the Intel Corporation or contributors be liable for any direct,
# indirect, incidental, special, exemplary, or consequential damages
# (including, but not limited to, procurement of substitute goods or services;
# loss of use, data, or profits; or business interruption) however caused
# and on any theory of liability, whether in contract, strict liability,
# or tort (including negligence or otherwise) arising in any way out of
# the use of this software, even if advised of the possibility of such damage.
#








from ast import Break
from asyncio.windows_events import NULL
from glob import glob
from operator import ne
from pickle import STOP
from sqlite3 import Time
import sys
from re import X
from tracemalloc import stop
import cv2
from random import randrange
from cv2 import waitKey
from datetime import datetime
from tkinter import *

import smtplib
import imghdr
from email.message import EmailMessage
from email.utils import formataddr


from pyparsing import null_debug_action


# GLOBAL PARAMETERS
XML_File_of_Trained_Data = 'haarcascade_frontalface_alt2.xml'   # alt2 avoids most of the false positives
ShowCaptureWindow = True            # If True, the video window will be displayed on screen

DetectDelay = 1000                  # Once a face is detected, wait this amount of  ms  before going on - 1.000 is advised for 1 seconds
NoDetectDelay = 100                 # If no face is detected, wait this amount of ms ( to save CPU )    - 100 is advised for 0.1 seconds

SaveDetectedFace = True             # If true, the detected faces will be saved in the video file.
SaveAlways = True                   # If true, all captures (including the ones without faces) will be saved in the video file.

OutputFileName = 'watchdog.avi'     # This file will be created in the folder of the running path
OutputFileFPS = 5                   # The Frame per Second of Output file. Make it low to see frame by frame captured faces

SendWarningEmail = False            # If TRUE, a mail will be sent with attachment
MaxAttachedImages = 10              # When Captured Faces reach this number, mail will be sent (if enabled)
SendMailInterval = 3                # If any face is captured, and this interval is reached, the images will be sent by email 
TempJPGFileName = '_temp.JPG'       # Name for the cached image. Keep it short

# Parameters for sending email - THESE NEED TO BE CHANGED IF YOU ARE USING SendWarningEmail = TRUE
Sender_Email = "PUTMAILHERE@YOURDOMAIN.COM"           # Senders E-mail adress
Sender_Name =  "WATCHDOG"               # To see as the senders name
Reciever_Email = "PUTMAILHERE@YOURDOMAIN.COM"    # Receivers E-mail adress
Password = 'PASSWORDHERE'                   # Password to send E-Mail
SMPTServer = 'SMTP.MAILSERVER.COM'              # SMTP Server 

# END OF GLOBAL PARAMETERS




# Startup parameters to run the code
newMessage = NULL 
lasttime = datetime.now()
lastminute = int(lasttime.strftime("%M"))
attachednumber = 0



def SendTheEMail(MailReason):
    global attachednumber
    global newMessage
    
    if attachednumber >0:
        newMessage['Subject'] = MailReason + ' - Files: ' + str(attachednumber)
        with smtplib.SMTP(SMPTServer, 587) as smtp:
            smtp.login(Sender_Email, Password)              
            smtp.send_message(newMessage)             
            smtp.close           
        print("Successfully sent email")
        attachednumber = 0
        newMessage = NULL 
    return(True)

def TimeSpent():
    global lastminute
    global SendMailInterval
    newtime = datetime.now()
    newminute = int(newtime.strftime("%M"))
    tempminute = newminute
    if newminute < SendMailInterval:
        tempminute = newminute + 60
    difference = tempminute - lastminute
    if (difference >= SendMailInterval):
        lastminute = newminute 
        return (True)
    else:
        return (False)

def AddNewAttachment():
    global attachednumber
    global newMessage
    attachednumber=attachednumber+1

    if newMessage == NULL:
        newMessage = EmailMessage()                
        newMessage['From'] = formataddr ((Sender_Name, Sender_Email))
         
        # newMessage['From'] = Sender_Email                   
        newMessage['To'] = Reciever_Email                   
        newMessage.set_content('Files attached') 

    with open(TempJPGFileName, 'rb') as f:
        image_data = f.read()
        #image_type = imghdr.what(f.name)
        image_type = 'jpeg'
        image_name = str(attachednumber) + ".JPG"

    newMessage.add_attachment(image_data, maintype='image', subtype=image_type, filename=image_name)
    print (attachednumber)

    if attachednumber>=MaxAttachedImages:
        SendTheEMail('Watchdog - MAX # images') 
        print ("Max number of JPG attachments reached")


    


running = True  # Global flag
DelayTime = NoDetectDelay
trained_face_data = cv2.CascadeClassifier(cv2.data.haarcascades + XML_File_of_Trained_Data)
webcam = cv2.VideoCapture(0)
if (webcam.isOpened() == False):
    print("Error connecting to WebCam")
frame_width = int(webcam.get(3))
frame_height = int(webcam.get(4))
size = (frame_width, frame_height)

if SaveDetectedFace == True or SaveAlways == True:
    result = cv2.VideoWriter(OutputFileName,
                            cv2.VideoWriter_fourcc(*'MJPG'),
                            OutputFileFPS, size)



def scanning():
    global newMessage
    if running:  # Only do this if the Stop button has not been clicked

        frame_read, frame = webcam.read()

        if frame_read == True:
            global DelayTime
            greyimg = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            facecoords = trained_face_data.detectMultiScale(greyimg)

            detectedface = False
            DelayTime = NoDetectDelay

            mydatetime = datetime.now()
            mywriteDateTime = mydatetime.strftime("%x") + " " +mydatetime.strftime("%X")

            for (x,y,w,h) in facecoords:
                #cv2.rectangle(frame,(x,y),(x+w,y+h),(100+randrange(156),100+randrange(156),100+randrange(156)),2)
                cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
                detectedface = True
                DelayTime=DetectDelay

            cv2.putText(frame, mywriteDateTime, (20, 40), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, mywriteDateTime, (20, 60), cv2.FONT_HERSHEY_PLAIN, 1, (0, 255, 255), 2, cv2.LINE_AA)

            # alttaki satırı kaldırınca, göstermez ama çalışır..
            if ShowCaptureWindow:
                cv2.imshow ('Webcam Face Detector',frame)

            if (detectedface == True & SaveDetectedFace == True) or SaveAlways == True:
                result.write(frame)
            
            if (detectedface == True & SendWarningEmail == True):
                cv2.imwrite(TempJPGFileName, frame)     # save frame as JPEG file   
                AddNewAttachment()
        
        if TimeSpent():
            SendTheEMail('Watchdog - Time Interval')
            print ("Time Interval Reached")



    # After 1 second, call scanning again (create a recursive loop)
    root.after(DelayTime, scanning)

#def start():
    """Enable scanning by setting the global flag to True."""
#    global running
#    running = True

def stop():
    """Stop scanning by setting the global flag to False."""
    global running
    running = False
    root.destroy()

root = Tk()
root.title("WatchDog")
root.geometry("300x100")

app = Frame(root)
app.grid()

# start = Button(app, text="Start Scan", command=start)
stop = Button(app, text="Stop", command=stop)

#start.grid()
#stop.grid()
stop.pack(side=LEFT, padx=100,   pady=30 )
stop.config(height=2, width=12)

root.after(1, scanning)  # After 1 second, call scanning
root.mainloop()

if attachednumber >0:
    SendTheEMail('Watchdog - Code STOPPED')
    print ("Code Stopped. Sent items in cache.")

webcam.release()
print ("Webcam Released")

if SaveDetectedFace == True or SaveAlways == True:
    result.release()
    print ("Result Released")

cv2.destroyAllWindows()

print ("**************")
print ("CODE COMPLETED")
print ("**************")