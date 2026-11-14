# Test Cases — Smart Password Generator Pro

## Testing Environment

- **Operating System:** Windows 10 / 11
- **Programming Language:** Python 3.10+
- **IDE:** Visual Studio Code
- **GUI Framework:** Tkinter / ttk
- **Random Number Generator:** Python `secrets` module (Cryptographically Secure Pseudo-Random Number Generator - CSPRNG)

---

## Test Results

| ID | Test | Expected Result | Actual Result | Status |
|---|---|---|---|---|
| **TC01** | Launch application | Main window opens with all controls initialized | Main window displays with profile selectors, character option checkboxes, and generation button | **Pass** |
| **TC02** | Generate password | Password appears in list with correct length and character sets | Password of selected length (default 20) appears in generated list | **Pass** |
| **TC03** | Select Numeric PIN profile | Only digits are generated (length 8) | Generated output contains only digits `0-9` with exact length 8 | **Pass** |
| **TC04** | Generate 5 passwords | Five unique passwords appear in the output list | 5 distinct passwords are created and listed without duplication | **Pass** |
| **TC05** | Copy selected password | Selected password copies to system clipboard | Password is copied to clipboard; paste verification succeeds | **Pass** |
| **TC06** | Analyze a common password | Rating and security feedback appear for weak/common passwords | Feedback correctly flags common pattern and suggests improvements | **Pass** |
| **TC07** | Enter invalid settings | Error message dialog appears preventing invalid state | Validation triggers when length is out of bounds or all character types are disabled | **Pass** |
| **TC08** | Exclude ambiguous characters | Excluded characters (`O`, `0`, `I`, `l`, `1`) do not appear in generated passwords | Tested across 50 iterations; zero ambiguous characters present in output | **Pass** |

---

## Detailed Test Logs

### TC01: Launch Application
- **Input:** Execute `python smart_password_generator.py`
- **Output:** GUI window titled *"Smart Password Generator Pro"* rendered cleanly at dimensions 760x690.
- **Verification:** UI components (Preset Profile dropdown, Character Types checkboxes, Length slider, Batch Count, Output Listbox, and Password Analyzer) initialized in valid states.

### TC02: Password Generation (Default Profile)
- **Input:** Profile "Strong Password", Length = 20, Character Types: Upper, Lower, Digits, Symbols.
- **Output:** E.g. `=#V(-1squ5!1KN00` (length 20).
- **Verification:** Length matches 20; contains at least one uppercase, lowercase, digit, and symbol.

### TC03: Numeric PIN Profile
- **Input:** Profile "Numeric PIN" (Length = 8, Only Digits enabled).
- **Output:** E.g. `48896551`.
- **Verification:** Length is 8; `password.isdigit()` evaluates to `True`.

### TC04: Batch Generation (5 Passwords)
- **Input:** Count = 5, Length = 12.
- **Output:** 5 generated passwords added to list.
- **Verification:** All 5 items are distinct strings; `len(set(passwords)) == 5`.

### TC05: Clipboard Copy
- **Input:** Select generated password and click "Copy Password".
- **Output:** Notification indicating password copied.
- **Verification:** Windows clipboard buffer matches the selected password string.

### TC06: Security Analyzer Evaluation
- **Input:** Entered password `password123`.
- **Output:** Rating: `Weak (estimated)`, Score: `0/6`.
- **Feedback:** "Use at least 12 characters; 16 or more is preferable", "Consider using more character types", "This matches a commonly used password pattern".
- **Verification:** Detected dictionary pattern and insufficient character variance.

### TC07: Boundary & Error Handling
- **Input A:** Password length set to `0`.
- **Output A:** `ValueError` caught: *"Length must be between 1 and 128."*
- **Input B:** All character category checkboxes unchecked.
- **Output B:** `ValueError` caught: *"Select at least one character type."*
- **Verification:** Input validation prevents execution and alerts the user.

### TC08: Ambiguous Character Exclusion
- **Input:** `exclude_ambiguous = True`, Length = 30.
- **Output:** Checked across 50 sample generations.
- **Verification:** None of the characters `O, 0, I, l, 1` appeared in any of the 50 outputs.

---

## Notes

- All test cases were executed and verified against `smart_password_generator.py` in the Windows environment.
- The built-in Security Analyzer provides an educational metric based on length, entropy, and dictionary lookups; it does not replace multi-factor authentication or cryptographic hardware security.
