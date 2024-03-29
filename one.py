import tkinter
import cv2
import time
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import pairwise

def capture():
    num=0
    cap=cv2.VideoCapture(0)
    i=0
    _,frame=cap.read()
    back=None
    roi=cv2.selectROI(frame)
    (x,y,w,h)=tuple(map(int,roi))
    while True:
        _,frame=cap.read()
        if i<50:
            i+=1
            if back is None:
                back=frame[y:y+h,x:x+w].copy()
                back=np.float32(back)
            else:            
                cv2.accumulateWeighted(frame[y:y+h,x:x+w].copy(),back,0.2)
        else:
                    #print(back.shape,frame.shape)
            back=cv2.convertScaleAbs(back)
            back_gray=cv2.cvtColor(back,cv2.COLOR_BGR2GRAY)
            frame_gray=cv2.cvtColor(frame[y:y+h,x:x+w],cv2.COLOR_BGR2GRAY)
                    
            img=cv2.absdiff(back_gray,frame_gray)
            _,img=cv2.threshold(img,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            con,hie=cv2.findContours(img,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            img2=img.copy()        
            con=max(con,key=cv2.contourArea)
            conv_hull=cv2.convexHull(con)
            cv2.drawContours(img,[conv_hull],-1,225,3)    
                    
            top=tuple(conv_hull[conv_hull[:,:,1].argmin()][0])
            bottom=tuple(conv_hull[conv_hull[:,:,1].argmax()][0])
            left=tuple(conv_hull[conv_hull[:,:,0].argmin()][0])
            right=tuple(conv_hull[conv_hull[:,:,0].argmax()][0])
            cx=(left[0]+right[0])//2
            cy=(top[1]+bottom[1])//2

            dist=pairwise.euclidean_distances([left,right,bottom,top],[[cx,cy]])[0]
            radi=int(0.80*dist)
                    
            circular_roi=np.zeros_like(img,dtype='uint8')
            cv2.circle(circular_roi,(cx,cy),radi,255,8)
            wighted=cv2.addWeighted(img.copy(),0.6,circular_roi,0.4,2)

            mask=cv2.bitwise_and(img2,img2,mask=circular_roi)
                    #mask
            con,hie=cv2.findContours(mask.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
                    
            circumfrence=2*np.pi*radi
            count = 0
            for cnt in con:
                (m_x,m_y,m_w,m_h)=cv2.boundingRect(cnt)
                out_wrist_range=(cy+(cy*0.25))>(m_y+m_h)
                limit_pts=(circumfrence*0.25)>cnt.shape[0]
                if limit_pts and out_wrist_range:
                            #print(limit_pts,out_wrist_range)
                    count+=1



            cv2.putText(frame,'count: '+str(count),(460,70),cv2.FONT_HERSHEY_SIMPLEX ,1,(0,250,0),thickness=4)
            cv2.rectangle(frame,(x,y),(x+w,y+h),255,3)
            cv2.imshow('mask',mask)
            cv2.imshow('frame',frame)
            cv2.imshow('weight',wighted)

                    
        k=cv2.waitKey(30) & 0xff
        if k==27:
            num = count
            break
            
    cap.release()
    cv2.destroyAllWindows()
    return num

