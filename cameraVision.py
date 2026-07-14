"""
cameraVision Module

Detects different coloured balls in camera feed using HSV color masking and Hough Circle detection.
Calculates ball position and distance from camera using focal length calibration.

---
カメラ検出モジュール

HSV色マスキングと円形ハフ変換を使用してカメラフィードから異なる色のボールを検出できる。
焦点距離キャリブレーションを使用して、ボールの位置とカメラからの距離を計算できる。
"""

import cv2
import numpy as np

#init camera
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW) #use webcam
if not cap.isOpened(): #if aint got webcam, use laptop cam
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

#aspect ratio and dimensions
cameraWidth = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1280)
cameraHeight = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 720)

# Ball and camera detection calibration values
ballDiameter = 66 # Diameter of the ball in millimeters
focalLength = (18 * 2 * 1126) / ballDiameter
maxDist = 2700 # Maximum distance (MM) to consider a detection valid [arena's diagonal] (if it's over, that's probably a guy)

def findBiggestCircle(circles):
    if circles is None:
        return None
    return max(circles[0], key=lambda c: c[2])

#the actual detecting part of the code
def houghCircles(frame):
    #sets up the HSV mask for red
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower1 = np.array([140, 100, 100])
    upper1 = np.array([180, 255, 255])
    lower2 = np.array([0, 100, 100])
    upper2 = np.array([10, 255, 255])

    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)
    red = cv2.medianBlur(mask1 + mask2, 5)

    #detect circles using Hough Transform
    circles = cv2.HoughCircles(
        red,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=30,
        param1=20,
        param2=10,
        minRadius=1,
        maxRadius=50,
    )
    if circles is None:
        return None
    return circles
    #finds the biggest circle so we can track towards it
    biggest = findBiggestCircle(circles)
    if biggest is None:
        return None
    
    # Remove target ball from circles array to prevent overlap
    target_idx = np.where((circles[0] == biggest).all(axis=1))[0]
    if len(target_idx) > 0:
        circles_filtered = np.delete(circles[0], target_idx[0], axis=0)
        if circles_filtered.size > 0:
            circles = np.array([circles_filtered])
        else:
            circles = None
    
    #Draw frame info
    drawFrameInfo(frame, circles)
    drawTargetBall(frame, biggest)

    x, y, r = int(biggest[0]), int(biggest[1]), int(biggest[2])
    distance = (ballDiameter * focalLength) / (r * 2)
    if distance > maxDist:
        return None

    return (x, y, r, distance)

def drawFrameInfo(frame, circles):
    if circles is not None:
        for circle in circles[0]:
            x, y, r = int(circle[0]), int(circle[1]), int(circle[2])
            # Draw non-target circles in YELLOW
            cv2.circle(frame, (x, y), r, (0, 255, 255), 2) #Outline
            cv2.circle(frame, (x, y), 3, (0, 255, 255), 1) #Center
            cv2.putText(frame, f"({x},{y})", (x - 40, y - r - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(frame, f"Diameter={r}", (x - 40, y - r - 25),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            cv2.putText(frame, f"OffsetX={x - cameraWidth // 2}", (x - 40, y - r - 45),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
def drawTargetBall(frame, ball):
    center_x = cameraWidth // 2
    cv2.line(frame, (center_x, 0), (center_x, cameraHeight), (255, 0, 0), 1)
    if ball is not None:
        x, y, r = int(ball[0]), int(ball[1]), int(ball[2])
        # Draw TARGET circle in RED with thicker outline
        cv2.circle(frame, (x, y), r, (0, 0, 255), 3) #Outline
        cv2.circle(frame, (x, y), 2, (0, 0, 255), 3) #Center
        cv2.putText(frame, f"({x},{y})", (x - 40, y - r - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.putText(frame, f"Diameter={r}", (x - 40, y - r - 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame, f"OffsetX={x - center_x}", (x - 40, y - r - 45),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        cv2.putText(frame,"TARGET", (x - 40, y - r - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)