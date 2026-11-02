# Changelog

All notable changes are documented here. Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · Versioning: [SemVer](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-10-31

First public release.

### Added
- **PC → phone**: live, orientation-aware phone view; mouse = tap / long-press / swipe / scroll / Back / Home with ripple feedback; PC keyboard typing; icon toolbar (Back, Home, Recents, power, volume, screenshot, copy, record, rotate, notifications, open folder); pixel coordinates + colour picker and FPS on the view.
- **Connection**: USB, **QR pairing** (Android 11+), pairing code, manual `IP:port`, USB → Wi-Fi switch, automatic `adb` discovery / download / manual choice, auto-reconnect.
- **50 feature additions**: gesture pad, wake & unlock, rotate, quick screenshot, copy screenshot, screen recording, in-app shortcuts, media keys, brightness, macros (record / play / loop / save / load); quick settings (Wi-Fi, mobile data, DND, dark mode, stay awake, touch overlay, font size, screen timeout, settings shortcuts, close background apps, clear caches); device dashboard, battery gauge, live battery/RAM graph, ping test; file manager, upload, drag & drop, APK install, app manager, APK extraction, open link / dial / SMS, take-a-photo-and-fetch; Logcat and adb terminal; system-tray mode.
- **Phone → PC** web page (no install on the phone): typing with sticky modifiers, multi-touch trackpad, slide remote with timer, media keys, 20 shortcuts, shared clipboard, PC → phone messages, PC screen view/control (opt-in), lock/sleep/shutdown (opt-in, Windows).
- **UI**: minimal dark/light themes, vector icons, Vazirmatn font, English ⇄ Persian with full RTL/LTR layout, `--lang` / `--version` options.
- **Project**: unit, GUI end-to-end and phone-page tests with a fake `adb`; CI on Python 3.10 / 3.12 / 3.13; English + Persian documentation; screenshot generator.

### Security
- Remote server requires a random per-run token; screen sharing and power commands are off at every start. See [docs/en/security.md](docs/en/security.md) for the limits (plain HTTP, no rate limiting).
