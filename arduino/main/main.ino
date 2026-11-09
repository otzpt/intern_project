// Le o DHT22 de 5 em 5 s e envia 'temperatura,humidade' pela porta serie.
#include <DHT.h>

// pino de dados e modelo do sensor
#define DHTPIN 2
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);

void setup() {
    // 9600 baud tem de ser igual ao do main.py
    Serial.begin(9600);
    dht.begin();    
}

void loop() {
    // sem delay(): so le quando passaram 5 s desde a ultima leitura
    static unsigned long ultima = 0;
    if (millis() - ultima >= 5000) {
        ultima = millis();

        float t = dht.readTemperature();
        float h = dht.readHumidity();
        // o DHT devolve NaN quando falha
        if (isnan(t) || isnan(h)) {
            Serial.println("Erro a ler o DHT");
            return;
        }
        // formato da linha: 21.90,39.70
        Serial.print(t);
        Serial.print(",");
        Serial.println(h);
    }
    
}
