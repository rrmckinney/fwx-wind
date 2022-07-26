# Wind Sensor Code

The sensors are controlled by Arduino sketches. Three modules from Arduino were used. 

```
#include "TimerOne.h"
#include <math.h>
#include <SD.h>
#include <SPI.h>
```

Two pins are used to read the wind speed and wind direction from the davis senor. Wind speed is connected to a digital pin and wind direction is connected to a analog pin. If testing indicated the wind vane having an offset from the intented rest position, it can also be defined as a variable here. 

```
#define WindSensor_Pin (2) // digital pin for wind speed sensor
#define WindVane_Pin (A4) // analog pin for wind direction sensor
#define VaneOffset 0 // define the offset for caclulating wind direction
```

Set variables for the sketch. 

```
volatile bool isSampleRequired; // this is set every 2.5sec to generate wind speed
volatile unsigned int timerCount; // used to count ticks for 2.5sec timer count
volatile unsigned long rotations; // cup rotation counter for wind speed calcs
volatile unsigned long contactBounceTime; // timer to avoid contact bounce in wind speed sensor
volatile float windSpeed;

int vaneValue; // raw analog value from wind vane
int vaneDirection; // translated 0 - 360 wind direction
int calDirection; // calibrated direction after offset applied
int lastDirValue; // last recorded direction value

const int chipSelect = 10; // pin with sd card connected
```

Setup file for data to be written to. 

```
static char fileName[] = "windtest.txt";
static char header[] = {"time\twsp\twdir"};
```

Setup loop to reset senors and ensure everything is connected properly. 

```
void setup() {
  // This prevents any pins floating.
  //for (byte i = 2 ; i <= 19 ; i++)
  //  pinMode (i, INPUT_PULLUP);
    
  // setup anemometer values
  lastDirValue = 0;
  rotations = 0;
  isSampleRequired = false;

  // setup timer values
  timerCount = 0;

  Serial.begin(9600);
  Serial.println(" ");
  Serial.println("UBC Wind Sensor");

  Serial.begin(9600);
  if (SD.begin(chipSelect)) {
    Serial.println("SD card is present & ready");
  } else {
    Serial.println("SD card missing or failure");
    while (1); //wait here forever
  }

  File myFile = SD.open(fileName, FILE_WRITE);
  if (myFile) {
    myFile.println((char*)header);
    myFile.close();
    Serial.println((char*)header);
  }
  else {
    Serial.println("error opening .txt");
  }

  pinMode(WindSensor_Pin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(WindSensor_Pin), isr_rotation, FALLING);

  //pinMode(WindSensor_Pin, INPUT_PULLUP);
  //attachInterrupt(digitalPinToInterrupt(WindSensor_Pin), isr_rotation, RISING);

  // setup the timer for 0.5 second
  Timer1.initialize(500000);
  Timer1.attachInterrupt(isr_timer);

 sei(); // Enable Interrupts

}
```
Setup loop to write wind speed and direction to the ouput file. The sensor does not have an internal clock, but does keep track of millisecinds since power was introduced. However, due to memory it can only keep track of a certain number of milliseconds, so we need to convert them to hours:minutes:seconds.

```
void loop() {

//    getWindDirection();
//    if (abs(calDirection - lastDirValue) > 5) {
//      lastDirValue = calDirection;
//    }
  
  if (isSampleRequired) {
    getWindDirection();
    unsigned long prMillis = millis();
    while (millis() - prMillis < 1000) {
      ;
    }
    prMillis = millis() / 1000;
    byte sec = prMillis % 60;
    prMillis = prMillis / 60;
    byte min = prMillis % 60;
    prMillis = prMillis / 60;
    byte hrs = prMillis % 24;

    Serial.print(hrs);
    Serial.print(':');
    Serial.print(min);
    Serial.print(':');
    Serial.print(sec);
    Serial.print("\t");

    Serial.print(windSpeed);
    Serial.print(" mph\t");
    Serial.print(calDirection);
  
    Serial.println("*");
    File myFile = SD.open(fileName, FILE_WRITE);
    if (myFile) // it opened OK
    {
      //Serial.println("Writing to windtest.txt");
      myFile.print(hrs);
      myFile.print(':');
      myFile.print(min);
      myFile.print(':');
      myFile.print(sec);
      myFile.print("\t");
      myFile.print(windSpeed);
      myFile.print("\t");
      myFile.println(calDirection);
      myFile.close();
    } else{
      Serial.println("Error opening simple.txt");
    }
    isSampleRequired = false;
    //Serial.end(); // not sure if needed

  }
}
```
Wind speed is collected as the number of rotations every 2.5s. The pin is then interrupted for 0.5s so the total can be reset. The total number of rotations is multiplied by 0.9 to get the wind speed as specified by the [Davis cup anemometer manual](https://cdn.shopify.com/s/files/1/0515/5992/3873/files/6410_SS.pdf). 
```
void isr_timer() {
  timerCount++;
  if (timerCount == 6) {
    windSpeed = rotations * 0.9;
    rotations = 0;
    isSampleRequired = true;
    timerCount = 0;
  }
}
```
Function for getting wind direction. Wind direction is read as an offset from the orgin position (0 degrees) up to 1023 degrees. This needs to be re-mapped to follow the 360 degrees we use for direction. 
```
void getWindDirection() {
  //vaneValue = analogRead(WindVane_Pin); 
 // vaneDirection = (vaneValue / 1024.0) * 360.0;
  vaneValue = analogRead(WindVane_Pin);
  vaneDirection = map(vaneValue, 0, 1023, 0, 359);
  calDirection = vaneDirection + VaneOffset;
  if (calDirection > 360)
    calDirection = calDirection - 360;

  if(calDirection < 0)
    calDirection = calDirection + 360;
}
```


