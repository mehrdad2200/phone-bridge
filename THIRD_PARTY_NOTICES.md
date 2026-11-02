# Third-party notices

Phone Bridge's own source code is licensed under the [MIT License](LICENSE). It depends on, downloads or uses the following third-party software. Licences belong to their respective owners; check each project for the authoritative text.

## Runtime dependencies (installed with `pip install -r requirements.txt`)

| Component | Licence | Notes |
|---|---|---|
| [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) (and the Qt libraries it ships) | **GPL v3** or a commercial licence from Riverbank; Qt: LGPL v3 / GPL v3 / commercial | Not bundled in this repository; installed by `pip`. **Binary redistributions that include PyQt6 must comply with the GPL** — see [docs/dev/release.md](docs/dev/release.md#licensing-note-pyqt6-is-gpl). |
| [pynput](https://github.com/moses-palmer/pynput) | LGPL v3 | Keyboard/mouse control on the PC. |

## Downloaded at the user's request

| Component | Licence | When |
|---|---|---|
| [Vazirmatn](https://github.com/rastikerdar/vazirmatn) font (Saber Rastikerdar and contributors) | SIL Open Font License 1.1 | First run, if the font files are missing. May be bundled/redistributed together with its licence. |
| Android SDK **Platform-Tools** (`adb`) — Google LLC | Android Software Development Kit License Agreement | Only when the user presses *Download adb automatically*. Not redistributed by this project. |

## Optional: ADBKeyBoard

Typing non-ASCII text into the phone optionally uses the [ADBKeyBoard](https://github.com/senzhk/ADBKeyBoard) input method that the **user** installs on their phone. It is a separate project with its own licence; nothing of it is included here.

## Development / test / documentation tooling (not shipped)

pytest (MIT) · ruff (MIT) · OpenCV-Python (Apache-2.0) · NumPy (BSD-3-Clause) · Pillow (HPND) · jsdom (MIT) · PyQt6-WebEngine / Chromium (used only to render the screenshots in `docs/images`).

## Images

`assets/` (icon) and `docs/images/` (screenshots, social preview) were created for this project from its own UI. The demo phone wallpaper in `tests/assets/demo_screen.png` is an original illustration; it contains no third-party logos.

## Trademarks

*Android* is a trademark of Google LLC. *Windows* is a trademark of Microsoft Corporation. *Qt* is a trademark of The Qt Company. All other names are the property of their owners. This project is independent and is not affiliated with, sponsored or endorsed by them.
