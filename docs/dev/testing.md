# Testing

[← Docs index](../README.md) · Developer documentation (English)

Phone Bridge is a GUI app that drives hardware (a phone). The test-suite therefore has four layers, and none of them needs a phone: a **fake `adb`** stands in for it.

| Layer | Command | Count | Needs |
|---|---|---|---|
| Unit | `python -m pytest` | 23 | Python deps (offscreen Qt) |
| GUI end-to-end | `xvfb-run -a python tests/gui_e2e.py --lang fa` (and `en`) | 70 per language | Xvfb (Linux) or any desktop session |
| Phone web page | `cd tests/page && npm install && npm test` | 72 | Node ≥ 18 |
| Lint | `ruff check .` | — | ruff |

CI (`.github/workflows/ci.yml`) runs all of them on every push/PR: lint · unit on Python **3.10 / 3.12 / 3.13** · e2e in **fa** and **en** · page tests · Markdown link check.

## Setup

```bash
pip install -r requirements-dev.txt            # PyQt6, pynput, pytest, ruff, opencv, numpy, Pillow
# Linux only, for the GUI test:
sudo apt install xvfb libegl1 libgl1 libxkbcommon-x11-0 libxcb-cursor0 libxcb-icccm4 libxcb-image0 \
                 libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 libxcb-shape0 libxcb-xinerama0 libxcb-xkb1
chmod +x tests/fake_adb/adb
```

## Unit tests — `tests/test_units.py`

Fast, no window. Highlights:

- helpers: `human()`, `shq()` (shell quoting), `parse_mdns()`, the `ls -la` regex (modern and old formats), `_restart_argv()`, `_data_dir()`.
- **QR encoder**: geometry and finder patterns; version grows with payload; round-trip decode with OpenCV (skipped if OpenCV isn't installed).
- icons render (every entry in `ICONS`).
- **Translation guards** — these fail the build when:
  - a `tr("…")` string has no English entry in `EN`;
  - an English entry has different `%s/%d` placeholders;
  - an `EN` entry is no longer used by any `tr()` call;
  - a Persian string literal appears in the code **without** `tr()` (docstrings, the `EN` table and the web page excluded).
- the web page has its placeholders, no external `src/href`, and its `fa`/`en` tables have identical keys.

## GUI end-to-end — `tests/gui_e2e.py`

Starts the **real `MainWindow`**, with:

- `tests/fake_adb/adb` first on `PATH` (a Python script that answers `devices`, `wm size`, `exec-out screencap`, `shell …`, `pull/push/install`, `logcat`, `screenrecord`, mdns, …) and **logs every command** to a file;
- `tests/assets/demo_screen.png` as the "phone screen";
- a throw-away `HOME` and `PHONE_BRIDGE_HOME` in a temp dir (nothing of yours is touched; deleted afterwards unless `--keep`).

It then drives the UI (clicks real buttons, sends real Qt mouse/keyboard events to the phone view, calls the same slots the buttons call) and asserts:

- the exact `adb` commands that reached the "phone" (gestures, wake/unlock, rotate, brightness, media keys, macro playback loops, every Tools-tab command, app launch/stop/clear/uninstall, mkdir, push, install…);
- files created on the PC (screenshots, recorded video pulled, photo fetched, downloaded file with a space in its name, extracted split APKs);
- parsed data shown in the Info tab (model, RAM, storage, IP, battery gauge, live graph, ping), file list ordering and icons, app search/details;
- Logcat streaming, level filter, text search; terminal output;
- the **HTTP server** end to end (real requests from a thread): page + token + language injected, font served (and path-traversal refused), 403 on bad token, `/state`, `/inbox`, `/pcclip`, JPEG from `/screen`, every event type accepted, clipboard set;
- the **watchdog**: kill the persistent shell → app reconnects by itself.

It prints `PASS/FAIL` per check and exits non-zero on any failure. `--lang fa|en` runs the whole thing in that language (so layout direction and `tr()` are exercised too).

> **Teardown noise:** under Xvfb you may see `X IO Error` / `Unspecified Application Error` at the very end. That's Xvfb closing while Qt shuts down; the exit code is what matters.

### The fake adb

`tests/fake_adb/adb` (executable Python). Environment:

| Variable | Meaning |
|---|---|
| `FAKE_ADB_LOG` | file receiving `CMD …`, `SH> …` (persistent shell), `PUSH/PULL/INSTALL/RECORD` lines |
| `FAKE_ADB_SCREEN` | PNG returned by `screencap` |
| `FAKE_ADB_STATE` | folder for tiny flags (e.g. `stop_rec` written by `pkill screenrecord`) |

Add a command by extending the `elif cmd.startswith(...)` chain; make it print what the real tool would print (copy real output from a phone).

## Phone web page — `tests/page`

`dump_page.py` renders `PAGE` for `fa` and `en` (placeholders substituted); `page_test.js` loads each in **jsdom** with a mocked `fetch` and:

- checks there are no JS errors on load and after all actions; `lang`/`dir` attributes; 5 nav items; icon injection; language toggle;
- navigation to every view and the *More* sub-views;
- typing: text event, autocorrect/backspace **diff**, `Ctrl`+letter → combo and the box reverts;
- **trackpad**: one-finger move (accelerated), tap → click, two-finger tap → right-click, two-finger drag → 4 scroll notches, tap-then-drag → `mouse down` then `mouse up`;
- media, shortcut buttons, slide timer, **shutdown needs confirmation** (no event before the sheet is accepted), inbox text + link button, `/state` messages.

jsdom has no layout engine, so it can't judge looks — that's what the screenshot script is for.

## Screenshots

```bash
pip install PyQt6-WebEngine
xvfb-run -a python scripts/make_screenshots.py --fonts /path/to/Vazirmatn-ttf-folder
```

Regenerates everything in `docs/images/` from the real app (desktop window in both languages and light theme, every tab, the phone page rendered in real Chromium via Qt WebEngine, overview strips and the social-preview card). The fake adb and a brand-free demo screen keep private data out of the pictures.

## What the tests do **not** cover

- A real phone: Android versions/OEM quirks, real latency, `screenrecord`/camera behaviour, Xiaomi security toggles.
- Real keystrokes landing in other programs (the server calls `pynput`; tests assert the request is accepted, not what Windows does with it).
- The system tray, Windows firewall prompts, PyInstaller builds, macOS.
- Visual regressions (no pixel-diff tests; look at the regenerated screenshots in review).

If you can test on a real device, say which phone/Android version in your PR — that's valuable.

## Writing a new test

- Pure function → add to `tests/test_units.py`.
- New button/flow → add a `check(...)` in the next step of `tests/gui_e2e.py` (steps are chained with `QTimer`; use `wait_until()` for slow work) and, if it needs a new adb reply, teach the fake adb.
- New phone-page behaviour → add to `tests/page/page_test.js` (remember events are sent through an async queue: `await fl()` before asserting).
