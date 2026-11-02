# Publishing & releasing

[← Docs index](../README.md) · Developer documentation (English)

- [Put the project on GitHub (first time)](#put-the-project-on-github-first-time)
- [Repository settings worth switching on](#repository-settings-worth-switching-on)
- [Versioning & changelog](#versioning--changelog)
- [Cutting a release](#cutting-a-release)
- [Building a Windows exe](#building-a-windows-exe)
- [Licensing note: PyQt6 is GPL](#licensing-note-pyqt6-is-gpl)

---

## Put the project on GitHub (first time)

1. Create an **empty** repository named `phone-bridge` on GitHub (no README/licence — they're already here).
2. In the unzipped project folder, replace the placeholder with your account name:
   ```bash
   python scripts/set_repo_owner.py YOUR_GITHUB_NAME          # badges, links, issue-template URLs
   python scripts/set_repo_owner.py --check                   # should report 0 placeholders
   ```
   (Different repository name? add `--repo my-name`.)
3. Put your real name or handle in `LICENSE` (it currently says *"Phone Bridge contributors"*; that's a valid choice too) and check `pyproject.toml`.
4. Initialise and push:
   ```bash
   git init -b main
   git add .
   git commit -m "Initial release v1.0.0"
   git remote add origin https://github.com/YOUR_GITHUB_NAME/phone-bridge.git
   git push -u origin main
   ```
5. Open the **Actions** tab — CI starts automatically. Everything should be green (lint, unit ×3 Python versions, GUI e2e ×2 languages, phone-page tests, docs links).
   > First time on GitHub: the Linux jobs install Qt libraries with `apt`; if one step fails because Ubuntu renamed a package, fix the package name in `ci.yml` — the tests themselves are verified to pass locally with the same command lines.

## Repository settings worth switching on

- **About → Topics:** `android`, `adb`, `remote-control`, `pyqt6`, `persian`, `farsi`, `rtl`, `trackpad`, `presentation-remote`.
- **Settings → General → Social preview:** upload `docs/images/social-preview.png` (1280×640) — it's what link previews show.
- **Settings → Features:** enable *Issues* and *Discussions* (optional).
- **Settings → Branches:** protect `main` — require the CI checks to pass before merging.
- **Settings → Code security:** enable *Dependabot alerts*, *private vulnerability reporting* (referenced by `SECURITY.md`), *secret scanning*.
- Pin a short *"Help wanted"* issue list (ideas are in `docs/en/features.md` → *Ideas not implemented yet*).

## Versioning & changelog

[Semantic Versioning](https://semver.org): `MAJOR.MINOR.PATCH`.

- The single source of truth is `__version__` in `phone_bridge.py` (pyproject reads it dynamically; `--version` prints it).
- Keep `CHANGELOG.md` in the [Keep a Changelog](https://keepachangelog.com) style: an `Unreleased` section while you work, a dated section per release.
- A new **user-visible text** means a new `EN` entry; a new **behaviour** means docs in `docs/en` **and** `docs/fa`.

## Cutting a release

```bash
# 1. bump __version__, move "Unreleased" → "[1.0.1] - YYYY-MM-DD" in CHANGELOG.md
python -m pytest && ruff check . && xvfb-run -a python tests/gui_e2e.py --lang en && xvfb-run -a python tests/gui_e2e.py --lang fa
python scripts/check_links.py
# 2. refresh screenshots if the UI changed
xvfb-run -a python scripts/make_screenshots.py --fonts <Vazirmatn folder>
# 3. commit, tag, push
git commit -am "Release v1.0.1"
git tag v1.0.1
git push && git push --tags
```

Pushing a `v*` tag triggers `.github/workflows/release.yml`, which builds the Windows folder-build and attaches `PhoneBridge-v1.0.1-windows.zip` to a GitHub Release with auto-generated notes. (You can also create the release by hand in the GitHub UI.)

## Building a Windows exe

`scripts\build_windows.bat` (or the same PyInstaller command in the workflow):

```bat
py -m pip install -r requirements.txt pyinstaller
py -m PyInstaller --noconfirm --clean --windowed --name PhoneBridge --icon assets\icon.ico phone_bridge.py
```

Result: `dist\PhoneBridge\PhoneBridge.exe` (+ support files). Notes:

- Use the **folder** build, not `--onefile`: a one-file exe unpacks to a temp folder on every start (slower, more antivirus noise) and the app's data folder logic expects a stable exe folder. When frozen, settings/fonts/`platform-tools` are stored **next to the exe**.
- Fonts are **not** bundled; the exe downloads Vazirmatn on first run like the script does. To ship them, put `fonts/Vazirmatn-*.ttf` next to the exe and include the font's licence (OFL).
- Unsigned executables may trigger Windows SmartScreen / antivirus heuristics (they see a "program that sends keystrokes"). That's expected for pynput-based tools; code-signing helps.
- **This build path is provided but could not be tested on Windows when this repository was prepared** — try it, and fix the spec/workflow if PyInstaller needs hidden imports on your versions.

## Licensing note: PyQt6 is GPL

*(Plain-language summary, not legal advice.)*

- Phone Bridge's own code is **MIT**. It `import`s **PyQt6**, which Riverbank licenses under **GPL v3 or a commercial licence**. `pynput` is LGPL v3.
- **Running from source** (`git clone` + `pip install`): you don't redistribute PyQt6 — pip fetches it from PyPI for the user. Publishing MIT source that imports a GPL library is common practice and compatible.
- **Redistributing a binary** (PyInstaller zip, installer) *does* redistribute PyQt6 (and Qt, LGPL v3). Then you must comply: ship the GPL/LGPL licence texts, state where the corresponding source for PyQt6/Qt can be obtained, and make the source of the combined work available under GPL-compatible terms (this repository's MIT source is GPL-compatible, and the release workflow copies `LICENSE` and `THIRD_PARTY_NOTICES.md` into the zip). If you want a build you can ship under non-GPL terms: buy a PyQt commercial licence, or…
- **…port to PySide6** (LGPL v3, same Qt API). The code mostly needs: `pyqtSignal→Signal`, `pyqtSlot→Slot`, import names, and a check of flag/enum handling (`int(Qt.AlignmentFlag…)` usages). This is a good "help wanted" task; the e2e suite is there to prove the port.
- The UI font **Vazirmatn** is SIL Open Font License 1.1: you may bundle and redistribute it with its licence. The project downloads it rather than bundling it.
- **Android SDK Platform-Tools (`adb`)** is under Google's SDK licence; the app downloads it from Google on demand and doesn't redistribute it. If you bundle `adb` in your own release, you take on those terms.
