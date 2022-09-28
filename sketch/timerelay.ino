// TODO: 
// ***1. Удобоваримо выдавать текущее состояние, включакя оставшееся время.
// ***2. Переписать чтение команд на неблокитующий способ. Собирать строку до возникновения перевода строки и потом ее анализировать.
// 3. Сделать регулируемый "таймаут" на срабатывание, чтобы исключить включение на коротком свете.
// ***4. Предусмотреть несколько каналаов.
// ***5. Убрать настройки в массив структур с разделением по каналам. 
// ???6. Предусмотреть режим "pin-change"

#define CHANNELS 2
#define CYCLES 10
#define BUFFLEN 20
#define INITFLAG 0x10
#define INITDATA 0xA0 + CHANNELS
#define EEPROMOFFSET 0x20

#include <EEPROM.h>

struct CHANNEL {
  unsigned int on_delay, off_delay;
  byte mode;
};

struct STATE {
  unsigned int on_delay, off_delay;
  uint8_t mode;
  unsigned int count;
  unsigned long timemillis;
};

volatile CHANNEL settings[CHANNELS];
volatile STATE state[CHANNELS];
volatile byte pin_mask = 0;

void printSettings() {
  char buffer[40];
  for (int i = 0; i < CHANNELS; i++) {
    sprintf(buffer,"%c: on_delay:  %i",'A'+i,settings[i].on_delay); Serial.println(buffer);
    sprintf(buffer,"%c: off_delay: %i",'A'+i,settings[i].off_delay); Serial.println(buffer);
    sprintf(buffer,"%c: mode:      %i",'A'+i,settings[i].mode); Serial.println(buffer);
  }
}

void printState() {
  char buffer[40];
  for (int i = 0; i < CHANNELS; i++) {
    sprintf(buffer,"%c: on_delay:  %i",'A'+i,state[i].on_delay); Serial.println(buffer);
    sprintf(buffer,"%c: off_delay: %i",'A'+i,state[i].off_delay); Serial.println(buffer);
    sprintf(buffer,"%c: mode:      %i",'A'+i,state[i].mode); Serial.println(buffer);
    sprintf(buffer,"%c: count:     %i",'A'+i,state[i].count); Serial.println(buffer);
  }  
}

byte bits(byte exponent)
{
    byte product = 0;
    while (exponent--) {
      product |= 1 << exponent;
    }
    return product;
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
//      debug = !debug;
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
    Serial.print(incomingChar);
    switch (incomingChar) {
      case 0x0d:
      case 0x0a:
        // command completed;
        command_string[command_idx] = 0x0;
        //Serial.println(command_string);
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

ISR(PCINT0_vect) {
  static byte lastState;
  byte pinstate, changed;
  unsigned long now, delta;
  pinstate = PINB & pin_mask;
  changed = lastState & ~pinstate;
  lastState = pinstate;
  now = millis();
  for (byte channel = 0; channel < CHANNELS; channel++) {
    if (changed & 1 << channel) {
      delta = now - state[channel].timemillis;
      if (delta > 8 && delta < 12) {
        state[channel].count++;
      }
      if (state[channel].count > CYCLES) {
        state[channel].off_delay = settings[channel].off_delay;
        state[channel].count = 0;
      }
      state[channel].timemillis = now;  
    }
  }
}

ISR(TIMER1_COMPA_vect) {
  unsigned long now = millis();
  for (byte i = 0; i <  CHANNELS; i++) {
    if (now - state[i].timemillis > 1000) {
      state[i].count = 0;
    }
    if (state[i].off_delay > 0) {
      state[i].off_delay--;
    }
  }
}

void setup() {
  Serial.begin(57600);
  Serial.println("Starting...");
  readEEPROM();
  pinMode(13,OUTPUT);
  pinMode(13,LOW);
  for (byte i = 0; i < CHANNELS; i++) {
    pinMode(i+2,OUTPUT);
    digitalWrite(i+2,LOW);
    pinMode(i+8,INPUT_PULLUP);
  }
  cli(); 

  pin_mask = bits(CHANNELS);
  PCICR  |= 0b00000001;
  PCMSK0 |= pin_mask;

  TCCR1A = 0; 
  TCCR1B = 0; 

  OCR1A = 15624; // регистр совпадения
  TCCR1B |= (1 << WGM12); // включение в CTC режим

  // Установка битов CS10 и CS12 на коэффициент деления 1024
  TCCR1B |= (1 << CS10) | (1 << CS12);

  TIMSK1 |= (1 << OCIE1A);  // прерывание по совпадению

  sei(); 
}

void loop() {
  byte m0,n1;
  for (byte i = 0; i < CHANNELS; i++) {
    state[i].mode = ~bitRead(settings[i].mode,1) & (bitRead(settings[i].mode,0) | state[i].off_delay > 0);
    digitalWrite(i+2,state[i].mode);
  }
  commandif();
}
