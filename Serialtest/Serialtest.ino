#include <Dynamixel2Arduino.h>

#define BDPIN_LED_USER_1        22
#define BDPIN_LED_USER_2        23
#define BDPIN_LED_USER_3        24
#define BDPIN_LED_USER_4        25
#define BDPIN_PUSH_SW_1         34
#define BDPIN_PUSH_SW_2         35
#define BDPIN_BUZZER_           31

#define BAUDRATE  57600
#define PACKET_HEADER_0 0xAA
#define PACKET_HEADER_1 0x55
#define PACKET_PAYLOAD_SIZE 3
#define PACKET_CHECKSUM_IDX 3

// Using Serial3 for Dynamixel (OpenCR)
const int DXL_DIR_PIN = 84;
Dynamixel2Arduino dxl(Serial3, DXL_DIR_PIN);

bool result = false;
int led_pin = 13;
int led_pin_user[4] = { BDPIN_LED_USER_1, BDPIN_LED_USER_2, BDPIN_LED_USER_3, BDPIN_LED_USER_4 };
uint8_t dxl_id[2] = {1, 2, 3};
void setup() {
  // put your setup code here, to run once:
  Serial.begin(57600);

  pinMode(led_pin, OUTPUT);
  pinMode(led_pin_user[0], OUTPUT);
  pinMode(led_pin_user[1], OUTPUT);
  pinMode(led_pin_user[2], OUTPUT);
  pinMode(led_pin_user[3], OUTPUT);
  pinMode(BDPIN_PUSH_SW_2, INPUT);

  // Initialize Dynamixel2Arduino
  dxl.begin(BAUDRATE);

  char response = 'e';
  while(response != 'y') response = Serial.read(); //buffer to wait for python

  // Ping and configure motors
  for(size_t i = 0; i < sizeof(dxl_id); i++){
    uint8_t id = dxl_id[i];
    if(dxl.ping(id)){
      Serial.println("Succeeded to ping");
      Serial.print("id : ");
      Serial.print(id);
    }
    else {
      Serial.println("Failed to ping: ");
      Serial.println(id);
    }
  }

  // Set motors to velocity control mode and enable torque
  for(size_t i = 0; i < sizeof(dxl_id); i++){
    uint8_t id = dxl_id[i];
    if(dxl.setOperatingMode(id, OP_VELOCITY)){
      Serial.print("Set velocity mode for id: ");
      Serial.println(id);
    }
    else{
      Serial.print("Failed to set velocity mode for id: ");
      Serial.println(id);
    }
    
    // Enable torque
    if(dxl.torqueOn(id)){
      Serial.print("Torque enabled for id: ");
      Serial.println(id);
    }
    else{
      Serial.print("Failed to enable torque for id: ");
      Serial.println(id);
    }
  }

  Serial.println("Setup concluded.");
}

void loop(){
  // Discard bytes until we find the packet header.
  while(Serial.available() > 0 && Serial.peek() != PACKET_HEADER_0){
    Serial.read();
  }

  if(Serial.available() >= 5)
  {
    // Read the packet header and verifies if we got the correct header bytes.
    //without it, we get sync issues and the motors might read dumbass garbage data
    uint8_t header0 = Serial.read();
    uint8_t header1 = Serial.read();
    if(header0 != PACKET_HEADER_0 || header1 != PACKET_HEADER_1){
      return;
    }

    uint8_t buf[4];
    if(Serial.readBytes(buf, 4) != 4){
      return;
    }

    uint8_t checksum = (buf[0] + buf[1] + buf[2]) & 0xFF;
    if(checksum != buf[3]){
      Serial.println("BAD CHECKSUM");
      return;
    }

    Serial.print("packet bytes: ");
    Serial.print(header0, HEX);
    Serial.print(" ");
    Serial.print(header1, HEX);
    Serial.print(" ");
    Serial.print(buf[0], HEX);
    Serial.print(" ");
    Serial.print(buf[1], HEX);
    Serial.print(" ");
    Serial.print(buf[2], HEX);
    Serial.print(" ");
    Serial.println(buf[3], HEX);

    uint32_t input = ((uint32_t)buf[0] << 16) |
                     ((uint32_t)buf[1] << 8) |
                     (uint32_t)buf[2];

    Serial.print("RAW input: ");
    Serial.println(input);
    
    // Extract as 12-bit signed values
    int16_t motor1_raw = (input >> 12) & 0x0FFF;
    int16_t motor2_raw = input & 0x0FFF;
    
    // Convert to signed range (-2047 to 2047)
    if(motor1_raw > 2047) motor1_raw -= 4096;
    if(motor2_raw > 2047) motor2_raw -= 4096;
    
    float motor1 = (float)motor1_raw;
    float motor2 = (float)motor2_raw;
    
    Serial.print("motor1: ");
    Serial.println(motor1);
    Serial.print("motor2: ");
    Serial.println(motor2);

    goalVel(1, motor1);
    goalVel(2, motor2);
    Serial.println("END");
  }
}

bool goalVel(int dxl_id, float input){
  Serial.print("Moving Motor ");
  Serial.print(dxl_id);
  Serial.print(" to velocity ");
  Serial.println(input);
  
  result = dxl.setGoalVelocity(dxl_id, input);
  if(result == false){
    Serial.print("setGoalVelocity failed for id: ");
    Serial.println(dxl_id);
  }
  else{
    Serial.print("setGoalVelocity success for id: ");
    Serial.println(dxl_id);
  }
  return result;
}
