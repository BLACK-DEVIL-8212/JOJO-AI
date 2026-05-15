#include <WiFi.h>
#include <esp_camera.h>
#include <ESPAsyncWebServer.h>

// Replace with your WiFi credentials
const char* ssid = "Your_SSID";
const char* password = "Your_PASSWORD";

// Web server on port 80
AsyncWebServer server(80);

// querys for the Arduino
String currentquery = "";

void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi!");
  Serial.println(WiFi.localIP()); // Print the ESP32 IP address

  // Initialize camera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound()) {
    config.frame_size = FRAMESIZE_UXGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  if (esp_camera_init(&config) != ESP_OK) {
    Serial.println("Camera initialization failed");
    return;
  }

  // Setup Web server for video streaming and query handling
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(200, "text/plain", "ESP32-CAM is online!");
  });

  // Video stream endpoint
  server.on("/video", HTTP_GET, [](AsyncWebServerRequest *request) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (!fb) {
      request->send(500, "text/plain", "Camera capture failed");
      return;
    }
    AsyncWebServerResponse* response = request->beginChunkedResponse("image/jpeg", [fb](uint8_t* buffer, size_t maxLen, size_t index) -> size_t {
      size_t len = fb->len;
      if (index == 0) memcpy(buffer, fb->buf, len);
      return index == 0 ? len : 0;
    });
    response->addHeader("Content-Disposition", "inline; filename=capture.jpg");
    esp_camera_fb_return(fb);
    request->send(response);
  });

  // query endpoint (to receive hand gesture or system querys)
  server.on("/query", HTTP_POST, [](AsyncWebServerRequest *request) {
    if (request->hasParam("cmd", true)) {
      currentquery = request->getParam("cmd", true)->value();
      Serial.println("query Received: " + currentquery); // Send to Arduino via Serial
    }
    request->send(200, "text/plain", "query received");
  });

  server.begin();
}

void loop() {
  // Send querys to Arduino
  if (!currentquery.isEmpty()) {
    Serial.println(currentquery); // Send query to Arduino
    currentquery = ""; // Reset after sending
  }
}
