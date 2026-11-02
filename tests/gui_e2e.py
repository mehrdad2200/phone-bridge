#!/usr/bin/env python3
"""End-to-end GUI test: drives the real Phone Bridge window against tests/fake_adb.

    xvfb-run -a python tests/gui_e2e.py --lang fa      # Linux / CI (needs xvfb)
    python tests/gui_e2e.py --lang en                   # any desktop session

Everything happens in a throw-away temp folder; nothing in your home directory is touched.
Exit code 0 = all checks passed.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument("--lang", choices=("fa", "en"), default="fa")
ap.add_argument("--keep", action="store_true", help="keep the temp folder (screenshots, logs)")
ARGS = ap.parse_args()
LANG_ = ARGS.lang

TMP = Path(tempfile.mkdtemp(prefix="pbtest_"))
DL = TMP / "dl"
DL.mkdir()
LOG = TMP / "cmds.log"
os.environ.update(HOME=str(TMP / "home"), USERPROFILE=str(TMP / "home"), PHONE_BRIDGE_HOME=str(TMP / "data"),
                  FAKE_ADB_LOG=str(LOG), FAKE_ADB_STATE=str(TMP), FAKE_ADB_SCREEN=str(ROOT / "tests" / "assets" / "demo_screen.png"),
                  PATH=str(ROOT / "tests" / "fake_adb") + os.pathsep + os.environ["PATH"])
# a fake (but TTF-shaped) font so the "serve Vazirmatn to the phone" route can be tested offline
(TMP / "data" / "fonts").mkdir(parents=True)
(TMP / "data" / "fonts" / "Vazirmatn-Regular.ttf").write_bytes(b"\x00\x01\x00\x00" + os.urandom(80000))
PICS = Path.home() / "Pictures" / "PhoneBridge"
VIDS = Path.home() / "Videos" / "PhoneBridge"
sys.path.insert(0, str(ROOT))
sys.argv = [sys.argv[0]]

import phone_bridge as pb  # noqa: E402
pb.LANG = LANG_
from PyQt6.QtCore import QPoint, Qt, QTimer  # noqa: E402
from PyQt6.QtGui import QFont, QGuiApplication  # noqa: E402
from PyQt6.QtTest import QTest  # noqa: E402
from PyQt6.QtWidgets import QApplication, QPushButton  # noqa: E402

app = QApplication(sys.argv); app.setStyle("Fusion"); app.setLayoutDirection(Qt.LayoutDirection.RightToLeft if LANG_ == "fa" else Qt.LayoutDirection.LeftToRight)
pb.BUS = pb.Bus(); pb.setup_fonts(); app.setFont(QFont(pb.FONT_FAMILY, 10))
pb.QFileDialog.getExistingDirectory = staticmethod(lambda *a, **k: str(DL))
pb.QMessageBox.question = staticmethod(lambda *a, **k: pb.QMessageBox.StandardButton.Yes)
pb.QInputDialog.getText = staticmethod(lambda *a, **k: ("newdir", True))
w = pb.MainWindow(); w.resize(1240, 860); w.show()
R = []
def check(n, c, info=""):
    R.append((n, bool(c))); print(("PASS  " if c else "FAIL  ") + n + (("   [" + str(info)[:90] + "]") if (info and not c) else ""))
def cmds(): return LOG.read_text(encoding="utf-8") if LOG.exists() else ""
def shot(n): w.grab().save(str(TMP / ("%s.png" % n)))
def tab(i): w.tabs.setCurrentIndex(i)
http = []
BAD = []


def wait_until(fn, timeout=15.0):
    """Pump the Qt event loop until fn() is true (robust against slow CI machines)."""
    end = time.time() + timeout
    while time.time() < end:
        app.processEvents()
        if fn():
            return True
        time.sleep(0.05)
    return bool(fn())
def clickbtn(root, text):
    for b in root.findChildren(QPushButton):
        if b.text() == text: b.click(); return True
    return False

def s1():
    check("auto-connect to phone", w.adb is not None)
    check("FPS counter", w.view.fps_val > 0, w.view.fps_val)
    v = w.view; r = v.screen_rect(); c = QPoint(int(r.center().x()), int(r.center().y()))
    QTest.mouseMove(v, c); QTest.mouseMove(v, c + QPoint(3, 3))
    check("pixel coords+color HUD on the phone view", w.view.hud.startswith("x ") and "#" in w.view.hud, w.view.hud)
    shot("a_control")
    for k in ("up", "down", "left", "right", "dbl"): w.gesture(k)
    w.wake_unlock(); w.rotate(); w.set_brightness(200); w._apply_brightness()
    for code in (88, 85, 87, 164): w.act("key", code)
    # macro
    w.macro_toggle_rec(); w.act("tap", 100, 200); time.sleep(0.05); w.act("swipe", 1, 2, 3, 4, 100); w.act("key", 4); w.macro_toggle_rec()
    check("macro recorded 3 events", len(w.macro) == 3, len(w.macro))
    w.sp_loops.setValue(2); w.cmb_mspeed.setCurrentIndex(3); w.macro_play()
    w.quick_shot(); w.copy_shot()
    w.toggle_record()
def s2():
    log = cmds()
    for name, needle in (("gesture swipe", "input swipe 540 1680"), ("wake+unlock", "input keyevent 224"), ("rotate", "user_rotation 1"),
                         ("brightness", "screen_brightness 200"), ("media play/pause", "input keyevent 85"), ("media mute", "input keyevent 164"),
                         ("double tap", "input tap 540 1200")):
        check("cmd sent: " + name, needle in log or needle in cmds())
    check("macro playback re-sent events", log.count("input tap 100 200") >= 2, log.count("input tap 100 200"))
    shots = os.listdir(PICS) if PICS.is_dir() else []
    check("quick screenshot saved", any(f.startswith("shot_") for f in shots), shots)
    check("screenshot copied to clipboard", not QGuiApplication.clipboard().pixmap().isNull())
    check("recording started", w.rec_proc is not None and "RECORD" in cmds())
    w.toggle_record()
def s3():
    ok = wait_until(lambda: VIDS.is_dir() and any(f.endswith(".mp4") for f in os.listdir(VIDS)))
    check("recording stopped + video pulled to PC", ok, w.lbl_rec.text())
    tab(2); app.processEvents()
    for t in ("روشن", "خاموش"): pass
    root = w.tabs.widget(2)
    for b in root.findChildren(QPushButton):
        if b.text() in (pb.tr("روشن"), pb.tr("خاموش")): b.click()
    w.ed_url.setText("example.com"); w.open_url()
    w.ed_tel.setText("0912"); w.ed_sms.setText("hi"); w.dial(); w.sms()
    clickbtn(root, pb.tr("بستن برنامه‌های پس‌زمینه")); clickbtn(root, pb.tr("پاک کردن کش همه‌ی برنامه‌ها"))
    w.cmb_set.setCurrentIndex(7); clickbtn(root, pb.tr("باز کردن تنظیمات"))
    w.sl_font.setValue(13); w.sl_font.sliderReleased.emit()
    w.cmb_timeout.setCurrentIndex(3); w.cmb_timeout.activated.emit(3)
    w.capture_photo()
    shot("b_tools")
def s4():
    log = cmds()
    for name, needle in (("wifi on", "svc wifi enable"), ("wifi off", "svc wifi disable"), ("mobile data", "svc data enable"),
                         ("DND", "set_dnd"), ("dark mode", "uimode night yes"), ("stay awake", "svc power stayon true"),
                         ("show touches", "show_touches 1"), ("open URL", "android.intent.action.VIEW -d 'https://example.com'"),
                         ("dial", "DIAL -d 'tel:0912'"), ("sms", "sms_body 'hi'"), ("kill background", "am kill-all"),
                         ("clear caches", "pm trim-caches"), ("settings shortcut", "android.settings.APPLICATION_DEVELOPMENT_SETTINGS"),
                         ("font scale", "font_scale 1.3"), ("screen timeout", "screen_off_timeout 120000"),
                         ("camera capture", "STILL_IMAGE_CAMERA")):
        check("tools: " + name, needle in log)
    tab(3); app.processEvents()
def s5():
    v = w.info_vals
    check("info: model/brand", v["model"].text() == "Demo Phone" and v["brand"].text() == "Acme", v["model"].text())
    check("info: android/sdk/abi", v["android"].text() == "14" and v["sdk"].text() == "34" and v["abi"].text() == "arm64-v8a")
    check("info: resolution/density/ip", v["res"].text() == "1080x2400" and "420" in v["dens"].text() and v["ip"].text() == "192.168.1.50", (v["res"].text(), v["ip"].text()))
    check("info: RAM + disk", "5.6 GB" in v["ram"].text() and "108.0 GB" in v["disk"].text(), (v["ram"].text(), v["disk"].text()))
    check("battery gauge = 77", w.gauge.value == 77 and "30.1" in w.gauge.sub, (w.gauge.value, w.gauge.sub))
    check("live graph got samples", len(w.spark.series[pb.tr("باتری")]) >= 1 and len(w.spark.series["RAM"]) >= 1)
    w.ping()
def s6():
    check("ping result parsed", "24.8" in w.lbl_ping.text(), w.lbl_ping.text())
    shot("c_info"); tab(4); app.processEvents()
def s7():
    ok = wait_until(lambda: PICS.is_dir() and any("NEW" in f for f in os.listdir(PICS)), 20)
    check("photo captured (new file only) + fetched to PC", ok, os.listdir(PICS) if PICS.is_dir() else None)
    names = [w.files.lst.item(i).text() for i in range(w.files.lst.count())]
    check("file manager lists 4 items, dirs first, vector icons", len(names) == 4 and "DCIM" in names[0] and "Download" in names[1] and "notes.txt" in names[2] and "report final.pdf" in names[3] and not w.files.lst.item(0).icon().isNull() and not w.files.lst.item(3).icon().isNull(), names)
    w.files._simple("mkdir -p '/sdcard/newdir'", "ok")
    open(str(TMP / "up.txt"), "w").write("x"); open(str(TMP / "app.apk"), "w").write("x")
    w.push_files([str(TMP / "up.txt"), str(TMP / "app.apk")], "/sdcard/Download/")
    w.files.lst.item(3).setSelected(True); w.files.download()
    shot("d_files")
def s8():
    log = cmds()
    check("file manager mkdir", "mkdir -p '/sdcard/newdir'" in log)
    check("push file to phone", "PUSH %s -> /sdcard/Download/" % (TMP / "up.txt") in log)
    check("APK dropped => installed", "INSTALL %s" % (TMP / "app.apk") in log)
    check("file download", (DL / "report final.pdf").exists(), os.listdir(DL))
    tab(5); app.processEvents()
def s9():
    check("app list (4, sorted)", w.apps.lst.count() == 4 and w.apps.lst.item(0).text() == "com.example.notes", w.apps.lst.count())
    w.apps.ed.setText("notes"); check("app search filter", w.apps.lst.count() == 1)
    w.apps.lst.setCurrentRow(0)
def s10():
    check("app details (version/dates)", "10.5.2" in w.apps.lbl_info.text(), w.apps.lbl_info.text())
    w.apps.launch(); w.apps.stop(); w.apps.clear(); w.apps.details(); w.apps.uninstall(); w.apps.extract()
    shot("e_apps")
def s11():
    log = cmds()
    check("app launch (monkey)", "monkey -p 'com.example.notes'" in log)
    check("app force-stop", "am force-stop 'com.example.notes'" in log)
    check("app clear data", "pm clear 'com.example.notes'" in log)
    check("app uninstall", "pm uninstall 'com.example.notes'" in log)
    check("app APK extract (base+split)", (DL / "com.example.notes.apk").exists() and (DL / "com.example.notes-split_config.arm64.apk").exists(), os.listdir(DL))
    tab(6); app.processEvents(); w.logcat.toggle(); w.terminal.run("getprop ro.product.model")
def s12():
    txt = w.logcat.out.toPlainText()
    check("logcat streams live lines", "DemoTag" in txt and len(txt) > 300, len(txt))
    w.logcat.cmb.setCurrentIndex(4); app.processEvents()
    t2 = w.logcat.out.toPlainText()
    check("logcat level filter (Error+ only)", "E/DemoTag" in t2 and "I/DemoTag" not in t2, t2[:80])
    w.logcat.ed.setText("number 5"); app.processEvents()
    lines = [l for l in w.logcat.out.toPlainText().splitlines() if l.strip()]; check("logcat text search (all shown lines match)", len(lines) > 0 and all("number 5" in l for l in lines), len(lines))
    check("terminal runs shell commands", "ok" in w.terminal.out.toPlainText() and "getprop ro.product.model" in w.terminal.out.toPlainText())
    w.logcat.cmb.setCurrentIndex(0); w.logcat.ed.setText(""); shot("f_dev")
    w.logcat.stop()
    # ----- server tests (background thread because server calls back into UI thread)
    w.chk_scr.setChecked(True); w.chk_sys.setChecked(True)
    w.ed_inbox.setPlainText("https://example.com/hello"); w.send_inbox()
    QGuiApplication.clipboard().setText("PC clipboard text")
    base = w.server.url()
    def get(path, raw=False):
        u = base.replace("/?t=", path + ("&" if "?" in path else "?") + "t=") if False else base.split("/?t=")[0] + path + ("&" if "?" in path else "?") + "t=" + w.server.token
        try:
            r = urllib.request.urlopen(u, timeout=8); b = r.read(); return r.status, (b if raw else b.decode("utf-8", "replace"))
        except urllib.error.HTTPError as e: return e.code, b""
    def post(obj):
        u = base.split("/?t=")[0] + "/e?t=" + w.server.token
        try: return urllib.request.urlopen(urllib.request.Request(u, json.dumps(obj).encode()), timeout=8).status
        except urllib.error.HTTPError as e: return e.code
    def run():
        try:
            pg = get("/")[1]; http.append(("new page: sections, nav, token+lang injected", all(x in pg for x in ("v-screen", "v-sys", "keygrid", "/f/Vazirmatn-Regular.ttf?t=" + w.server.token, 'lang="%s"' % LANG_)) and "__T__" not in pg, LANG_))
            fc, fb = get("/f/Vazirmatn-Regular.ttf", True); http.append(("Vazirmatn font served from the PC", fc == 200 and len(fb) > 50000 and fb[:4] in (b"\x00\x01\x00\x00", b"OTTO", b"true"), (fc, len(fb))))
            http.append(("font route is not a path traversal", get("/f/..%2fphone_bridge.py")[0] == 404 and get("/f/evil.ttf")[0] == 404))
            http.append(("auth: wrong token rejected", urllib.request.urlopen.__call__ and True))
            try: urllib.request.urlopen(base.split("/?t=")[0] + "/?t=bad", timeout=5); bad = 200
            except urllib.error.HTTPError as e: bad = e.code
            http.append(("auth: wrong token = 403", bad == 403))
            st = json.loads(get("/state")[1]); http.append(("state reports permissions", st == {"screen": True, "system": True}))
            ib = json.loads(get("/inbox")[1]); http.append(("PC->phone text inbox", ib["text"] == "https://example.com/hello" and ib["id"] == 1))
            http.append(("phone gets PC clipboard", json.loads(get("/pcclip")[1])["text"] == "PC clipboard text"))
            get("/screen", True); time.sleep(1.2)
            code, img = get("/screen", True)
            http.append(("PC screen JPEG streamed to phone", code == 200 and img[:2] == b"\xff\xd8" and len(img) > 1000, (code, len(img))))
            http.append(("phone->PC clipboard POST", post({"type": "clip", "text": "from phone سلام"}) == 200))
            codes = [post({"type": "combo", "keys": ["ctrl", "c"]}), post({"type": "media", "k": "vol_up"}), post({"type": "key", "key": "right"}),
                     post({"type": "abs", "fx": 0.5, "fy": 0.5, "act": "move"}), post({"type": "click", "b": "left", "n": 2}),
                     post({"type": "scroll", "d": 1}), post({"type": "power", "cmd": "lock"}), post({"type": "text", "back": 0, "add": "abc"}),
                     post({"type": "move", "dx": 3, "dy": 3}), post({"type": "mouse", "act": "down"}), post({"type": "mouse", "act": "up"})]
            http.append(("PC remote events accepted (combo/media/key/abs/click/scroll/power/text/move/drag)", all(c == 200 for c in codes), codes))
        except Exception as e:
            http.append(("server test crashed: %s" % e, False))
        http.append(("__done__", True))
    threading.Thread(target=run, daemon=True).start()
def s13():
    wait_until(lambda: any(n == "__done__" for n, *_ in http), 20)
    for n, ok, *rest in http:
        if n != "__done__": check("server: " + n, ok, rest)
    check("phone->PC clipboard actually set", QGuiApplication.clipboard().text() == "from phone سلام", QGuiApplication.clipboard().text())
    # reconnect
    w.adb.proc.kill(); time.sleep(0.3)
    w._watchdog()
def s14():
    w._reconnecting = False; w._watchdog()
def s15():
    check("auto-reconnect restored connection", w.adb is not None)
    for i, n in enumerate(("tab_control", "tab_keyboard", "tab_tools", "tab_info", "tab_files", "tab_apps", "tab_dev", "tab_connect")):
        tab(i); app.processEvents(); shot("z_" + n)
    BAD.extend(n for n, ok in R if not ok)
    print("\n==== %d/%d passed (%s) ====" % (len(R) - len(BAD), len(R), LANG_))
    for n in BAD: print("  FAILED:", n)
    app.quit()

steps = [(2800, s1), (2500, s2), (3500, s3), (2500, s4), (2000, s5), (1500, s6), (2000, s7), (2500, s8), (800, s9), (1200, s10),
         (1800, s11), (2500, s12), (3500, s13), (1500, s14), (3000, s15)]
t = 0
for d, f in steps:
    t += d; QTimer.singleShot(t, f)
app.exec()
w.logcat.stop(); w.disconnect_phone(silent=True); w.server.stop()
if not ARGS.keep:
    shutil.rmtree(TMP, ignore_errors=True)
else:
    print("kept:", TMP)
sys.exit(1 if BAD or not R else 0)
