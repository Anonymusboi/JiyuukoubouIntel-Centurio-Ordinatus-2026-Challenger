import cv2
import numpy as np
#ALL UNITS ARE IN mm OR pixels BECAUSE YOU STUPID PIECE OF SHIT CAN'T DECIDE.
#THIS PREVENTS UGLY-ASS *1000 /1000 IN THE GODAMMN CALCULATIONS AND PRINT WHICH MAKES CODING HARDER
#FUCK YOU, *ME*

cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)
diameter = 66 
contourFocalLength = (33*1200) / diameter #Calibrated to be 33 pixels at 1200 mm distance, so focal length is (pixel width * distance) / diameter
houghFocalLength = (18*2*1126) / diameter #Calibrated to be 18 pixels radius at 1126 mm distance, so focal length is (pixel width * distance) / diameter
distance = 0
maxDistance = 2700 #max distance for ball detection, anymore is outside the range of the arena in MM
#On the note of maxDistance, it's for the diagonal of the arena, so
#with the power of THE PYTHAGORAS THEREOM, it's 2,687mm rounded to 2.7m
cameraHeight = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
cameraWidth = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
#-7.82996+30 cm is where the center intersects the bounds at 12.8cm, 7.2cm. Aka, for 1280cm, it's at -7.83*100cm.
big = 0

def update_location():
    ret, frame = cap.read()
    if not ret:
        print("can't find frame")
        return 0.1
    index = 1
    #contourDetection(frame)
    houghCircleDetection(frame)

    # Show the original frame and the mask
    cv2.imshow("frame", frame)
    if big is not None:
        x, y, r = big[0], big[1], big[2]
        distance = ((diameter * houghFocalLength) / (r * 2)) # calculate distance to the object, in millimeters.
        offsetX = distance*(-12.8/22.17) + (x/cameraWidth)*(distance*(12.8/22.17)*2)
        offsetY = distance*(7.2/22.17) - (y/cameraHeight)*(distance*(7.2/22.17)*2)
        AngleX = np.arctan(offsetX/distance) * (180/np.pi)
    #return 0.05
def contourDetection(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Red wraps around HSV, so use two ranges
    lower1 = np.array([140, 100, 100])
    upper1 = np.array([360, 255, 255])
    lower2 = np.array([0, 100, 100])
    upper2 = np.array([20, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)

    redMask = mask1 + mask2

    # Find contours in the mask
    contours, _ = cv2.findContours(redMask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in contours:
        # Filter out small contours to reduce noise
        area = cv2.contourArea(c)
        if area > 500:
            # Get bounding box and center of the contour
            x, y, w, h = cv2.boundingRect(c)
            distance = ((diameter * contourFocalLength) / w ) # calculate distance to the object, in millimeters.
            # calculate center of the bounding box
            cx = x + w // 2
            cy = y + h // 2 
            # Draw bounding box on the original frame
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
            # Draw a circle at the center of the detected ball
            cv2.circle(frame, (cx, cy), 5, (255,0,0), -1)
            #Display Aspect ratio of the bounding box
            aspect_ratio = w / h
            cv2.putText(frame, f"Rect: {aspect_ratio:.2f}", (x, y-90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            # Display the width of the bounding box in pixels
            cv2.putText(frame, f"W:{w:.1f} p", (x, y-70),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            #Display height of the bounding box in pixels
            cv2.putText(frame, f"H:{h:.1f} p", (x, y-50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            #Display distance to the ball in m
            cv2.putText(frame, f"Dist: {distance:.1f} mm", (x, y-30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            # Display the coordinates of the center on the frame -10 pixels above box
            cv2.putText(frame, f"{cx},{cy}", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
            #Checks if it's a ball by checking if the aspect ratio is close to 1, and if so, updates the location of the ball in Blender
            if aspect_ratio > 0.7 and aspect_ratio < 1.3:
                cv2.putText(frame, "Ball "+ str(index), (x, y+h+20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                objectName = "redBall.00" + str(index)
                #data.objects[objectName].location[1] = distance*100
                #data.objects[objectName].location[0] = distance*100*(-12.8/22.17) + (x/cameraWidth)*(distance*100*(12.8/22.17)*2)
                #data.objects[objectName].location[2] = distance*100*(7.2/22.17) - (y/cameraHeight)*(distance*100*(7.2/22.17)*2)
                index += 1
            else:
                cv2.putText(frame, f"No Ball", (x, y+h+20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.imshow("mask", redMask)
def houghCircleDetection(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower1 = np.array([140, 100, 100])
    upper1 = np.array([180, 255, 255])
    lower2 = np.array([0, 100, 100])
    upper2 = np.array([10, 255, 255])
    
    mask1 = cv2.inRange(hsv, lower1, upper1)
    mask2 = cv2.inRange(hsv, lower2, upper2)

    redMask = mask1 + mask2
    #red = cv2.cvtColor(redMask, cv2.COLOR_BGR2GRAY)
    red = cv2.medianBlur(redMask, 5)
    circles = cv2.HoughCircles(
        red, 
        cv2.HOUGH_GRADIENT, 
        1, 
        30, 
        param1=20, 
        param2=10, 
        minRadius=1, 
        maxRadius=50)
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            x, y, r = i[0], i[1], i[2]
            distance = ((diameter * houghFocalLength) / (r * 2)) # calculate distance to the object, in millimeters.
            if distance < maxDistance: #Ensures the ball is within the range of the arena, otherwise it will be ignored
                # Draw the outer circle
                cv2.circle(frame, (x, y), r, (0, 255, 0), 2)
                # Draw the center of the circle
                cv2.circle(frame, (x, y), 2, (0, 0, 255), 3)
                # Calculate distance to the objectqqqqqqqqqqqqqq
                cv2.putText(frame, f"Dist: {distance:.1f} mm", (x-50, y-r),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
                cv2.putText(frame, f"Radius: {r:.1f} p", (x-50, y-int(1.1*r-20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 2)
    cv2.imshow("mask", red)
    big = findBiggestCircle(circles)
def findBiggestCircle(circles):
    if circles is None:
        return None
    largest_circle = max(circles[0], key=lambda c: c[2])  # c[2] is the radius
    return largest_circle
while True:
    update_location()
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
#bpy.app.timers.register(update_location)