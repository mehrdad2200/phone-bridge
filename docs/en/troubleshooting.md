# Troubleshooting & FAQ

[← Docs index](../README.md) · **English** · [فارسی](../fa/troubleshooting.md)

Find your symptom, follow the fix. If it's still broken, open an issue with the **adb log** (Connection tab) — see [reporting a bug](#reporting-a-bug).

- [Starting the app](#starting-the-app)
- [adb & connecting](#adb--connecting)
- [The picture](#the-picture)
- [Taps and typing do nothing](#taps-and-typing-do-nothing)
- [QR / wireless pairing](#qr--wireless-pairing)
- [The phone remote page](#the-phone-remote-page)
- [Typing Persian into the phone](#typing-persian-into-the-phone)
- [Recording, camera, quick settings](#recording-camera-quick-settings)
- [Fonts & language](#fonts--language)
- [FAQ](#faq)
- [Reporting a bug](#reporting-a-bug)

---

## Starting the app

| Symptom | Cause → fix |
|---|---|
| `Python was not found; run without arguments to install from the Microsoft Store` | Windows' Store shortcut is shadowing Python. Use **`py phone_bridge.py`**, or reinstall Python with *Add python.exe to PATH*, or switch off *App execution aliases* for `python.exe` in Settings. |
| `ModuleNotFoundError: No module named 'PyQt6'` / `'pynput'` | `py -m pip install -r requirements.txt` (use the same `py`/`python` you run the app with). |
| You typed `pip install …` **inside** the Python prompt (`>>>`) | Type `exit()` first, then run the command in the normal terminal. |
| Running `phone_bridge(1).py` prints "not recognized" in PowerShell | Rename the file (no parentheses) and run `py phone_bridge.py`. |
| `qt.qpa.plugin: Could not load the Qt platform plugin "xcb"` (Linux) | `sudo apt install libxcb-cursor0 libxkbcommon-x11-0 libegl1`. |
| Window opens but is blank / crashes on a very new Python | Try Python 3.12 or 3.13; PyQt6 wheels for brand-new Python versions can lag. |
| Nothing happens after the language button | The app restarts itself; if it doesn't, start it again — the new language is already saved. |

## adb & connecting

| Symptom | Cause → fix |
|---|---|
| `[WinError 2] The system cannot find the file specified` or *adb not found* | adb isn't installed. **Connection tab → Download adb automatically** (or *Choose adb.exe*). |
| The download fails | Your network may block `dl.google.com`. Use **Open the download page in the browser**, unzip the Platform-Tools zip anywhere, then **Choose adb.exe**. |
| Device list shows `unauthorized` | Unlock the phone and accept **Allow USB debugging?** (tick *Always allow*). Still nothing? *Developer options → Revoke USB debugging authorizations*, replug. |
| Device shows `offline` | Replug the cable; toggle USB debugging off/on; or run `adb kill-server` and press refresh. |
| `more than one device/emulator` | Select the right entry in the device list before pressing *Connect to the selected device*; or disconnect the others. |
| Connects, then drops every few minutes (Wi-Fi) | Phone power-saving is killing Wi-Fi: set the phone's Wi-Fi to *always on*, exclude it from battery optimisation, keep *Reconnect automatically* ticked. |
| `adb devices` is empty with a cable | Use a **data** cable (not charge-only), set USB mode to *File transfer*, install your vendor's USB driver on Windows (Google USB driver or the manufacturer's). |

## The picture

| Symptom | Cause → fix |
|---|---|
| Black window with a red message under it | The message names the cause: `unauthorized`, `offline`, "screencap returned no image", … Fix that first. |
| "The phone image is completely black" | The phone screen is **off/locked** (press *Wake and unlock*), or the foreground app blocks screenshots (banking apps, some video apps, screens marked *secure*). This is an Android restriction; nothing in Phone Bridge can bypass it. |
| Picture updates slowly (1–3 FPS) | It is screenshot-based. Use **Live screen → Fast (0.25 s)**, prefer a **USB cable** over weak Wi-Fi, close the Developer tab's logcat, and note that some phones take 300–600 ms per `screencap`. For smooth video use scrcpy. |
| Picture is sideways | Rotate the phone, or use the **Rotate** toolbar button. |
| Picture is blurry | The view is scaled to fit the window — enlarge the window. |

## Taps and typing do nothing

The screen is visible but clicking has no effect:

1. **Xiaomi / Redmi / POCO:** *Developer options → **USB debugging (Security settings)*** must be on (it asks you to sign in to a Mi account). Same for some Oppo/Realme/Vivo builds: look for *"Disable permission monitoring"* / *"USB debugging (security)"*.
2. Test by hand: open **Developer tab → adb terminal** and run `input tap 540 1200`. If that doesn't tap either, it's a phone setting, not the app.
3. The device might be showing a secure system dialog (permission prompt, lock screen) that ignores injected input — touch it on the phone once.

Typing: ASCII works if a text field is focused on the phone. For Persian see [below](#typing-persian-into-the-phone).

## QR / wireless pairing

| Symptom | Cause → fix |
|---|---|
| The phone's normal camera shows a weird text or nothing | Scan from **Developer options → Wireless debugging → Pair device with QR code** (it opens its own scanner). |
| "Timed out; the phone didn't scan the QR" | The PC never saw the phone's pairing service. Check: phone and PC on the **same** Wi-Fi; not a *guest* network / *AP isolation*; **no VPN** on either; Wireless debugging switched on; the Windows firewall allows `adb.exe` on private networks. Then try again or use **pairing code**. |
| "This adb version doesn't support mDNS" | Update to the latest Platform-Tools (use the app's download button). |
| "Pairing failed" | The one-time code expired — press **Create QR and start** again. |
| "Paired, but the connection port wasn't found" | Paired fine; type the **IP:port** from the main *Wireless debugging* screen into the wireless field and press **Connect**. |
| Works for a day, then fails | The wireless port changes whenever Wireless debugging is toggled or the phone reboots — pair/connect again. |
| Phone is on mobile hotspot from the PC (or vice-versa) | Works, but mDNS may be filtered; prefer the pairing code. |

## The phone remote page

| Symptom | Cause → fix |
|---|---|
| The address doesn't open on the phone | Same Wi-Fi? Use **http://** (not https). Allow Python in the Windows firewall for **Private** networks (Start → *Allow an app through Windows Firewall*). Router with "client isolation"? Try a hotspot from the phone. |
| `403 forbidden` | The link's token is stale. A new random token is generated **every time the app starts** (and when you press *New token*), so old bookmarks stop working. Copy the current address from the app or scan its QR again. |
| "Port is in use" in the app | Another program uses 8765. Change **Port**, toggle the server off/on. |
| Typing works but the cursor jumps / text duplicates | Press **Clear box** after finishing a sentence; it keeps a copy of the box content to compute differences. |
| Trackpad is too fast/slow | Speed is fixed at a comfortable default in v1.0; see the roadmap. Two-finger scrolling is *natural* (content follows fingers). |
| *PC screen* says it's off | Tick **Show and control the PC screen from the phone** in the app. |
| *System* buttons do nothing | Tick **System commands** in the app; only Windows is supported. |
| Persian text typed on the phone shows as boxes on the PC | The PC app you type into lacks Persian font/keyboard support — not a Phone Bridge issue. |
| Fonts on the page look like Tahoma, not Vazirmatn | The fonts weren't on the PC when the page loaded. Check the `fonts` folder next to the script contains `Vazirmatn-*.ttf`, reload the page. |

## Typing Persian into the phone

Two different things get mixed up here:

- **Phone → PC (typing on the PC with the phone's keyboard):** Persian works out of the box — use the *Type* page of the remote.
- **PC → phone (typing into a field on the phone from the PC):** `adb` can inject ASCII keystrokes only, **not** Persian letters. For Persian/Unicode you need a small helper keyboard on the phone:

1. Install the open-source **[ADBKeyBoard](https://github.com/senzhk/ADBKeyBoard)** APK on the phone (you can simply drop the `.apk` onto the Phone Bridge window and it installs it).
2. Enable it as an input method and select it (phone settings → *Languages & input → On-screen keyboard*; or with the `ime enable` / `ime set` commands from the ADBKeyBoard README, which you can run in the **adb terminal**).
3. In Phone Bridge: *Control → Input* → tick **Persian/Unicode via ADBKeyboard**, type in the box, press **Send**. The app sends the text Base64-encoded as an `ADB_INPUT_B64` broadcast, which that keyboard types into the focused field.
4. Switch your normal keyboard back afterwards.

Typing directly on the phone *view* with your PC keyboard uses the same path for non-ASCII characters (and shows a hint if the option is off).

## Recording, camera, quick settings

| Symptom | Cause → fix |
|---|---|
| Recording says failed / empty file | `screenrecord` isn't available on some phones (and is blocked while DRM/secure content plays). The limit is 3 minutes per recording. Check free space on the phone. |
| Camera button didn't take a photo | Not every camera app reacts to the shutter key event. Tap the shutter on the phone view, then press **Fetch the latest phone photo**. |
| *Mobile data / Wi-Fi / Do not disturb / Dark mode* do nothing | These use `svc`/`cmd` shell commands that some Android versions or OEM builds restrict. Check the status bar message; try the same command in the *adb terminal* and tell us the output in an issue. |
| *Clear cache of all apps* seems to do nothing | Android 8+ restricts this for the shell user on many phones; clear individual apps from the **Apps** tab instead. |
| *Brightness* slider ignored | Some OEMs override it with adaptive brightness; disable adaptive brightness on the phone. |

## Fonts & language

- The app shows Persian with **Vazirmatn**. If you see another font, check the `fonts` folder (see [data folder](getting-started.md#command-line-options--data-folder)). Delete it to force a re-download.
- To start in a language: `python phone_bridge.py --lang en` (or `fa`).
- Right-to-left layout is automatic for Persian; if a mixed English/Persian label looks odd, that's the Unicode bidi algorithm — please report it with a screenshot.

## FAQ

**Do I need to install an app on the phone?**
No. Everything goes through `adb` (PC→phone) and the phone's browser (phone→PC). Only *typing Persian into the phone* optionally needs the ADBKeyBoard IME.

**Does it work over USB and Wi-Fi?**
Both. USB is faster and more stable; Wi-Fi is convenient.

**Does it need internet?**
No. Internet is only used for optional downloads (fonts, Platform-Tools). The phone page and everything else work on a LAN without internet. (The *Ping* test needs the phone to reach its target.)

**Does the phone page work on iPhone?**
It is a normal web page and should work in Safari, but it was designed and tested for Android/Chrome-like browsers; haptics (`navigator.vibrate`) are unavailable on iOS.

**Is it safe?**
Read [security](security.md). Short version: random token, LAN only, risky features opt-in, no telemetry.

**Can several PCs control one phone, or one PC several phones?**
One phone at a time per window. You can run two windows with different `PHONE_BRIDGE_HOME` folders and ports.

**Why is it screenshot-based and not video?**
Simplicity and zero phone-side install. Video needs a helper process on the phone (that's what scrcpy does).

**Where are my settings?**
`phone_bridge_config.json` in the data folder — see [getting started](getting-started.md#command-line-options--data-folder).

**How do I update?**
`git pull` (or download the new ZIP) — settings are kept because they live in the data folder / are git-ignored.

**How do I uninstall?**
Delete the folder (and `~/.phone-bridge` if you used pip). On the phone: *Developer options → Revoke USB debugging authorizations* and turn Wireless debugging off.

## Reporting a bug

Open an issue with the form and include:

1. `python phone_bridge.py --version`, your OS, Python version.
2. Phone model + Android version (+ UI skin: MIUI, One UI, …).
3. How you connect (USB / QR / code).
4. The **adb log** box from the Connection tab and any red message under the phone view.
5. A screenshot if it's visual.

Never post your pairing codes, QR images or the remote-page address (it contains your access token).
