#include <DynamixelWorkbench.h>

#define BDPIN_LED_USER_1        22
#define BDPIN_LED_USER_2        23
#define BDPIN_LED_USER_3        24
#define BDPIN_LED_USER_4        25
#define BDPIN_PUSH_SW_1         34
#define BDPIN_PUSH_SW_2         35
#define BDPIN_BUZZER_           31
#if defined(__OPENCM904__)
  #define DEVICE_NAME "3" //Dynamixel on Serial3(USART3)  <-OpenCM 485EXP
#elif defined(__OPENCR__)
  #define DEVICE_NAME ""
#endif   

#define BAUDRATE  57600
#define PACKET_HEADER_0 0xAA
#define PACKET_HEADER_1 0x55
#define PACKET_PAYLOAD_SIZE 3
#define PACKET_CHECKSUM_IDX 3
DynamixelWorkbench dxl_wb;

bool result = false;
int led_pin = 13;
int led_pin_user[4] = { BDPIN_LED_USER_1, BDPIN_LED_USER_2, BDPIN_LED_USER_3, BDPIN_LED_USER_4 };
uint8_t dxl_id[2] = {1, 2};
void setup() {
  // put your setup code here, to run once:
  Serial.begin(57600);

  pinMode(led_pin, OUTPUT);
  pinMode(led_pin_user[0], OUTPUT);
  pinMode(led_pin_user[1], OUTPUT);
  pinMode(led_pin_user[2], OUTPUT);
  pinMode(led_pin_user[3], OUTPUT);
  pinMode(BDPIN_PUSH_SW_2, INPUT);
  // while(!Serial); // Wait for Opening Serial Monitor

  const char *log;
  bool result = false;

  uint16_t model_number = 0;
  char response = 'e';

  while(response != 'y') response = Serial.read(); //buffer to wait for python

  result = dxl_wb.init(DEVICE_NAME, BAUDRATE, &log);
  if (result == false)
  {
    Serial.println(log);
    Serial.println("Failed to init");
  }
  else
  {
    Serial.print("Succeeded to init : ");
    Serial.println(BAUDRATE);  
  }
  for(size_t i = 0; i < sizeof(dxl_id); i++){
    uint8_t id = dxl_id[i];
    result = dxl_wb.ping(id, &model_number, &log);
    if (result == false)
    {
      Serial.println(log);
      Serial.println("Failed to ping: ");
      Serial.print(id);
    }
    else
    {
      Serial.println("Succeeded to ping");
      Serial.print("id : ");
      Serial.print(id);
      Serial.print(" model_number : ");
      Serial.println(model_number);
    }
  }

  for(size_t i = 0; i < sizeof(dxl_id); i++){
    uint8_t id = dxl_id[i];
    result = dxl_wb.jointMode(id, 0, 0, &log);
    if(result == false){
      Serial.println(log);
      Serial.print("Failed to set joint mode for id: ");
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
    uint16_t motor1 = input >> 12;
    uint16_t motor2 = input & 0x0FFF;
    Serial.print("motor1: ");
    Serial.println(motor1);
    Serial.print("motor2: ");
    Serial.println(motor2);

    goalPos(1, motor1);
    goalPos(2, motor2);
    Serial.println("END");
  }
}

bool goalPos(int dxl_id, int input){
  const char *log;
  Serial.print("Moving Motor ");
  Serial.print(dxl_id);
  Serial.print(" to ");
  Serial.println(input);
  digitalWrite(led_pin_user[3], HIGH);
  digitalWrite(led_pin_user[0], HIGH);
  result = dxl_wb.goalPosition(dxl_id, input);
  if(result == false){
    Serial.print("goalPosition failed for id: ");
    Serial.println(dxl_id);
  }
  return result;
}
