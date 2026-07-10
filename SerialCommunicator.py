import serial
import numpy as np
import time

#Variables related to sending info to serial
SERIAL_PORT = "COM4" #Serial port duh
SERIAL_BAUD = 57600 #Serial BAUDRATE
PACKET_HEADER_0 = 0xAA #Packet header bytes for the Arduino to recognize the start of a command packet.
PACKET_HEADER_1 = 0x55 #Packet header bytes for the Arduino to recognize the start of the next command packet.

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
def sendCommand(ser, motor1, motor2, MAX_VALUE, moveMode):
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
    packet = packageCommands(motor1, motor2, MAX_VALUE)
    if ser is None:
        return False
    ser.write(packet)
    return readSerial(ser)