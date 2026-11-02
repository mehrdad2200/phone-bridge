# Contributing to Phone Bridge

Thanks for helping! You can write issues and pull requests in **English or فارسی**. Small fixes (typos, wording, a missing translation) are as welcome as features.

## Ways to help

- **Test on real phones** and report what works/breaks (phone model, Android version, UI skin). This is the most valuable contribution — most automated tests use a simulated `adb`.
- **Improve translations / add a language** → [docs/dev/translations.md](docs/dev/translations.md).
- **Docs**: fix mistakes, add screenshots of your setup, translate between `docs/en` and `docs/fa`.
- **Code**: see "Ideas" below or pick an open issue labelled *help wanted* / *good first issue*.

### Ideas (not yet implemented)

PySide6 port (LGPL) · macOS testing · bind-address selection and rate-limiting for the remote server · trackpad sensitivity setting · multi-device sessions · saved text snippets · more languages · splitting `phone_bridge.py` into a package ([plan](docs/dev/architecture.md#roadmap-for-restructuring)) · H.264 mirroring helper.

## Development setup

```bash
git clone https://github.com/YOUR_USERNAME/phone-bridge.git && cd phone-bridge
python -m venv .venv && . .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt
python phone_bridge.py                                 # run it
```

Run the same checks CI runs:

```bash
ruff check .
python -m pytest
chmod +x tests/fake_adb/adb
xvfb-run -a python tests/gui_e2e.py --lang fa          # Linux; on desktop sessions omit xvfb-run
xvfb-run -a python tests/gui_e2e.py --lang en
(cd tests/page && npm install && npm test)
python scripts/check_links.py
```

Details: [docs/dev/testing.md](docs/dev/testing.md) · structure: [docs/dev/architecture.md](docs/dev/architecture.md).

## Pull-request checklist

1. **One focused change** per PR; describe *why*.
2. Tests: add/adjust tests with the change. The suite must pass (see above).
3. **User-visible text** → `tr("…")` **and** an English entry in `EN` (the unit tests fail otherwise).
4. **Docs**: update `docs/en` *and* `docs/fa` when behaviour changes (a machine translation is OK — say so and a Persian speaker will polish it), and add a line under *Unreleased* in `CHANGELOG.md`.
5. **UI changes**: regenerate the screenshots (`scripts/make_screenshots.py`) or attach new ones.
6. Say **what you tested on** (OS, Python, phone + Android version).

## Code style

- Python ≥ 3.10, 4-space indent, type hints optional. `ruff` enforces real errors only; keep lines reasonable (≤ 140).
- Qt: do UI work only on the main thread — use `bg()` for slow work and `ui(...)` to come back ([architecture](docs/dev/architecture.md#threads--the-ui-bridge)).
- Send phone input through `MainWindow.act(...)` so macros can record it.
- Anything passed to the phone's shell from user input must go through `shq()`.
- New dangerous capability ⇒ off by default, confirm in the UI, document it in `docs/*/security.md`.
- Comments may be in English or Persian; identifiers in English.

## Commit messages

Short imperative subject (≤ 72 chars), optional body explaining *why*: `Fix pairing timeout on Windows`, `Add trackpad sensitivity setting`.

## Reporting bugs & security issues

- Bugs: use the **Bug report** form; include the *adb log* and your versions.
- **Security issues: don't open a public issue** — follow [SECURITY.md](SECURITY.md).

By contributing you agree that your contribution is licensed under the project's [MIT license](LICENSE). Please follow the [Code of Conduct](CODE_OF_CONDUCT.md).

---

### راهنمای کوتاه به فارسی

- **سادەترین کمک:** روی گوشی واقعی تست کن و نتیجه را (مدل گوشی، نسخه‌ی اندروید) در یک Issue بنویس.
- برای تغییر کد: مخزن را fork کن، تغییر را در یک شاخه بده، تست‌ها را اجرا کن (`python -m pytest` و `tests/gui_e2e.py`) و Pull Request بفرست.
- هر متن جدید رابط باید با `tr("…")` نوشته شود و معادل انگلیسی‌اش در جدول `EN` بیاید؛ تست‌ها این را بررسی می‌کنند.
- اگر مستندات را تغییر دادی، هم `docs/fa` و هم `docs/en` را به‌روز کن (ترجمه‌ی ماشینی هم قابل قبول است).
- فارسی یا انگلیسی نوشتن در Issue و PR هر دو خوب است.
