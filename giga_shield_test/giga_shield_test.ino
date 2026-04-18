// GigaShield v0.2 — Z80 RetroShield Profiling/Test Sketch
// Tests level shifter operation and Z80 bus timing
//
// Wiring:
//   J11-7  (DIR_U7)  → A0 (data bus direction)
//   J11-10 (DIR_U10) → +3.3V (control outputs always Giga→Z80)
//   J11-11 (GND)     → Giga GND
//   All other J11 pins float to pulldown (B→A default)

// ── DIR control ──
#define DIR_DATA    A0    // J11-7: LOW = Z80→Giga, HIGH = Giga→Z80

// ── Z80 control outputs (U10, always Giga → Z80) ──
#define Z80_CLK     52
#define Z80_RESET   38
#define Z80_INT     50
#define Z80_NMI     51

// ── Z80 control inputs (U9, always Z80 → Giga) ──
// Verify these match your RetroShield wiring
#define Z80_M1      37
#define Z80_RD      39
#define Z80_WR      40
#define Z80_MREQ    41
#define Z80_IORQ    53

// ── Z80 data bus (U7, bidirectional) ──
const uint8_t DATA_PINS[8] = {42, 43, 44, 45, 46, 47, 48, 49};  // D0–D7

// ── Timing ──
static unsigned long cycleCount = 0;
static unsigned long lastReport = 0;
static const unsigned long REPORT_INTERVAL_MS = 2000;

// Clock generation via timer or manual toggle
static bool manualClock = true;
static unsigned long clkHalfPeriodUs = 500;  // 1 kHz default

void setDataDir(bool gigaDrives) {
  digitalWrite(DIR_DATA, gigaDrives ? HIGH : LOW);
  if (gigaDrives) {
    for (int i = 0; i < 8; i++) pinMode(DATA_PINS[i], OUTPUT);
  } else {
    for (int i = 0; i < 8; i++) pinMode(DATA_PINS[i], INPUT);
  }
}

uint8_t readDataBus() {
  uint8_t val = 0;
  for (int i = 0; i < 8; i++) {
    if (digitalRead(DATA_PINS[i])) val |= (1 << i);
  }
  return val;
}

void writeDataBus(uint8_t val) {
  for (int i = 0; i < 8; i++) {
    digitalWrite(DATA_PINS[i], (val >> i) & 1);
  }
}

void printBusState() {
  Serial.print("CTRL: M1=");
  Serial.print(digitalRead(Z80_M1));
  Serial.print(" RD=");
  Serial.print(digitalRead(Z80_RD));
  Serial.print(" WR=");
  Serial.print(digitalRead(Z80_WR));
  Serial.print(" MREQ=");
  Serial.print(digitalRead(Z80_MREQ));
  Serial.print(" IORQ=");
  Serial.print(digitalRead(Z80_IORQ));

  setDataDir(false);  // Z80→Giga to read
  Serial.print("  DATA=0x");
  Serial.println(readDataBus(), HEX);
}

// ── Test 1: Shifter loopback ──
// Writes a pattern on the data bus and reads it back.
// Requires the 5V side to be looped back (or a Z80 that echoes).
// Without loopback, verifies Giga→shifter output toggles correctly.
void testShifterOutput() {
  Serial.println("\n=== Test 1: Data bus output ===");
  setDataDir(true);  // Giga drives

  uint8_t patterns[] = {0x00, 0xFF, 0xAA, 0x55, 0x01, 0x80, 0xDE, 0xAD};
  for (uint8_t pat : patterns) {
    writeDataBus(pat);
    delayMicroseconds(10);
    Serial.print("  Wrote: 0x");
    Serial.println(pat, HEX);
  }

  setDataDir(false);  // back to read mode
  Serial.println("  Output test complete — verify with scope/logic analyzer on 5V side");
}

// ── Test 2: Control output verification ──
void testControlOutputs() {
  Serial.println("\n=== Test 2: Control outputs (CLK, RESET, INT, NMI) ===");

  // Toggle each control line
  struct { const char* name; int pin; } signals[] = {
    {"RESET", Z80_RESET}, {"INT", Z80_INT}, {"NMI", Z80_NMI}, {"CLK", Z80_CLK}
  };

  for (auto& sig : signals) {
    digitalWrite(sig.pin, HIGH);
    delayMicroseconds(100);
    digitalWrite(sig.pin, LOW);
    delayMicroseconds(100);
    Serial.print("  Toggled ");
    Serial.println(sig.name);
  }
  Serial.println("  Verify transitions on 5V side with scope");
}

// ── Test 3: Control input read ──
void testControlInputs() {
  Serial.println("\n=== Test 3: Control inputs (active-low Z80 signals) ===");
  Serial.print("  /M1=");    Serial.print(digitalRead(Z80_M1));
  Serial.print("  /RD=");    Serial.print(digitalRead(Z80_RD));
  Serial.print("  /WR=");    Serial.print(digitalRead(Z80_WR));
  Serial.print("  /MREQ=");  Serial.print(digitalRead(Z80_MREQ));
  Serial.print("  /IORQ=");  Serial.println(digitalRead(Z80_IORQ));
  Serial.println("  With no Z80 clock, all should read HIGH (inactive)");
}

// ── Test 4: Clock + bus profiling ──
void testClockAndProfile() {
  Serial.println("\n=== Test 4: Clock generation + bus profiling ===");
  Serial.print("  Running 100 clock cycles at ");
  Serial.print(1000000UL / (2 * clkHalfPeriodUs));
  Serial.println(" Hz...");

  setDataDir(false);  // Z80→Giga (read mode)

  unsigned long t0 = micros();
  int mreqCount = 0;
  bool prevMreq = HIGH;

  for (int i = 0; i < 100; i++) {
    digitalWrite(Z80_CLK, HIGH);
    delayMicroseconds(clkHalfPeriodUs);

    // Sample on falling edge (Z80 convention)
    bool mreq = digitalRead(Z80_MREQ);
    if (prevMreq == HIGH && mreq == LOW) {
      mreqCount++;
    }
    prevMreq = mreq;

    digitalWrite(Z80_CLK, LOW);
    delayMicroseconds(clkHalfPeriodUs);
  }

  unsigned long elapsed = micros() - t0;

  Serial.print("  Elapsed: ");
  Serial.print(elapsed);
  Serial.println(" us");
  Serial.print("  Avg cycle: ");
  Serial.print(elapsed / 100);
  Serial.println(" us");
  Serial.print("  /MREQ falling edges seen: ");
  Serial.println(mreqCount);

  if (mreqCount == 0) {
    Serial.println("  ⚠ No MREQ activity — Z80 may not be running");
    Serial.println("    Check: RESET released? CLK reaching Z80? U10 DIR = 3.3V?");
  }
}

// ── Test 5: Z80 boot + memory read capture ──
void testZ80Boot() {
  Serial.println("\n=== Test 5: Z80 boot — first 16 bus cycles ===");

  // Hold reset
  digitalWrite(Z80_RESET, LOW);
  delay(10);

  // Ensure data bus readable
  setDataDir(false);

  // Release reset
  digitalWrite(Z80_RESET, HIGH);
  Serial.println("  RESET released");

  for (int cycle = 0; cycle < 16; cycle++) {
    digitalWrite(Z80_CLK, HIGH);
    delayMicroseconds(clkHalfPeriodUs);

    // Sample on falling edge
    digitalWrite(Z80_CLK, LOW);
    delayMicroseconds(1);  // setup time

    bool m1   = digitalRead(Z80_M1);
    bool rd   = digitalRead(Z80_RD);
    bool mreq = digitalRead(Z80_MREQ);
    uint8_t data = readDataBus();

    Serial.print("  T");
    if (cycle < 10) Serial.print("0");
    Serial.print(cycle);
    Serial.print(": /M1=");
    Serial.print(m1);
    Serial.print(" /RD=");
    Serial.print(rd);
    Serial.print(" /MREQ=");
    Serial.print(mreq);
    Serial.print(" DATA=0x");
    if (data < 0x10) Serial.print("0");
    Serial.println(data, HEX);

    delayMicroseconds(clkHalfPeriodUs);
  }

  // Hold reset again
  digitalWrite(Z80_RESET, LOW);
  Serial.println("  RESET asserted — Z80 halted");
}

// ── Test 6: DIR toggle speed ──
void testDirToggleSpeed() {
  Serial.println("\n=== Test 6: DIR toggle speed (U7) ===");

  unsigned long t0 = micros();
  for (int i = 0; i < 10000; i++) {
    digitalWrite(DIR_DATA, HIGH);
    digitalWrite(DIR_DATA, LOW);
  }
  unsigned long elapsed = micros() - t0;

  Serial.print("  10000 DIR toggles in ");
  Serial.print(elapsed);
  Serial.print(" us (");
  Serial.print(elapsed / 10);
  Serial.println(" ns per toggle)");
}

void setup() {
  Serial.begin(115200);
  while (!Serial && millis() < 3000);

  Serial.println("GigaShield v0.2 — Z80 RetroShield Test");
  Serial.println("=======================================");

  // DIR control
  pinMode(DIR_DATA, OUTPUT);
  digitalWrite(DIR_DATA, LOW);  // default: Z80→Giga

  // Control outputs
  pinMode(Z80_CLK, OUTPUT);
  pinMode(Z80_RESET, OUTPUT);
  pinMode(Z80_INT, OUTPUT);
  pinMode(Z80_NMI, OUTPUT);

  // Hold Z80 in reset, INT/NMI inactive (active-low, so HIGH = inactive)
  digitalWrite(Z80_RESET, LOW);
  digitalWrite(Z80_INT, HIGH);
  digitalWrite(Z80_NMI, HIGH);
  digitalWrite(Z80_CLK, LOW);

  // Control inputs (active-low from Z80)
  pinMode(Z80_M1, INPUT_PULLUP);
  pinMode(Z80_RD, INPUT_PULLUP);
  pinMode(Z80_WR, INPUT_PULLUP);
  pinMode(Z80_MREQ, INPUT_PULLUP);
  pinMode(Z80_IORQ, INPUT_PULLUP);

  // Data bus starts as input
  for (int i = 0; i < 8; i++) pinMode(DATA_PINS[i], INPUT);

  Serial.println("\nCommands:");
  Serial.println("  1 — Shifter output test");
  Serial.println("  2 — Control output toggle");
  Serial.println("  3 — Control input read");
  Serial.println("  4 — Clock + bus profiling (100 cycles)");
  Serial.println("  5 — Z80 boot capture (16 cycles)");
  Serial.println("  6 — DIR toggle speed");
  Serial.println("  s — Print current bus state");
  Serial.println("  f — Set clock frequency (enter Hz)");
  Serial.println();
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    switch (c) {
      case '1': testShifterOutput(); break;
      case '2': testControlOutputs(); break;
      case '3': testControlInputs(); break;
      case '4': testClockAndProfile(); break;
      case '5': testZ80Boot(); break;
      case '6': testDirToggleSpeed(); break;
      case 's': printBusState(); break;
      case 'f': {
        Serial.print("Enter frequency (Hz): ");
        while (!Serial.available());
        long freq = Serial.parseInt();
        if (freq > 0 && freq <= 1000000) {
          clkHalfPeriodUs = 500000UL / freq;
          if (clkHalfPeriodUs < 1) clkHalfPeriodUs = 1;
          Serial.print("Clock set to ");
          Serial.print(freq);
          Serial.print(" Hz (half-period ");
          Serial.print(clkHalfPeriodUs);
          Serial.println(" us)");
        } else {
          Serial.println("Invalid — range: 1–1000000 Hz");
        }
        break;
      }
    }
  }
}
