#include <DHT.h>


//macros
#define DHTPIN 2
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

//pins

void setup() {
    Serial.begin(9600);
    dht.begin();    
}

void loop() {
    static unsigned long ultima = 0;
    if (millis() - ultima >= 5000) {
        ultima = millis();

        float t = dht.readTemperature();
        float h = dht.readHumidity();
        if (isnan(t) || isnan(h)) {
            Serial.println("Erro a ler o DHT");
            return;
        }
        Serial.print(t);
        Serial.print(",");
        Serial.println(h);
    }
    
}
