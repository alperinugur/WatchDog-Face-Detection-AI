# WatchDog-Face-Detection-AI
This small software uses the webcam on your PC, and looks to identify faces.  

When a face is identified in a frame, the frame will be added to the Video file that the program creates. 
If selected, the WatchDog also sends e-mail of the captured faces.   
There are a lot of variables, which you can change and play under #GLOBAL PARAMETERS 

The XML file "haarcascade_frontalface_alt2.xml" can be found on the OpenCV github page. 

Link: https://github.com/opencv/opencv/tree/4.x/data/haarcascades

You can also find different trained XML files there.

I selected alt2 to avoid most of the false-positice detections.


