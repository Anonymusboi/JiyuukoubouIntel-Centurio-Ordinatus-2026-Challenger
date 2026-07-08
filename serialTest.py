import serial
import io
import time


try:
    ser = serial.Serial("COM4", 57600, timeout=1) # open serial port
    ser.reset_input_buffer()
    ser.reset_output_buffer()
except:
    print("COM4 NOT FOUND.")
    exit()

def readSerial():
    test = ""
    while test != "END":
        test = ser.readline().decode('utf-8').strip()
        print("[SERIAL MONITOR]", test)
        
def pack_two_12bit(v1, v2):
    v1 &= 0x0FFF
    v2 &= 0x0FFF
    combined = (v1 << 12) | v2
    payload = [
        (combined >> 16) & 0xFF,
        (combined >> 8) & 0xFF,
        combined & 0xFF
    ]
    checksum = sum(payload) & 0xFF
    return bytes([0xAA, 0x55] + payload + [checksum])
    
response = input("enter y to start Arduino init, s to skip: ")
if response == "y":
    ser.write(bytes("y", 'utf-8')) #send init command to Arduino
    test = ""
    while test != "Setup concluded.":
        test = ser.readline().decode('utf-8').strip()
        print("[SERIAL MONITOR]", test)
elif response == "s":
    pass

def send_command(motor1, motor2):
    command = pack_two_12bit(motor1, motor2)
    ser.write(command) #send command to Arduino, then bitshift in arduino to get the next command
    readSerial()

while True:
    num = input("Enter rotation to send to Arduino [motor1, motor2]: ")
    command1 = num.split(",")[0]
    command2 = num.split(",")[1]
    send_command(int(command1), int(command2))