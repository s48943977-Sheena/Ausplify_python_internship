# Test Cases — Task 4: Modern Desktop & CLI Weather Information App

## Testing Environment

- **Operating System:** Windows 10 / 11
- **Programming Language:** Python 3.10+ (Verified on Python 3.14)
- **IDE / Environment:** Visual Studio Code / Windows PowerShell
- **GUI Framework:** Python Tkinter (Standard Library, zero external dependencies)
- **Weather Engine:** Open-Meteo REST API (100% Free, worldwide geocoding, zero API key required)
- **Offline Resilience:** Realistic Mock Data Engine with automatic failover
- **Automated Test Runner:** Python `unittest` framework (`test_weather_app.py`)

---

## Test Results Summary

| ID | Test Case | Expected Result | Actual Result | Status |
| :--- | :--- | :--- | :--- | :--- |
| **TC01** | City Geocoding & Coordinate Lookup | Resolves city names (e.g. London, Mumbai, New York) into lat/lon coordinates | Coordinates and administrative hierarchy successfully fetched | **Pass** |
| **TC02** | Live Atmospheric Conditions Fetch | Retrieves temperature, feels-like, humidity, wind speed, pressure, and rain | Current weather metrics accurately extracted and mapped to UI | **Pass** |
| **TC03** | 5-Day Daily Extended Forecast | Retrieves daily dates, weather condition codes, and maximum/minimum temperatures | 5 distinct forecast days formatted with high/low values | **Pass** |
| **TC04** | WMO Weather Code & Icon Mapping | Accurately maps WMO meteorological codes (0-99) to human descriptions and icons | Code `0` displays "Clear sky", Code `61` displays "Slight rain" | **Pass** |
| **TC05** | Dual Unit Conversion (°C / °F) | Accurately converts Celsius to Fahrenheit and km/h to mph; toggles dynamically | `0°C -> 32°F`, `100°C -> 212°F`, `100 km/h -> 62.1 mph` | **Pass** |
| **TC06** | Empty / Invalid City Validation | Gracefully rejects empty city queries without crashing or throwing unhandled errors | Raises `CityNotFoundError` with message "City name cannot be empty." | **Pass** |
| **TC07** | Offline Fallback & Network Timeout | Switches automatically to realistic mock mode if disconnected from internet | Renders complete weather dashboard with "(Offline Demo Mode)" badge | **Pass** |
| **TC08** | City Search History & Deduplication | Tracks searched cities in memory, avoids duplicate entries, and limits list size | Most recent searches appear at top; duplicates re-order correctly | **Pass** |
| **TC09** | Desktop GUI Interactivity & Layout | Modern midnight-blue responsive card layout with quick-search city pills | Window centered at 520x760; smooth button hovers and typography | **Pass** |
| **TC10** | Terminal CLI Interface & Commands | Full interactive terminal mode with ASCII banner, formatted receipt, and `--gui` flag | Command-line reports render with clean ASCII icons and history | **Pass** |

---

## Detailed Test Logs

### TC01: City Geocoding & Coordinate Lookup
- **Input:** Search for `"London"`
- **Expected Result:** Latitude $\approx 51.51$, Longitude $\approx -0.13$, Country: `United Kingdom`.
- **Actual Result:** Open-Meteo Geocoding returns `51.50853, -0.12574, United Kingdom`.
- **Verification:** Successfully parsed into application coordinates structure.

### TC02: Live Atmospheric Conditions Fetch
- **Input:** Search for `"New Delhi"`
- **Expected Result:** Valid temperature range, humidity percentage, wind speed, and weather condition.
- **Actual Result:** `Temperature: 24.6 °C`, `Humidity: 52%`, `Wind: 14.5 km/h`, `Condition: Clear sky`.
- **Verification:** All primary atmospheric parameters populated with live data.

### TC03: 5-Day Daily Extended Forecast
- **Input:** Inspect `forecast` array for `"Tokyo"`.
- **Expected Result:** 5 daily objects containing day name, weather code, high/low temperatures, and rain probability.
- **Actual Result:** 5 distinct daily cards populated with high and low temperatures and conditions.

### TC04: WMO Weather Code & Icon Mapping
- **Input Values:** Codes `0`, `2`, `61`, `95`.
- **Expected Results:**
  - `0` $\rightarrow$ "Clear sky", `☀️`, `[SUNNY]`
  - `2` $\rightarrow$ "Partly cloudy", `⛅`, `[PARTLY CLOUDY]`
  - `61` $\rightarrow$ "Slight rain", `🌧️`, `[LIGHT RAIN]`
  - `95` $\rightarrow$ "Thunderstorm", `⛈️`, `[THUNDERSTORM]`
- **Verification:** Both GUI emojis and CLI safe ASCII tags mapped accurately.

### TC05: Dual Unit Conversion (°C / °F)
- **Input:** Current temperature `25.0 °C`. Click unit toggle button.
- **Expected Result:** Displays `77.0 °F`, wind speed converts from `km/h` to `mph`.
- **Actual Result:** Instant conversion without re-fetching from API.

### TC06: Empty / Invalid City Validation
- **Input:** Empty string `""` or whitespace `"   "`.
- **Expected Result:** Caught gracefully; user shown clear error dialog/message.
- **Actual Result:** `CityNotFoundError: City name cannot be empty.` displayed in status bar.

### TC07: Offline Fallback & Network Timeout
- **Action:** Simulate network disconnection or timeout.
- **Expected Result:** Seamless fallback to realistic mock data payload without application crash.
- **Actual Result:** Dashboard renders full temperature, metrics, and forecast with `(Offline Demo Mode)` badge.

### TC08: City Search History & Deduplication
- **Input Sequence:** Search `"London"`, then `"Paris"`, then `"London"`.
- **Expected Result:** History list contains `["London", "Paris"]` with `"London"` at index 0.
- **Verification:** Deduplication maintains chronological most-recent order.

### TC09: Desktop GUI Interactivity & Layout
- **Actions:** Run `python weather_gui.py`.
- **Observations:**
  - Window centers on screen at 520x760.
  - Midnight-blue palette (`#080F1E`) with elevated card panels (`#132238`).
  - Search entry accepts physical keyboard Enter key.
  - Quick-select pills (`Mumbai`, `London`, `Tokyo`, etc.) trigger instant lookups.

### TC10: Terminal CLI Interface & Commands
- **Actions:** Run `python weather_app.py --city "London"`.
- **Observations:** Clean formatted receipt printed with safe ASCII tags and 5-day forecast.
