import time
import cv2
import numpy as np
import serial
import cameraVision
import serialCommunicator

#Camera Values
cap = cameraVision.cap
cameraWidth = cameraVision.cameraWidth
cameraHeight = cameraVision.cameraHeight


#Variables related to sending goalVelocity to the motors
MAX_VELOCITY = 1023 #Max size for 10-bit values, to make sure that the values we send are within the dynamixel's goalVel range.
RVELOCITY_SCALE = 2.0 #Scale factor for converting pixel offset to motor velocity
MVELOCITY_SCALE = 1 #

# Motor control calibration values for rotation
deadzoneX = 0.05 # Deadzone for X-axis (pan) control

#Variables related to approaching ball
targetBallSize = 100 #How big the ball should be to be counted as "in range" in pixels

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

def main():
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

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read camera frame")
            break

        ball = cameraVision.houghCircles(frame)
        if ball is not None:
            velocityX = faceBall(ball)
            if velocityX != 0:
                # Send motor1 positive, motor2 negative (for opposite direction)
                serialCommunicator.sendCommand(ser, velocityX/2, velocityX/2, MAX_VELOCITY, "R")
            else:
                serialCommunicator.sendCommand(ser, 0, 0, MAX_VELOCITY, "R")
                #time.sleep(3) #delay 3 seconds to confirm ball is in middle
                velocityX = approachBall
                if velocityX != 0:
                    serialCommunicator.sendCommand(ser, velocityX, velocityX, MAX_VELOCITY, "F",) #Move towards the ball

        cv2.imshow("FaceBall", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    if ser is not None:
        ser.close()


if __name__ == "__main__":
    main()
