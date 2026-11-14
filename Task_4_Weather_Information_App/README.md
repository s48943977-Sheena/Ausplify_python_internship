# Auspify Weather Pro

**Auspify Technologies — Python Development Internship**  
*Task 4: Modern Desktop GUI & Command-Line Weather Information Application*

---

## 📌 Project Overview

**Auspify Weather Pro** is a high-precision, production-grade meteorological desktop and terminal application developed in Python. Designed to deliver live global atmospheric observations without complex setup, the application integrates with the **Open-Meteo REST API** to provide instant real-time weather conditions and 5-day daily forecasts for any city worldwide.

Many standard weather tutorials force users to register on third-party commercial platforms (such as OpenWeatherMap) to generate private API keys. In an academic or internship evaluation environment, hardcoded API keys frequently expire, exceed free-tier request limits, or fail if an evaluator does not possess their own key.

To ensure **100% zero-configuration evaluation**, this project utilizes the **Open-Meteo Open Data API**:
- **Zero API Key Required:** Runs out of the box on any machine with internet access.
- **Global Geocoding:** Automatically translates city names (e.g. *New Delhi*, *London*, *Tokyo*) into exact latitude and longitude coordinates.
- **WMO Standard Weather Codes:** Interprets World Meteorological Organization codes (0–99) into human-readable conditions and icons.
- **Automated Offline Fallback:** Includes a built-in mock weather engine that activates automatically if network connectivity is lost, ensuring the application and evaluation never crash.

---

## ✨ Key Features

1. **Zero-Configuration Live Weather Engine:**
   - Powered by Open-Meteo REST API.
   - Requires **no API keys, no registration, and no rate-limit hurdles**.

2. **Dual-Interface Architecture:**
   - **Modern Desktop GUI (`weather_gui.py`):** High-contrast midnight-blue theme, elevated metric cards, large temperature well, 5-day forecast cards, and quick-select city pills.
   - **Interactive CLI Terminal (`weather_app.py`):** Structured ASCII weather receipts, command-line query flag (`--city "Paris"`), and direct `--gui` launch flag.

3. **Comprehensive Atmospheric Parameters:**
   - **Current Temperature & Feels-Like:** Real and apparent temperatures.
   - **Relative Humidity:** Ambient moisture percentage.
   - **Wind Velocity:** Speed measured in `km/h` or `mph`.
   - **Surface Pressure:** Atmospheric pressure measured in `hPa`.
   - **Precipitation:** Real-time rain volume in `mm`.

4. **5-Day Extended Weather Forecast:**
   - Daily high and low temperature ranges.
   - Weather condition badges and meteorological icons for each upcoming day.

5. **Instant Dual-Unit Switching (°C / °F):**
   - Single-click toggle between Metric (`°C`, `km/h`) and Imperial (`°F`, `mph`).
   - Dynamically re-renders the dashboard instantly without redundant network re-queries.

6. **Quick-Select City Pills & Search History:**
   - Instant 1-click weather shortcuts for major metropolitan hubs: *New Delhi*, *Mumbai*, *London*, *New York*, *Tokyo*, and *Paris*.
   - Stores recent search queries in memory with deduplication.

7. **Resilient Offline Fallback:**
   - Seamlessly falls back to realistic demo data if offline, guaranteeing zero crashes during reviews or network timeouts.

8. **Zero External Dependencies:**
   - Built purely using Python's Standard Library (`urllib.request`, `json`, `tkinter`, `datetime`, `unittest`).
   - Requires zero `pip install` packages.

---

## 📂 Project Directory Structure

```text
Task_4_Weather_Information_App/
├── weather_gui.py            # Main desktop GUI application (Tkinter)
├── weather_app.py            # Interactive CLI application & dual-launcher
├── weather_core.py           # Core Open-Meteo API client, geocoder, and unit converter
├── test_weather_app.py       # Automated unit test suite (16 unit tests)
├── test_cases.md             # Formal verification report (TC01 – TC10)
├── README.md                 # Project documentation and user guide
├── package_submission.py     # Automated ZIP packaging script for internship submission
└── screenshots/              # Visual proof captures of the application
    └── README.md             # Screenshot capture guide and specifications
```

---

## 🚀 Getting Started

### System Requirements
- Python 3.10 or higher (Verified on Python 3.14).
- Windows 10 / 11, macOS, or Linux.
- Active internet connection *(or runs via built-in offline demo mode)*.

### 1. Launching the Desktop GUI Application

Open your terminal or PowerShell inside the `Task_4_Weather_Information_App` directory and run:

```powershell
python weather_gui.py
```

*Alternatively, launch via the dual launcher:*
```powershell
python weather_app.py --gui
```

### 2. Running the Interactive Terminal (CLI) Version

If you prefer a terminal experience:

```powershell
python weather_app.py
```

*Or query a specific city directly via arguments:*
```powershell
python weather_app.py --city "London" --unit C
```

**Example Terminal Output:**
```text
=======================================================
  LOCATION  : London, Greater London, United Kingdom
  TIMESTAMP : 2026-10-18 20:00:00
-------------------------------------------------------
  CONDITION : Clear sky [SUNNY]
  TEMP      : 14.5 deg C
  FEELS LIKE: 13.8 deg C
  HUMIDITY  : 52%
  WIND      : 12.0 km/h
  PRESSURE  : 1015 hPa
  RAIN      : 0.0 mm
-------------------------------------------------------
  5-DAY EXTENDED FORECAST:
  Day         Condition               High / Low
  ----------------------------------------------
  Sun   [CLEAR]    Clear sky            17 / 10   deg C
  Mon   [PARTLY CLOUDY] Partly cloudy   16 /  9   deg C
  Tue   [SUNNY]    Clear sky            18 / 11   deg C
  Wed   [RAIN]     Slight rain          14 /  8   deg C
  Thu   [CLEAR]    Mainly clear         15 /  9   deg C
=======================================================
```

---

## 🧪 Automated Testing

An automated test suite containing **16 unit tests** is provided in `test_weather_app.py`. It verifies unit conversions, meteorological WMO code lookups, API response normalization, history tracking, and offline data structures.

Run the test suite with:

```powershell
python -m unittest test_weather_app.py -v
```

**Expected Test Output:**
```text
test_empty_city_validation (test_weather_app.TestMockDataAndParsing.test_empty_city_validation) ... ok
test_mock_weather_structure (test_weather_app.TestMockDataAndParsing.test_mock_weather_structure) ... ok
test_parse_weather_response (test_weather_app.TestMockDataAndParsing.test_parse_weather_response) ... ok
test_add_and_retrieve (test_weather_app.TestSearchHistory.test_add_and_retrieve) ... ok
test_capacity_limit (test_weather_app.TestSearchHistory.test_capacity_limit) ... ok
test_clear_history (test_weather_app.TestSearchHistory.test_clear_history) ... ok
test_deduplication (test_weather_app.TestSearchHistory.test_deduplication) ... ok
test_celsius_to_fahrenheit_boiling (test_weather_app.TestUnitConversions.test_celsius_to_fahrenheit_boiling) ... ok
test_celsius_to_fahrenheit_freezing (test_weather_app.TestUnitConversions.test_celsius_to_fahrenheit_freezing) ... ok
test_celsius_to_fahrenheit_negative_crossover (test_weather_app.TestUnitConversions.test_celsius_to_fahrenheit_negative_crossover) ... ok
test_celsius_to_fahrenheit_room_temp (test_weather_app.TestUnitConversions.test_celsius_to_fahrenheit_room_temp) ... ok
test_kmh_to_mph (test_weather_app.TestUnitConversions.test_kmh_to_mph) ... ok
test_clear_sky (test_weather_app.TestWMOCodeMapping.test_clear_sky) ... ok
test_rain_code (test_weather_app.TestWMOCodeMapping.test_rain_code) ... ok
test_thunderstorm_code (test_weather_app.TestWMOCodeMapping.test_thunderstorm_code) ... ok
test_unknown_code_fallback (test_weather_app.TestWMOCodeMapping.test_unknown_code_fallback) ... ok

----------------------------------------------------------------------
Ran 16 tests in 0.014s

OK
```

For complete manual and automated test logs, consult [`test_cases.md`](file:///c:/Users/HP/Desktop/Auspify_Python_Internship/Task_4_Weather_Information_App/test_cases.md).

---

## 📦 Packaging for Internship Submission

To produce the official submission archive for Auspify Technologies:

```powershell
python package_submission.py
```

This script:
1. Automatically purges all `__pycache__` directories and temporary `.pyc` files.
2. Compresses the entire project into `Task_4_Weather_Information_App.zip` directly onto your Windows **Desktop**.
3. Displays an itemized manifest of all included files and their byte sizes.
