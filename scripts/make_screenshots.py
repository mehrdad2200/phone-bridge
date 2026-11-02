#!/usr/bin/env python3
"""Regenerate every image in docs/images from the *real* app, using the fake adb + demo phone screen.

    pip install -r requirements-dev.txt PyQt6-WebEngine
    xvfb-run -a python scripts/make_screenshots.py --fonts /path/to/folder/with/Vazirmatn-*.ttf     # Linux
    python scripts/make_screenshots.py                                                             # desktop session

Pieces:  desktop  (the main window, both languages)       remote  (the phone web page, via Qt WebEngine)
         compose  (overview strips + social preview)       all     (default: runs the three above)
Nothing is read from or written to your real config; a throw-away data folder is used.
"""
import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "images"
TAB_NAMES = ["control", "keyboard", "tools", "info", "files", "apps", "developer", "connection"]


def env_for(tmp, fonts):
    """Isolated environment: temp data dir, fake adb on PATH, optional font folder copied in."""
    data = tmp / "data"
    (data / "fonts").mkdir(parents=True, exist_ok=True)
    if fonts:
        for f in Path(fonts).glob("Vazirmatn-*.ttf"):
            shutil.copy(f, data / "fonts" / f.name)
    os.environ.update(HOME=str(tmp / "home"), USERPROFILE=str(tmp / "home"), PHONE_BRIDGE_HOME=str(data),
                      FAKE_ADB_LOG=str(tmp / "cmds.log"), FAKE_ADB_STATE=str(tmp),
                      FAKE_ADB_SCREEN=str(ROOT / "tests" / "assets" / "demo_screen.png"),
                      PATH=str(ROOT / "tests" / "fake_adb") + os.pathsep + os.environ["PATH"])
    sys.path.insert(0, str(ROOT))


def save(pixmap, name, max_w=None):
    from PIL import Image
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = OUT / (name + ".tmp.png")
    pixmap.save(str(tmp))
    im = Image.open(tmp).convert("RGB")
    if max_w and im.width > max_w:
        im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    im.save(OUT / (name + ".png"), optimize=True)
    tmp.unlink()
    print("  saved", name + ".png", im.size)


# ----------------------------------------------------------------------------- desktop window
def desktop(lang, fonts):
    tmp = Path(tempfile.mkdtemp(prefix="pbshots_"))
    env_for(tmp, fonts)
    import phone_bridge as pb
    pb.LANG = lang
    from PyQt6.QtCore import QPoint, Qt
    from PyQt6.QtGui import QFont
    from PyQt6.QtTest import QTest
    from PyQt6.QtWidgets import QApplication
    app = QApplication(["shots"])
    app.setStyle("Fusion")
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft if lang == "fa" else Qt.LayoutDirection.LeftToRight)
    pb.BUS = pb.Bus()
    pb.setup_fonts()
    app.setFont(QFont(pb.FONT_FAMILY, 10))

    def pump(sec):
        end = time.time() + sec
        while time.time() < end:
            app.processEvents()
            time.sleep(0.01)

    w = pb.MainWindow()
    w.resize(1240, 860)
    w.show()
    pump(3.5)
    w.lbl_adb.setText("✅ C:\\platform-tools\\adb.exe")       # keep the local test path out of the screenshots
    for msg in ("Phone connected (192.168.1.50)", "Typed: 24 characters", "Text sent to the PC clipboard") if lang == "en" else \
            ("گوشی وصل شد (192.168.1.50)", "تایپ شد: ۲۴ نویسه", "متن به کلیپ‌بورد PC رفت"):
        w.log_server("ok" if "onnected" in msg or "وصل" in msg else "info", msg)
    r = w.view.screen_rect()
    QTest.mouseMove(w.view, QPoint(int(r.center().x()), int(r.center().y() - 120)))
    pump(0.4)
    save(w.grab(), "control-dark-" + lang)
    if lang == "en":
        w.toggle_theme()
        pump(0.5)
        save(w.grab(), "control-light-en")
        w.toggle_theme()
    w.view.leaveEvent(None)
    for i, name in enumerate(TAB_NAMES[1:], start=1):
        w.tabs.setCurrentIndex(i)
        if name == "developer":
            w.logcat.toggle()
            pump(2.0)
        elif name == "info":
            pump(10.0)                      # let the live graph collect a few samples
        elif name == "apps":
            w.apps.lst.setCurrentRow(0)
            pump(1.0)
        elif name == "connection":
            w.start_qr_pair()
            pump(0.8)
        else:
            pump(0.7)
        save(w.grab(), "tab-%s-%s" % (name, lang))
        if name == "developer":
            w.logcat.stop()
        if name == "connection":
            w.cancel_qr()
    w.tabs.setCurrentIndex(0)
    w.disconnect_phone(silent=True)
    pump(0.6)
    save(w.grab(), "disconnected-" + lang)
    w.server.stop()
    shutil.rmtree(tmp, ignore_errors=True)


# ----------------------------------------------------------------------------- phone web page
DARK_JS = ("(function(){var r=document.documentElement.style,v={'--bg':'#0A0A0F','--s1':'#13131A','--s2':'#1B1B24','--s3':'#272733',"
           "'--tx':'#F2F2F7','--mu':'#8E8E9A','--ln':'rgba(255,255,255,.07)','--glass':'rgba(19,19,26,.82)'};"
           "for(var k in v)r.setProperty(k,v[k]);})();")

def remote(lang, fonts):
    tmp = Path(tempfile.mkdtemp(prefix="pbshots_"))
    env_for(tmp, fonts)
    os.environ["QT_SCALE_FACTOR"] = "2"
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox --disable-gpu --disable-dev-shm-usage --blink-settings=preferredColorScheme=0"
    import phone_bridge as pb
    pb.LANG = lang
    from PyQt6.QtCore import QUrl
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWidgets import QApplication
    app = QApplication(["shots"])
    pb.BUS = pb.Bus()
    srv = pb.PhoneKeyboardServer(lambda *a: None)
    srv.allow_system = True
    srv.start(8795)
    srv.send_to_phone("https://example.com/shared-link" if lang == "en" else "لینک مقاله: https://example.com/shared-link")
    view = QWebEngineView()
    view.resize(390, 800)
    view.show()
    view.setUrl(QUrl("http://127.0.0.1:8795/?t=%s" % srv.token))

    def pump(sec):
        end = time.time() + sec
        while time.time() < end:
            app.processEvents()
            time.sleep(0.01)
    pump(4)
    view.page().runJavaScript(DARK_JS)
    pump(0.3)
    pages = [("type", "type"), ("trackpad", "pad"), ("slides", "pres"), ("media", "media"), ("more", "more"),
             ("shortcuts", "keys"), ("clipboard", "clip"), ("system", "sys")]
    for name, view_id in pages:
        view.page().runJavaScript("go('%s')" % view_id)
        pump(0.9)
        if name == "type":
            view.page().runJavaScript("document.querySelectorAll('#mods .chip')[0].classList.add('on');")
            pump(0.2)
        save(view.grab(), "remote-%s-%s" % (name, lang), max_w=780)
    srv.stop()
    shutil.rmtree(tmp, ignore_errors=True)


# ----------------------------------------------------------------------------- composites
def compose(fonts):
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    fdir = Path(fonts) if fonts else None

    def font(weight, size):
        if fdir and (fdir / ("Vazirmatn-%s.ttf" % weight)).exists():
            return ImageFont.truetype(str(fdir / ("Vazirmatn-%s.ttf" % weight)), size)
        return ImageFont.load_default()

    def strip(lang):
        names = ["type", "trackpad", "slides", "media"]
        ims = [Image.open(OUT / ("remote-%s-%s.png" % (n, lang))) for n in names]
        h = 1000
        ims = [im.resize((round(im.width * h / im.height), h), Image.LANCZOS) for im in ims]
        gap = 28
        sheet = Image.new("RGB", (sum(i.width for i in ims) + gap * (len(ims) + 1), h + gap * 2), (10, 10, 15))
        x = gap
        for im in ims:
            sheet.paste(im, (x, gap))
            x += im.width + gap
        sheet.save(OUT / ("remote-overview-%s.png" % lang), optimize=True)
        print("  saved remote-overview-%s.png" % lang, sheet.size)
    for lang in ("en", "fa"):
        strip(lang)

    # social preview 1280x640
    W, H = 1280, 640
    bg = Image.new("RGB", (W, H), (10, 10, 15))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((700, -250, 1500, 450), fill=(124, 92, 255))
    g.ellipse((-300, 350, 500, 950), fill=(79, 140, 255))
    bg = Image.blend(bg, glow.filter(ImageFilter.GaussianBlur(140)), 0.55)
    d = ImageDraw.Draw(bg)
    icon = Image.open(ROOT / "assets" / "icon.png").convert("RGBA").resize((132, 132), Image.LANCZOS)
    bg.paste(icon, (80, 96), icon)
    d.text((80, 250), "Phone Bridge", font=font("Bold", 76), fill="white")
    for i, line in enumerate(("Control your Android phone", "from your PC — and use your phone", "as keyboard, trackpad & remote.")):
        d.text((82, 350 + i * 40), line, font=font("Regular", 27), fill=(214, 214, 236))
    d.text((82, 526), "English · فارسی   ·   Windows · Linux   ·   MIT", font=font("Medium", 21), fill=(150, 130, 255))
    ctl = Image.open(OUT / "control-dark-en.png").convert("RGB")
    cw, ch = ctl.size
    ctl = ctl.crop((250, 135, 880, ch - 40))                      # phone mirror + toolbar only
    ctl = ctl.resize((round(ctl.width * 430 / ctl.height), 430), Image.LANCZOS)
    ph = Image.open(OUT / "remote-trackpad-en.png").convert("RGB")
    ph = ph.resize((round(ph.width * 430 / ph.height), 430), Image.LANCZOS)
    for im, pos in ((ctl, (600, 105)), (ph, (600 + ctl.width + 40, 105))):
        shadow = Image.new("RGBA", (im.width + 60, im.height + 60), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle((30, 40, im.width + 30, im.height + 40), 26, fill=(0, 0, 0, 150))
        shadow = shadow.filter(ImageFilter.GaussianBlur(18))
        bg.paste(shadow, (pos[0] - 30, pos[1] - 30), shadow)
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), 22, fill=255)
        bg.paste(im, pos, mask)
    bg.save(OUT / "social-preview.png", optimize=True)
    print("  saved social-preview.png", bg.size)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", nargs="?", default="all", choices=("all", "desktop", "remote", "compose"))
    ap.add_argument("--lang", choices=("fa", "en"), help="(desktop/remote) one language only")
    ap.add_argument("--fonts", help="folder containing Vazirmatn-Regular/Medium/Bold.ttf")
    a = ap.parse_args()
    if a.what == "all":                                  # each piece in its own process (Qt apps don't like sharing)
        base = [sys.executable, __file__] + (["--fonts", a.fonts] if a.fonts else [])
        for lang in ("fa", "en"):
            subprocess.check_call(base[:2] + ["desktop", "--lang", lang] + base[2:])
            subprocess.check_call(base[:2] + ["remote", "--lang", lang] + base[2:])
        subprocess.check_call(base[:2] + ["compose"] + base[2:])
        return
    if a.what == "desktop":
        desktop(a.lang or "en", a.fonts)
    elif a.what == "remote":
        remote(a.lang or "en", a.fonts)
    else:
        compose(a.fonts)


if __name__ == "__main__":
    main()
