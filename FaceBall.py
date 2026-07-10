import time
import cv2
import numpy as np
import serial

#Variables related to sending info to serial
SERIAL_PORT = "COM4" #Serial port duh
SERIAL_BAUD = 57600 #Serial BAUDRATE
PACKET_HEADER_0 = 0xAA #Packet header bytes for the Arduino to recognize the start of a command packet.
PACKET_HEADER_1 = 0x55 #Packet header bytes for the Arduino to recognize the start of the next command packet.

#Variables related to sending goalVelocity to the motors
MAX_VELOCITY = 1023 #Max size for 10-bit values, to make sure that the values we send are within the dynamixel's goalVel range.
RVELOCITY_SCALE = 2.0 #Scale factor for converting pixel offset to motor velocity
MVELOCITY_SCALE = 1 #

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

# Motor control calibration values for rotation
deadzoneX = 0.05 # Deadzone for X-axis (pan) control

#Variables related to approaching ball
targetBallSize = 100 #How big the ball should be to be counted as "in range" in pixels

#initialise serial port
def initSerialPort():
    try:
        ser = serial.Serial(SERIAL_PORT, SERIAL_BAUD, timeout=1)
        #DONT YOU FUCKING FORGET TO RESET IT OR IT DIES DIPSHIT
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        print(f"Opened serial port {SERIAL_PORT} @ {SERIAL_BAUD}")
        return ser
    #check if serial port opened
    except Exception as exc:
        print(f"Unable to open serial port {SERIAL_PORT}: {exc}")
        return None

#reads serial until arduino prints out END, also a timeout to prevent infinite loop
def readSerial(ser, timeout=1.0):
    if ser is None:
        return False

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            #what errors?
            line = ser.readline().decode('utf-8', errors='ignore').strip()
        except Exception as exc:
            #somehow, the computer can't read.
            print(f"Error reading serial: {exc}")
            return False
        if not line:
            continue
        print("[SERIAL MONITOR]", line)
        if line == "END":
            return True
    print("[SERIAL MONITOR] timed out waiting for END")
    return False

#this is the juicy part. Basically, it takes the values we send for both motors,
#makes them kiss and then sends them to the Arduino as a singular 24-bit value.
#The arduino then bitshifts the data to get the values, and then uses that to control the motors.
def packageCommands(v1, v2, MAX_VALUE):
    # Clip to signed 12-bit range (-2048 to 2047)
    v1 = int(np.clip(v1, -2048, 2047))
    v2 = int(np.clip(v2, -2048, 2047))
    
    # Convert to unsigned 12-bit for transmission (two's complement)
    if v1 < 0:
        v1 = v1 + 4096
    if v2 < 0:
        v2 = v2 + 4096
    
    combined = (v1 << 12) | v2
    #THIS FUCKER IS THE THING THAT MAKES SHIT WORK
    #APPARENTLY YOU SEND DATA THROUGH SERIAL USING BYTES. 8 BIT PACKETS.
    #SO LAST TIME I TRIED SENDING THAT SHIT IT KEPT TRUNCATING MY DATA
    #SO THE MOTORS KEPT GOING CRAZY AND BEING SCHIZOPHRENIC AND SHIT.
    #GOBLOK ANJING IF IT WASN'T FOR AI I WOULDN'T HAVE KNOWN BECAUSE GOBLOK
    #DASAR ANJING
    #I GIVE THIS TO THE AI 
    #FOR ONCE ABOMINABLE INTELLIGENCE IS USEFUL
    payload = [
        #The [& 0xFF] parts is to make sure that the value is within 8 bits and truncates everything past that
        (combined >> 16) & 0xFF, #byte 1 (leftmost)
        (combined >> 8) & 0xFF, #byte 2 (middle)
        combined & 0xFF, #byte 3 (rightmost)
    ]
    #you know. i asked ai for why my shit was breaking. it went nuclear and
    #added a checksum and everything. After reviewing the code, i'll keep it
    #because there's no harm in it. i guess.
    #should protect against corruption if i use comically long cable^tm
    checksum = sum(payload) & 0xFF
    #Packet header 0 and 1 are used for synchronisation, so the arduino knows when a new packet starts.
    #without it, the arduino would just read the serial data as a stream of bytes and not know where to start reading the next packet.
    return bytes([PACKET_HEADER_0, PACKET_HEADER_1] + payload + [checksum])

#do.... do i need to explain this part?
def sendCommand(ser, motor1, motor2, moveMode):
    match moveMode.upper():
        case "R":
            pass
        case "L":
            motor1 *= -1
            motor2 *= -1
        case "F":
            motor2 *= -1
        case "B":
            motor1 *= -1
        case _:
            print("Unexpected moveMode, but proceeding anyways with default")
    packet = packageCommands(motor1, motor2, MAX_VELOCITY)
    if ser is None:
        return False
    ser.write(packet)
    return readSerial(ser)


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

def approachBall(ball):
    x, y, r, _ = ball
    if r >= targetBallSize:
        return 0
    velocity_x = 500 * MVELOCITY_SCALE
    return(velocity_x)

#computes how the motor moves based on the ball's x position in frame.
def faceBall(ball):
    x, y, r, _ = ball
    center_x = cameraWidth / 2
    if abs(x - center_x) < deadzoneX * cameraWidth:
        return 0
    offset_x = center_x - x
    velocity_x = offset_x * -RVELOCITY_SCALE #negative velocity scale since the motors are reversed?

    return (velocity_x)

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

def main():
    ser = initSerialPort()
    answer = input("Enter y to init Arduino, anything else to skip: ").strip().lower()
    if answer == "y" and ser is not None:
        ser.write(b"y")
        deadline = time.time() + 10.0  # 10 second timeout
        while time.time() < deadline:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print("[SERIAL MONITOR]", line)
            if line == "Setup concluded.":
                break
        else:
            print("Something broke during setup")
            exit(0)
    else:
        print("Skipping Arduino init.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read camera frame")
            break

        ball = houghCircles(frame)
        if ball is not None:
            velocityX = faceBall(ball)
            if velocityX != 0:
                # Send motor1 positive, motor2 negative (for opposite direction)
                sendCommand(ser, velocityX/2, velocityX/2, "R")
            else:
                sendCommand(ser, 0, 0, "R")
                #time.sleep(3) #delay 3 seconds to confirm ball is in middle
                velocityX = approachBall
                if velocityX != 0:
                    sendCommand(ser, velocityX, velocityX, "F") #Move towards the ball

        cv2.imshow("FaceBall", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if ser is not None:
        ser.close()


if __name__ == "__main__":
    main()
