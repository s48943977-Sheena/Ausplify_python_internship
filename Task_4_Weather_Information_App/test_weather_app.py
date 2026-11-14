"""
test_weather_app.py
===================
Unit Test Suite for Task 4: Weather Information Application
Auspify Technologies — Python Development Internship

Comprehensive offline and unit verification:
- Temperature and velocity unit conversions (°C <-> °F, km/h <-> mph)
- WMO Weather interpretation code mappings & ASCII fallbacks
- Search history tracking, deduplication, and capacity boundaries
- Mock data payload integrity and structure
- API response parsing and normalization
- Validation and error handling for missing/empty cities
"""

import json
import unittest
from unittest.mock import MagicMock, patch

from weather_core import (
    CityNotFoundError,
    SearchHistory,
    WeatherAPIError,
    celsius_to_fahrenheit,
    geocode_city,
    get_mock_weather,
    get_weather_description,
    kmh_to_mph,
    parse_weather_response,
)


class TestUnitConversions(unittest.TestCase):
    """Test mathematical temperature and speed conversions."""

    def test_celsius_to_fahrenheit_freezing(self):
        self.assertEqual(celsius_to_fahrenheit(0.0), 32.0)

    def test_celsius_to_fahrenheit_boiling(self):
        self.assertEqual(celsius_to_fahrenheit(100.0), 212.0)

    def test_celsius_to_fahrenheit_room_temp(self):
        self.assertEqual(celsius_to_fahrenheit(25.0), 77.0)

    def test_celsius_to_fahrenheit_negative_crossover(self):
        self.assertEqual(celsius_to_fahrenheit(-40.0), -40.0)

    def test_kmh_to_mph(self):
        self.assertEqual(kmh_to_mph(0.0), 0.0)
        self.assertEqual(kmh_to_mph(100.0), 62.1)
        self.assertEqual(kmh_to_mph(50.0), 31.1)


class TestWMOCodeMapping(unittest.TestCase):
    """Test meteorological code lookups."""

    def test_clear_sky(self):
        desc, icon, ascii_icon, tag = get_weather_description(0)
        self.assertEqual(desc, "Clear sky")
        self.assertEqual(ascii_icon, "[SUNNY]")
        self.assertEqual(tag, "Clear")

    def test_rain_code(self):
        desc, icon, ascii_icon, tag = get_weather_description(61)
        self.assertEqual(desc, "Slight rain")
        self.assertEqual(ascii_icon, "[LIGHT RAIN]")
        self.assertEqual(tag, "Rain")

    def test_thunderstorm_code(self):
        desc, icon, ascii_icon, tag = get_weather_description(95)
        self.assertEqual(desc, "Thunderstorm")
        self.assertEqual(ascii_icon, "[THUNDERSTORM]")

    def test_unknown_code_fallback(self):
        desc, icon, ascii_icon, tag = get_weather_description(9999)
        self.assertEqual(desc, "Unknown weather")
        self.assertEqual(ascii_icon, "[WEATHER]")


class TestSearchHistory(unittest.TestCase):
    """Test city search history management."""

    def setUp(self):
        self.history = SearchHistory(max_items=3)

    def test_add_and_retrieve(self):
        self.history.add("London")
        self.history.add("Paris")
        self.assertEqual(self.history.get_all(), ["Paris", "London"])

    def test_deduplication(self):
        self.history.add("Tokyo")
        self.history.add("New York")
        self.history.add("Tokyo")  # Re-adding brings Tokyo to front
        self.assertEqual(self.history.get_all(), ["Tokyo", "New York"])

    def test_capacity_limit(self):
        self.history.add("City A")
        self.history.add("City B")
        self.history.add("City C")
        self.history.add("City D")  # Pushes City A out
        all_cities = self.history.get_all()
        self.assertEqual(len(all_cities), 3)
        self.assertEqual(all_cities, ["City D", "City C", "City B"])

    def test_clear_history(self):
        self.history.add("Rome")
        self.history.clear()
        self.assertEqual(self.history.get_all(), [])


class TestMockDataAndParsing(unittest.TestCase):
    """Test fallback data and API JSON normalization."""

    def test_mock_weather_structure(self):
        data = get_mock_weather("Mumbai")
        self.assertEqual(data["city"], "Mumbai")
        self.assertTrue(data["is_mock"])
        self.assertIn("current", data)
        self.assertIn("temperature_c", data["current"])
        self.assertIn("humidity_percent", data["current"])
        self.assertEqual(len(data["forecast"]), 5)

    def test_parse_weather_response(self):
        geo = {
            "name": "Berlin",
            "country": "Germany",
            "admin1": "Berlin",
            "latitude": 52.52,
            "longitude": 13.405,
            "timezone": "Europe/Berlin",
        }
        raw_api = {
            "current": {
                "temperature_2m": 18.5,
                "apparent_temperature": 18.0,
                "relative_humidity_2m": 60,
                "wind_speed_10m": 12.0,
                "surface_pressure": 1015.0,
                "precipitation": 0.0,
                "weather_code": 2,
                "is_day": 1,
            },
            "daily": {
                "time": ["2026-10-18", "2026-10-19"],
                "weather_code": [2, 61],
                "temperature_2m_max": [20.0, 16.0],
                "temperature_2m_min": [10.0, 9.0],
                "precipitation_probability_max": [10, 80],
            },
        }
        parsed = parse_weather_response(geo, raw_api)
        self.assertEqual(parsed["city"], "Berlin")
        self.assertEqual(parsed["current"]["temperature_c"], 18.5)
        self.assertEqual(parsed["current"]["temperature_f"], 65.3)
        self.assertEqual(parsed["current"]["condition"], "Partly cloudy")
        self.assertEqual(len(parsed["forecast"]), 2)
        self.assertEqual(parsed["forecast"][1]["description"], "Slight rain")

    def test_empty_city_validation(self):
        with self.assertRaises(CityNotFoundError):
            geocode_city("")
        with self.assertRaises(CityNotFoundError):
            geocode_city("   ")


if __name__ == "__main__":
    unittest.main()
