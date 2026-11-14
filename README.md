# Auspify Technologies — Python Development Internship

**Intern Name:** Sheena Parwaz  
**Domain:** Python Development Internship  
**Organization:** Auspify Technologies  
**Internship Requirement:** Complete at least 4 out of 6 assigned tasks  
**Status:** **4 / 4 Core Tasks Completed (Ready for Final Submission)**  

Comprehensive submission repository containing 4 production-grade Python applications with dual interfaces (Tkinter Desktop GUI + Interactive Command-Line Terminal), 62 passing unit tests, defensive error handling, and complete documentation.

---

## 📋 Completed Internship Projects Overview

| Task # | Project Title | Primary Interface | Key Capabilities | Automated Test Suite |
| :--- | :--- | :--- | :--- | :--- |
| **Task 1** | **Smart Password Generator Pro** | Modern Tkinter GUI + CLI | CSPRNG `secrets` entropy, profiles (Website, Wi-Fi, PIN), security strength scorer, clipboard sync | 11 unit tests (`test_password_generator.py`) |
| **Task 2** | **To-Do List Productivity Manager** | Tkinter Canvas GUI + CLI | JSON persistence, priority badges, category chips, search filters, undo/clear | 12 unit tests (`test_todo_list.py`) |
| **Task 3** | **Modern Calculator Application** | Dark Theme GUI + CLI | Safe AST parser, PEMDAS evaluation, history memory drawer, keyboard bindings | 23 unit tests (`test_calculator.py`) |
| **Task 4** | **Weather & Air Quality Dashboard** | Atmospheric Neon GUI + CLI | Open-Meteo REST API (zero API keys), AQI analysis, 10-hr timeline, 5-day daily forecast, mouse-wheel scrolling | 16 unit tests (`test_weather_app.py`) |

**Total Automated Test Coverage:** **62 Passing Tests** (100% standard library, zero `pip install` requirements).

---

## 🚀 Quick Execution Guide

All applications require only standard Python 3.10+ (no third-party dependencies required).

### Task 1: Password Generator
```powershell
# Desktop GUI
python Task_1_Password_Generator/smart_password_generator.py

# Run Unit Tests
python Task_1_Password_Generator/test_password_generator.py
```

### Task 2: To-Do List Application
```powershell
# Desktop GUI
python Task_2_To-Do_List_Application/todo_list_gui.py

# Interactive Terminal CLI
python Task_2_To-Do_List_Application/todo_list.py

# Run Unit Tests
python Task_2_To-Do_List_Application/test_todo_list.py
```

### Task 3: Calculator (GUI + CLI)
```powershell
# Desktop GUI
python Task_3_Calculator_GUI/calculator_gui.py

# Terminal CLI
python Task_3_Calculator_GUI/calculator.py

# Run Unit Tests
python Task_3_Calculator_GUI/test_calculator.py
```

### Task 4: Weather Information Application
```powershell
# Atmospheric Desktop Dashboard
python Task_4_Weather_Information_App/weather_gui.py

# Interactive Terminal CLI
python Task_4_Weather_Information_App/weather_app.py --city Hubballi

# Run Unit Tests
python Task_4_Weather_Information_App/test_weather_app.py
```

---

## 📦 Individual Submission Packages

Clean `.zip` archives with cache-cleaned source code, documentation, and test cases have been compiled directly to the Desktop:
1. `C:\Users\HP\Desktop\Smart_Password_Generator_Pro.zip`
2. `C:\Users\HP\Desktop\Task_2_To_Do_List_Application.zip`
3. `C:\Users\HP\Desktop\Task_3_Calculator_GUI.zip`
4. `C:\Users\HP\Desktop\Task_4_Weather_Information_App.zip`

---

## 🛡️ Engineering Highlights
- **Standard Library Compliance**: Developed strictly with Python standard library modules (`tkinter`, `urllib.request`, `json`, `datetime`, `ast`, `secrets`, `unittest`), guaranteeing seamless evaluation on any evaluator machine without dependency conflicts.
- **Robust Exception Handling**: Defensive programming prevents crashes from invalid network responses, corrupted JSON, illegal math syntax (e.g. division by zero, unclosed parentheses), or invalid file inputs.
- **High-DPI & Screen Compatibility**: Responsive layouts with mouse-wheel canvas scrolling optimized for standard laptop screens (1366×768) and high-resolution monitors alike.
