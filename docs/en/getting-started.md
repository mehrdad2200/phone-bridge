# Getting started

[← Docs index](../README.md) · **English** · [فارسی](../fa/getting-started.md)

This guide takes you from nothing to a working connection. It has four parts: **install**, **prepare the phone**, **connect**, **first look**.

- [1. Install](#1-install)
- [2. Prepare the phone](#2-prepare-the-phone)
- [3. Connect — pick one method](#3-connect--pick-one-method)
- [4. First look](#4-first-look)
- [5. Use the phone as a remote](#5-use-the-phone-as-a-remote-for-the-pc)
- [Command-line options & data folder](#command-line-options--data-folder)

---

## 1. Install

### Requirements

| | |
|---|---|
| **Python** | 3.10 or newer (tested on 3.10, 3.12, 3.13). On Windows install from [python.org](https://www.python.org/downloads/) and tick **"Add python.exe to PATH"**. |
| **PC** | Windows 10/11 (primary), Linux (works; power commands from the phone page are Windows-only). macOS is untested. |
| **Phone** | Android 5.0+ for USB; **Android 11+** for wireless pairing / QR. |
| **Network** | For Wi-Fi use, phone and PC on the **same** Wi-Fi/LAN (not a guest network with "client isolation"). |
| **adb** | The app can download it for you (Google's *Platform-Tools*, ~7 MB) — or use your own. |

### Windows

1. Install Python 3.10+ (tick *Add to PATH*).
2. Download this repository (`Code → Download ZIP`, or `git clone`) and unzip it.
3. Double-click **`scripts\run.bat`**. The first time it installs the two dependencies (`PyQt6`, `pynput`), then opens the app.

Manual way (PowerShell / cmd):

```bat
cd path\to\phone-bridge
py -m pip install -r requirements.txt
py phone_bridge.py
```

> If `python` says *"Python was not found"* (Microsoft Store shortcut), use **`py`** instead, or turn off *App execution aliases* for python in Windows settings.

### Linux / macOS

```bash
./scripts/run.sh                       # creates .venv on first run
# or
pip install -r requirements.txt && python3 phone_bridge.py
```

On Linux you may need Qt's runtime libraries (`libxcb-cursor0`, `libxkbcommon-x11-0`, `libegl1`). On macOS, `pynput` needs *System Settings → Privacy & Security → Accessibility* permission for the terminal/app.

### As a package

```bash
pip install .          # from the repository folder
phone-bridge           # starts the app; settings live in ~/.phone-bridge
```

### First start

On the very first run the app downloads the **Vazirmatn** font (3 small files) into the `fonts` folder next to the script. If you're offline it falls back to a system font and tries again next time. You can also drop `Vazirmatn-Regular.ttf`, `-Medium.ttf`, `-Bold.ttf` into that folder yourself.

---

## 2. Prepare the phone

Do this once per phone.

1. **Enable Developer options** — *Settings → About phone* → tap **Build number** seven times (on some phones it's under *Software information*).
2. **Turn on USB debugging** — *Settings → System → Developer options → USB debugging*.
3. **Xiaomi / Redmi / POCO (MIUI/HyperOS) only:** also turn on **"USB debugging (Security settings)"** and, if offered, **"Install via USB"**. Without it, taps and typing are silently ignored although the screen is visible.
4. For **Wi-Fi without a cable (Android 11+)**: in Developer options turn on **Wireless debugging** (you may be asked to allow it on the current network).
5. Keep the phone **unlocked** the first time — Android shows an *"Allow USB debugging?"* prompt for each new computer; tick *Always allow* and accept.

---

## 3. Connect — pick one method

Open the **Connection** tab.

### Step A — get adb (one time)

| Button | What it does |
|---|---|
| **Find automatically** | Looks in `PATH`, next to the app, `ANDROID_HOME`, common folders. |
| **Choose adb.exe** | Pick it yourself (e.g. from an Android Studio SDK). |
| **Download adb automatically** | Downloads Google's *Platform-Tools* zip and unpacks it to `platform-tools/` next to the app. |
| **Open the download page in the browser** | If the download is blocked on your network: get the zip yourself, unzip, then *Choose adb.exe*. |

The status line shows ✅ and the path when adb is ready.

### Method 1 — USB cable (simplest)

1. Plug the phone in, accept the prompt on the phone.
2. Press the refresh button next to the device list → your phone appears as `device`.
3. Press **Connect to the selected device**.

The app switches to the **Control** tab as soon as the first picture arrives. If only one device is attached, it connects automatically at start-up.

*Want to unplug afterwards?* With the cable still attached press **Connected by USB; switch to Wi-Fi**. The app reads the phone's IP, runs `adb tcpip 5555`, connects wirelessly and tells you when you can unplug.

### Method 2 — QR code (Android 11+, no cable)

1. On the PC: **Create QR and start**. A QR code appears; the status reads *"Waiting for the phone to scan the QR…"*.
2. On the phone: *Developer options → Wireless debugging → **Pair device with QR code*** and scan the QR on the PC screen.
   *Use that scanner screen — the normal camera app cannot read it.*
3. The app discovers the phone on the network (mDNS), pairs, then connects. Status: *Phone found → Paired → ✅ Connected*. The Control tab opens.

How it works, in case something goes wrong: the QR contains a one-time service name and password (`WIFI:T:ADB;S:studio-xxxx;P:xxxxxxxx;;`). The phone advertises a pairing service with that name; the app finds it with `adb mdns services`, runs `adb pair <ip:port> <password>`, waits for the phone's connect service and runs `adb connect`. If your router blocks mDNS (guest Wi-Fi, "AP isolation", VPN) it times out after ~2.5 minutes — use Method 3.

### Method 3 — pairing code

1. On the phone: *Wireless debugging → **Pair device with pairing code***. Note the **IP:port** and the 6-digit code shown there.
2. In the app, under *Connect to the phone*: type that IP:port in **Pairing IP:port**, the code in **6-digit code**, press **Pair**.
3. Back on the main *Wireless debugging* screen note the (different!) **IP:port** and type it in the wireless field → **Connect**.

### Method 4 — manual

If the phone is already listening on a TCP port (e.g. after `adb tcpip 5555` from another tool), type `IP:5555` in the wireless field and press **Connect**. The last address is remembered.

---

## 4. First look

The **Control** tab:

- **Left of the toolbar:** the live phone view. Move the mouse over it — the pill at the bottom shows `x y #colour` of the pixel under the cursor; the top-left pill shows FPS.
- **Vertical toolbar:** Back · Home · Recents · Power · Volume ± · Screenshot · Copy image · Record · Rotate · Notifications · Open folder.
- **Side panel** (3 pages): *Control* (gesture pad, wake & unlock, brightness, media keys, display options), *Input* (type text on the phone), *Macro*.

Try it: click an icon on the phone view (= tap), drag to scroll (= swipe), spin the mouse wheel, right-click for Back.
To type: click the phone view once, then type on your keyboard.

Full explanation of everything: **[User guide](usage.md)**.

---

## 5. Use the phone as a remote for the PC

1. Tab **Keyboard & PC remote**. The server starts automatically and shows an address like `http://192.168.1.9:8765/?t=Ab3dEf9Z`.
2. On the phone (same Wi-Fi) open that address in any browser — or scan the QR shown below it with the camera app.
3. The page has five bottom tabs: **Type**, **Trackpad**, **Slides**, **Media**, **More** (shortcuts, PC screen, clipboard, system).
4. Windows may ask to allow Python through the firewall — choose **Private networks**.

Optional switches (off by default, in the same tab): *Show and control the PC screen from the phone*, *System commands (lock / sleep / shutdown)*.

---

## Command-line options & data folder

```text
phone-bridge --version          # print the version
phone-bridge --lang en|fa       # choose the interface language (remembered)
```

The language can also be switched in the app (header button **EN / فا**; the app restarts itself).

Where things are stored:

| What | Where |
|---|---|
| Settings (`phone_bridge_config.json`), fonts, downloaded `platform-tools/` | next to `phone_bridge.py` (portable). If installed with `pip`: `~/.phone-bridge`. If built as an exe: next to the exe. Override with the environment variable `PHONE_BRIDGE_HOME`. |
| Screenshots | `Pictures/PhoneBridge` |
| Screen recordings | `Videos/PhoneBridge` |
| Photos fetched from the phone | `Pictures/PhoneBridge` |

To reset everything, close the app and delete `phone_bridge_config.json`.

Next: **[User guide](usage.md)** · **[Troubleshooting](troubleshooting.md)**
