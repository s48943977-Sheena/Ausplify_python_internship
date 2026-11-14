"""
weather_app.py
==============
Task 4: Weather Information Application (CLI & GUI Dual Launcher)
Auspify Technologies — Python Development Internship

Interactive command-line weather terminal with live atmospheric metrics,
5-day forecasts, unit switching, history recall, and desktop GUI launch.
"""

import argparse
import sys
from typing import Optional

try:
    from weather_core import (
        CityNotFoundError,
        SearchHistory,
        WeatherAPIError,
        celsius_to_fahrenheit,
        get_city_weather,
        kmh_to_mph,
    )
except ImportError:
    from .weather_core import (
        CityNotFoundError,
        SearchHistory,
        WeatherAPIError,
        celsius_to_fahrenheit,
        get_city_weather,
        kmh_to_mph,
    )


def print_banner():
    """Print styled ASCII terminal banner."""
    print("=" * 60)
    print("       AUSPIFY TECHNOLOGIES -- PYTHON INTERNSHIP       ")
    print("        Task 4: Weather Information Application        ")
    print("=" * 60)
    print("Features:")
    print("  * Live weather data powered by Open-Meteo REST API")
    print("  * 5-Day daily forecast with high/low temperatures")
    print("  * Atmospheric metrics (Humidity, Wind, Pressure, Rain)")
    print("  * Dual unit modes: Celsius (C) and Fahrenheit (F)")
    print("Commands:")
    print("  * Type any City name (e.g., 'London', 'New Delhi', 'Tokyo')")
    print("  * 'unit'     -- Toggle between Celsius (C) and Fahrenheit (F)")
    print("  * 'history'  -- View recent city searches")
    print("  * 'gui'      -- Launch Desktop Tkinter Weather App")
    print("  * 'quit'/'q' -- Exit application")
    print("-" * 60)


def launch_gui():
    """Launch the Tkinter Desktop GUI interface."""
    try:
        import weather_gui
        print("\n[INFO] Launching Desktop GUI Weather App...")
        weather_gui.main()
    except Exception as e:
        print(f"\n[ERROR] Failed to start GUI: {e}")


def display_weather_report(data: dict, unit: str = "C"):
    """Display a structured ASCII weather report."""
    curr = data["current"]
    aqi = data.get("aqi", {})
    u = unit.upper()

    temp_val = curr["temperature_c"] if u == "C" else curr["temperature_f"]
    feels_val = curr["feels_like_c"] if u == "C" else curr["feels_like_f"]
    wind_val = curr["wind_speed_kmh"] if u == "C" else curr["wind_speed_mph"]
    wind_lbl = "km/h" if u == "C" else "mph"

    print("\n" + "=" * 60)
    print(f"  LOCATION  : {data['location_display']}")
    print(f"  TIMESTAMP : {data['timestamp']}")
    print(f"  ADVISORY  : {data.get('advisory', 'Normal conditions.')}")
    print("-" * 60)
    print(f"  CONDITION : {curr['condition']} {curr.get('ascii_icon', '')}")
    print(f"  TEMP      : {temp_val:.1f} deg {u}  (Feels like: {feels_val:.1f} deg {u})")
    print(f"  HUMIDITY  : {curr['humidity_percent']}% ({curr.get('humidity_status', 'Normal')})")
    print(f"  WIND      : {wind_val:.1f} {wind_lbl} ({curr.get('wind_direction', 'E')})")
    print(f"  RAIN CHANCE: {curr.get('rain_probability', 0)}%  (Volume: {curr['precipitation_mm']:.1f} mm)")
    print(f"  PRESSURE  : {curr['pressure_hpa']:.0f} hPa  (UV Index: {curr.get('uv_index', 5.0):.1f})")
    print(f"  AIR QUALITY: {aqi.get('rating', 'Good')} (AQI: {aqi.get('value', 30)})")
    print(f"  SUN TIMING: Sunrise {curr.get('sunrise', '06:14 AM')} | Sunset {curr.get('sunset', '06:02 PM')}")
    print("-" * 60)
    print("  5-DAY EXTENDED FORECAST:")
    print("  Day   Condition               High / Low    Rain %")
    print("  --------------------------------------------------")
    for f in data.get("forecast", []):
        f_max = f["temp_max_c"] if u == "C" else f["temp_max_f"]
        f_min = f["temp_min_c"] if u == "C" else f["temp_min_f"]
        desc_short = f["description"][:16]
        r_prob = f.get("rain_probability", 0)
        print(f"  {f['day_short']:<5} {desc_short:<16}  {f_max:>4.0f}/{f_min:<4.0f} deg {u}   {r_prob:>3d}%")
    print("=" * 60)


def run_cli():
    """Main interactive terminal loop."""
    print_banner()
    history = SearchHistory(max_items=15)
    current_unit = "C"

    # Pre-load initial city
    try:
        initial = get_city_weather("New Delhi", use_mock_on_failure=True)
        display_weather_report(initial, current_unit)
        history.add("New Delhi")
    except Exception:
        pass

    while True:
        try:
            prompt = f"\nEnter city name (or command, Unit: deg {current_unit}): "
            user_input = input(prompt).strip()

            if not user_input:
                continue

            cmd_lower = user_input.lower()

            if cmd_lower in ("q", "quit", "exit"):
                print("\nThank you for using Auspify Weather App! Goodbye.\n")
                break

            if cmd_lower in ("gui", "start-gui"):
                launch_gui()
                continue

            if cmd_lower in ("unit", "u", "toggle"):
                current_unit = "F" if current_unit == "C" else "C"
                print(f"\n[INFO] Temperature unit switched to deg {current_unit}.")
                continue

            if cmd_lower == "history":
                cities = history.get_all()
                print("\n" + "-" * 40)
                print("       RECENT SEARCH HISTORY")
                print("-" * 40)
                if not cities:
                    print("  (No searches recorded yet)")
                else:
                    for i, c in enumerate(cities, 1):
                        print(f"  [{i:02d}] {c}")
                print("-" * 40)
                continue

            print(f"\nFetching live weather for '{user_input}'...")
            data = get_city_weather(user_input, use_mock_on_failure=True)
            display_weather_report(data, current_unit)
            history.add(data["city"])

        except CityNotFoundError as cne:
            print(f"\n[ERROR] City not found: {cne}")
        except WeatherAPIError as wae:
            print(f"\n[ERROR] Weather service error: {wae}")
        except KeyboardInterrupt:
            print("\n\nOperation cancelled. Exiting...")
            break
        except Exception as e:
            print(f"\n[ERROR] Unexpected error: {e}")


def main():
    """Entry point with CLI argument support."""
    parser = argparse.ArgumentParser(
        description="Auspify Technologies -- Task 4: Weather Information App"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the desktop Tkinter GUI weather app directly.",
    )
    parser.add_argument(
        "--city",
        type=str,
        help="Look up weather for a specific city and exit.",
    )
    parser.add_argument(
        "--unit",
        type=str,
        choices=["C", "F"],
        default="C",
        help="Temperature unit (C or F). Default is C.",
    )
    args = parser.parse_args()

    if args.gui:
        launch_gui()
    elif args.city:
        data = get_city_weather(args.city, use_mock_on_failure=True)
        display_weather_report(data, args.unit)
    else:
        run_cli()


if __name__ == "__main__":
    main()
