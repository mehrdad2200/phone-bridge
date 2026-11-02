# Feature list

[← Docs index](../README.md) · **English** · [فارسی](../fa/features.md)

Everything Phone Bridge can do, grouped by where you find it. Details for each item are in the **[User guide](usage.md)**.

> *Verification legend* — **R** = confirmed on a real phone by a user · **S** = covered by automated tests against a simulated `adb` (behaviour on real phones can vary with Android version/manufacturer).

## Core

| Feature | Where | Verification |
|---|---|---|
| Live phone screen (orientation-aware, 0.25–1 s refresh) | Control | R, S |
| Mouse → tap, long-press, swipe, scroll, Back (right-click), Home (middle-click) with ripple feedback | Control | R, S |
| PC keyboard → typing & special keys on the phone | Control | R, S |
| Navigation keys (Back, Home, Recents), power, volume, notifications | Control toolbar | S |
| Connect by USB, QR pairing, pairing code, manual IP, USB→Wi-Fi switch | Connection | R (QR), S |
| Automatic `adb` discovery / download / manual choice | Connection | S |
| Dark & light themes, vector icons, Vazirmatn font | whole app | R |
| English ⇄ Persian UI, full RTL/LTR mirroring | header button | R, S |
| Phone as PC keyboard (autocorrect- and Persian-safe) and touchpad | phone page | S |

## The 50 additions

### Control tab (14)

| # | Feature | Notes |
|---|---|---|
| 1 | **Gesture pad** | ↑ ↓ ← → swipes and a double-tap button |
| 2 | **Wake & unlock / screen off** | wakes, swipes up; separate sleep button |
| 3 | **Rotate screen** | 90° steps; turns auto-rotate off |
| 4 | **Pixel coordinates & colour picker** | live `x y #RRGGBB` over the view |
| 5 | **FPS counter** | measured over the last 2 s |
| 6 | **Quick screenshot** | auto-named PNG in `Pictures/PhoneBridge` · `Ctrl+S` |
| 7 | **Copy screenshot to clipboard** | `Ctrl+Shift+C` |
| 8 | **Screen recording** | up to 3 min, auto-copied to `Videos/PhoneBridge` · `Ctrl+R` |
| 9 | **In-app shortcuts** | `Alt+←`, `Alt+Home`, `Alt+↓`, `Ctrl+S`, `Ctrl+R`, `Ctrl+Shift+C` |
| 10 | **Media controls** | previous / play-pause / next / mute |
| 11 | **Brightness slider** | |
| 12 | **Macro recording** | taps, swipes, keys, text with timing |
| 13 | **Macro playback** | 0.5×–4× speed, repeat N or ∞ |
| 14 | **Macro save / load** | JSON files |

### Tools tab (11)

| # | Feature |
|---|---|
| 15 | Wi-Fi on/off |
| 16 | Mobile data on/off |
| 17 | Do not disturb on/off |
| 18 | Dark mode on/off |
| 19 | Keep screen on while charging |
| 20 | Show touches + pointer coordinates overlay |
| 21 | Font-size slider |
| 22 | Screen-timeout presets (15 s – 30 min) |
| 23 | 12 shortcuts into Android settings pages |
| 24 | Close background apps |
| 25 | Clear cache of all apps |

### Info tab (4)

| # | Feature |
|---|---|
| 26 | Device dashboard (model, Android, CPU, RAM, storage, IP, …) + save report |
| 27 | Battery gauge (percent, temperature, charging state) |
| 28 | Live battery / RAM graph |
| 29 | Phone-side internet ping test |

### Files, apps & sending (10)

| # | Feature |
|---|---|
| 30 | **File manager** — browse, download, delete, new folder, rename, open |
| 31 | Upload files to the phone |
| 32 | **Drag & drop** files onto the window (APKs are installed automatically) |
| 33 | Install APK from PC |
| 34 | **App list** with search (+ system apps toggle) |
| 35 | App actions: launch · force-stop · clear data · uninstall · app info page |
| 36 | **Extract APK** (including split APKs) to PC |
| 37 | Open a **link** in the phone browser |
| 38 | Open the **dialer** / compose an **SMS** from the PC |
| 39 | **Take a photo with the phone camera and fetch it** (or fetch the latest photo) |

### Developer tab (2)

| # | Feature |
|---|---|
| 40 | **Logcat** — live, level filter, search, pause, save, clear |
| 41 | **adb terminal** — history, quick commands |

### Phone remote page (7)

| # | Feature |
|---|---|
| 42 | **Slide remote** with timer, F5 / Shift+F5 / Esc / B / W |
| 43 | **Media & volume** keys of the PC |
| 44 | **20 keyboard shortcuts** (Copy … Alt+Tab, Win+D, …) |
| 45 | **Lock / sleep / shutdown / restart** the PC (confirmation; opt-in; Windows) |
| 46 | **Shared clipboard** — phone → PC and PC → phone (fetch) |
| 47 | **PC → phone messages** (text/link with Copy / Open buttons) |
| 48 | **View & control the PC screen** from the phone (opt-in) |

### System (2)

| # | Feature |
|---|---|
| 49 | **System-tray mode** (keep running when the window closes) |
| 50 | **Auto-reconnect** when the phone drops |

## Also in the phone page (beyond the 50)

Multi-touch trackpad gestures (2-finger scroll, 2-finger-tap right-click, tap-then-drag), sticky Ctrl/Alt/Shift/Win, bilingual UI with its own EN/فا switch, dark/light following the phone, haptic feedback, font served from the PC (works offline).

## Ideas not implemented yet

Multi-device sessions · saved snippets · notification mirroring · clipboard sync to the phone (needs an Android helper app) · scrcpy-style H.264 video · PySide6 build · macOS support · bind-address selection and rate-limiting for the remote server. See [CONTRIBUTING](../../CONTRIBUTING.md).
