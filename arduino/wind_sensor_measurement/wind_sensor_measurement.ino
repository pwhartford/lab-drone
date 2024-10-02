#define N_SAMPLES 900

unsigned long startMillis;  //some global variables available anywhere in the program
unsigned long currentMillis;

const int OutPin  = A0;   // wind sensor analog pin  hooked up to Wind P sensor "OUT" pin
const int TempPin = A1;   // temp sesnsor analog pin hooked up to Wind P sensor "TMP" pin
const int OutPin2 = A2;
const int TempPin2 = A3; 

const unsigned long SAMPLE_FREQUENCY = 1000; //Hz 
const long SAMPLE_PERIOD_MS = 1000/SAMPLE_FREQUENCY;
const int OFFSET = 200; //offset for ensuring array doesn't go over


int data[N_SAMPLES];

void setup() {
    Serial.begin(115200);

}

// Function to attempt constant sample frequency

void loop() {    
    // read wind pin 
    // if (Serial.available()>0){
    // Serial.readStringUntil('\n');
    
    // int i = 0;

    // while (i<=N_SAMPLES){
    //   currentMillis = millis();  //get the current "time" (actually the number of milliseconds since the program started)
      
    //   if ((currentMillis - startMillis) >= SAMPLE_PERIOD_MS)  //test whether the period has elapsed
    //   {
    //       //read and print to serial 
    //       data[i] = analogRead(OutPin);
    //       // Serial.println(windAD);

    //       startMillis = currentMillis; //IMPORTANT to save the start time of the current LED state.
    //       i++;  
    //   }

    // }

    // delay(100);
    // // Serial.write((uint8_t*)data, sizeof data);
    // Serial.write((byte*)&data, sizeof data);
    //   // Serial.write('\n');

    // }

    int serial_read = false;
    if(Serial.available() > 0)
    {
      int reset1 = Serial.read();
      int analogData = analogRead(OutPin);
      int tempAnalogData = analogRead(TempPin);
      int analogData2 = analogRead(OutPin2);
      int tempAnalogData2 = analogRead(TempPin2);

      Serial.print(analogData);
      Serial.print(',');
      Serial.print(tempAnalogData);
      Serial.print(',');
      Serial.print(analogData2);
      Serial.print(',');
      Serial.println(tempAnalogData2);
        }

  
    // Serial.println(tempAnalogData)

}

