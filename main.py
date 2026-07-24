import time
import cv2
import cameraVision
from cameraVision import RawBall
import serialCommunicator
import mapping
from mapping import Robot, Ball
import rendering
import json
import math

#obtain pre-recorded values
with open("Data.json", "r") as file:
    config = json.load(file)
    
    
#Camera Values
cap = cameraVision.cap
cameraWidth = cameraVision.cameraWidth
cameraHeight = cameraVision.cameraHeight
cameraFOV = cameraVision.cameraFOV


#Variables related to sending goalVelocity to the motors
MAX_VELOCITY = 1023 #Max size for 10-bit values, to make sure that the values we send are within the dynamixel's goalVel range.
RVELOCITY_SCALE = config["tracking_calibration"]["turn_velocity_scale"] #Scale factor for converting pixel offset to motor velocity FOR ROTATION
AVELOCITY_SCALE = config["tracking_calibration"]["approach_velocity_scale"] #APPROACHING BALL

# Motor control calibration values for rotation
deadzoneX = config["tracking_calibration"]["turn_deadzone"] # Deadzone for X-axis (pan) control

#Variables related to approaching ball
targetBallSize = 100 #How big the ball should be to be counted as "in range" in pixels

def approachBall(ball : RawBall):
    x, y, r, _, _ = ball.getData()
    if r >= targetBallSize:
        return 0
    velocity_x = 500 * AVELOCITY_SCALE
    return(velocity_x)

#rotating the robot?
def calculateAngularVelocity(vel_scale):
    vel = (vel_scale/1023)* (((config["robot"]["no_load_RPM"] * config["robot"]["wheel_diameter_mm"] * math.pi)/60))
    angVel = (2*vel/config["robot"]["track_width_mm"])
    print("-----------------------------")
    print("ANGULAR VELOCITY: " + str(angVel))
    print("-----------------------------")
    return angVel
    
#computes how the motor moves based on the ball's x position in frame.
def faceBall(ball : RawBall):
    x, y, r, distance, _ = ball.getData()
    center_x = cameraWidth / 2
    if abs(x - center_x) < deadzoneX * cameraWidth:
        return 0
    offset_x = center_x - x
    velocity_x = offset_x * -RVELOCITY_SCALE #negative velocity scale since the motors are reversed?

    return float(velocity_x)

def main():
    #ARDUINO INITIALISE
    ser = serialCommunicator.initSerialPort()
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

    previous_time = time.perf_counter()
    robot = Robot((134, 65), 5, 5, 0)
    #ACTUAL LOGIC SECTION
    screen = rendering.init()
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read camera frame")
            break
        
        
        #OBTAIN BALL INFORMATION
        balls = cameraVision.houghCircles(frame)
        targetBall = cameraVision.findBiggestCircle(balls)
        
        
        digitalTargetBall = mapping.createBall(targetBall, 66)
        if digitalTargetBall is not None:
            digitalTargetBall.transform.updateWorldCoords(robot)
        digitalBalls = []
        if balls is not None:
            for ball in balls:
                digitalBall = mapping.createBall(ball, 66)
                digitalBall.transform.updateWorldCoords(robot)
                digitalBalls.append(digitalBall)
        rendering.render(screen, digitalBalls, digitalTargetBall, robot)
        
        
        cv2.imshow("mask", cameraVision.getMask(frame))
        cameraVision.drawFrameInfo(frame, balls, targetBall)
        
        if targetBall is not None:
            velocityX = faceBall(targetBall)
            if velocityX != 0:
                # Send motor1 positive, motor2 negative (for opposite direction)
                serialCommunicator.sendCommand(ser, velocityX, velocityX, MAX_VELOCITY, "R")
                angularVel = calculateAngularVelocity(velocityX)
                current_time = time.perf_counter()
                dt = current_time - previous_time
                previous_time = current_time
                angularVel *= dt
                robot.transform.rotate(math.degrees(-angularVel))
            else:
                serialCommunicator.sendCommand(ser, 0, 0, MAX_VELOCITY, "R")
                #time.sleep(3) #delay 3 seconds to confirm ball is in middle
                velocityX = 0
                #velocityX = approachBall(targetBall)
                if velocityX != 0:
                    #approachVel = calculateVelocity(velocityX)
                    serialCommunicator.sendCommand(ser, velocityX, velocityX, MAX_VELOCITY, "F",) #Move towards the ball
                else:
                    serialCommunicator.sendCommand(ser, 0, 0, MAX_VELOCITY, "R")
        else:
            serialCommunicator.sendCommand(ser, 0, 0, MAX_VELOCITY, "R")

        cv2.imshow("FaceBall", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if ser is not None:
        ser.close()


if __name__ == "__main__":
    main()
