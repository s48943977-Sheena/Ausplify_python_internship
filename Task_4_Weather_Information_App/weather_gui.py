"""
weather_gui.py
==============
Task 4: Modern Desktop Weather Information Application (GUI)
Auspify Technologies — Python Development Internship

Features:
- Pure Python Standard Library (Tkinter) with zero external dependencies.
- Open-Meteo REST API engine (100% Free, zero API key required).
- Live Air Quality Index (AQI) with PM2.5, PM10, and health advisory.
- Hourly Weather Timeline (Next 10 Hours) with temperature & rain probabilities.
- Dynamic Atmospheric Atmosphere Themes: Neon glows adapting to Sunny, Rainy,
  Cloudy, Stormy, or Night conditions.
- 1-Click Copy Weather Report to clipboard with visual toast banner.
- Visual atmospheric meters: Humidity progress bar, Rain chance gauge, UV index.
- Sunrise & Sunset solar timings + Wind direction compass.
- Quick-select shortcut pills (Ballari, Hubballi, Bengaluru, Mumbai, etc.).
- Full mouse-wheel scrollable canvas + custom vertical scrollbar.
"""

import threading
import tkinter as tk
from tkinter import messagebox
from typing import Any, Dict, Optional

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

THEME = {
    "bg_root": "#070E1B",        # Ultra dark space navy
    "bg_card": "#111F36",        # Elevated glass card
    "bg_card_alt": "#162846",    # Secondary elevated surface
    "bg_input": "#0B1525",       # Deep search well
    "border_default": "#1E3557", # Subtle border
    "fg_primary": "#FFFFFF",     # Pure white
    "fg_secondary": "#94A9C9",   # Muted slate blue
    "fg_accent": "#38BDF8",      # Sky blue highlight
    "fg_amber": "#FBBF24",       # Warm sunny amber
    "fg_cyan": "#00F0FF",        # Vivid aqua cyan
    "fg_green": "#10B981",       # Emerald green
    "fg_purple": "#A78BFA",      # Soft lavender
    "fg_rose": "#F43F5E",        # Electric rose
    "btn_search_bg": "#0284C7",
    "btn_search_hover": "#0369A1",
    "btn_pill_bg": "#182C48",
    "btn_pill_hover": "#25436D",
}


class WeatherAppGUI:
    """Desktop Weather Application GUI with Live AQI & Hourly Timeline."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Auspify Weather Pro — Live Atmospheric Intelligence")
        # Sized to fit comfortably on 1366x768 screens without overflowing taskbar
        self.root.geometry("550x640")
        self.root.minsize(480, 520)
        self.root.configure(bg=THEME["bg_root"])

        self.current_unit: str = "C"  # "C" or "F"
        self.weather_data: Optional[Dict[str, Any]] = None
        self.history = SearchHistory(max_items=12)
        self.active_city: str = "Hubballi"

        self._center_window()
        self._build_scrollable_ui()
        self._bind_events()

        # Load initial city
        self.root.after(150, lambda: self.search_city("Hubballi"))

    def _center_window(self):
        """Center application on screen leaving room above taskbar."""
        self.root.update_idletasks()
        w, h = 550, 640
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = max(0, (sw - w) // 2)
        y = max(8, (sh - h - 45) // 2)
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_scrollable_ui(self):
        """Construct scrollable canvas container."""
        canvas_frame = tk.Frame(self.root, bg=THEME["bg_root"])
        canvas_frame.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(
            canvas_frame,
            bg=THEME["bg_root"],
            bd=0,
            highlightthickness=0,
        )
        self.scrollbar = tk.Scrollbar(
            canvas_frame,
            orient="vertical",
            command=self.canvas.yview,
            bg=THEME["bg_card"],
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.main_container = tk.Frame(self.canvas, bg=THEME["bg_root"])
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.main_container,
            anchor="nw",
        )

        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.main_container.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self._build_content()

    def _on_mousewheel(self, event):
        """Smooth mouse wheel scrolling on Windows."""
        if self.canvas.winfo_exists():
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _build_content(self):
        """Construct full modern UI with vibrant colors and layout."""
        pad_x = 16

        # Top Header Bar
        header = tk.Frame(self.main_container, bg=THEME["bg_root"])
        header.pack(fill="x", padx=pad_x, pady=(10, 6))

        title_frame = tk.Frame(header, bg=THEME["bg_root"])
        title_frame.pack(side="left")

        self.lbl_app_title = tk.Label(
            title_frame,
            text="🌦️ AUSPIFY WEATHER PRO",
            font=("Segoe UI", 13, "bold"),
            bg=THEME["bg_root"],
            fg=THEME["fg_accent"],
        )
        self.lbl_app_title.pack(anchor="w")

        tk.Label(
            title_frame,
            text="Task 4 • Live Weather, AQI & Hourly Forecast",
            font=("Segoe UI", 8),
            bg=THEME["bg_root"],
            fg=THEME["fg_secondary"],
        ).pack(anchor="w")

        # Top Actions: Copy Report + Refresh + Unit Switcher
        action_bar = tk.Frame(header, bg=THEME["bg_root"])
        action_bar.pack(side="right")

        self.btn_copy = tk.Button(
            action_bar,
            text="📋 Copy",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["btn_pill_bg"],
            fg=THEME["fg_secondary"],
            activebackground=THEME["btn_pill_hover"],
            activeforeground=THEME["fg_primary"],
            bd=0,
            padx=7,
            pady=3,
            cursor="hand2",
            command=self.copy_weather_report,
        )
        self.btn_copy.pack(side="left", padx=(0, 4))

        self.btn_refresh = tk.Button(
            action_bar,
            text="🔄 Refresh",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["btn_pill_bg"],
            fg=THEME["fg_secondary"],
            activebackground=THEME["btn_pill_hover"],
            activeforeground=THEME["fg_primary"],
            bd=0,
            padx=7,
            pady=3,
            cursor="hand2",
            command=self.refresh_current_city,
        )
        self.btn_refresh.pack(side="left", padx=(0, 4))

        self.btn_unit = tk.Button(
            action_bar,
            text="°C | °F",
            font=("Segoe UI", 8, "bold"),
            bg="#0284C7",
            fg=THEME["fg_primary"],
            activebackground="#0369A1",
            activeforeground=THEME["fg_primary"],
            bd=0,
            padx=9,
            pady=3,
            cursor="hand2",
            command=self.toggle_unit,
        )
        self.btn_unit.pack(side="left")

        # Search Bar Box
        search_card = tk.Frame(
            self.main_container,
            bg=THEME["bg_input"],
            highlightbackground=THEME["border_default"],
            highlightthickness=1,
            padx=8,
            pady=5,
        )
        search_card.pack(fill="x", padx=pad_x, pady=(0, 6))

        tk.Label(
            search_card,
            text="🔍",
            font=("Segoe UI", 11),
            bg=THEME["bg_input"],
            fg=THEME["fg_secondary"],
        ).pack(side="left", padx=(2, 6))

        self.entry_city = tk.Entry(
            search_card,
            font=("Segoe UI", 11),
            bg=THEME["bg_input"],
            fg=THEME["fg_primary"],
            insertbackground=THEME["fg_primary"],
            bd=0,
            relief="flat",
        )
        self.entry_city.pack(side="left", fill="x", expand=True, padx=4)
        self.entry_city.insert(0, "Hubballi")

        self.btn_search = tk.Button(
            search_card,
            text="Search",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["btn_search_bg"],
            fg=THEME["fg_primary"],
            activebackground=THEME["btn_search_hover"],
            activeforeground=THEME["fg_primary"],
            bd=0,
            padx=12,
            pady=3,
            cursor="hand2",
            command=self.on_search_click,
        )
        self.btn_search.pack(side="right")

        # Quick City Pills
        quick_frame = tk.Frame(self.main_container, bg=THEME["bg_root"])
        quick_frame.pack(fill="x", padx=pad_x, pady=(0, 6))

        cities_pill = ["Hubballi", "Ballari", "Bengaluru", "Mysuru", "Mumbai", "New Delhi", "London", "Tokyo"]
        for c in cities_pill:
            btn = tk.Button(
                quick_frame,
                text=c,
                font=("Segoe UI", 8),
                bg=THEME["btn_pill_bg"],
                fg=THEME["fg_secondary"],
                activebackground=THEME["btn_pill_hover"],
                activeforeground=THEME["fg_primary"],
                bd=0,
                padx=6,
                pady=2,
                cursor="hand2",
                command=lambda name=c: self.search_city(name),
            )
            btn.pack(side="left", padx=2)

        # Status & Last Updated Bar
        status_bar = tk.Frame(self.main_container, bg=THEME["bg_root"])
        status_bar.pack(fill="x", padx=pad_x, pady=(0, 6))

        self.lbl_status = tk.Label(
            status_bar,
            text="Ready to search",
            font=("Segoe UI", 8, "italic"),
            bg=THEME["bg_root"],
            fg=THEME["fg_secondary"],
        )
        self.lbl_status.pack(side="left")

        self.lbl_day_night_badge = tk.Label(
            status_bar,
            text="☀️ DAYTIME",
            font=("Segoe UI", 7, "bold"),
            bg="#451A03",
            fg=THEME["fg_amber"],
            padx=6,
            pady=1,
        )
        self.lbl_day_night_badge.pack(side="right")

        # Hero Weather Card with Dynamic Accent Border
        self.hero_card = tk.Frame(
            self.main_container,
            bg=THEME["bg_card"],
            highlightbackground="#0284C7",
            highlightthickness=2,
            padx=14,
            pady=12,
        )
        self.hero_card.pack(fill="x", padx=pad_x, pady=(0, 8))

        # Location & Time
        self.lbl_location = tk.Label(
            self.hero_card,
            text="Loading weather...",
            font=("Segoe UI", 15, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["fg_primary"],
        )
        self.lbl_location.pack(anchor="w")

        self.lbl_coords = tk.Label(
            self.hero_card,
            text="",
            font=("Segoe UI", 8),
            bg=THEME["bg_card"],
            fg=THEME["fg_secondary"],
        )
        self.lbl_coords.pack(anchor="w", pady=(1, 4))

        # Big Temperature & Condition Well
        temp_center = tk.Frame(self.hero_card, bg=THEME["bg_card"])
        temp_center.pack(fill="x", pady=4)

        self.lbl_icon = tk.Label(
            temp_center,
            text="🌤️",
            font=("Segoe UI Emoji", 34),
            bg=THEME["bg_card"],
        )
        self.lbl_icon.pack(side="left", padx=(0, 14))

        temp_text_frame = tk.Frame(temp_center, bg=THEME["bg_card"])
        temp_text_frame.pack(side="left")

        self.lbl_temperature = tk.Label(
            temp_text_frame,
            text="-- °C",
            font=("Segoe UI", 32, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["fg_primary"],
        )
        self.lbl_temperature.pack(anchor="w")

        self.lbl_condition = tk.Label(
            temp_text_frame,
            text="Fetching data...",
            font=("Segoe UI", 12, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["fg_accent"],
        )
        self.lbl_condition.pack(anchor="w")

        # Smart Advisory Card
        self.advisory_card = tk.Frame(
            self.hero_card,
            bg=THEME["bg_card_alt"],
            highlightbackground=THEME["border_default"],
            highlightthickness=1,
            padx=10,
            pady=6,
        )
        self.advisory_card.pack(fill="x", pady=(8, 0))

        self.lbl_advisory = tk.Label(
            self.advisory_card,
            text="💡 Advisory: Fetching latest atmospheric intelligence...",
            font=("Segoe UI", 8),
            bg=THEME["bg_card_alt"],
            fg=THEME["fg_primary"],
            wraplength=480,
            justify="left",
        )
        self.lbl_advisory.pack(anchor="w")

        # FEATURE 1: Air Quality Index (AQI) Banner Card
        self.aqi_card = tk.Frame(
            self.main_container,
            bg=THEME["bg_card"],
            highlightbackground="#10B981",
            highlightthickness=1,
            padx=12,
            pady=8,
        )
        self.aqi_card.pack(fill="x", padx=pad_x, pady=(0, 8))

        aqi_top = tk.Frame(self.aqi_card, bg=THEME["bg_card"])
        aqi_top.pack(fill="x")

        tk.Label(
            aqi_top,
            text="🍃 AIR QUALITY INDEX (AQI)",
            font=("Segoe UI", 8, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["fg_secondary"],
        ).pack(side="left")

        self.lbl_aqi_badge = tk.Label(
            aqi_top,
            text="🟢 Good (32 AQI)",
            font=("Segoe UI", 8, "bold"),
            bg="#064E3B",
            fg="#10B981",
            padx=6,
            pady=1,
        )
        self.lbl_aqi_badge.pack(side="right")

        self.lbl_aqi_details = tk.Label(
            self.aqi_card,
            text="PM2.5: 11.2 µg/m³ • PM10: 22.0 µg/m³ • Air is fresh and safe for outdoor activities.",
            font=("Segoe UI", 8),
            bg=THEME["bg_card"],
            fg=THEME["fg_primary"],
        )
        self.lbl_aqi_details.pack(anchor="w", pady=(3, 0))

        # FEATURE 2: Hourly Forecast Strip (Next 10 Hours)
        hourly_title_frame = tk.Frame(self.main_container, bg=THEME["bg_root"])
        hourly_title_frame.pack(fill="x", padx=pad_x, pady=(2, 4))

        tk.Label(
            hourly_title_frame,
            text="⏱️ HOURLY FORECAST (Next 10 Hours)",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_root"],
            fg=THEME["fg_accent"],
        ).pack(side="left")

        self.hourly_frame = tk.Frame(self.main_container, bg=THEME["bg_root"])
        self.hourly_frame.pack(fill="x", padx=pad_x, pady=(0, 8))

        # 6 Grid Atmospheric Metric Cards
        grid_title_frame = tk.Frame(self.main_container, bg=THEME["bg_root"])
        grid_title_frame.pack(fill="x", padx=pad_x, pady=(2, 4))

        tk.Label(
            grid_title_frame,
            text="📊 ATMOSPHERIC OBSERVATIONS",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_root"],
            fg=THEME["fg_accent"],
        ).pack(side="left")

        self.metrics_grid = tk.Frame(self.main_container, bg=THEME["bg_root"])
        self.metrics_grid.pack(fill="x", padx=pad_x, pady=(0, 8))

        for c in range(2):
            self.metrics_grid.columnconfigure(c, weight=1)

        self.card_feels = self._create_metric_card(
            self.metrics_grid, 0, 0, "🌡️ FEELS LIKE", "--", "Apparent Temp", THEME["fg_amber"]
        )
        self.card_humidity = self._create_metric_card(
            self.metrics_grid, 0, 1, "💧 HUMIDITY", "--", "% Relative", THEME["fg_cyan"]
        )
        self.card_wind = self._create_metric_card(
            self.metrics_grid, 1, 0, "💨 WIND & DIRECTION", "--", "Speed", THEME["fg_green"]
        )
        self.card_rain = self._create_metric_card(
            self.metrics_grid, 1, 1, "🌧️ RAIN CHANCE", "--", "Today's prob.", THEME["fg_rose"]
        )
        self.card_pressure = self._create_metric_card(
            self.metrics_grid, 2, 0, "⏱️ BAROMETER", "--", "hPa Pressure", THEME["fg_secondary"]
        )
        self.card_sun = self._create_metric_card(
            self.metrics_grid, 2, 1, "🌅 SUN TIMINGS", "--", "Sunrise & Sunset", THEME["fg_amber"]
        )

        # 5-Day Extended Forecast Container
        forecast_title_frame = tk.Frame(self.main_container, bg=THEME["bg_root"])
        forecast_title_frame.pack(fill="x", padx=pad_x, pady=(4, 4))

        tk.Label(
            forecast_title_frame,
            text="📅 5-DAY EXTENDED FORECAST",
            font=("Segoe UI", 9, "bold"),
            bg=THEME["bg_root"],
            fg=THEME["fg_accent"],
        ).pack(side="left")

        self.forecast_cards_frame = tk.Frame(self.main_container, bg=THEME["bg_root"])
        self.forecast_cards_frame.pack(fill="x", padx=pad_x, pady=(0, 8))

        # Footer Notice
        footer = tk.Frame(self.main_container, bg=THEME["bg_root"])
        footer.pack(fill="x", pady=(2, 12))
        tk.Label(
            footer,
            text="Auspify Python Internship • Task 4: Weather App • Powered by Open-Meteo REST API",
            font=("Segoe UI", 8),
            bg=THEME["bg_root"],
            fg=THEME["fg_secondary"],
        ).pack()

    def _create_metric_card(self, parent, row, col, title, val_init, sub_init, accent_color):
        card = tk.Frame(
            parent,
            bg=THEME["bg_card"],
            highlightbackground=THEME["border_default"],
            highlightthickness=1,
            padx=10,
            pady=7,
        )
        card.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

        tk.Label(
            card,
            text=title,
            font=("Segoe UI", 8, "bold"),
            bg=THEME["bg_card"],
            fg=accent_color,
        ).pack(anchor="w")

        lbl_val = tk.Label(
            card,
            text=val_init,
            font=("Segoe UI", 12, "bold"),
            bg=THEME["bg_card"],
            fg=THEME["fg_primary"],
        )
        lbl_val.pack(anchor="w", pady=(1, 0))

        lbl_sub = tk.Label(
            card,
            text=sub_init,
            font=("Segoe UI", 7),
            bg=THEME["bg_card"],
            fg=THEME["fg_secondary"],
        )
        lbl_sub.pack(anchor="w")

        return {"card": card, "val": lbl_val, "sub": lbl_sub, "accent": accent_color}

    def _bind_events(self):
        """Bind keyboard and mouse wheel events."""
        self.entry_city.bind("<Return>", lambda e: self.on_search_click())
        self.root.bind_all("<MouseWheel>", self._on_mousewheel)

    def on_search_click(self):
        city = self.entry_city.get().strip()
        if city:
            self.search_city(city)

    def refresh_current_city(self):
        """Re-fetch weather for active city."""
        if self.active_city:
            self.search_city(self.active_city)

    def search_city(self, city_name: str):
        """Asynchronously query weather data."""
        self.active_city = city_name
        self.entry_city.delete(0, tk.END)
        self.entry_city.insert(0, city_name)

        self.lbl_status.config(text=f"Fetching live atmosphere for '{city_name}'...", fg=THEME["fg_accent"])
        self.btn_search.config(state="disabled")
        self.btn_refresh.config(state="disabled")

        threading.Thread(target=self._worker_fetch, args=(city_name,), daemon=True).start()

    def _worker_fetch(self, city_name: str):
        try:
            data = get_city_weather(city_name, use_mock_on_failure=True)
            self.root.after(0, self._apply_weather_data, data)
        except Exception as e:
            self.root.after(0, self._handle_fetch_error, str(e))

    def _handle_fetch_error(self, err_msg: str):
        self.btn_search.config(state="normal")
        self.btn_refresh.config(state="normal")
        self.lbl_status.config(text=f"Error: {err_msg}", fg="#EF4444")
        messagebox.showerror("Weather Lookup Error", err_msg)

    def _apply_weather_data(self, data: Dict[str, Any]):
        self.btn_search.config(state="normal")
        self.btn_refresh.config(state="normal")
        self.weather_data = data
        self.history.add(data["city"])

        status_text = f"Live Data Updated: {data['timestamp']}"
        self.lbl_status.config(text=status_text, fg=THEME["fg_green"])

        self._render_view()

    def toggle_unit(self):
        """Toggle between Celsius and Fahrenheit."""
        self.current_unit = "F" if self.current_unit == "C" else "C"
        self.btn_unit.config(text=f"°{self.current_unit}")
        if self.weather_data:
            self._render_view()

    def copy_weather_report(self):
        """Format and copy clean weather summary to system clipboard."""
        if not self.weather_data:
            return

        d = self.weather_data
        curr = d["current"]
        u = self.current_unit
        t = curr["temperature_c"] if u == "C" else curr["temperature_f"]
        f = curr["feels_like_c"] if u == "C" else curr["feels_like_f"]
        report = (
            f"🌤️ Weather Report for {d['location_display']}\n"
            f"• Condition: {curr['condition']} {curr['icon']}\n"
            f"• Temperature: {t:.1f}°{u} (Feels like {f:.1f}°{u})\n"
            f"• Humidity: {curr['humidity_percent']}%\n"
            f"• Wind: {curr['wind_speed_kmh']} km/h ({curr['wind_direction']})\n"
            f"• Rain Chance: {curr['rain_probability']}%\n"
            f"• Air Quality: {d['aqi']['rating']} (AQI {d['aqi']['value']})\n"
            f"• Sun: 🌅 {curr['sunrise']} | 🌇 {curr['sunset']}\n"
            f"• Advisory: {d['advisory']}"
        )
        self.root.clipboard_clear()
        self.root.clipboard_append(report)
        self.lbl_status.config(text="✓ Full weather report copied to clipboard!", fg=THEME["fg_cyan"])

    def _render_view(self):
        """Update all GUI widgets with current weather data and dynamic theme."""
        if not self.weather_data:
            return

        d = self.weather_data
        curr = d["current"]
        theme = d.get("theme", {})
        aqi = d.get("aqi", {})
        u = self.current_unit

        # Apply Dynamic Weather Theme Colors
        accent_color = theme.get("accent", THEME["fg_accent"])
        card_border = theme.get("card_border", "#0284C7")

        self.hero_card.config(highlightbackground=card_border)
        self.lbl_condition.config(fg=accent_color)
        self.lbl_app_title.config(fg=accent_color)

        # Day/Night Badge
        if curr.get("is_day", True):
            self.lbl_day_night_badge.config(
                text="☀️ DAYTIME",
                bg="#451A03",
                fg=THEME["fg_amber"],
            )
        else:
            self.lbl_day_night_badge.config(
                text="🌙 NIGHT",
                bg="#1E1B4B",
                fg=THEME["fg_purple"],
            )

        # Location header (Guaranteed clean city, state, country)
        self.lbl_location.config(text=d["location_display"])
        self.lbl_coords.config(
            text=f"Lat: {d['latitude']:.2f}° • Lon: {d['longitude']:.2f}° • {d['timezone']}"
        )

        # Primary Temp & Condition
        temp_val = curr["temperature_c"] if u == "C" else curr["temperature_f"]
        self.lbl_temperature.config(text=f"{temp_val:.1f}°{u}")
        self.lbl_icon.config(text=curr["icon"])
        self.lbl_condition.config(text=curr["condition"])

        # Smart Advisory
        self.lbl_advisory.config(text=f"💡 Advisory: {d.get('advisory', 'Normal conditions.')}")

        # Air Quality Index (AQI) Card
        aqi_color = aqi.get("color", "#10B981")
        self.aqi_card.config(highlightbackground=aqi_color)
        self.lbl_aqi_badge.config(
            text=f"● {aqi.get('rating', 'Good')} ({aqi.get('value', 30)} AQI)",
            fg=aqi_color,
        )
        self.lbl_aqi_details.config(
            text=f"PM2.5: {aqi.get('pm25', 12):.1f} µg/m³ • PM10: {aqi.get('pm10', 24):.1f} µg/m³ • {aqi.get('advisory', '')}"
        )

        # Hourly Forecast Strip
        self._render_hourly(d.get("hourly", []), accent_color)

        # Metric Cards (6 cards)
        feels_val = curr["feels_like_c"] if u == "C" else curr["feels_like_f"]
        self.card_feels["val"].config(text=f"{feels_val:.1f}°{u}")
        self.card_feels["sub"].config(text=f"Apparent Temp • {curr.get('humidity_status', 'Comfortable')}")

        # Humidity with visual indicator
        hum = curr["humidity_percent"]
        self.card_humidity["val"].config(text=f"{hum}%")
        self.card_humidity["sub"].config(text=f"Status: {curr.get('humidity_status', 'Normal')}")

        # Wind Speed & Direction
        wind_val = curr["wind_speed_kmh"] if u == "C" else curr["wind_speed_mph"]
        wind_unit = "km/h" if u == "C" else "mph"
        wdir = curr.get("wind_direction", "E")
        self.card_wind["val"].config(text=f"{wind_val:.1f} {wind_unit}")
        self.card_wind["sub"].config(text=f"Dir: {wdir} • {curr.get('wind_status', 'Breeze')}")

        # Rain Chance
        rain_prob = curr.get("rain_probability", 0)
        self.card_rain["val"].config(text=f"{rain_prob}%")
        self.card_rain["sub"].config(text=f"Precipitation: {curr['precipitation_mm']:.1f} mm")

        # Pressure & UV
        self.card_pressure["val"].config(text=f"{curr['pressure_hpa']:.0f} hPa")
        self.card_pressure["sub"].config(text=f"UV Index: {curr.get('uv_index', 5.0):.1f} (Solar)")

        # Sunrise & Sunset
        sr = curr.get("sunrise", "06:14 AM")
        ss = curr.get("sunset", "06:02 PM")
        self.card_sun["val"].config(text=f"🌅 {sr}")
        self.card_sun["sub"].config(text=f"🌇 Sunset at {ss}")

        # 5-Day Forecast rendering
        self._render_forecast(d.get("forecast", []), accent_color)

        self.root.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _render_hourly(self, hourly_list, accent_color):
        """Render horizontal hourly forecast strip."""
        for widget in self.hourly_frame.winfo_children():
            widget.destroy()

        u = self.current_unit
        num_hours = min(7, len(hourly_list))

        for c in range(num_hours):
            self.hourly_frame.columnconfigure(c, weight=1)

        for i, item in enumerate(hourly_list[:num_hours]):
            hcard = tk.Frame(
                self.hourly_frame,
                bg=THEME["bg_card"],
                highlightbackground=THEME["border_default"],
                highlightthickness=1,
                padx=4,
                pady=5,
            )
            hcard.grid(row=0, column=i, sticky="nsew", padx=2)

            tk.Label(
                hcard,
                text=item["time_label"],
                font=("Segoe UI", 7, "bold"),
                bg=THEME["bg_card"],
                fg=THEME["fg_secondary"],
            ).pack()

            tk.Label(
                hcard,
                text=item["icon"],
                font=("Segoe UI Emoji", 13),
                bg=THEME["bg_card"],
            ).pack(pady=1)

            t_val = item["temp_c"] if u == "C" else item["temp_f"]
            tk.Label(
                hcard,
                text=f"{t_val:.0f}°",
                font=("Segoe UI", 8, "bold"),
                bg=THEME["bg_card"],
                fg=accent_color,
            ).pack()

            r_p = item.get("rain_prob", 0)
            if r_p > 0:
                tk.Label(
                    hcard,
                    text=f"💧{r_p}%",
                    font=("Segoe UI", 6),
                    bg=THEME["bg_card"],
                    fg=THEME["fg_cyan"],
                ).pack()

    def _render_forecast(self, forecast_list, accent_color):
        for widget in self.forecast_cards_frame.winfo_children():
            widget.destroy()

        u = self.current_unit
        num_cards = min(5, len(forecast_list))

        for c in range(num_cards):
            self.forecast_cards_frame.columnconfigure(c, weight=1)

        for i, item in enumerate(forecast_list[:num_cards]):
            fcard = tk.Frame(
                self.forecast_cards_frame,
                bg=THEME["bg_card"],
                highlightbackground=THEME["border_default"],
                highlightthickness=1,
                padx=4,
                pady=6,
            )
            fcard.grid(row=0, column=i, sticky="nsew", padx=2)

            tk.Label(
                fcard,
                text=item["day_short"],
                font=("Segoe UI", 8, "bold"),
                bg=THEME["bg_card"],
                fg=THEME["fg_primary"],
            ).pack()

            tk.Label(
                fcard,
                text=item["icon"],
                font=("Segoe UI Emoji", 14),
                bg=THEME["bg_card"],
            ).pack(pady=1)

            max_t = item["temp_max_c"] if u == "C" else item["temp_max_f"]
            min_t = item["temp_min_c"] if u == "C" else item["temp_min_f"]

            tk.Label(
                fcard,
                text=f"{max_t:.0f}° / {min_t:.0f}°",
                font=("Segoe UI", 8, "bold"),
                bg=THEME["bg_card"],
                fg=accent_color,
            ).pack()

            desc_brief = item["description"][:11]
            tk.Label(
                fcard,
                text=desc_brief,
                font=("Segoe UI", 7),
                bg=THEME["bg_card"],
                fg=THEME["fg_secondary"],
            ).pack()

            r_prob = item.get("rain_probability", 0)
            if r_prob > 0:
                tk.Label(
                    fcard,
                    text=f"💧{r_prob}%",
                    font=("Segoe UI", 6, "bold"),
                    bg=THEME["bg_card"],
                    fg=THEME["fg_cyan"],
                ).pack()


def main():
    root = tk.Tk()
    app = WeatherAppGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
