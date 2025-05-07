#include "HX711.h"
#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

// ========== WiFi 設定 ==========
const char* ssid     ="xxxx";
const char* password = "xxxx";

// ========== Django API ==========
String djangoURL = "http://192.168.1.136:8080/devices/sensor/data/";  
String registerURL = "http://192.168.1.136:8080/devices/register_device/";  

// 使用內建 chipID 作為識別碼，轉成十六進位字串
String chipID = String(ESP.getChipId(), HEX);
String location="";
String patient_id="";
// 設定預設閾值（或可從伺服器端取得並更新）
float threshold = 100.0;

// ========== HX711 設定 ==========
// HX711 模組接到 DOUT=GPIO12, SCK=GPIO13
#define DOUT 12  
#define SCK 13   
HX711 scale;

// 實際校正因子請根據自已的感測器、標準砝碼測定
#define scaleFactor 455.0


// ========== 蜂鳴器 ==========
// 假設使用 GPIO2 接蜂鳴器，若蜂鳴器為 Active HIGH，HIGH=鳴叫
#define BUZZER_PIN 2

// ========== 函式宣告 ==========
bool registerDevice();
void uploadSensorData(float value);

void setup() {
  Serial.begin(115200);
  
  // 設定蜂鳴器腳位
  pinMode(BUZZER_PIN, OUTPUT);
 

  // 連線至 WiFi
  // Serial.print("Connecting to WiFi: ");
  // Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.print("\nWiFi connected! IP: ");
  Serial.println(WiFi.localIP());

  // 初始化 HX711
  scale.begin(DOUT, SCK);
  
  // 開機直接歸零，可呼叫:
  scale.tare(10);  // 取10次平均，視需求增減
  delay(500);
 
  // 註冊裝置，直到成功
  while (!registerDevice()) {
    Serial.println("Register device failed, retry in 2 seconds...");
    delay(2000);
  }
  Serial.println("Device Registered!");
  delay(1000);
}

void loop() {
  // 讀取感測器數值：以10次平均
  scale.set_scale(scaleFactor);
  // float sensorValue = (scale.get_value(10) - OFFSET) / scale.get_scale();
  float sensorValue = scale.get_units(10);  // 若已tare過

  // 若 sensorValue 超過 threshold，啟動蜂鳴器
  if (sensorValue > threshold) {
    analogWrite(BUZZER_PIN, 512);
    tone(BUZZER_PIN, 1000); 
    delay(500);            
    noTone(BUZZER_PIN);     
    delay(500);            // 等待1秒
    tone(BUZZER_PIN, 1000); 
    delay(500);            
    Serial.println("Buzzer ON");
    // 視需求可加個短延遲
    delay(500);
    noTone(BUZZER_PIN);     
    delay(1000);           
  
  }
  // 上傳資料
  uploadSensorData(sensorValue);

  // 根據需求設定回報頻率 (每5秒)
  delay(5000);

  // 若有非常龐大的或長迴圈運算，可在過程中加上 yield() 以避免 WDT Reset
  // e.g. for (long i = 0; i < veryLargeNumber; i++) { ... if (i % 1000 == 0) yield(); }
}

// ------------------------------------------------
// 註冊裝置 (POST /register_device/)
// ------------------------------------------------
bool registerDevice() {
  // 確認 WiFi 連線
  if (WiFi.status() != WL_CONNECTED) {
    return false;
  }

  WiFiClient client;
  HTTPClient http;
  http.setTimeout(5000);//因為 HTTPClient 是同步阻塞，如果網路或伺服器稍慢，預設的等待時間可能不夠，導致還沒收到完整回應就結束，或只有部分回應。
  // 開始連線
  http.begin(client, registerURL);
  http.addHeader("Content-Type", "application/json");

  // 組裝 JSON 資料
  String jsonData = "{\"chipID\": \"" + chipID + "\"}";

  // 發送 POST
  int httpResponseCode = http.POST(jsonData);
  Serial.print("[Register] HTTP code: ");
  Serial.println(httpResponseCode);
  delay(1000);
  bool success = false;
  if (httpResponseCode > 0) {
    // 讀取回應
    String payload = http.getString();
    Serial.print("Server response: ");
    Serial.println(payload);
    delay(500);
    // 200 表示成功
    if (httpResponseCode == 200) {
      success = true;
      // 如果伺服器有回傳閾值等資訊，也可在這裡解析
      // threshold = ...
    }
  } else {
    Serial.print("Register POST failed, error: ");
    Serial.println(http.errorToString(httpResponseCode).c_str());
  }

  http.end();
  return success;
}

// ------------------------------------------------
// 上傳感測器資料 (POST /sensor/data/)
// ------------------------------------------------
void uploadSensorData(float value) {
  String status="";
  Serial.println("Entering uploadSensorData...");
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClient client;
    HTTPClient http;
    http.setTimeout(5000);
    http.begin(client, djangoURL);
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");
    if(value>threshold){
      status="警示";
    }else{
      status="正常";
    }
    String postData = "chip_id=" + chipID + "&value=" + String(value)+"&location="+location+"&status="+status+"&patient_id="+patient_id;
    Serial.print("Post data: ");
    Serial.println(postData);

    int httpCode = http.POST(postData);
    Serial.print("httpCode = ");
    Serial.println(httpCode);
    delay(500);
    if (httpCode > 0) {
      String payload = http.getString();
      Serial.printf("[POST %d] %s\n", httpCode, payload.c_str());
      // 簡單字串處理解析 threshold 與 django_url                            
      int idxThreshold = payload.indexOf("\"threshold\":");
      int idxDjangoURL = payload.indexOf("\"url\":");
      int idxLocation = payload.indexOf("\"room\":");
      int idxPatient = payload.indexOf("\"patient_id\":");
      if (idxThreshold != -1) {
        int start = idxThreshold + 12;
        int end = payload.indexOf(",", start);
        if (end == -1) {
          end = payload.indexOf("}", start);
        }
        String valStr = payload.substring(start, end);
        valStr.trim();
        threshold = valStr.toFloat();
        Serial.printf("Updated threshold = %.2f\n", threshold);
      } 
      if (idxDjangoURL != -1) {
        int start = payload.indexOf(":", idxDjangoURL) + 1;
        int quoteStart = payload.indexOf("\"", start);
        int quoteEnd = payload.indexOf("\"", quoteStart + 1);
        djangoURL = payload.substring(quoteStart + 1, quoteEnd);
        Serial.println("Updated djangoURL = " + djangoURL);
      }
      if (idxLocation != -1) {
        int start = payload.indexOf(":", idxLocation) + 1;
        int quoteStart = payload.indexOf("\"", start);
        int quoteEnd = payload.indexOf("\"", quoteStart + 1);
        location = payload.substring(quoteStart + 1, quoteEnd);
        Serial.println("Updated location = " + location);
      }
      if (idxPatient != -1) {
        int start = payload.indexOf(":", idxPatient) + 1;
        int quoteStart = payload.indexOf("\"", start);
        int quoteEnd = payload.indexOf("\"", quoteStart + 1);
        patient_id = payload.substring(quoteStart + 1, quoteEnd);
        Serial.println("Updated Patient = " + patient_id);
      }
    } else {
      Serial.printf("POST failed, error: %s\n", http.errorToString(httpCode).c_str());
    }
    
    http.end();
  } else {
    Serial.println("WiFi not connected.");
  }
}

