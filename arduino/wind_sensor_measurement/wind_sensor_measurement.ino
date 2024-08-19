#define N_SAMPLES 1000

unsigned long startMillis;  //some global variables available anywhere in the program
unsigned long currentMillis;

const int OutPin  = A0;   // wind sensor analog pin  hooked up to Wind P sensor "OUT" pin
const int TempPin = A1;   // temp sesnsor analog pin hooked up to Wind P sensor "TMP" pin
const unsigned long SAMPLE_FREQUENCY = 1000; //Hz 
 
uint8_t data[N_SAMPLES];

void setup() {
    Serial.begin(57600);

}

void loop() {    
    // read wind pin 
    for (int i=0; i<N_SAMPLES; i++){
      currentMillis = millis();  //get the current "time" (actually the number of milliseconds since the program started)
      
      if (currentMillis - startMillis >= 1/SAMPLE_FREQUENCY*1000)  //test whether the period has elapsed
      {
          //read and print to serial 
          data[i] = analogRead(OutPin);
          // Serial.println(windAD);

          startMillis = currentMillis;  //IMPORTANT to save the start time of the current LED state.
      }
    }
    Serial.write((uint8_t*)data, (N_SAMPLES) * sizeof(uint8_t));
    Serial.write('\n');
    

}

