// TODO: 
// ***1. Удобоваримо выдавать текущее состояние, включакя оставшееся время.
// ***2. Переписать чтение команд на неблокитующий способ. Собирать строку до возникновения перевода строки и потом ее анализировать.
// 3. Сделать регулируемый "таймаут" на срабатывание, чтобы исключить включение на коротком свете.
// ???4. Предусмотреть несколько каналаов.
// ***5. Убрать настройки в массив структур с разделением по каналам. 
// 6. Предусмотреть режим "pin-change"

#define CHANNELS 2
#define BUFFLEN 20
#define INITFLAG 0x10
#define INITDATA 0xFA
#define EEPROMOFFSET 0x20

#include <EEPROM.h>

struct CHANNEL {
  unsigned int on_delay, off_delay;
  byte mode;
};

struct STATE {
  unsigned int on_delay, off_delay;
  uint8_t mode;
  unsigned long timemillis;
};

volatile CHANNEL settings[CHANNELS];
volatile STATE state[CHANNELS];
volatile bool debug;

void printSettings() {
  char buffer[40];
  for (int i = 0; i < CHANNELS; i++) {
    sprintf(buffer,"%i: on_delay:  %i",i,settings[i].on_delay); Serial.println(buffer);
    sprintf(buffer,"%i: off_delay: %i",i,settings[i].off_delay); Serial.println(buffer);
    sprintf(buffer,"%i: mode:      %i",i,settings[i].mode); Serial.println(buffer);
  }
}

bool parseInteger(unsigned int *data, char *chars) {
  unsigned int tmp = 0;
  tmp = atoi(chars);
  if (!tmp) return false;
  *data = tmp;
  return true;
}

bool parseMode(byte *data, char mode) {
  switch (mode) {
    case '+':
      *data = 1;
      return true;
    case '-':
      *data = 2;
      return true;
    case '*':
      *data = 0;
      return true;
  }
  return false;
}

void printState() {
  char buffer[40];
  for (int i = 0; i < CHANNELS; i++) {
    sprintf(buffer,"%i: on_delay:  %i",i,state[i].on_delay); Serial.println(buffer);
    sprintf(buffer,"%i: off_delay: %i",i,state[i].off_delay); Serial.println(buffer);
    sprintf(buffer,"%i: mode:      %i",i,state[i].mode); Serial.println(buffer);
  }  
}

bool parseGo(byte channel, char command) {
  switch (command) {
    case '+':
      state[channel].off_delay = settings[channel].off_delay;
      return true;
    case '-':
      state[channel].off_delay = 0;
      return true;
  }
  return false;
}

bool parseCommand(char *command) {
  byte channel;
  unsigned int tmp;
  channel = command[1] - 'A';
  switch (command[0]) {
    case 'T':
      return (channel < CHANNELS) && parseInteger(&settings[channel].off_delay,&command[2]);
    case 'D':
      return (channel < CHANNELS) && parseInteger(&settings[channel].on_delay,&command[2]);
    case 'M':
      return (channel < CHANNELS) && parseMode(&settings[channel].mode,command[2]);
    case 'Q':
      printSettings();
      return true;
    case 'S':
      printState();
      return true;
    case 'W':
      writeEEPROM();
      return true;
    case 'B':
      debug = !debug;
      return true;
    case 'G':
      return (channel < CHANNELS) && parseGo(channel,command[2]);
  }
  return false;
}

void writeEEPROM() {
  EEPROM.put(EEPROMOFFSET,settings);
  EEPROM.update(INITFLAG,INITDATA);
  delay(1000);
}

void readEEPROM() {
  int flag = EEPROM.read(INITFLAG);
  delay(1000);
  if (flag == INITDATA) {
    Serial.println("Reading defaults...");
    EEPROM.get(EEPROMOFFSET,settings);
  } else {
    Serial.println("Writing defaults...");
    for (int i = 0; i < CHANNELS; i++) {
      settings[i].on_delay = 60; settings[i].off_delay = 600; settings[i].mode = 2;
    }
    writeEEPROM();
  }
}

void commandif() {
  static char command_string[BUFFLEN];
  static byte command_idx = 0;
  char incomingChar;
  if (Serial.available() > 0) {
    incomingChar = Serial.read();
    switch (incomingChar) {
      case 0x0d:
      case 0x0a:
        // command completed;
        command_string[command_idx] = 0x0;
        Serial.println(command_string);
        command_idx = 0;
        if (parseCommand(command_string)) {
          Serial.println("OK");
        } else {
          Serial.println("ERROR");
        }
        break;
      default:
        if (command_idx < BUFFLEN) {
          command_string[command_idx++] = incomingChar;
        }
    }    
  }
}

void phaseChange() {
  unsigned long now = millis();
  unsigned long delta = now - state[0].timemillis;
  if (debug) Serial.println(delta);
  if (delta > 8 && delta < 12) {
    state[0].on_delay++;
  }
  if (state[0].on_delay > 100) {
    state[0].off_delay = settings[0].off_delay*10;
    state[0].on_delay = 0;
  }
  state[0].timemillis = now;
}

void setup() {
  Serial.begin(57600);
  Serial.println("Starting...");
  readEEPROM();
  pinMode(3,INPUT_PULLUP);
  pinMode(12,OUTPUT);
  pinMode(13,OUTPUT);
  digitalWrite(12,LOW);
  digitalWrite(13,LOW);
  attachInterrupt(1, phaseChange, FALLING);
  memset(state,0,sizeof(state));
  debug = 0;
  for (int i = 0; i < CHANNELS; i++) {
    state[i].mode = LOW; 
  }
}

void loop() {
  if (millis() - state[0].timemillis > 1000) {
    state[0].on_delay = 0;
  }
  if (settings[0].mode == 1) {
    state[0].off_delay = 1;
  } else if (settings[0].mode == 2) {
    state[0].off_delay = 0;
  }
  if (state[0].off_delay > 0) {
    state[0].mode = HIGH;
    state[0].off_delay--;
  } else {
    state[0].mode = LOW;
  }
  digitalWrite(13,state[0].mode);
  commandif();
  delay(99);
}
