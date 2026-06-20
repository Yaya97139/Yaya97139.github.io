/*IEMN Stage 2026 27/03/2026 */

#include <SPI.h>
#include <DW1000Ranging.h>
#include <WiFi.h>


// CONFIGURATION (À MODIFIER ) 
const char*    WIFI_SSID = "VOTRE_SSID";          // Nom du réseau Wi-Fi
const char*    WIFI_PASS = "VOTRE_MOT_DE_PASSE";  // Mot de passe Wi-Fi
const char*    SRV_IP    = "192.168.1.XX";         // IP de l'ordinateur (ipconfig)
const uint16_t SRV_PORT  = 8080;                   // Port du serveur Python


//Broches UWB 
#define PIN_RST 27
#define PIN_IRQ 34
#define PIN_SS   4

//Paramètres UWB
const uint8_t  CHANNELS[]    = {1, 2, 3, 5};
const int      NUM_CHANNELS  = sizeof(CHANNELS) / sizeof(CHANNELS[0]);
const uint16_t ANTENNA_DELAY = 16465;
const int      AVG_WINDOW    = 5;

//Géométrie des ancres (en mm)
const float BL = 300.0f;   // Distance (mm)

// Connexion TCP
WiFiClient client;
unsigned long lastReconnect = 0;

// structure de données UWB
struct AnchorData {
  uint16_t addr;
  float rangeHistory[NUM_CHANNELS][AVG_WINDOW];
  float tofHistory  [NUM_CHANNELS][AVG_WINDOW];
  int   idx         [NUM_CHANNELS];
  bool  valid       [NUM_CHANNELS];
};

const int  MAX_ANCHORS = 10;
AnchorData anchors[MAX_ANCHORS];
int        currentChannelIndex = 0;
unsigned long lastPrint = 0;


void     connectToServer();
uint16_t getFreqMHz(uint8_t channel);
void     switchChannel(uint8_t channel);
float    calculateAvgRange(int anchorIdx, int ch);
float    calculateAvgTof  (int anchorIdx, int ch);
float    radialDistance   (float x, float y);
bool     hyperbolicPosition(float d1_m, float d2_m, float d3_m,
                             float BL_mm, float* x_out, float* y_out);
void     onNewRange();
void     onNewDevice      (DW1000Device* device);
void     onInactiveDevice (DW1000Device* device);


// Setup

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Connexion Wi-Fi 
  Serial.printf("[WiFi] Connexion à '%s' ...\n", WIFI_SSID);
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(false);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }
  Serial.printf("\n[WiFi] Connecté ! IP locale : %s\n",
                WiFi.localIP().toString().c_str());

  // Connexion serveur Python 
  connectToServer();

  // Initialisation UWB 
  SPI.begin(18, 19, 23);
  DW1000Ranging.initCommunication(PIN_RST, PIN_SS, PIN_IRQ);
  switchChannel(CHANNELS[0]);

  DW1000Ranging.attachNewRange(onNewRange);
  DW1000Ranging.attachNewDevice(onNewDevice);
  DW1000Ranging.attachInactiveDevice(onInactiveDevice);

  DW1000Ranging.startAsTag("7D:00:22:EA:82:60:3B:9C",
                            DW1000.MODE_LONGDATA_RANGE_LOWPOWER);

  // Réinitialisation des structures
  for (int i = 0; i < MAX_ANCHORS; i++) {
    anchors[i].addr = 0;
    for (int ch = 0; ch < NUM_CHANNELS; ch++) {
      anchors[i].valid[ch] = false;
      anchors[i].idx[ch]   = 0;
      for (int k = 0; k < AVG_WINDOW; k++) {
        anchors[i].rangeHistory[ch][k] = 0.0f;
        anchors[i].tofHistory  [ch][k] = 0.0f;
      }
    }
  }

  Serial.println("[INIT] Système prêt — en attente de mesures UWB.");
}


void loop() {
  DW1000Ranging.loop();

  // Rotation des canaux toutes les 200 ms
  static unsigned long lastSwitch = 0;
  if (millis() - lastSwitch > 200) {
    currentChannelIndex = (currentChannelIndex + 1) % NUM_CHANNELS;
    switchChannel(CHANNELS[currentChannelIndex]);
    lastSwitch = millis();
  }

  // Tentative de reconnexion si déconnecté (toutes les 5 s)
  if (!client.connected() && millis() - lastReconnect > 5000) {
    connectToServer();
    lastReconnect = millis();
  }

  // Publication des données toutes les secondes
  if (millis() - lastPrint >= 1000) {
    unsigned long ts = millis();

    float positionsX[NUM_CHANNELS]; memset(positionsX, 0, sizeof(positionsX));
    float positionsY[NUM_CHANNELS]; memset(positionsY, 0, sizeof(positionsY));
    bool  validPos  [NUM_CHANNELS]; memset(validPos,   0, sizeof(validPos));

    for (int ch = 0; ch < NUM_CHANNELS; ch++) {
      uint16_t freq = getFreqMHz(CHANNELS[ch]);
      Serial.printf("[Canal %d - %u MHz]\n", CHANNELS[ch], freq);

      //  Mesures réaliser par le capteur
      for (int i = 0; i < MAX_ANCHORS; i++) {
        if (!anchors[i].addr || !anchors[i].valid[ch]) continue;

        float avgRange = calculateAvgRange(i, ch);
        float avgTof   = calculateAvgTof  (i, ch);

        Serial.printf("  Capteur %04X | ToF: %.2f ps | Distance: %.3f m\n",
                      anchors[i].addr, avgTof, avgRange);

      
        if (client.connected()) {
          client.printf("%lu,%d,%u,%04X,%.2f,%.3f\n",
                        ts, CHANNELS[ch], freq,
                        anchors[i].addr, avgTof, avgRange);
        }
      }

      // Calcul de position en utilisant les hyperboles
      float d1 = 0, d2 = 0, d3 = 0;
      bool has1 = false, has2 = false, has3 = false;

      for (int i = 0; i < MAX_ANCHORS; i++) {
        if (!anchors[i].valid[ch]) continue;
        if      (anchors[i].addr == 0x1783) { d1 = calculateAvgRange(i, ch); has1 = true; }
        else if (anchors[i].addr == 0x1785) { d2 = calculateAvgRange(i, ch); has2 = true; }
        else if (anchors[i].addr == 0x1787) { d3 = calculateAvgRange(i, ch); has3 = true; }
      }

      if (has1 && has2 && has3) {
        float x, y;
        if (hyperbolicPosition(d1, d2, d3, BL, &x, &y)) {
          float radial     = radialDistance(x, y);
          positionsX[ch]   = x;
          positionsY[ch]   = y;
          validPos[ch]     = true;

          Serial.printf("[Canal %d] Position: (%.1f mm, %.1f mm)"
                        " = (%.2f m, %.2f m) | Distance radiale: %.1f mm\n\n",
                        CHANNELS[ch], x, y, x / 1000.0f, y / 1000.0f, radial);

          
          if (client.connected()) {
            client.printf("%lu,%d,%u,POS,%.1f,%.1f,%.1f\n",
                          ts, CHANNELS[ch], freq, x, y, radial);
          }
        }
      }
    }  

    // Position finale moyenne 
    float sumX = 0, sumY = 0;
    int   count = 0;
    for (int ch = 0; ch < NUM_CHANNELS; ch++) {
      if (validPos[ch]) { sumX += positionsX[ch]; sumY += positionsY[ch]; count++; }
    }

    if (count > 0) {
      float avgX   = sumX / count;
      float avgY   = sumY / count;
      float avgRad = radialDistance(avgX, avgY);

      Serial.println("=== POSITION FINALE MOYENNE ===");
      Serial.printf("(%.1f mm, %.1f mm) = (%.2f m, %.2f m) | Distance radiale: %.1f mm\n",
                    avgX, avgY, avgX / 1000.0f, avgY / 1000.0f, avgRad);

      // CSV : millis,MOYENNE,,MOY,x_mm,y_mm,radial_mm
      if (client.connected()) {
        client.printf("%lu,MOYENNE,,MOY,%.1f,%.1f,%.1f\n",
                      ts, avgX, avgY, avgRad);
      }
    }

    lastPrint = millis();
  }
}


// CONNEXION AU SERVEUR PYTHON

void connectToServer() {
  Serial.printf("[TCP] Connexion à %s:%d ...\n", SRV_IP, SRV_PORT);
  if (client.connect(SRV_IP, SRV_PORT)) {
    Serial.println("[TCP] Connecté au serveur Python !");
  } else {
    Serial.println("[TCP] Serveur non disponible — données en Serial uniquement.");
  }
}


// FONCTIONS UTILITAIRES

uint16_t getFreqMHz(uint8_t channel) {
  switch (channel) {
    case 1: return 3494;
    case 2: return 3994;
    case 3: return 4494;
    case 5: return 6489;
    default: return 0;
  }
}

void switchChannel(uint8_t channel) {
  DW1000.setChannel(channel);
  DW1000.setAntennaDelay(ANTENNA_DELAY);
}

float calculateAvgRange(int anchorIdx, int ch) {
  float s = 0;
  for (int k = 0; k < AVG_WINDOW; k++)
    s += anchors[anchorIdx].rangeHistory[ch][k];
  return s / AVG_WINDOW;
}

float calculateAvgTof(int anchorIdx, int ch) {
  float s = 0;
  for (int k = 0; k < AVG_WINDOW; k++)
    s += anchors[anchorIdx].tofHistory[ch][k];
  return s / AVG_WINDOW;
}

float radialDistance(float x, float y) {
  return sqrtf(x * x + y * y);
}

/**
 * Localisation par intersection de deux hyperboles (méthode de balayage).
 * Hyperbole 1 : différence de dist capteur 1783 et 1785 (axe x)
 * Hyperbole 2 : différence de dist capteur 1783 et 1787 (axe y)
 */
bool hyperbolicPosition(float d1_m, float d2_m, float d3_m,
                        float BL_mm, float* x_out, float* y_out) {
  float d1 = d1_m * 1000.0f;
  float d2 = d2_m * 1000.0f;
  float d3 = d3_m * 1000.0f;

  // Hyperbole 1 (axe x)
  float a1 = (d1 - d2) / 2.0f;
  float A1 = a1 * a1;
  float t1 = (BL_mm / 2.0f) * (BL_mm / 2.0f) - A1;
  if (t1 <= 0) return false;
  float B1 = sqrtf(t1);

  // Hyperbole 2 (axe y)
  float a2 = (d1 - d3) / 2.0f;
  float A2 = a2 * a2;
  float t2 = (BL_mm / 2.0f) * (BL_mm / 2.0f) - A2;
  if (t2 <= 0) return false;
  float B2 = sqrtf(t2);

  // Balayage — pas de 10 mm, domaine 0..5000 mm
  float min_dist = 1e30f;
  float x_int = 0, y_int = 0;

  for (float x = fabsf(a1); x <= 5000.0f; x += 10.0f) {
    float y1 = B1 * sqrtf((x * x) / A1 - 1.0f);
    for (float y = fabsf(a2); y <= 5000.0f; y += 10.0f) {
      float x2   = B2 * sqrtf((y * y) / A2 - 1.0f);
      float dx   = x - x2;
      float dy   = y1 - y;
      float dist = dx * dx + dy * dy;
      if (dist < min_dist) {
        min_dist = dist;
        x_int = (x + x2) / 2.0f;
        y_int = (y1 + y) / 2.0f;
      }
    }
  }

  *x_out = x_int;
  *y_out = y_int;
  return true;
}


// CALLBACKS DW1000

void onNewRange() {
  DW1000Device* device = DW1000Ranging.getDistantDevice();
  uint16_t addr  = device->getShortAddress();
  float    range = device->getRange();
  int      ch    = currentChannelIndex;

  // Conversion distance → ToF en picosecondes
  const float C_LIGHT = 0.299792458f;  // m/ns
  float tof_ps = (range / C_LIGHT) * 1000.0f;

  for (int i = 0; i < MAX_ANCHORS; i++) {
    if (anchors[i].addr == addr || anchors[i].addr == 0) {
      if (anchors[i].addr == 0) anchors[i].addr = addr;
      int k = anchors[i].idx[ch];
      anchors[i].rangeHistory[ch][k] = range;
      anchors[i].tofHistory  [ch][k] = tof_ps;
      anchors[i].idx[ch]  = (k + 1) % AVG_WINDOW;
      anchors[i].valid[ch] = true;
      return;
    }
  }
}

void onNewDevice(DW1000Device* device) {
  // Géré par onNewRange()
}

void onInactiveDevice(DW1000Device* device) {
  uint16_t addr = device->getShortAddress();
  for (int i = 0; i < MAX_ANCHORS; i++) {
    if (anchors[i].addr == addr) {
      anchors[i].addr = 0;
      break;
    }
  }
}
