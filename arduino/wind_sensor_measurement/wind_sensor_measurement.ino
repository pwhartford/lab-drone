

const int OutPin  = A0;   // wind sensor analog pin  hooked up to Wind P sensor "OUT" pin
const int TempPin = A2;   // temp sesnsor analog pin hooked up to Wind P sensor "TMP" pin
const int SAMPLE_TIME = 10; //seconds 


void setup() {
    Serial.begin(115200);

}

void loop() {    
    // read wind pin 
    int windAD = analogRead(OutPin);
    Serial.println(windAD);
  
}

