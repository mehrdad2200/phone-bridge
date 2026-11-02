# Translations (i18n)

[← Docs index](../README.md) · Developer documentation (English)

The app ships in **Persian (`fa`)** and **English (`en`)**. This page explains how texts are translated, how to add or change a string, and how to add another language.

## How it works

```python
LANG = "fa"                       # chosen once at start (config / --lang)
EN = {"گوشی متصل نیست": "Phone not connected", ...}

def tr(s):                        # the Persian text IS the key
    return EN.get(s, s) if LANG == "en" else s
```

- Every user-visible Persian string in the Python code is written as `tr("…")`.
- In Persian mode `tr` returns the string unchanged; in English mode it looks it up in `EN`, falling back to the Persian text if missing (so a forgotten entry degrades gracefully — and fails the unit test).
- The language never changes while the process runs. **Switching language restarts the app** (`MainWindow.switch_language` → `_restart_argv()` → new process). That is why widgets can build their text once, at construction, with no retranslation code.
- The layout direction follows the language: `main()` sets `QApplication.setLayoutDirection` to RTL for `fa`, LTR for `en`. Widgets that must stay left-to-right regardless (URLs, paths, adb output, the D-pad, media row) call `ltr(widget)` or set `LeftToRight` on a container.

## Add or change a string

1. Write the Persian text in code: `label = mk_label(tr("متن جدید"))`.
2. Add the English text to the `EN` table:
   ```python
   "متن جدید": "New text",
   ```
3. Run `python -m pytest tests/test_units.py -k "translat"` (or the whole suite). It tells you exactly what's missing, orphaned or inconsistent.

Rules the tests enforce:

| Rule | Why |
|---|---|
| Every `tr("…")` has an `EN` entry | no Persian leaking into English mode |
| No Persian literal outside `tr()` (docstrings, the `EN` table and `PAGE` excepted) | same |
| Same `%s` / `%d` / `%.1f` placeholders in both | formatting must not crash |
| No unused `EN` entries | keeps the table clean when code is deleted |

Tips:

- **Formatting**: wrap the *format string*, then apply `%`: `tr("%d مورد") % n`. A literal percent in the translation is `%%` (e.g. `"%d٪"` → `"%d%%"`).
- **Keep spaces**: a string like `"در حال شارژ "` (trailing space) must keep it in English, because code concatenates.
- **Fragments**: avoid building sentences from pieces; if you must (`tr("فعال شد")`), translate the pieces so they read well after concatenation.
- **Tab titles / button texts with `&`**: Qt treats `&` as a keyboard-mnemonic marker. Write `&&` in the translation (`"Keyboard && PC remote"`).
- **Newlines**: use `\n` in both languages; labels are word-wrapped.
- **Tooltips and placeholders** go through `tr()` too.
- Prefer short English; the UI is dense.

## The phone web page has its own table

The page is plain HTML/JS and can't call Python's `tr()`. Its texts live in `PAGE` as a JS object:

```js
const L = { fa: { title: '…', n_type: '…', … }, en: { title: '…', … } };
```

Elements use `data-t="key"` (text) / `data-ph="key"` (placeholder); `applyLang()` fills them. The server injects the *app's* language as the initial one (`__LANG__`), and the page's own **EN / فا** button overrides it per phone (stored in `localStorage`). A unit test checks that both tables have identical keys. The 20 shortcut labels are in the `KEYS` array as `[fa, en, keys]`.

## Adding a third language (e.g. German `de`)

The current design is "Persian source → English", which is simple but two-language. To add `de`:

1. Turn `EN` into a dict of dicts: `TR = {"en": {...}, "de": {...}}` and make `tr()` look up `TR.get(LANG, {})`.
2. Allow the new code in `parse_args` (`choices=("fa","en","de")`), the language button (cycle or a menu), and `main()` (RTL only for RTL languages — a `RTL_LANGS = {"fa"}` set).
3. Extend the unit-test guards to loop over every language.
4. Add a `de` block to the page's `L` table and the 20 `KEYS`.
5. Add screenshots (`scripts/make_screenshots.py` takes `--lang`).
6. Fonts: Vazirmatn already covers Latin; for other scripts you may need another font file in `fonts/` and a family fallback in `setup_fonts()`.

Pull requests for new languages are very welcome — please open an issue first so we can agree on the structure.

## Translating without touching code

Translators can edit only the `EN` table (it's alphabetised by first use, one pair per line). If you only want to improve English wording: change the **value**, never the key — the key is the Persian source text that the code looks up.
