# -*- coding: utf-8 -*-
"""
Phone Bridge  -  پل گوشی ↔ کامپیوتر
====================================
Control an Android phone from your PC (mouse + keyboard, over adb) and use your
phone as a keyboard / trackpad / presenter remote for the PC (small web page).
UI languages: Persian (فارسی) and English.  Font: Vazirmatn.

    pip install -r requirements.txt
    python phone_bridge.py            # --lang fa|en , --version

Docs: README.md, docs/.   License: MIT.
"""
__version__ = "1.0.0"
import base64
import hmac
import html
import json
import os
import queue
import re
import secrets
import shutil
import socket
import string
import subprocess
import sys
import tempfile
import threading
import time
import urllib.request
import webbrowser
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from math import hypot
from collections import deque
from pathlib import Path, PurePosixPath
from urllib.parse import parse_qs, urlparse

from PyQt6.QtCore import (QBuffer, QByteArray, QIODevice, QObject, QPointF, QRectF, QSize, Qt, QTimer, QUrl,
                          pyqtSignal, pyqtSlot)
from PyQt6.QtGui import (QColor, QDesktopServices, QFont, QFontDatabase, QGuiApplication, QIcon, QImage,
                         QKeySequence, QLinearGradient, QPainter, QPainterPath, QPen, QPixmap, QPolygonF, QRadialGradient,
                         QShortcut)
from PyQt6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFileDialog, QFrame, QGridLayout, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget, QListWidgetItem,
                             QMainWindow, QMenu, QMessageBox, QProgressBar, QPushButton, QScrollArea, QSizePolicy,
                             QSlider, QSpinBox, QStackedWidget, QSystemTrayIcon, QTabWidget, QTextEdit, QVBoxLayout, QWidget)

LANG = "fa"          # زبان رابط: fa یا en (از تنظیمات خوانده می‌شود)
EN = {
    "زمان انتظار تمام شد (timeout)": "Timed out",
    "پاسخی از گوشی نیامد": "No response from the phone",
    "خروجی خالی": "Empty output",
    "تصویری از گوشی نیامد:\n": "No image from the phone:\n",
    "دستور سیستمی «%s» رد شد (در برنامه فعال نیست)": "System command \"%s\" rejected (not enabled in the app)",
    "دستورهای سیستمی فقط در ویندوز پشتیبانی می‌شوند": "System commands are only supported on Windows",
    "دستور سیستمی اجرا شد: %s": "System command executed: %s",
    "درخواست با توکن نادرست از %s رد شد": "Request with a wrong token from %s was rejected",
    "گوشی وصل شد (%s)": "Phone connected (%s)",
    "متن به کلیپ‌بورد PC رفت": "Text sent to the PC clipboard",
    "تایپ شد: %d نویسه": "Typed: %d characters",
    "خطا: %s": "Error: %s",
    "متن برای QR خیلی بلند است": "Text is too long for a QR code",
    "اتصال به گوشی": "Connect to phone",
    "در حال گرفتن تصویر از گوشی…": "Fetching the phone screen…",
    "تصویر دریافتی قابل نمایش نیست.": "The received image can't be displayed.",
    "تصویر گوشی کاملاً سیاه است: صفحه را روشن و قفل را باز کنید؛ اگر باز هم سیاه بود، برنامه‌ی باز روی گوشی جلوی ضبط صفحه را گرفته.": "The phone image is completely black. Turn the screen on and unlock it; if it stays black, the open app is blocking screen capture.",
    "گوشی متصل نیست": "Phone not connected",
    "برای دیدن و کنترل گوشی، اول وصلش کن.": "Connect your phone first to see and control it.",
    "%d٪": "%d%%",
    "باتری": "Battery",
    "مدیر فایل گوشی": "Phone file manager",
    "پوشه‌ی بالاتر": "Parent folder",
    "حافظه‌ی داخلی": "Internal storage",
    "ریشه /": "Root /",
    "تازه‌سازی": "Refresh",
    "دانلود": "Download",
    "ارسال فایل": "Upload file",
    "حذف": "Delete",
    "نصب APK": "Install APK",
    "برای شروع به گوشی وصل شو. فایل‌ها را می‌توانی روی پنجره‌ی برنامه هم رها کنی.": "Connect a phone to start. You can also drop files onto the app window.",
    "گوشی متصل نیست.": "Phone not connected.",
    "%d مورد": "%d items",
    "در حال دانلود برای باز کردن…": "Downloading to open…",
    "چیزی انتخاب نشده.": "Nothing selected.",
    "ذخیره در…": "Save to…",
    "در حال دانلود %d مورد…": "Downloading %d items…",
    "دانلود کامل نشد؛ گزارش را در تب اتصال ببین.": "Download incomplete; check the log in the Connection tab.",
    "✅ دانلود شد: ": "✅ Downloaded: ",
    "فایل‌ها را انتخاب کن": "Choose files",
    "پوشه‌ی جدید": "New folder",
    "نام پوشه:": "Folder name:",
    "پوشه ساخته شد": "Folder created",
    "برای تغییر نام، دقیقاً یک مورد را انتخاب کن.": "To rename, select exactly one item.",
    "تغییر نام": "Rename",
    "نام جدید:": "New name:",
    "نام تغییر کرد": "Renamed",
    "%d مورد برای همیشه از گوشی حذف شود؟": "Permanently delete %d items from the phone?",
    "حذف شد": "Deleted",
    "برنامه‌های نصب‌شده": "Installed apps",
    "جستجو (مثلاً telegram)…": "Search (e.g. telegram)…",
    "شامل برنامه‌های سیستمی": "Include system apps",
    "ذخیره‌ی لیست": "Save list",
    "عملیات روی برنامه‌ی انتخاب‌شده": "Actions for the selected app",
    "یک برنامه را از لیست انتخاب کن.": "Select an app from the list.",
    "اجرا": "Launch",
    "توقف اجباری": "Force stop",
    "تنظیمات برنامه روی گوشی": "App settings on phone",
    "استخراج APK به کامپیوتر": "Extract APK to computer",
    "پاک کردن داده‌ها": "Clear data",
    "حذف برنامه": "Uninstall app",
    "نصب APK از کامپیوتر": "Install APK from computer",
    "%d برنامه": "%d apps",
    "اول یک برنامه را انتخاب کن": "Select an app first",
    "در حال خواندن اطلاعات…": "Reading info…",
    "نسخه: %s\nنصب: %s\nآخرین به‌روزرسانی: %s": "Version: %s\nInstalled: %s\nLast updated: %s",
    "اجرا شد: ": "Launched: ",
    "متوقف شد: ": "Stopped: ",
    "باز شد": "Opened",
    "پاک کردن داده": "Clear data",
    "همه‌ی داده‌های %s پاک شود؟": "Clear all data of %s?",
    "داده‌های برنامه پاک شد": "App data cleared",
    "%s حذف شود؟": "Uninstall %s?",
    "حذف: ": "Uninstall: ",
    "ذخیره‌ی APK در…": "Save APK to…",
    "استخراج ناموفق": "Extraction failed",
    "✅ %d از %d فایل APK ذخیره شد": "✅ %d of %d APK files saved",
    "لیست خالی است": "The list is empty",
    "ذخیره": "Save",
    "ذخیره شد: ": "Saved: ",
    "شروع": "Start",
    "همه (Verbose)": "All (Verbose)",
    "Debug به بالا": "Debug and above",
    "Info به بالا": "Info and above",
    "Warning به بالا": "Warning and above",
    "Error به بالا": "Error and above",
    "جستجو در لاگ…": "Search the log…",
    "مکث": "Pause",
    "پاک کردن نمایش": "Clear view",
    "ذخیره در فایل": "Save to file",
    "لاگ گوشی": "Clear phone log",
    "اجرای logcat ناموفق: %s": "Failed to start logcat: %s",
    "توقف": "Stop",
    "لاگ گوشی پاک شد": "Phone log cleared",
    "دستور shell (مثلاً: getprop ro.product.model) — Enter؛ بالا/پایین = تاریخچه": "Shell command (e.g. getprop ro.product.model) — Enter; Up/Down = history",
    "پاک کردن": "Clear",
    "مشخصات": "Specs",
    "شبکه": "Network",
    "پردازش‌ها": "Processes",
    "حافظه": "Storage",
    "برنامه‌ی فعال": "Foreground app",
    "(بدون خروجی)": "(no output)",
    "اول به گوشی وصل شو (تب «اتصال»)": "Connect to your phone first (Connection tab)",
    "انجام شد": "Done",
    "توقف ضبط  (Ctrl+R)": "Stop recording  (Ctrl+R)",
    "برگشت  (Alt+←)": "Back  (Alt+←)",
    "خانه  (Alt+Home)": "Home  (Alt+Home)",
    "برنامه‌های اخیر  (Alt+↓)": "Recent apps  (Alt+↓)",
    "روشن/خاموش صفحه": "Screen on/off",
    "صدا بیشتر": "Volume up",
    "صدا کمتر": "Volume down",
    "اسکرین‌شات سریع  (Ctrl+S)": "Quick screenshot  (Ctrl+S)",
    "کپی تصویر  (Ctrl+Shift+C)": "Copy image  (Ctrl+Shift+C)",
    "ضبط ویدیوی صفحه  (Ctrl+R)": "Record screen  (Ctrl+R)",
    "چرخش صفحه": "Rotate screen",
    "باز کردن اعلان‌ها": "Open notifications",
    "پوشه‌ی تصاویر و ویدیوها": "Images and videos folder",
    "ورودی": "Input",
    "ماکرو": "Macro",
    "حرکت‌ها": "Gestures",
    "اسکرول به پایین": "Scroll down",
    "اسکرول به بالا": "Scroll up",
    "swipe به چپ": "Swipe left",
    "swipe به راست": "Swipe right",
    "دوبار لمس وسط صفحه": "Double tap the center",
    "صفحه و نور": "Screen and light",
    "بیدار کردن و باز کردن قفل": "Wake and unlock",
    "خاموش کردن صفحه": "Turn screen off",
    "روشنایی": "Brightness",
    "رسانه": "Media",
    "نمایش": "Display",
    "نمایش زنده‌ی صفحه": "Live screen",
    "سریع (هر ۰٫۲۵ ثانیه)": "Fast (every 0.25 s)",
    "معمولی (هر ۰٫۵ ثانیه)": "Normal (every 0.5 s)",
    "کم‌مصرف (هر ۱ ثانیه)": "Low power (every 1 s)",
    "ذخیره‌ی اسکرین‌شات به‌صورت دلخواه…": "Save screenshot as…",
    "ضبط ویدیو تا ۳ دقیقه؛ بعد از توقف خودکار به کامپیوتر می‌آید.": "Recording lasts up to 3 minutes, then is copied to your computer automatically.",
    "تایپ روی گوشی": "Type on the phone",
    "متن را بنویس و Enter بزن…": "Type text and press Enter…",
    "فارسی/یونیکد با ADBKeyboard": "Persian/Unicode via ADBKeyboard",
    "برنامه‌ی ADBKeyboard باید روی گوشی نصب و به‌عنوان کیبورد انتخاب شده باشد.": "ADBKeyboard must be installed on the phone and selected as the keyboard.",
    "ارسال": "Send",
    "موس روی صفحه": "Mouse on screen",
    "کلیک چپ = لمس\nنگه‌داشتن = لمس طولانی\nکشیدن = swipe\nچرخ موس = اسکرول\nکلیک راست = برگشت\nکلیک وسط = خانه": "Left click = tap\nHold = long press\nDrag = swipe\nMouse wheel = scroll\nRight click = back\nMiddle click = home",
    "کیبورد": "Keyboard",
    "روی صفحه‌ی گوشی کلیک کن و با کیبورد کامپیوتر تایپ کن. حروف فارسی فقط با ADBKeyboard تایپ می‌شوند؛ یا از تب «کیبورد و ریموت PC» استفاده کن.": "Click the phone screen and type with your computer keyboard. Persian letters need ADBKeyboard, or use the \"Keyboard & PC remote\" tab.",
    "ضبط": "Record",
    "شروع ضبط": "Start recording",
    "پخش": "Playback",
    "تکرار:": "Repeat:",
    "۰٫۵×": "0.5×",
    "۱×": "1×",
    "۲×": "2×",
    "۴×": "4×",
    "پخش ماکرو": "Play macro",
    "فایل": "File",
    "باز کردن": "Open",
    "ماکرویی ضبط نشده. «شروع ضبط» را بزن و کارها را روی صفحه انجام بده.": "No macro recorded. Press \"Start recording\" and perform actions on the screen.",
    "بیدار شد؛ اگر PIN دارد دستی وارد کن": "Woke up; enter the PIN manually if there is one",
    "روشنایی: %d٪": "Brightness: %d%%",
    "هنوز تصویری از گوشی نیامده": "No image from the phone yet",
    "ذخیره شد: %s": "Saved: %s",
    "تصویر در کلیپ‌بورد کپی شد": "Image copied to the clipboard",
    "هنوز تصویری نیست": "No image yet",
    "شروع ضبط ناموفق: %s": "Failed to start recording: %s",
    "در حال ضبط… %d ثانیه": "Recording… %d s",
    "در حال پایان ضبط و انتقال به کامپیوتر…": "Finishing the recording and copying it to the computer…",
    "ضبط/انتقال ناموفق بود.": "Recording/transfer failed.",
    "✅ ویدیو ذخیره شد: %s": "✅ Video saved: %s",
    "پایان ضبط": "Stop recording",
    "در حال ضبط… کارها را روی صفحه انجام بده.": "Recording… perform actions on the screen.",
    "%d عمل ضبط شد.": "%d actions recorded.",
    "ماکرویی ضبط یا باز نشده": "No macro recorded or opened",
    "دور %d تمام شد": "Round %d finished",
    "پخش ماکرو تمام شد.": "Macro playback finished.",
    "ماکرویی برای ذخیره نیست": "No macro to save",
    "ذخیره‌ی ماکرو": "Save macro",
    "ماکرو ذخیره شد": "Macro saved",
    "باز کردن ماکرو": "Open macro",
    "%d عمل بارگذاری شد.": "%d actions loaded.",
    "فایل ماکرو معتبر نیست: %s": "Invalid macro file: %s",
    "روشن": "On",
    ": روشن": ": On",
    "خاموش": "Off",
    ": خاموش": ": Off",
    "تنظیمات سریع": "Quick settings",
    "داده‌ی موبایل": "Mobile data",
    "مزاحم نشوید": "Do not disturb",
    "حالت تاریک": "Dark mode",
    "روشن ماندن صفحه (شارژ)": "Keep screen on (charging)",
    "نمایش لمس‌ها و مختصات": "Show touches and coordinates",
    "تنظیمات": "Settings",
    "اندازه‌ی فونت: ۱٫۰×": "Font size: 1.0×",
    "اندازه‌ی فونت: %.1f×": "Font size: %.1f×",
    "اندازه‌ی فونت تغییر کرد": "Font size changed",
    "خاموشی خودکار صفحه:": "Screen timeout:",
    "۱۵ ثانیه": "15 seconds",
    "۳۰ ثانیه": "30 seconds",
    "۱ دقیقه": "1 minute",
    "۲ دقیقه": "2 minutes",
    "۵ دقیقه": "5 minutes",
    "۱۰ دقیقه": "10 minutes",
    "۳۰ دقیقه": "30 minutes",
    "زمان خاموشی تغییر کرد": "Screen timeout changed",
    "بلوتوث": "Bluetooth",
    "نمایشگر": "Display",
    "صدا": "Sound",
    "گزینه‌های توسعه‌دهنده": "Developer options",
    "دسترس‌پذیری": "Accessibility",
    "موقعیت مکانی": "Location",
    "زبان": "Language",
    "درباره‌ی گوشی": "About phone",
    "باز کردن تنظیمات": "Open settings",
    "تنظیمات باز شد": "Settings opened",
    "نگهداری": "Maintenance",
    "بستن برنامه‌های پس‌زمینه": "Close background apps",
    "برنامه‌های پس‌زمینه بسته شدند": "Background apps closed",
    "پاک کردن کش همه‌ی برنامه‌ها": "Clear cache of all apps",
    "کش پاک شد (روی بعضی گوشی‌ها محدود است)": "Cache cleared (limited on some phones)",
    "ارسال به گوشی": "Send to phone",
    "باز کردن لینک در مرورگر گوشی:": "Open a link in the phone browser:",
    "باز کن": "Open",
    "شماره‌گیری / پیامک:": "Dial / SMS:",
    "متن پیامک (اختیاری)": "SMS text (optional)",
    "شماره‌گیری": "Dial",
    "ساخت پیامک": "Compose SMS",
    "عکس بگیر و بیاور": "Take a photo and fetch it",
    "دوربین گوشی را باز می‌کند، عکس می‌گیرد و همان لحظه به کامپیوتر می‌آورد. اگر عکس نگرفت، شاتر را روی تصویر کلیک کن و «آخرین عکس را بیاور» را بزن.": "Opens the phone camera, takes a photo and brings it to the computer right away. If it doesn't shoot, click the shutter on the screen and press \"Fetch the latest photo\".",
    "آخرین عکس گوشی را بیاور": "Fetch the latest phone photo",
    "لینک روی گوشی باز شد": "Link opened on the phone",
    "شماره‌گیر باز شد": "Dialer opened",
    "پیامک آماده شد (ارسال با خودت)": "SMS ready (you send it)",
    "در حال گرفتن عکس…": "Taking a photo…",
    "در حال آوردن آخرین عکس…": "Fetching the latest photo…",
    "عکس آمد: %s": "Photo received: %s",
    "عکس جدیدی پیدا نشد؛ شاتر را دستی بزن و «آخرین عکس» را بگیر.": "No new photo found; press the shutter manually and fetch the latest photo.",
    "مشخصات دستگاه": "Device specs",
    "مدل": "Model",
    "سازنده": "Manufacturer",
    "نسخه‌ی اندروید": "Android version",
    "معماری CPU": "CPU architecture",
    "وصله‌ی امنیتی": "Security patch",
    "رزولوشن": "Resolution",
    "تراکم": "Density",
    "سریال": "Serial",
    "نسخه‌ی سیستم": "System build",
    "ذخیره‌ی گزارش": "Save report",
    "پایش زنده (هر ۳ ثانیه)": "Live monitor (every 3 s)",
    "پایش باتری و RAM": "Monitor battery and RAM",
    "تست اینترنت گوشی (ping)": "Phone internet test (ping)",
    "تست": "Test",
    "%s  (آزاد: %s)": "%s  (free: %s)",
    "%s  (استفاده‌شده: %s)": "%s  (used: %s)",
    "در حال شارژ ": "Charging ",
    "در حال مصرف": "Discharging",
    "شارژ نمی‌شود": "Not charging",
    "پر": "Full",
    "گزارش ذخیره شد: ": "Report saved: ",
    "در حال تست…": "Testing…",
    "✅ میانگین %s ms   (کمینه %s / بیشینه %s)": "✅ Average %s ms   (min %s / max %s)",
    "❌ پاسخی نیامد:\n": "❌ No reply:\n",
    "Logcat زنده": "Live Logcat",
    "ترمینال adb": "adb terminal",
    "APK را انتخاب کن": "Choose an APK",
    "در حال انتقال %d مورد…": "Transferring %d items…",
    "نصب ": "Install ",
    "ارسال ": "Send ",
    "انتقال ناموفق: %s": "Transfer failed: %s",
    "✅ %d از %d مورد انجام شد": "✅ %d of %d items done",
    "دسترسی‌های ریموت (برای امنیت پیش‌فرض خاموش)": "Remote permissions (off by default for safety)",
    "نمایش و کنترل صفحه‌ی کامپیوتر از گوشی": "Show and control the PC screen from the phone",
    "دستورهای سیستمی (قفل / خواب / خاموشی)": "System commands (lock / sleep / shutdown)",
    "دستورهای سیستمی ": "System commands ",
    "صفحه‌ی وب گوشی ۸ بخش دارد: تایپ، موس، ارائه، رسانه، میانبر، صفحه‌ی PC، کلیپ‌بورد، سیستم.": "The phone web page has 8 sections: type, mouse, slides, media, shortcuts, PC screen, clipboard, system.",
    "ارسال متن یا لینک از کامپیوتر به گوشی": "Send text or a link from the computer to the phone",
    "متن یا لینک… (در صفحه‌ی وب گوشی نمایش داده می‌شود)": "Text or link… (shown on the phone web page)",
    "ارسال به صفحه‌ی گوشی": "Send to the phone page",
    "نمایش صفحه‌ی PC ": "PC screen sharing ",
    "فعال شد": "enabled",
    "غیرفعال شد": "disabled",
    "متن برای گوشی ارسال شد": "Text sent to the phone",
    "سرور روشن نیست یا متن خالی است": "The server is off or the text is empty",
    "نمایش / مخفی کردن": "Show / hide",
    "اسکرین‌شات سریع": "Quick screenshot",
    "خروج": "Quit",
    "پل گوشی ↔ کامپیوتر": "Phone Bridge",
    "تنظیمات برنامه": "App settings",
    "هنگام بستن پنجره، در سینی سیستم بماند": "Keep running in the system tray when the window is closed",
    "اتصال خودکار مجدد وقتی گوشی قطع شد": "Reconnect automatically when the phone drops",
    "⚠ ارتباط با گوشی قطع شد.": "⚠ Connection to the phone was lost.",
    "ارتباط با گوشی قطع شد": "Connection to the phone was lost",
    "؛ تلاش برای اتصال مجدد…": "; trying to reconnect…",
    "✅ اتصال مجدد برقرار شد": "✅ Reconnected",
    "موس و کیبورد کامپیوتر برای گوشی، کیبورد گوشی برای کامپیوتر": "Your PC mouse and keyboard for the phone, your phone keyboard for the PC",
    "گوشی: قطع": "Phone: offline",
    "سرور کیبورد: خاموش": "Keyboard server: off",
    "فا": "فا",
    "تغییر زبان  /  Language": "Language  /  تغییر زبان",
    "تغییر تم تیره/روشن": "Toggle dark/light theme",
    "کنترل": "Control",
    "کیبورد و ریموت PC": "Keyboard && PC remote",
    "ابزارها": "Tools",
    "اطلاعات": "Info",
    "فایل‌ها": "Files",
    "برنامه‌ها": "Apps",
    "توسعه": "Developer",
    "اتصال": "Connection",
    "آماده": "Ready",
    "ابزار adb پیدا نشد. «دانلود خودکار adb» را بزنید یا adb.exe را دستی انتخاب کنید.": "adb was not found. Press \"Download adb automatically\" or choose adb.exe manually.",
    "آدرس برای مرورگر گوشی": "Address for the phone browser",
    "این آدرس را در مرورگر گوشی (همان وای‌فای) باز کن. هرچه با کیبورد گوشی تایپ کنی، روی کامپیوتر — همان‌جا که مکان‌نما هست — تایپ می‌شود.": "Open this address in your phone browser (same Wi-Fi). Whatever you type on the phone keyboard is typed on the computer — wherever the cursor is.",
    "روشن/خاموش کردن سرور": "Turn server on/off",
    "کپی آدرس": "Copy address",
    "توکن جدید": "New token",
    "آدرس قبلی از کار می‌افتد": "The old address will stop working",
    "پورت:": "Port:",
    "امنیت": "Security",
    "آدرس یک توکن تصادفی دارد و فقط کسی که آن را دارد می‌تواند روی کامپیوتر تایپ کند. اگر فایروال ویندوز پرسید، Python را روی «شبکه‌ی خصوصی» مجاز کن.": "The address contains a random token; only someone who has it can type on your computer. If Windows Firewall asks, allow Python on \"Private networks\".",
    "رویدادها": "Events",
    "۱) ابزار adb": "1) adb tool",
    "پیدا کردن خودکار": "Find automatically",
    "انتخاب adb.exe": "Choose adb.exe",
    "دانلود خودکار adb (حدود ۷ مگابایت)": "Download adb automatically (about 7 MB)",
    "باز کردن صفحه‌ی دانلود در مرورگر": "Open the download page in the browser",
    "۲) اتصال به گوشی": "2) Connect to the phone",
    "تازه‌سازی لیست": "Refresh list",
    "✅ اتصال به دستگاه انتخاب‌شده": "✅ Connect to the selected device",
    "قطع اتصال": "Disconnect",
    "— اتصال بی‌سیم (IP:پورت از Wireless debugging گوشی) —": "— Wireless connection (IP:port from the phone's Wireless debugging) —",
    "IP:پورت جفت‌سازی": "Pairing IP:port",
    "کد ۶ رقمی": "6-digit code",
    "جفت‌سازی": "Pair",
    "با کابل USB وصل است؛ تبدیل به وای‌فای": "Connected by USB; switch to Wi-Fi",
    "یک‌بار با کابل، بعد بی‌سیم": "Once by cable, then wireless",
    "اتصال سریع با QR  (اندروید ۱۱ به بالا)": "Quick connect with QR  (Android 11+)",
    "برای شروع «ساخت QR» را بزن": "Press \"Create QR\" to start",
    "۱. گوشی و کامپیوتر به یک وای‌فای باشند.\n۲. روی گوشی: تنظیمات ← گزینه‌های توسعه‌دهنده ← Wireless debugging‏ را روشن کن.\n۳. گزینه‌ی Pair device with QR code‏ را بزن و این QR را اسکن کن. (با دوربین معمولی گوشی کار نمی‌کند.)\n۴. بقیه خودکار است: جفت‌سازی، اتصال و نمایش صفحه.": "1. Phone and computer must be on the same Wi-Fi.\n2. On the phone: Settings → Developer options → turn on Wireless debugging.\n3. Tap \"Pair device with QR code\" and scan this QR. (The regular camera app won't work.)\n4. The rest is automatic: pairing, connecting and showing the screen.",
    "ساخت QR و شروع": "Create QR and start",
    "لغو": "Cancel",
    "گزارش adb": "adb log",
    "گوشی: متصل ✓": "Phone: connected ✓",
    "سرور کیبورد: روشن ✓": "Keyboard server: on ✓",
    "حروف غیرانگلیسی با adb تایپ نمی‌شود؛ ADBKeyboard را نصب و تیک گزینه را بزن، یا از تب «کیبورد گوشی» استفاده کن.": "Non-English characters can't be typed through adb; install ADBKeyboard and tick the option, or use the \"Keyboard & PC remote\" tab.",
    "❌ adb پیدا نشد": "❌ adb not found",
    "adb پیدا نشد. دانلود خودکار را بزنید یا adb.exe را دستی انتخاب کنید.": "adb not found. Press \"Download automatically\" or choose adb.exe manually.",
    "adb.exe را انتخاب کنید": "Choose adb.exe",
    "adb (adb.exe adb);;همه (*)": "adb (adb.exe adb);;All (*)",
    "در حال دانلود از dl.google.com …": "Downloading from dl.google.com …",
    "adb داخل فایل دانلودشده نبود": "adb was not in the downloaded file",
    "دانلود نشد: %s\nصفحه‌ی دانلود را در مرورگر باز کنید، zip را استخراج کنید و «انتخاب adb.exe» را بزنید.": "Download failed: %s\nOpen the download page in the browser, extract the zip and press \"Choose adb.exe\".",
    "ابتدا adb را پیدا یا دانلود کنید.": "Find or download adb first.",
    "دستگاه‌ها:\n": "Devices:\n",
    "(خالی)": "(empty)",
    "⚠ پنجره‌ی «Allow USB debugging» را روی گوشی تأیید کنید و دوباره تازه‌سازی بزنید.": "⚠ Approve the \"Allow USB debugging\" prompt on the phone and refresh again.",
    "در حال اتصال…": "Connecting…",
    "اتصال ناموفق": "Connection failed",
    "اتصال ناموفق: ": "Connection failed: ",
    "✅ وصل شد: %s (%dx%d)": "✅ Connected: %s (%dx%d)",
    "پیش‌فرض": "default",
    "گوشی متصل شد": "Phone connected",
    "اتصال قطع شد.": "Disconnected.",
    "IP:پورت را بنویسید.": "Enter IP:port.",
    "IP:پورت جفت‌سازی و کد را بنویسید.": "Enter the pairing IP:port and code.",
    "دستگاه USB پیدا نشد. کابل را وصل و USB debugging را روشن کنید.": "No USB device found. Plug in the cable and enable USB debugging.",
    "IP گوشی پیدا نشد؛ گوشی را به همان وای‌فای وصل کنید.\n": "Couldn't find the phone's IP; connect the phone to the same Wi-Fi.\n",
    "\nحالا کابل را می‌توانید جدا کنید.": "\nYou can unplug the cable now.",
    "منتظر اسکن QR توسط گوشی…": "Waiting for the phone to scan the QR…",
    "لغو شد": "Cancelled",
    "راه‌اندازی مجدد adb با mDNS…": "Restarting adb with mDNS…",
    "این نسخه‌ی adb از mDNS پشتیبانی نمی‌کند؛ از «جفت‌سازی با کد» استفاده کن.": "This adb version doesn't support mDNS; use \"pair with code\" instead.",
    "گوشی QR را اسکن نکرد (یا mDNS در این شبکه مسدود است).": "The phone didn't scan the QR (or mDNS is blocked on this network).",
    "زمان تمام شد؛ گوشی QR را اسکن نکرد. دوباره امتحان کن.": "Timed out; the phone didn't scan the QR. Try again.",
    "گوشی پیدا شد؛ در حال جفت‌سازی…": "Phone found; pairing…",
    "جفت‌سازی ناموفق بود (گزارش را ببین).": "Pairing failed (see the log).",
    "جفت شد؛ در حال اتصال…": "Paired; connecting…",
    "جفت شد ولی پورت اتصال پیدا نشد. IP:پورت صفحه‌ی Wireless debugging را در «اتصال بی‌سیم» بزن.": "Paired, but the connection port wasn't found. Enter the IP:port from the Wireless debugging screen under \"Wireless connection\".",
    "جفت شد؛ ولی آدرس اتصال پیدا نشد (راهنما در گزارش).": "Paired, but the connection address wasn't found (see the log).",
    "✅ وصل شد": "✅ Connected",
    "✅\nگوشی وصل شد": "✅\nPhone connected",
    "pynput نصب نیست": "pynput is not installed",
    "کتابخانه‌ی pynput نصب نیست:  py -m pip install pynput": "pynput is not installed:  py -m pip install pynput",
    "پورت اشغال است": "Port is in use",
    "سرور روشن نشد (پورت اشغال؟): %s": "Server failed to start (port in use?): %s",
    "سرور روشن نشد: %s": "Server failed to start: %s",
    "سرور خاموش شد": "Server stopped",
    "توکن جدید ساخته شد": "New token created",
    "سرور خاموش است": "Server is off",
    "آدرس کپی شد": "Address copied",
    "پل گوشی": "Phone Bridge",
    "برنامه در سینی سیستم در حال اجراست.": "The app is running in the system tray.",
}


def tr(s):
    """ترجمه‌ی متن رابط؛ در حالت فارسی همان متن برمی‌گردد."""
    return EN.get(s, s) if LANG == "en" else s


def _data_dir():
    """پوشه‌ی تنظیمات/فونت/adb: کنار برنامه (قابل‌حمل)، یا ~/.phone-bridge برای نصب با pip، یا PHONE_BRIDGE_HOME."""
    env = os.environ.get("PHONE_BRIDGE_HOME")
    if env:
        p = Path(env).expanduser()
    elif getattr(sys, "frozen", False):
        p = Path(sys.executable).resolve().parent
    else:
        here = Path(os.path.abspath(__file__)).parent
        p = Path.home() / ".phone-bridge" if {"site-packages", "dist-packages"} & set(here.parts) else here
    try:
        p.mkdir(parents=True, exist_ok=True)
    except OSError:
        p = Path(tempfile.gettempdir()) / "phone-bridge"
        p.mkdir(parents=True, exist_ok=True)
    return p


APP_DIR = _data_dir()
CONFIG_FILE = APP_DIR / "phone_bridge_config.json"
NOWIN = {"creationflags": 0x08000000} if sys.platform == "win32" else {}   # بدون پنجره‌ی سیاه cmd


def load_cfg():
    try:
        return json.loads(CONFIG_FILE.read_text("utf-8"))
    except Exception:
        return {}


def save_cfg(d):
    try:
        CONFIG_FILE.write_text(json.dumps(d, ensure_ascii=False, indent=1), "utf-8")
    except Exception:
        pass


# =============================
# فونت وزیر
# =============================
FONT_FAMILY = "Segoe UI"
VAZIR_NAMES = ("Vazirmatn", "Vazirmatn UI", "Vazir", "Vazir FD")
FONT_FILES = ("Vazirmatn-Regular.ttf", "Vazirmatn-Medium.ttf", "Vazirmatn-Bold.ttf")
FONT_URLS = (
    "https://cdn.jsdelivr.net/npm/vazirmatn@33.0.3/fonts/ttf/{f}",
    "https://fastly.jsdelivr.net/npm/vazirmatn@33.0.3/fonts/ttf/{f}",
    "https://gcore.jsdelivr.net/npm/vazirmatn@33.0.3/fonts/ttf/{f}",
    "https://unpkg.com/vazirmatn@33.0.3/fonts/ttf/{f}",
    "https://raw.githubusercontent.com/rastikerdar/vazirmatn/master/fonts/ttf/{f}",
)
FALLBACK_FAMILIES = ("IRANSansX", "IRANSans", "Sahel", "Shabnam", "Samim", "Estedad", "Segoe UI")


def setup_fonts():
    global FONT_FAMILY
    for d in (APP_DIR / "fonts", APP_DIR, APP_DIR / "Vazirmatn", Path(tempfile.gettempdir()) / "phone_bridge_fonts"):
        try:
            if d.is_dir():
                for pat in ("Vazir*.ttf", "Vazir*.otf", "vazir*.ttf"):
                    for f in d.glob(pat):
                        QFontDatabase.addApplicationFont(str(f))
        except Exception:
            pass
    fams = set(QFontDatabase.families())
    for n in VAZIR_NAMES:
        if n in fams:
            FONT_FAMILY = n
            return True
    for n in FALLBACK_FAMILIES:
        if n in fams:
            FONT_FAMILY = n
            break
    return False


def fetch_fonts():
    """دانلود فونت وزیر در پس‌زمینه. True اگر چیزی دانلود شد."""
    target = APP_DIR / "fonts"
    try:
        target.mkdir(parents=True, exist_ok=True)
    except Exception:
        target = Path(tempfile.gettempdir()) / "phone_bridge_fonts"
        target.mkdir(parents=True, exist_ok=True)
    got = False
    for fname in FONT_FILES:
        dest = target / fname
        if dest.exists() and dest.stat().st_size > 50_000:
            got = True
            continue
        for url in FONT_URLS:
            try:
                req = urllib.request.Request(url.format(f=fname), headers={"User-Agent": "PhoneBridge/1.0"})
                with urllib.request.urlopen(req, timeout=7) as r:
                    data = r.read()
                if len(data) > 50_000 and data[:4] in (b"\x00\x01\x00\x00", b"OTTO", b"true"):
                    dest.write_bytes(data)
                    got = True
                    break
            except Exception:
                continue
    return got


# =============================
# تم‌ها (هم‌سبک برنامه‌ی Photo Memory)
# =============================
THEMES = {
    "dark": {
        "bg": "#0A0A0F", "bg2": "#101016", "card": "#13131A", "card2": "#191922", "btn": "#1B1B24", "btnh": "#262633",
        "input": "#0E0E14", "text": "#F2F2F7", "muted": "#8E8E9A", "a1": "#7C5CFF", "a2": "#4F8CFF",
        "a1h": "#9479FF", "a2h": "#7AA6FF", "pop": "#1B1B24", "list": "#0E0E14", "hover": "#1E1E28",
        "scroll": "#33333F", "border": "#1F1F2A", "border2": "#2E2E3B", "dis": "#111117", "danger1": "#FF5A5F",
        "danger2": "#E5484D", "ok": "#3DD68C", "warn": "#FFB224", "btn_top": "#1B1B24", "bezel": "#050508",
        "aur": 30, "dark": True,
    },
    "light": {
        "bg": "#F5F5F8", "bg2": "#ECECF1", "card": "#FFFFFF", "card2": "#FAFAFC", "btn": "#F0F0F5", "btnh": "#E6E6EE",
        "input": "#F7F7FA", "text": "#15151C", "muted": "#74747F", "a1": "#6B4DFF", "a2": "#3F7BFF",
        "a1h": "#7F66FF", "a2h": "#6894FF", "pop": "#FFFFFF", "list": "#F7F7FA", "hover": "#EEEEF4",
        "scroll": "#C9C9D4", "border": "#E8E8EF", "border2": "#D6D6E0", "dis": "#F2F2F6", "danger1": "#E5484D",
        "danger2": "#CE3A3F", "ok": "#1FA971", "warn": "#C77700", "btn_top": "#F0F0F5", "bezel": "#15151C",
        "aur": 20, "dark": False,
    },
}
CUR = THEMES["dark"]

QSS = """
* { font-family: '@font@', 'Vazirmatn', 'Segoe UI', 'Tahoma', sans-serif; }
QMainWindow { background: @bg@; }
QWidget { color: @text@; font-size: 9.5pt; }
QWidget#Root { background: transparent; }
QLabel { background: transparent; }
QToolTip { background: @pop@; color: @text@; border: 1px solid @border2@; border-radius: 8px; padding: 5px 9px; }
QFrame#Card, QFrame#Stage, QFrame#Panel { background: @card@; border: 1px solid @border@; border-radius: 18px; }
QFrame#Toolbar { background: @bg2@; border: none; border-radius: 16px; }
QFrame#Sep { background: @border2@; border: none; max-height: 1px; min-height: 1px; }
QLabel#CardTitle { color: @muted@; font-size: 8.5pt; font-weight: 700; }
QLabel#Caption { color: @muted@; font-size: 8.5pt; font-weight: 700; padding-top: 6px; }
QLabel#Brand { font-size: 14pt; font-weight: 800; }
QLabel#BrandSub { color: @muted@; font-size: 9pt; }
QLabel#Muted { color: @muted@; }
QLabel#Warn { color: @warn@; font-size: 9pt; }
QLabel#Url { background: @input@; border: 1px solid @border@; border-radius: 12px; padding: 12px 14px;
             font-size: 11.5pt; font-weight: 700; color: @a1h@; }
QLabel#Pill { border-radius: 12px; padding: 4px 12px; font-weight: 600; font-size: 8.5pt;
              background: @btn@; color: @muted@; }
QLabel#Pill[state="ok"] { background: rgba(61,214,140,34); color: @ok@; }
QLabel#Pill[state="warn"] { background: rgba(255,178,36,30); color: @warn@; }
QPushButton { background: @btn@; color: @text@; border: none; border-radius: 10px; padding: 8px 14px; font-weight: 500; }
QPushButton:hover { background: @btnh@; }
QPushButton:pressed { background: @a1@; color: white; }
QPushButton:disabled { background: @dis@; color: @muted@; }
QPushButton[variant="primary"] {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 @a1@, stop:1 @a2@); color: white; font-weight: 700;
}
QPushButton[variant="primary"]:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 @a1h@, stop:1 @a2h@);
}
QPushButton[variant="primary"]:disabled { background: @dis@; color: @muted@; }
QPushButton[variant="danger"] { background: @danger2@; color: white; font-weight: 700; }
QPushButton[variant="danger"]:hover { background: @danger1@; }
QPushButton#NavBtn { padding: 10px 6px; font-weight: 600; }
QPushButton#Round { padding: 0; border-radius: 12px; min-width: 38px; max-width: 38px; min-height: 38px; max-height: 38px; }
QPushButton#Tool { background: transparent; padding: 0; border-radius: 12px; min-width: 42px; max-width: 42px;
                   min-height: 42px; max-height: 42px; }
QPushButton#Tool:hover { background: @btnh@; }
QPushButton#Tool:pressed { background: @a1@; }
QPushButton#IconText { text-align: left; padding: 9px 12px; }
QPushButton#Dpad { padding: 0; border-radius: 14px; min-height: 46px; background: @btn@; }
QFrame#Seg { background: @btn@; border: none; border-radius: 12px; }
QPushButton#SegBtn { background: transparent; border-radius: 9px; padding: 7px 4px; color: @muted@; font-weight: 600; }
QPushButton#SegBtn:hover { color: @text@; }
QPushButton#SegBtn:checked { background: @card@; color: @text@; }
QLineEdit, QSpinBox {
    background: @input@; color: @text@; border: 1px solid @border@; border-radius: 10px;
    padding: 8px 11px; selection-background-color: @a1@;
}
QLineEdit:focus, QSpinBox:focus { border: 1px solid @a1@; }
QComboBox { background: @input@; color: @text@; border: 1px solid @border@; border-radius: 10px; padding: 7px 11px; }
QComboBox:hover, QComboBox:focus { border-color: @a1@; }
QComboBox::drop-down { border: none; width: 26px; }
QComboBox::down-arrow { image: url("@arrow@"); width: 12px; height: 12px; }
QComboBox QAbstractItemView {
    background: @pop@; color: @text@; border: 1px solid @border2@; border-radius: 10px; padding: 4px;
    selection-background-color: @a1@; selection-color: white; outline: 0;
}
QCheckBox { spacing: 10px; }
QCheckBox::indicator { width: 20px; height: 20px; border-radius: 7px; border: 1px solid @border2@; background: @input@; }
QCheckBox::indicator:hover { border-color: @a1@; }
QCheckBox::indicator:checked {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 @a1@, stop:1 @a2@); border: none; image: url("@check@");
}
QSlider::groove:horizontal { height: 4px; background: @btn@; border-radius: 2px; }
QSlider::sub-page:horizontal { background: @a1@; border-radius: 2px; }
QSlider::handle:horizontal { background: white; width: 16px; height: 16px; margin: -6px 0; border-radius: 8px;
                             border: 1px solid @border2@; }
QTabWidget::pane { border: none; background: transparent; top: 8px; }
QTabBar { background: transparent; }
QTabBar::tab { background: transparent; color: @muted@; border: none; border-radius: 15px; padding: 7px 15px;
               margin: 0 2px; font-weight: 600; }
QTabBar::tab:hover { color: @text@; background: @hover@; }
QTabBar::tab:selected { color: white;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 @a1@, stop:1 @a2@); }
QListWidget, QTextEdit {
    background: @list@; color: @text@; border: 1px solid @border@; border-radius: 12px; padding: 8px; outline: 0;
}
QListWidget::item { padding: 6px 4px; border-radius: 8px; }
QListWidget::item:hover { background: @hover@; }
QListWidget::item:selected { background: @a1@; color: white; }
QProgressBar { border: none; border-radius: 7px; background: @btn@; height: 14px; text-align: center; font-size: 8pt; }
QProgressBar::chunk { border-radius: 7px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 @a1@, stop:1 @a2@); }
QScrollBar:vertical { background: transparent; width: 10px; margin: 6px 2px; }
QScrollBar::handle:vertical { background: @scroll@; border-radius: 3px; min-height: 36px; margin: 0 2px; }
QScrollBar::handle:vertical:hover { background: @a1@; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
QStatusBar { background: transparent; color: @muted@; border: none; padding: 2px 10px; }
"""


def build_qss(t, icons):
    s = QSS.replace("@font@", FONT_FAMILY)
    for k, v in {**t, **icons}.items():
        s = s.replace("@%s@" % k, str(v))
    return s


def make_icons(t):
    d = Path(tempfile.gettempdir()) / "phone_bridge_icons"
    d.mkdir(exist_ok=True)
    tag = "d" if t["dark"] else "l"
    chk, arr = d / "check.png", d / ("arrow_%s.png" % tag)
    pm = QPixmap(20, 20)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor("white"), 2.4)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.drawPolyline([QPointF(5, 10.5), QPointF(8.6, 14), QPointF(15, 6.5)])
    p.end()
    pm.save(str(chk))
    pm = QPixmap(12, 12)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(t["muted"]), 1.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.drawPolyline([QPointF(2.5, 4.2), QPointF(6, 7.8), QPointF(9.5, 4.2)])
    p.end()
    pm.save(str(arr))
    return {"check": chk.as_posix(), "arrow": arr.as_posix()}


def qc(h, a=None):
    c = QColor(h)
    if a is not None:
        c.setAlpha(int(max(0, min(255, a))))
    return c


# =============================
# ابزار ارسال کار به نخ اصلی
# =============================
class Bus(QObject):
    call = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.call.connect(self._run)

    @pyqtSlot(object)
    def _run(self, fn):
        try:
            fn()
        except Exception as e:
            print("UI error:", e)


BUS = None


def ui(fn):
    """اجرای fn در نخ اصلی (از هر نخی امن است)."""
    BUS.call.emit(fn)


# =============================
# ADB
# =============================
def find_adb(saved=None):
    cands = []
    if saved:
        cands.append(Path(saved))
    w = shutil.which("adb")
    if w:
        cands.append(Path(w))
    exe = "adb.exe" if sys.platform == "win32" else "adb"
    cands += [APP_DIR / "platform-tools" / exe, APP_DIR / exe, Path.cwd() / "platform-tools" / exe]
    for env in ("ANDROID_HOME", "ANDROID_SDK_ROOT"):
        if os.environ.get(env):
            cands.append(Path(os.environ[env]) / "platform-tools" / exe)
    if os.environ.get("LOCALAPPDATA"):
        cands.append(Path(os.environ["LOCALAPPDATA"]) / "Android" / "Sdk" / "platform-tools" / exe)
    cands += [Path.home() / "Downloads" / "platform-tools" / exe, Path("C:/platform-tools") / exe,
              Path("C:/adb") / exe, Path("C:/Android/platform-tools") / exe]
    for c in cands:
        try:
            if c.is_file():
                return str(c)
        except Exception:
            pass
    return None


def adb_cmd(exe, args, timeout=25):
    """اجرای یک‌بارهی adb؛ (کد خروج، خروجی متنی)"""
    try:
        r = subprocess.run([exe] + args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=timeout, env={**os.environ, "ADB_MDNS_OPENSCREEN": "1"}, **NOWIN)
        return r.returncode, ((r.stdout or "") + (r.stderr or "")).strip()
    except subprocess.TimeoutExpired:
        return 1, tr("زمان انتظار تمام شد (timeout)")
    except Exception as e:
        return 1, str(e)


def parse_mdns(out):
    """خروجی `adb mdns services` ← [(نام، نوع سرویس، ip:port)]"""
    res = []
    for l in out.splitlines():
        p = l.split()
        if len(p) >= 3 and p[1].startswith("_adb"):
            res.append((p[0], p[1], p[2]))
    return res


class Adb:
    """یک shell دائمی با adb نگه می‌دارد تا لمس و تایپ سریع باشد."""

    def __init__(self, exe, serial=None):
        self.exe = exe
        self.serial = serial
        self.base = [exe] + (["-s", serial] if serial else [])
        rc, out = adb_cmd(exe, (["-s", serial] if serial else []) + ["shell", "wm", "size"], 15)
        lines = [l for l in out.splitlines() if "size" in l.lower() and ":" in l]
        if rc != 0 or not lines:
            raise RuntimeError(out or tr("پاسخی از گوشی نیامد"))
        w, h = lines[-1].split(":")[1].strip().split("x")
        self.size = (int(w), int(h))
        self.proc = subprocess.Popen(self.base + ["shell"], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL,
                                     stderr=subprocess.DEVNULL, text=True, bufsize=1, **NOWIN)
        self.q = queue.Queue()
        self.alive = True
        threading.Thread(target=self._worker, daemon=True).start()

    def _worker(self):
        while self.alive:
            cmd = self.q.get()
            if cmd is None:
                break
            try:
                self.proc.stdin.write(cmd + "\n")
                self.proc.stdin.flush()
            except Exception as e:
                print("ADB error:", e)

    def run(self, cmd):
        self.q.put(cmd)

    def tap(self, x, y):
        self.run("input tap %d %d" % (x, y))

    def swipe(self, x1, y1, x2, y2, ms=200):
        self.run("input swipe %d %d %d %d %d" % (x1, y1, x2, y2, ms))

    def key(self, code):
        self.run("input keyevent %d" % code)

    def text(self, s):
        safe = s.replace("'", "'\\''").replace(" ", "%s")
        self.run("input text '%s'" % safe)

    def text_unicode(self, s):
        """نیازمند برنامه‌ی ADBKeyboard روی گوشی (برای فارسی)."""
        b = base64.b64encode(s.encode("utf-8")).decode("ascii")
        self.run("am broadcast -a ADB_INPUT_B64 --es msg %s" % b)

    def screencap(self):
        try:
            r = subprocess.run(self.base + ["exec-out", "screencap", "-p"], capture_output=True, timeout=15, **NOWIN)
        except Exception as e:
            return None, str(e)
        if r.stdout[:4] == b"\x89PNG":
            return r.stdout, None
        return None, ((r.stderr or r.stdout)[:300].decode("utf-8", "replace").strip() or tr("خروجی خالی"))

    def _sargs(self):
        return ["-s", self.serial] if self.serial else []

    def sh(self, cmd, timeout=25):
        """یک دستور shell اجرا می‌کند و خروجی متنی را برمی‌گرداند."""
        return adb_cmd(self.exe, self._sargs() + ["shell", cmd], timeout)[1]

    def pull(self, remote, local, timeout=900):
        return adb_cmd(self.exe, self._sargs() + ["pull", remote, local], timeout)

    def push(self, local, remote, timeout=900):
        return adb_cmd(self.exe, self._sargs() + ["push", local, remote], timeout)

    def install(self, apk):
        return adb_cmd(self.exe, self._sargs() + ["install", "-r", apk], 900)

    def close(self):
        self.alive = False
        self.q.put(None)
        try:
            self.proc.terminate()
        except Exception:
            pass


class Grabber(threading.Thread):
    """تصویر صفحه‌ی گوشی را مرتب می‌گیرد و به نمایشگر می‌دهد."""

    def __init__(self, adb, view):
        super().__init__(daemon=True)
        self.adb, self.view = adb, view
        self.stop_ev = threading.Event()
        self.interval = 0.5
        self.live = True

    def run(self):
        while not self.stop_ev.is_set():
            if not self.live:
                time.sleep(0.2)
                continue
            t0 = time.time()
            png, err = self.adb.screencap()
            if self.stop_ev.is_set():
                break
            if png:
                ui(lambda p=png: self.view.set_png(p))
            else:
                ui(lambda e=err: self.view.set_message(tr("تصویری از گوشی نیامد:\n") + e))
                time.sleep(1.5)
            time.sleep(max(0.02, self.interval - (time.time() - t0)))


# =============================
# صفحه‌ی وب ریموت (روی گوشی باز می‌شود)
# =============================
PAGE = r"""<!doctype html>
<html lang="__LANG__" dir="__DIR__"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">
<meta name="theme-color" content="#0A0A0F">
<title>Phone Bridge</title>
<style>
@font-face{font-family:VZ;font-weight:400;src:url("/f/Vazirmatn-Regular.ttf?t=__T__") format("truetype")}
@font-face{font-family:VZ;font-weight:500;src:url("/f/Vazirmatn-Medium.ttf?t=__T__") format("truetype")}
@font-face{font-family:VZ;font-weight:700;src:url("/f/Vazirmatn-Bold.ttf?t=__T__") format("truetype")}
:root{--bg:#0A0A0F;--s1:#13131A;--s2:#1B1B24;--s3:#272733;--tx:#F2F2F7;--mu:#8E8E9A;--ln:rgba(255,255,255,.07);
      --a1:#7C5CFF;--a2:#4F8CFF;--ok:#3DD68C;--bad:#FF5A5F;--glass:rgba(19,19,26,.82)}
@media(prefers-color-scheme:light){:root{--bg:#F5F5F8;--s1:#FFFFFF;--s2:#F0F0F5;--s3:#E4E4EC;--tx:#15151C;--mu:#74747F;
      --ln:rgba(0,0,0,.08);--glass:rgba(255,255,255,.85)}}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{height:100%;margin:0}
body{background:var(--bg);color:var(--tx);font:400 15px/1.5 VZ,Vazirmatn,Tahoma,"Segoe UI",system-ui,sans-serif;
     -webkit-user-select:none;user-select:none;overscroll-behavior:none}
#app{display:flex;flex-direction:column;height:100dvh;
     background:radial-gradient(120% 60% at 100% 0%,rgba(124,92,255,.16),transparent 60%),
                radial-gradient(120% 60% at 0% 100%,rgba(79,140,255,.12),transparent 60%)}
header{display:flex;align-items:center;justify-content:space-between;padding:calc(env(safe-area-inset-top) + 12px) 18px 6px}
.brand{display:flex;align-items:center;gap:10px;font-weight:700;font-size:17px}
.dot{width:9px;height:9px;border-radius:50%;background:var(--ok);box-shadow:0 0 0 4px rgba(61,214,140,.18)}
.dot.off{background:var(--bad);box-shadow:0 0 0 4px rgba(255,90,95,.18)}
.lang{border:0;background:var(--s2);color:var(--tx);font:600 13px VZ,sans-serif;border-radius:12px;padding:7px 13px}
main{flex:1;overflow:auto;padding:8px 16px 118px;-webkit-overflow-scrolling:touch}
.view{display:none;animation:in .22s ease}.view.on{display:block}
@keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
h2{margin:6px 4px 10px;font-size:12px;font-weight:700;color:var(--mu);letter-spacing:.3px}
.card{background:var(--s1);border:1px solid var(--ln);border-radius:22px;padding:14px;margin-bottom:12px}
.btn{display:flex;align-items:center;justify-content:center;gap:8px;border:0;color:var(--tx);background:var(--s2);
     border-radius:16px;padding:14px 12px;font:500 15px VZ,sans-serif;transition:transform .08s,background .15s}
.btn:active{transform:scale(.96);background:var(--s3)}
.btn.pri{background:linear-gradient(135deg,var(--a1),var(--a2));color:#fff;font-weight:700}
.btn.bad{background:var(--bad);color:#fff}
.btn svg{width:20px;height:20px}
.row{display:flex;gap:8px;margin-top:8px}.row>*{flex:1}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.chip{border:1px solid var(--ln);background:var(--s2);color:var(--mu);border-radius:12px;padding:9px 14px;font:600 13px VZ,sans-serif}
.chip.on{background:linear-gradient(135deg,var(--a1),var(--a2));color:#fff;border-color:transparent}
.chips{display:flex;gap:6px;overflow-x:auto;padding:2px 0 8px}.chips>*{flex:0 0 auto}
textarea{width:100%;height:120px;border:1px solid var(--ln);background:var(--s1);color:var(--tx);border-radius:20px;
         padding:14px;font:400 18px/1.6 VZ,sans-serif;resize:none;outline:none;-webkit-user-select:text;user-select:text}
textarea:focus{border-color:var(--a1)}
#pad{height:46dvh;border-radius:26px;background:var(--s1);border:1px solid var(--ln);touch-action:none;display:flex;
     align-items:center;justify-content:center;text-align:center;color:var(--mu);padding:24px;font-size:13px}
.hint{color:var(--mu);font-size:12.5px;margin:10px 6px}
.big{font-size:20px;padding:30px 0;font-weight:700}
.play{width:92px;height:92px;border-radius:50%;margin:8px auto;padding:0}.play svg{width:34px;height:34px}
.tile{flex-direction:column;padding:22px 8px;gap:10px;border-radius:20px}.tile svg{width:26px;height:26px}
#scr{width:100%;border-radius:18px;display:block;background:#000;touch-action:none}
#inbox{white-space:pre-wrap;word-break:break-all;background:var(--s2);border-radius:16px;padding:12px;font-size:16px;
       margin-bottom:8px;-webkit-user-select:text;user-select:text}
nav{position:fixed;left:12px;right:12px;bottom:calc(env(safe-area-inset-bottom) + 12px);display:flex;justify-content:space-around;
    background:var(--glass);backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);border:1px solid var(--ln);
    border-radius:28px;padding:8px 6px;box-shadow:0 10px 30px rgba(0,0,0,.25)}
nav button{flex:1;border:0;background:none;color:var(--mu);display:flex;flex-direction:column;align-items:center;gap:3px;
           font:600 11px VZ,sans-serif;padding:6px 0;border-radius:18px}
nav button svg{width:23px;height:23px}
nav button.on{color:var(--tx)}
nav button.on svg{stroke:url(#g)}
nav button.on::after{content:"";width:18px;height:3px;border-radius:3px;background:linear-gradient(90deg,var(--a1),var(--a2))}
.back{border:0;background:var(--s2);color:var(--tx);border-radius:12px;padding:8px 12px;margin:0 2px 8px;font:600 13px VZ,sans-serif}
[dir=rtl] .flip{transform:scaleX(-1)}
svg{fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.sheet{position:fixed;inset:0;background:rgba(0,0,0,.5);display:none;align-items:flex-end;justify-content:center;z-index:9}
.sheet.on{display:flex}.sheet>div{background:var(--s1);width:100%;max-width:520px;border-radius:26px 26px 0 0;padding:22px 18px calc(env(safe-area-inset-bottom) + 18px)}
.ltr{direction:ltr}
.timer{font:700 40px VZ,sans-serif;text-align:center;margin:6px 0 4px;font-variant-numeric:tabular-nums;direction:ltr}
</style></head><body>
<svg width="0" height="0" style="position:absolute"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
 <stop offset="0" stop-color="#7C5CFF"/><stop offset="1" stop-color="#4F8CFF"/></linearGradient></defs></svg>
<div id="app">
<header><div class="brand"><span class="dot" id="dot"></span><span data-t="title"></span></div>
 <button class="lang" id="lang"></button></header>
<main>
 <section class="view" id="v-type">
  <textarea id="t" dir="auto" data-ph="ph_type"></textarea>
  <div class="hint" data-t="mods_hint"></div>
  <div class="chips ltr" id="mods"></div>
  <div class="grid ltr" style="grid-template-columns:repeat(4,1fr)" id="keyrow"></div>
  <div class="row"><button class="btn" onclick="clr()" data-t="clear"></button></div>
 </section>
 <section class="view" id="v-pad">
  <div id="pad" data-t="pad_hint"></div>
  <div class="row"><button class="btn pri" onclick="c('left')" data-t="left"></button>
   <button class="btn" onclick="c('left',2)" data-t="dbl"></button><button class="btn" onclick="c('right')" data-t="right"></button></div>
 </section>
 <section class="view" id="v-pres">
  <div class="timer" id="tm">00:00</div>
  <div class="row"><button class="btn" onclick="tmToggle()" id="tmb" data-t="timer_start"></button>
   <button class="btn" onclick="tmReset()" data-t="timer_reset"></button></div>
  <div class="row" style="margin-top:14px"><button class="btn big" onclick="k('left')"><i data-i="chevl" class="flip"></i><span data-t="prev"></span></button>
   <button class="btn pri big" onclick="k('right')"><span data-t="next"></span><i data-i="chev" class="flip"></i></button></div>
  <div class="grid" style="margin-top:12px">
   <button class="btn" onclick="cb(['f5'])" data-t="start"></button><button class="btn" onclick="cb(['shift','f5'])" data-t="cur"></button>
   <button class="btn" onclick="k('esc')" data-t="end"></button><button class="btn" onclick="cb(['b'])" data-t="black"></button>
   <button class="btn" onclick="cb(['w'])" data-t="white"></button></div>
 </section>
 <section class="view" id="v-media">
  <button class="btn pri play" onclick="m('play')"><i data-i="play"></i></button>
  <div class="row ltr"><button class="btn" onclick="m('prev')"><i data-i="prev"></i></button><button class="btn" onclick="m('next')"><i data-i="next"></i></button></div>
  <h2 data-t="volume" style="margin-top:18px"></h2>
  <div class="row ltr"><button class="btn" onclick="m('vol_down')"><i data-i="vdown"></i></button>
   <button class="btn" onclick="m('mute')"><i data-i="mute"></i></button><button class="btn" onclick="m('vol_up')"><i data-i="vup"></i></button></div>
 </section>
 <section class="view" id="v-more">
  <div class="grid" style="grid-template-columns:1fr 1fr">
   <button class="btn tile" onclick="go('keys')"><i data-i="keys"></i><span data-t="keys"></span></button>
   <button class="btn tile" onclick="go('screen')"><i data-i="screen"></i><span data-t="screen"></span></button>
   <button class="btn tile" onclick="go('clip')"><i data-i="clip"></i><span data-t="clip"></span></button>
   <button class="btn tile" onclick="go('sys')"><i data-i="sys"></i><span data-t="sys"></span></button></div>
 </section>
 <section class="view" id="v-keys"><button class="back" onclick="go('more')">‹ <span data-t="back"></span></button>
  <div class="grid" id="keygrid"></div></section>
 <section class="view" id="v-screen"><button class="back" onclick="go('more')">‹ <span data-t="back"></span></button>
  <img id="scr" alt=""><div class="hint" id="scrmsg"></div><div class="hint" data-t="scr_hint"></div>
  <div class="row"><button class="btn" onclick="c('left',2)" data-t="dbl"></button><button class="btn" onclick="s(-1)"><i data-i="up"></i></button>
   <button class="btn" onclick="s(1)"><i data-i="down"></i></button></div></section>
 <section class="view" id="v-clip"><button class="back" onclick="go('more')">‹ <span data-t="back"></span></button>
  <div class="card" id="inboxcard" style="display:none"><h2 data-t="from_pc"></h2><div id="inbox"></div>
   <div class="row"><button class="btn pri" onclick="cp($('inbox').textContent)" data-t="copy"></button>
    <button class="btn" id="openbtn" style="display:none" onclick="window.open($('inbox').textContent.trim())" data-t="open"></button></div></div>
  <textarea id="ct" dir="auto" data-ph="ph_clip"></textarea>
  <div class="row"><button class="btn pri" onclick="toPC()" data-t="to_pc"></button><button class="btn" onclick="fromPC()" data-t="from_pc_btn"></button></div></section>
 <section class="view" id="v-sys"><button class="back" onclick="go('more')">‹ <span data-t="back"></span></button>
  <div class="hint" id="sysmsg"></div>
  <div class="grid" style="grid-template-columns:1fr 1fr">
   <button class="btn tile" onclick="pw('lock')"><i data-i="lock"></i><span data-t="lock"></span></button>
   <button class="btn tile" onclick="pw('sleep')"><i data-i="moon"></i><span data-t="sleep"></span></button>
   <button class="btn tile bad" onclick="pw('shutdown')"><i data-i="sys"></i><span data-t="shutdown"></span></button>
   <button class="btn tile bad" onclick="pw('restart')"><i data-i="refresh"></i><span data-t="restart"></span></button></div>
  <div class="row"><button class="btn" onclick="pw('cancel')" data-t="cancel_off"></button></div></section>
</main>
<nav id="nav"></nav>
</div>
<div class="sheet" id="sheet"><div><div id="sheetmsg" style="font-weight:700;font-size:17px;margin-bottom:14px"></div>
 <div class="row"><button class="btn" onclick="sheetClose()" data-t="no"></button><button class="btn bad" id="sheetok" data-t="yes"></button></div></div></div>
<script>
const $=id=>document.getElementById(id);
const tok=new URLSearchParams(location.search).get('t');
const L={fa:{title:'ریموت کامپیوتر',n_type:'تایپ',n_pad:'تاچ‌پد',n_pres:'ارائه',n_media:'رسانه',n_more:'بیشتر',
 ph_type:'اینجا تایپ کن…',mods_hint:'ترکیب کلید: یک کلید را بزن، بعد یک حرف تایپ کن',clear:'پاک کردن کادر',
 pad_hint:'یک انگشت: حرکت · لمس: کلیک\nدو انگشت: اسکرول · لمس دو انگشتی: کلیک راست\nدوبار لمس و کشیدن: درگ',
 left:'چپ',right:'راست',dbl:'دابل‌کلیک',timer_start:'شروع زمان‌سنج',timer_stop:'توقف',timer_reset:'صفر',prev:'قبلی',next:'بعدی',
 start:'شروع (F5)',cur:'از اسلاید فعلی',end:'پایان',black:'سیاه',white:'سفید',volume:'صدا',keys:'میانبرها',screen:'صفحه‌ی PC',
 clip:'کلیپ‌بورد',sys:'سیستم',back:'بازگشت',scr_hint:'لمس = کلیک · نگه‌داشتن = کلیک راست · کشیدن = حرکت موس',
 scr_off:'نمایش صفحه در برنامه‌ی کامپیوتر خاموش است.',scr_err:'صفحه‌ی PC در دسترس نیست.',from_pc:'پیام از کامپیوتر',copy:'کپی',
 open:'باز کردن لینک',ph_clip:'متنی که باید روی کلیپ‌بورد کامپیوتر برود…',to_pc:'ارسال به PC',from_pc_btn:'گرفتن از PC',
 lock:'قفل',sleep:'خواب',shutdown:'خاموشی',restart:'ری‌استارت',cancel_off:'لغو خاموشی',sys_off:'دستورهای سیستمی در برنامه‌ی کامپیوتر غیرفعال است.',
 sure:'مطمئنی؟',yes:'بله',no:'انصراف'},
 en:{title:'PC Remote',n_type:'Type',n_pad:'Trackpad',n_pres:'Slides',n_media:'Media',n_more:'More',
 ph_type:'Type here…',mods_hint:'Combos: tap a modifier, then type one letter',clear:'Clear box',
 pad_hint:'One finger: move · Tap: click\nTwo fingers: scroll · Two‑finger tap: right‑click\nDouble‑tap & drag: drag',
 left:'Left',right:'Right',dbl:'Double click',timer_start:'Start timer',timer_stop:'Stop',timer_reset:'Reset',prev:'Previous',next:'Next',
 start:'Start (F5)',cur:'From current',end:'End',black:'Black',white:'White',volume:'Volume',keys:'Shortcuts',screen:'PC screen',
 clip:'Clipboard',sys:'System',back:'Back',scr_hint:'Tap = click · Hold = right‑click · Drag = move mouse',
 scr_off:'Screen sharing is off in the PC app.',scr_err:'PC screen unavailable.',from_pc:'From computer',copy:'Copy',
 open:'Open link',ph_clip:'Text to put on the PC clipboard…',to_pc:'Send to PC',from_pc_btn:'Get from PC',
 lock:'Lock',sleep:'Sleep',shutdown:'Shut down',restart:'Restart',cancel_off:'Cancel shutdown',sys_off:'System commands are disabled in the PC app.',
 sure:'Are you sure?',yes:'Yes',no:'Cancel'}};
const KEYS=[['کپی','Copy',['ctrl','c']],['چسباندن','Paste',['ctrl','v']],['برش','Cut',['ctrl','x']],['واگرد','Undo',['ctrl','z']],
 ['ازنو','Redo',['ctrl','y']],['انتخاب همه','Select all',['ctrl','a']],['ذخیره','Save',['ctrl','s']],['جستجو','Find',['ctrl','f']],
 ['تب جدید','New tab',['ctrl','t']],['بستن تب','Close tab',['ctrl','w']],['تعویض پنجره','Switch window',['alt','tab']],
 ['بستن پنجره','Close window',['alt','f4']],['دسکتاپ','Desktop',['win','d']],['منوی شروع','Start',['win']],
 ['اسکرین‌شات','Screenshot',['win','shift','s']],['تازه‌سازی','Refresh',['f5']],['تمام‌صفحه','Fullscreen',['f11']],['Esc','Esc',['esc']],
 ['Delete','Delete',['delete']],['Space','Space',['space']]];
const NAV=[['type','n_type','keyboard'],['pad','n_pad','pad'],['pres','n_pres','slides'],['media','n_media','media'],['more','n_more','more']];
const IC={keyboard:'<rect x="2.5" y="6" width="19" height="12" rx="3.5"/><path d="M6.5 10h.01M10.5 10h.01M14.5 10h.01M17.5 10h.01M7.5 14h9"/>',
 pad:'<rect x="3" y="4.5" width="18" height="15" rx="3.5"/><path d="M3 15h18M12 15v4.5"/>',slides:'<rect x="3" y="4" width="18" height="12" rx="2.5"/><path d="M12 16v4M8 20h8"/>',
 media:'<path d="M9 17.5V6.5l10-2v11"/><circle cx="6.5" cy="17.5" r="2.5"/><circle cx="16.5" cy="15.5" r="2.5"/>',
 more:'<circle cx="5" cy="12" r="1.3"/><circle cx="12" cy="12" r="1.3"/><circle cx="19" cy="12" r="1.3"/>',
 keys:'<path d="M9 9V6.5a2.5 2.5 0 1 0-2.5 2.5H9zm0 0h6m-6 0v6m6-6V6.5A2.5 2.5 0 1 1 17.5 9H15zm0 0v6m-6 0H6.5A2.5 2.5 0 1 0 9 17.5V15zm6 0h2.5a2.5 2.5 0 1 1-2.5 2.5V15zm-6 0h6"/>',
 screen:'<rect x="3" y="4" width="18" height="12.5" rx="2.5"/><path d="M8 20.5h8M12 16.5v4"/>',
 clip:'<rect x="5.5" y="4.5" width="13" height="16.5" rx="2.5"/><path d="M9 4.5h6v3H9z"/>',
 sys:'<path d="M12 3.5v8"/><path d="M6.6 7.2a7.8 7.8 0 1 0 10.8 0"/>',lock:'<rect x="5" y="10.5" width="14" height="10" rx="2.5"/><path d="M8 10.5V8a4 4 0 0 1 8 0v2.5"/>',
 moon:'<path d="M20 14.5A8 8 0 1 1 9.5 4a6.5 6.5 0 0 0 10.5 10.5z"/>',refresh:'<path d="M20 12a8 8 0 1 1-2.6-5.9M20 4v4.5h-4.5"/>',
 play:'<path d="M8 5.5v13l11-6.5z" fill="currentColor"/>',prev:'<path d="M18 6v12l-8.5-6z" fill="currentColor"/><path d="M6.5 6v12"/>',
 next:'<path d="M6 6v12l8.5-6z" fill="currentColor"/><path d="M17.5 6v12"/>',vup:'<path d="M4 9.5h3.5L12 5.5v13L7.5 14.5H4z"/><path d="M15.5 9a4.5 4.5 0 0 1 0 6M18 6.5a8 8 0 0 1 0 11"/>',
 vdown:'<path d="M4 9.5h3.5L12 5.5v13L7.5 14.5H4z"/><path d="M15.5 9a4.5 4.5 0 0 1 0 6"/>',mute:'<path d="M4 9.5h3.5L12 5.5v13L7.5 14.5H4z"/><path d="M16 9.5l5 5M21 9.5l-5 5"/>',
 chev:'<path d="M9 6l6 6-6 6"/>',chevl:'<path d="M15 6l-6 6 6 6"/>',up:'<path d="M12 19V6M6.5 11.5L12 6l5.5 5.5"/>',down:'<path d="M12 5v13M6.5 12.5L12 18l5.5-5.5"/>'};
let lang=localStorage.getItem('lang')||'__LANG__',cur='type',scrOn=false,scrBusy=false;
const svg=n=>'<svg viewBox="0 0 24 24">'+(IC[n]||'')+'</svg>';
function applyLang(){document.documentElement.lang=lang;document.documentElement.dir=lang==='fa'?'rtl':'ltr';
 document.querySelectorAll('[data-t]').forEach(e=>e.textContent=L[lang][e.dataset.t]||e.dataset.t);
 document.querySelectorAll('[data-ph]').forEach(e=>e.placeholder=L[lang][e.dataset.ph]);
 $('pad').style.whiteSpace='pre-line';$('lang').textContent=lang==='fa'?'EN':'فا';
 $('nav').querySelectorAll('span').forEach(s=>s.textContent=L[lang][s.dataset.k]);
 document.querySelectorAll('#keygrid .btn').forEach((b,i)=>b.textContent=KEYS[i][lang==='fa'?0:1]);
 tmRender();if(!stateScr)$('scrmsg').textContent=L[lang].scr_off;if(!stateSys)$('sysmsg').textContent=L[lang].sys_off;}
function icons(){document.querySelectorAll('i[data-i]').forEach(e=>e.innerHTML=svg(e.dataset.i));}
let stateScr=true,stateSys=true;
NAV.forEach(([id,key,ic])=>{const b=document.createElement('button');b.id='nb-'+id;
 b.innerHTML=svg(ic)+'<span data-k="'+key+'"></span>';b.onclick=()=>go(id);$('nav').appendChild(b);});
KEYS.forEach(([fa,en,ks])=>{const b=document.createElement('button');b.className='btn';b.onclick=()=>cb(ks);$('keygrid').appendChild(b);});
function go(id){cur=id;document.querySelectorAll('.view').forEach(v=>v.classList.toggle('on',v.id==='v-'+id));
 const main=['type','pad','pres','media'].includes(id)?id:'more';
 NAV.forEach(([n])=>$('nb-'+n).classList.toggle('on',n===main));scrOn=(id==='screen');if(scrOn)loopScr();vib(6);}
function vib(n){if(navigator.vibrate)navigator.vibrate(n);}
document.addEventListener('pointerdown',e=>{if(e.target.closest('.btn,.chip'))vib(6);});
let chain=Promise.resolve();
function send(p){chain=chain.then(()=>fetch('/e?t='+tok,{method:'POST',body:JSON.stringify(p)})
 .then(r=>{$('dot').className='dot'+(r.ok?'':' off')}).catch(()=>{$('dot').className='dot off'}));}
function k(x){send({type:'key',key:x});}function c(b,n){send({type:'click',b:b,n:n||1});}
function s(d){send({type:'scroll',d:d});}function m(x){send({type:'media',k:x});}function cb(keys){send({type:'combo',keys:keys});}
function cp(txt){const a=document.createElement('textarea');a.value=txt;document.body.appendChild(a);a.select();
 try{document.execCommand('copy')}catch(e){}document.body.removeChild(a);}
function toPC(){send({type:'clip',text:$('ct').value});}
async function fromPC(){try{const r=await fetch('/pcclip?t='+tok);const d=await r.json();$('ct').value=d.text||'';}catch(e){}}
function sheet(msg,fn){$('sheetmsg').textContent=msg;$('sheet').classList.add('on');$('sheetok').onclick=()=>{sheetClose();fn();};}
function sheetClose(){$('sheet').classList.remove('on');}
function pw(x){if(x==='cancel')return send({type:'power',cmd:x});sheet(L[lang].sure+'  ('+L[lang][x==='lock'?'lock':x==='sleep'?'sleep':x==='shutdown'?'shutdown':'restart']+')',()=>send({type:'power',cmd:x}));}
// ---- تایپ
const t=$('t');let prev='';const mods=new Set();
['ctrl','alt','shift','win'].forEach(n=>{const b=document.createElement('button');b.className='chip';b.textContent=n==='win'?'Win':n[0].toUpperCase()+n.slice(1);
 b.onclick=()=>{mods.has(n)?mods.delete(n):mods.add(n);b.classList.toggle('on',mods.has(n));t.focus();};$('mods').appendChild(b);});
function clearMods(){mods.clear();document.querySelectorAll('#mods .chip').forEach(b=>b.classList.remove('on'));}
t.addEventListener('input',()=>{const cur=t.value;let i=0;const mm=Math.min(prev.length,cur.length);
 while(i<mm&&prev[i]===cur[i])i++;const back=prev.length-i,add=cur.slice(i);
 if(mods.size&&add.length===1&&!back){send({type:'combo',keys:[...mods,add.toLowerCase()]});clearMods();t.value=prev;return;}
 if(back||add)send({type:'text',back:back,add:add});prev=cur;});
function clr(){t.value='';prev='';t.focus();}
[['Esc','esc'],['Tab','tab'],['⏎','enter'],['⌫','backspace'],['←','left'],['↑','up'],['↓','down'],['→','right'],
 ['Home','home'],['End','end'],['Del','delete'],['Space','space']].forEach(([l,kk])=>{const b=document.createElement('button');
 b.className='btn';b.style.padding='12px 4px';b.textContent=l;b.onclick=()=>k(kk);$('keyrow').appendChild(b);});
// ---- تاچ‌پد چندلمسی
const pad=$('pad');const tp={n:0,last:null,moved:0,t0:0,lastTap:0,drag:false,sa:0,ax:0,ay:0};
const mid=ts=>[(ts[0].clientX+ts[1].clientX)/2,(ts[0].clientY+ts[1].clientY)/2];
pad.addEventListener('touchstart',e=>{e.preventDefault();const n=e.touches.length;tp.n=Math.max(tp.n,n);
 if(n===1){tp.last=[e.touches[0].clientX,e.touches[0].clientY];tp.moved=0;tp.t0=Date.now();
  if(Date.now()-tp.lastTap<280){tp.drag=true;send({type:'mouse',act:'down'});}}
 else if(n===2){tp.last=mid(e.touches);tp.moved=0;tp.t0=Date.now();tp.sa=0;}},{passive:false});
pad.addEventListener('touchmove',e=>{e.preventDefault();
 if(e.touches.length===1&&tp.n<2){const p=e.touches[0];const dx=p.clientX-tp.last[0],dy=p.clientY-tp.last[1];
  tp.last=[p.clientX,p.clientY];tp.moved+=Math.abs(dx)+Math.abs(dy);const g=1.6+Math.min(2.2,Math.hypot(dx,dy)/14);tp.ax+=dx*g;tp.ay+=dy*g;}
 else if(e.touches.length===2){const mm=mid(e.touches);const dy=mm[1]-tp.last[1];tp.last=mm;tp.moved+=Math.abs(dy);tp.sa+=dy;
  while(Math.abs(tp.sa)>=16){send({type:'scroll',d:tp.sa>0?-1:1});tp.sa-=tp.sa>0?16:-16;}}},{passive:false});
pad.addEventListener('touchend',e=>{e.preventDefault();const dt=Date.now()-tp.t0;
 if(e.touches.length===0){
  if(tp.drag){send({type:'mouse',act:'up'});tp.drag=false;tp.lastTap=0;}
  else if(tp.n===1&&tp.moved<8&&dt<250){c('left');tp.lastTap=Date.now();}
  else if(tp.n===2&&tp.moved<10&&dt<300){c('right');}
  tp.n=0;}},{passive:false});
setInterval(()=>{if(tp.ax||tp.ay){send({type:'move',dx:Math.round(tp.ax),dy:Math.round(tp.ay)});tp.ax=0;tp.ay=0;}},30);
// ---- زمان‌سنج ارائه
let tmV=0,tmI=null;
function tmRender(){const a=Math.floor(tmV/60),b=tmV%60;$('tm').textContent=String(a).padStart(2,'0')+':'+String(b).padStart(2,'0');
 $('tmb').textContent=L[lang][tmI?'timer_stop':'timer_start'];}
function tmToggle(){if(tmI){clearInterval(tmI);tmI=null;}else{tmI=setInterval(()=>{tmV++;tmRender();},1000);}tmRender();}
function tmReset(){tmV=0;tmRender();}
// ---- صفحه‌ی PC
function loopScr(){if(!scrOn||scrBusy)return;scrBusy=true;const im=$('scr');
 im.onload=()=>{scrBusy=false;$('scrmsg').textContent='';setTimeout(loopScr,200)};
 im.onerror=()=>{scrBusy=false;$('scrmsg').textContent=L[lang].scr_err;setTimeout(loopScr,2000)};
 im.src='/screen?t='+tok+'&r='+Date.now();}
const im=$('scr');let st=null,lastMv=0;
function fr(p){const r=im.getBoundingClientRect();return [Math.min(1,Math.max(0,(p.clientX-r.left)/r.width)),Math.min(1,Math.max(0,(p.clientY-r.top)/r.height))];}
im.addEventListener('touchstart',e=>{e.preventDefault();const f=fr(e.touches[0]);st={t:Date.now(),f:f,mv:0};send({type:'abs',fx:f[0],fy:f[1],act:'move'});},{passive:false});
im.addEventListener('touchmove',e=>{e.preventDefault();const f=fr(e.touches[0]);st.mv+=Math.abs(f[0]-st.f[0])+Math.abs(f[1]-st.f[1]);st.f=f;
 const n=Date.now();if(n-lastMv>50){lastMv=n;send({type:'abs',fx:f[0],fy:f[1],act:'move'});}},{passive:false});
im.addEventListener('touchend',()=>{if(!st)return;if(st.mv<0.02)send({type:'abs',fx:st.f[0],fy:st.f[1],act:(Date.now()-st.t>500?'rclick':'click')});st=null;});
// ---- پیام کامپیوتر ← گوشی
let lastId=0;
async function poll(){try{const r=await fetch('/inbox?t='+tok);const d=await r.json();
 if(d.id&&d.id!==lastId){lastId=d.id;$('inbox').textContent=d.text;$('inboxcard').style.display='block';
  $('openbtn').style.display=new RegExp('^https?://','i').test(d.text.trim())?'flex':'none';vib(120);}}catch(e){}}
setInterval(poll,2000);poll();
$('lang').onclick=()=>{lang=lang==='fa'?'en':'fa';localStorage.setItem('lang',lang);applyLang();};
icons();
fetch('/state?t='+tok).then(r=>r.json()).then(d=>{stateScr=d.screen;stateSys=d.system;applyLang();}).catch(()=>{});
applyLang();go('type');
</script></body></html>
"""


class PhoneKeyboardServer:
    def __init__(self, on_event):
        self.on_event = on_event
        self.token = secrets.token_urlsafe(6)
        self.srv = None
        self.seen = set()
        self.port = 8765
        self.allow_screen = False       # نمایش صفحه‌ی PC روی گوشی (پیش‌فرض خاموش)
        self.allow_system = False       # قفل/خواب/خاموشی (پیش‌فرض خاموش)
        self.frame = None               # (jpeg, عرض واقعی، ارتفاع واقعی)
        self.last_frame_req = 0.0
        self.inbox_text, self.inbox_id = "", 0
        self.get_clip = lambda: ""
        self.set_clip = lambda t: None

    @property
    def running(self):
        return self.srv is not None

    def url(self):
        return "http://%s:%d/?t=%s" % (local_ip(), self.port, self.token)

    def send_to_phone(self, text):
        self.inbox_text = text
        self.inbox_id += 1

    def start(self, port):
        from pynput.keyboard import Controller as KB, Key
        from pynput.mouse import Controller as MS, Button
        kb, ms, lock = KB(), MS(), threading.Lock()
        special = {"enter": Key.enter, "backspace": Key.backspace, "tab": Key.tab, "esc": Key.esc,
                   "left": Key.left, "right": Key.right, "up": Key.up, "down": Key.down, "space": Key.space,
                   "delete": Key.delete, "home": Key.home, "end": Key.end, "ctrl": Key.ctrl, "alt": Key.alt,
                   "shift": Key.shift, "win": Key.cmd}
        for i in range(1, 13):
            special["f%d" % i] = getattr(Key, "f%d" % i)
        media = {"play": "media_play_pause", "next": "media_next", "prev": "media_previous",
                 "vol_up": "media_volume_up", "vol_down": "media_volume_down", "mute": "media_volume_mute"}
        btns = {"left": Button.left, "right": Button.right}
        me = self

        def combo(keys):
            ks = []
            for k in keys[:6]:
                if k in special:
                    ks.append(special[k])
                elif isinstance(k, str) and len(k) == 1:
                    ks.append(k)
            if not ks:
                return
            for m in ks[:-1]:
                kb.press(m)
            try:
                kb.tap(ks[-1])
            finally:
                for m in reversed(ks[:-1]):
                    kb.release(m)

        def power(cmd):
            if not me.allow_system:
                return me.on_event("warn", tr("دستور سیستمی «%s» رد شد (در برنامه فعال نیست)") % cmd)
            if sys.platform != "win32":
                return me.on_event("warn", tr("دستورهای سیستمی فقط در ویندوز پشتیبانی می‌شوند"))
            import ctypes
            if cmd == "lock":
                ctypes.windll.user32.LockWorkStation()
            elif cmd == "sleep":
                subprocess.Popen(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"], **NOWIN)
            elif cmd == "shutdown":
                subprocess.Popen(["shutdown", "/s", "/t", "30"], **NOWIN)
            elif cmd == "restart":
                subprocess.Popen(["shutdown", "/r", "/t", "30"], **NOWIN)
            elif cmd == "cancel":
                subprocess.Popen(["shutdown", "/a"], **NOWIN)
            me.on_event("info", tr("دستور سیستمی اجرا شد: %s") % cmd)

        class H(BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _auth(self):
                t = parse_qs(urlparse(self.path).query).get("t", [""])[0]
                return hmac.compare_digest(t, me.token)

            def _reply(self, code, body=b"ok", ctype="text/plain; charset=utf-8", cache=False):
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(body)))
                self.send_header("Cache-Control", "max-age=86400" if cache else "no-store")
                self.end_headers()
                self.wfile.write(body)

            def _json(self, obj):
                self._reply(200, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

            def do_GET(self):
                if not self._auth():
                    me.on_event("warn", tr("درخواست با توکن نادرست از %s رد شد") % self.client_address[0])
                    return self._reply(403, b"forbidden")
                path = urlparse(self.path).path
                if path == "/":
                    if self.client_address[0] not in me.seen:
                        me.seen.add(self.client_address[0])
                        me.on_event("ok", tr("گوشی وصل شد (%s)") % self.client_address[0])
                    html_ = PAGE.replace("__T__", me.token).replace("__LANG__", LANG).replace(
                        "__DIR__", "rtl" if LANG == "fa" else "ltr")
                    return self._reply(200, html_.encode("utf-8"), "text/html; charset=utf-8")
                if path.startswith("/f/"):
                    name = os.path.basename(path[3:])
                    for d in (APP_DIR / "fonts", APP_DIR):
                        f = d / name
                        if name.lower().startswith("vazir") and name.lower().endswith(".ttf") and f.is_file():
                            return self._reply(200, f.read_bytes(), "font/ttf", cache=True)
                    return self._reply(404, b"no font")
                if path == "/state":
                    return self._json({"screen": me.allow_screen, "system": me.allow_system})
                if path == "/inbox":
                    return self._json({"id": me.inbox_id, "text": me.inbox_text})
                if path == "/pcclip":
                    return self._json({"text": me.get_clip() or ""})
                if path == "/screen":
                    if not me.allow_screen:
                        return self._reply(403, b"screen sharing disabled")
                    me.last_frame_req = time.time()
                    if not me.frame:
                        return self._reply(503, b"no frame yet")
                    return self._reply(200, me.frame[0], "image/jpeg")
                self._reply(404, b"not found")

            def do_POST(self):
                if not self._auth():
                    return self._reply(403, b"forbidden")
                try:
                    n = int(self.headers.get("Content-Length", 0))
                    d = json.loads(self.rfile.read(n).decode("utf-8"))
                    k = d.get("type")
                    if k == "power":
                        power(d.get("cmd"))
                    elif k == "clip":
                        me.set_clip(str(d.get("text", ""))[:200000])
                        me.on_event("info", tr("متن به کلیپ‌بورد PC رفت"))
                    else:
                        with lock:
                            if k == "text":
                                for _ in range(int(d.get("back", 0))):
                                    kb.tap(Key.backspace)
                                if d.get("add"):
                                    kb.type(d["add"])
                                    me.on_event("info", tr("تایپ شد: %d نویسه") % len(d["add"]))
                            elif k == "key" and d.get("key") in special:
                                kb.tap(special[d["key"]])
                            elif k == "combo":
                                combo(list(d.get("keys", [])))
                            elif k == "media" and d.get("k") in media:
                                kb.tap(getattr(Key, media[d["k"]]))
                            elif k == "move":
                                ms.move(int(d.get("dx", 0)), int(d.get("dy", 0)))
                            elif k == "click" and d.get("b") in btns:
                                ms.click(btns[d["b"]], max(1, min(2, int(d.get("n", 1)))))
                            elif k == "scroll":
                                ms.scroll(0, -int(d.get("d", 0)))
                            elif k == "mouse":
                                (ms.press if d.get("act") == "down" else ms.release)(Button.left)
                            elif k == "abs" and me.allow_screen and me.frame:
                                W, H_ = me.frame[1], me.frame[2]
                                x = int(max(0.0, min(1.0, float(d["fx"]))) * (W - 1))
                                y = int(max(0.0, min(1.0, float(d["fy"]))) * (H_ - 1))
                                ms.position = (x, y)
                                act = d.get("act", "move")
                                if act == "click":
                                    ms.click(Button.left)
                                elif act == "rclick":
                                    ms.click(Button.right)
                    self._reply(200)
                except Exception as e:
                    me.on_event("warn", tr("خطا: %s") % e)
                    self._reply(400, b"bad request")

        self.port = port
        self.srv = ThreadingHTTPServer(("0.0.0.0", port), H)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()

    def stop(self):
        if self.srv:
            try:
                self.srv.shutdown()
                self.srv.server_close()
            except Exception:
                pass
        self.srv = None


def local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"
    finally:
        s.close()


# =============================
# تولید QR (بدون کتابخانه‌ی خارجی؛ بایت‌مود، سطح تصحیح M، نسخه‌ی ۱ تا ۱۰)
# =============================
_QR_ECC = [0, 10, 16, 26, 18, 24, 16, 18, 22, 22, 26]
_QR_BLK = [0, 1, 1, 1, 2, 2, 4, 4, 4, 5, 5]


def _rs_mul(x, y):
    z = 0
    for i in range(7, -1, -1):
        z = (z << 1) ^ ((z >> 7) * 0x11D)
        z ^= ((y >> i) & 1) * x
    return z


def _rs_div(deg):
    res = [0] * (deg - 1) + [1]
    root = 1
    for _ in range(deg):
        for j in range(deg):
            res[j] = _rs_mul(res[j], root)
            if j + 1 < deg:
                res[j] ^= res[j + 1]
        root = _rs_mul(root, 2)
    return res


def _rs_rem(data, div):
    res = [0] * len(div)
    for b in data:
        f = b ^ res.pop(0)
        res.append(0)
        for i, c in enumerate(div):
            res[i] ^= _rs_mul(c, f)
    return res


def _qr_raw(ver):
    r = (16 * ver + 128) * ver + 64
    if ver >= 2:
        na = ver // 7 + 2
        r -= (25 * na - 10) * na - 55
        if ver >= 7:
            r -= 36
    return r


def _qr_align(ver):
    if ver == 1:
        return []
    na = ver // 7 + 2
    step = (ver * 4 + na * 2 + 1) // (na * 2 - 2) * 2
    size = ver * 4 + 17
    return ([size - 7 - i * step for i in range(na - 1)] + [6])[::-1]


def qr_matrix(text, force_mask=None):
    data = text.encode("utf-8")
    for ver in range(1, 11):
        ndata = _qr_raw(ver) // 8 - _QR_ECC[ver] * _QR_BLK[ver]
        ccb = 8 if ver <= 9 else 16
        if 4 + ccb + len(data) * 8 <= ndata * 8:
            break
    else:
        raise ValueError(tr("متن برای QR خیلی بلند است"))
    bits = []

    def put(v, n):
        bits.extend((v >> i) & 1 for i in range(n - 1, -1, -1))
    put(4, 4)
    put(len(data), ccb)
    for b in data:
        put(b, 8)
    cap = ndata * 8
    put(0, min(4, cap - len(bits)))
    while len(bits) % 8:
        bits.append(0)
    pad = 0xEC
    while len(bits) < cap:
        put(pad, 8)
        pad ^= 0xEC ^ 0x11
    cw = [sum(bits[i + j] << (7 - j) for j in range(8)) for i in range(0, len(bits), 8)]
    nb, el, raw = _QR_BLK[ver], _QR_ECC[ver], _qr_raw(ver) // 8
    nshort, shortlen = nb - raw % nb, raw // nb
    div, blocks, k = _rs_div(el), [], 0
    for i in range(nb):
        dl = shortlen - el + (0 if i < nshort else 1)
        d = cw[k:k + dl]
        k += dl
        e = _rs_rem(d, div)
        if i < nshort:
            d = d + [0]
        blocks.append(d + e)
    allcw = []
    for i in range(len(blocks[0])):
        for j, b in enumerate(blocks):
            if i != shortlen - el or j >= nshort:
                allcw.append(b[i])

    size = ver * 4 + 17
    mod = [[False] * size for _ in range(size)]
    fn = [[False] * size for _ in range(size)]

    def setf(x, y, v):
        mod[y][x] = v
        fn[y][x] = True
    for i in range(size):
        setf(6, i, i % 2 == 0)
        setf(i, 6, i % 2 == 0)

    def finder(cx, cy):
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                x, y = cx + dx, cy + dy
                if 0 <= x < size and 0 <= y < size:
                    setf(x, y, max(abs(dx), abs(dy)) not in (2, 4))
    finder(3, 3)
    finder(size - 4, 3)
    finder(3, size - 4)
    ap = _qr_align(ver)
    for i, cy in enumerate(ap):
        for j, cx in enumerate(ap):
            if (i == 0 and j == 0) or (i == 0 and j == len(ap) - 1) or (i == len(ap) - 1 and j == 0):
                continue
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    setf(cx + dx, cy + dy, max(abs(dx), abs(dy)) != 1)

    def fmt(mask):
        d = mask          # سطح M = ۰۰  →  (0 << 3) | mask
        r = d
        for _ in range(10):
            r = (r << 1) ^ ((r >> 9) * 0x537)
        bs = ((d << 10) | r) ^ 0x5412
        g = lambda i: (bs >> i) & 1 == 1
        for i in range(6):
            setf(8, i, g(i))
        setf(8, 7, g(6))
        setf(8, 8, g(7))
        setf(7, 8, g(8))
        for i in range(9, 15):
            setf(14 - i, 8, g(i))
        for i in range(8):
            setf(size - 1 - i, 8, g(i))
        for i in range(8, 15):
            setf(8, size - 15 + i, g(i))
        setf(8, size - 8, True)
    fmt(0)
    if ver >= 7:
        r = ver
        for _ in range(12):
            r = (r << 1) ^ ((r >> 11) * 0x1F25)
        bs = (ver << 12) | r
        for i in range(18):
            bit = (bs >> i) & 1 == 1
            a, b = size - 11 + i % 3, i // 3
            setf(a, b, bit)
            setf(b, a, bit)
    i = 0
    for right in range(size - 1, 0, -2):
        if right <= 6:
            right -= 1
        for vert in range(size):
            for j in range(2):
                x = right - j
                y = size - 1 - vert if ((right + 1) & 2) == 0 else vert
                if not fn[y][x] and i < len(allcw) * 8:
                    mod[y][x] = (allcw[i >> 3] >> (7 - (i & 7))) & 1 == 1
                    i += 1

    def mask_fn(m, x, y):
        return [(x + y) % 2 == 0, y % 2 == 0, x % 3 == 0, (x + y) % 3 == 0, (x // 3 + y // 2) % 2 == 0,
                x * y % 2 + x * y % 3 == 0, (x * y % 2 + x * y % 3) % 2 == 0,
                ((x + y) % 2 + x * y % 3) % 2 == 0][m]

    def apply(m):
        for y in range(size):
            for x in range(size):
                if not fn[y][x] and mask_fn(m, x, y):
                    mod[y][x] = not mod[y][x]

    def penalty():
        pen = 0
        for lines in (mod, [list(c) for c in zip(*mod)]):
            for line in lines:
                run = 1
                for t in range(1, size):
                    if line[t] == line[t - 1]:
                        run += 1
                    else:
                        pen += run - 2 if run >= 5 else 0
                        run = 1
                pen += run - 2 if run >= 5 else 0
        for y in range(size - 1):
            for x in range(size - 1):
                if mod[y][x] == mod[y][x + 1] == mod[y + 1][x] == mod[y + 1][x + 1]:
                    pen += 3
        dark = sum(sum(r) for r in mod)
        tot = size * size
        return pen + ((abs(dark * 20 - tot * 10) + tot - 1) // tot - 1) * 10
    best, bp = 0, None
    for m in (range(8) if force_mask is None else [force_mask]):
        apply(m)
        fmt(m)
        pn = penalty()
        if bp is None or pn < bp:
            best, bp = m, pn
        apply(m)
    apply(best)
    fmt(best)
    return mod


def qr_pixmap(text, size=260, force_mask=None):
    m = qr_matrix(text, force_mask)
    n, border = len(m), 4
    px = max(2, size // (n + 2 * border))
    dim = (n + 2 * border) * px
    img = QImage(dim, dim, QImage.Format.Format_RGB32)
    img.fill(QColor("white"))
    p = QPainter(img)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("black"))
    for y in range(n):
        for x in range(n):
            if m[y][x]:
                p.drawRect((x + border) * px, (y + border) * px, px, px)
    p.end()
    return QPixmap.fromImage(img)


# =============================
# نمایشگر گوشی
# =============================
ANDROID_KEYS = {
    Qt.Key.Key_Backspace: 67, Qt.Key.Key_Return: 66, Qt.Key.Key_Enter: 66, Qt.Key.Key_Escape: 4,
    Qt.Key.Key_Tab: 61, Qt.Key.Key_Up: 19, Qt.Key.Key_Down: 20, Qt.Key.Key_Left: 21, Qt.Key.Key_Right: 22,
    Qt.Key.Key_Delete: 112, Qt.Key.Key_Home: 122, Qt.Key.Key_End: 123, Qt.Key.Key_PageUp: 92,
    Qt.Key.Key_PageDown: 93,
}


class PhoneView(QWidget):
    """نمایشگر گوشی: قاب باریک، حالت خالی تمیز، مختصات/FPS روی تصویر."""
    message = pyqtSignal(str)
    hover = pyqtSignal(str)
    fps = pyqtSignal(float)

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.adb = None
        self.pix = None
        self.last_png = None
        self.qimg = None
        self._ft = []
        self.hud = ""
        self.fps_val = 0.0
        self.msg = ""
        self.size_phone = (1080, 2400)
        self.press = None
        self.cur = None
        self.ripples = []
        self.setMinimumSize(320, 560)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.btn_connect = QPushButton(tr("اتصال به گوشی"), self)
        self.btn_connect.setProperty("variant", "primary")
        self.btn_connect.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_connect.setFixedSize(170, 42)
        self.btn_connect.clicked.connect(lambda: win.tabs.setCurrentWidget(win.tab_connect_w))
        self.hover.connect(self._set_hud)
        self.fps.connect(self._set_fps)

    # ---- داده ----
    def _set_hud(self, t):
        self.hud = t
        self.update()

    def _set_fps(self, f):
        self.fps_val = f

    def leaveEvent(self, e):
        self.hud = ""
        self.update()

    def set_adb(self, adb):
        self.adb = adb
        self.btn_connect.setVisible(adb is None)
        if adb is None:
            self.pix = self.qimg = None
            self.msg = ""
        else:
            self.msg = tr("در حال گرفتن تصویر از گوشی…")
        self.update()

    def set_message(self, m):
        self.pix = None
        self.msg = m
        self.update()
        self.message.emit(m)

    def set_png(self, data):
        img = QImage()
        if not img.loadFromData(data):
            return self.set_message(tr("تصویر دریافتی قابل نمایش نیست."))
        self.last_png, self.qimg = data, img
        self.pix = QPixmap.fromImage(img)
        self.size_phone = (img.width(), img.height())
        small = img.scaled(12, 12)
        bright = max(QColor(small.pixel(x, y)).value() for x in range(12) for y in range(12))
        self.message.emit(tr("تصویر گوشی کاملاً سیاه است: صفحه را روشن و قفل را باز کنید؛ اگر باز هم سیاه بود، "
                             "برنامه‌ی باز روی گوشی جلوی ضبط صفحه را گرفته.") if bright < 8 else "")
        now = time.time()
        self._ft = [t for t in self._ft if now - t < 2.0] + [now]
        if len(self._ft) > 1:
            self.fps.emit((len(self._ft) - 1) / max(0.001, self._ft[-1] - self._ft[0]))
        self.update()

    # ---- هندسه ----
    def screen_rect(self):
        pw, ph = self.size_phone
        av = QRectF(self.rect()).adjusted(16, 16, -16, -16)
        k = min(av.width() / pw, av.height() / ph)
        w, h = pw * k, ph * k
        return QRectF(av.center().x() - w / 2, av.center().y() - h / 2, w, h)

    def to_phone(self, pos):
        r = self.screen_rect()
        pw, ph = self.size_phone
        x = (pos.x() - r.x()) / r.width() * pw
        y = (pos.y() - r.y()) / r.height() * ph
        return int(max(0, min(pw - 1, x))), int(max(0, min(ph - 1, y)))

    def inside(self, pos):
        return self.screen_rect().contains(pos)

    def resizeEvent(self, e):
        self.btn_connect.move(int(self.width() / 2 - 85), int(self.height() / 2 + 64))

    # ---- رسم ----
    def _pill(self, p, text, cx, y, alpha=165):
        f = QFont(FONT_FAMILY, 8)
        f.setWeight(QFont.Weight.DemiBold)
        p.setFont(f)
        w = p.fontMetrics().horizontalAdvance(text) + 22
        r = QRectF(cx - w / 2, y, w, 24)
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QColor(8, 8, 12, alpha))
        p.drawRoundedRect(r, 12, 12)
        p.setPen(QColor("#F2F2F7"))
        p.drawText(r, int(Qt.AlignmentFlag.AlignCenter), text)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        r = self.screen_rect()
        live = self.pix is not None
        # درخشش بسیار ملایم دور قاب
        if live:
            for i in range(7, 0, -1):
                p.setPen(QPen(qc(CUR["a1"], 5 + (7 - i) * 1.2), 1.6))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawRoundedRect(r.adjusted(-6 - i * 2.2, -6 - i * 2.2, 6 + i * 2.2, 6 + i * 2.2), 34 + i * 2, 34 + i * 2)
        p.setPen(QPen(qc(CUR["border2"]), 1.2))
        p.setBrush(qc(CUR["bezel"]))
        p.drawRoundedRect(r.adjusted(-6, -6, 6, 6), 33, 33)
        path = QPainterPath()
        path.addRoundedRect(r, 27, 27)
        p.save()
        p.setClipPath(path)
        if live:
            p.drawPixmap(r, self.pix, QRectF(self.pix.rect()))
        else:
            g = QLinearGradient(r.topLeft(), r.bottomRight())
            g.setColorAt(0, qc(CUR["a1"], 34))
            g.setColorAt(1, qc(CUR["a2"], 18))
            p.fillRect(r, qc("#07070B" if CUR["dark"] else "#101018"))
            p.fillRect(r, g)
        p.restore()
        if not live:
            cx, cy = r.center().x(), r.center().y()
            ic = make_icon("phone", CUR["a1h"], 54).pixmap(54, 54)
            p.drawPixmap(int(cx - 27), int(cy - 96), ic)
            p.setPen(QColor("#F2F2F7"))
            f = QFont(FONT_FAMILY, 12)
            f.setWeight(QFont.Weight.Bold)
            p.setFont(f)
            if self.adb is None:
                p.drawText(QRectF(r.left(), cy - 30, r.width(), 28), int(Qt.AlignmentFlag.AlignCenter), tr("گوشی متصل نیست"))
                p.setPen(QColor("#8E8E9A"))
                p.setFont(QFont(FONT_FAMILY, 9))
                p.drawText(QRectF(r.left() + 20, cy, r.width() - 40, 48),
                           int(Qt.AlignmentFlag.AlignHCenter | Qt.TextFlag.TextWordWrap),
                           tr("برای دیدن و کنترل گوشی، اول وصلش کن."))
            else:
                p.setFont(QFont(FONT_FAMILY, 10))
                p.drawText(r.adjusted(16, 16, -16, -16), int(Qt.AlignmentFlag.AlignCenter | Qt.TextFlag.TextWordWrap),
                           self.msg)
        if live and self.fps_val:
            self._pill(p, "%d FPS" % round(self.fps_val), r.left() + 46, r.top() + 12, 120)
        if live and self.hud:
            self._pill(p, self.hud, r.center().x(), r.bottom() - 36)
        if self.press and self.cur and hypot(self.cur.x() - self.press[0].x(), self.cur.y() - self.press[0].y()) > 8:
            pen = QPen(qc(CUR["a1h"], 230), 4)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(self.press[0], self.cur)
        now = time.time()
        for pos, t0 in self.ripples:
            k = min(1.0, (now - t0) / 0.45)
            rad = 12 + 34 * (1 - (1 - k) ** 3)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.setPen(QPen(qc(CUR["a2"], 230 * (1 - k)), 3))
            p.drawEllipse(pos, rad, rad)
            p.setBrush(qc(CUR["a1"], 120 * (1 - k)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(pos, rad * 0.4, rad * 0.4)

    def _tick(self):
        now = time.time()
        self.ripples = [x for x in self.ripples if now - x[1] < 0.45]
        if not self.ripples:
            self.timer.stop()
        self.update()

    def _ripple(self, pos):
        self.ripples.append((QPointF(pos), time.time()))
        if not self.timer.isActive():
            self.timer.start(16)

    # ---- موس ----
    def mousePressEvent(self, e):
        self.setFocus()
        if not self.adb:
            return
        if e.button() == Qt.MouseButton.RightButton:
            self.win.act("key", 4)
            return self._ripple(e.position())
        if e.button() == Qt.MouseButton.MiddleButton:
            self.win.act("key", 3)
            return self._ripple(e.position())
        if e.button() == Qt.MouseButton.LeftButton and self.inside(e.position()):
            self.press = (e.position(), time.time())
            self.cur = e.position()

    def mouseMoveEvent(self, e):
        if self.press:
            self.cur = e.position()
            self.update()
        elif self.qimg is not None and self.inside(e.position()):
            x, y = self.to_phone(e.position())
            x, y = min(x, self.qimg.width() - 1), min(y, self.qimg.height() - 1)
            self.hover.emit("x %d   y %d   %s" % (x, y, QColor(self.qimg.pixel(x, y)).name().upper()))
        elif self.hud:
            self.hover.emit("")

    def mouseReleaseEvent(self, e):
        if not (self.press and self.adb and e.button() == Qt.MouseButton.LeftButton):
            return
        p0, t0 = self.press
        self.press = None
        dt = time.time() - t0
        x0, y0 = self.to_phone(p0)
        x1, y1 = self.to_phone(e.position())
        if hypot(e.position().x() - p0.x(), e.position().y() - p0.y()) < 8:
            if dt > 0.6:
                self.win.act("swipe", x0, y0, x0, y0, 800)
            else:
                self.win.act("tap", x0, y0)
            self._ripple(p0)
        else:
            self.win.act("swipe", x0, y0, x1, y1, int(max(80, min(dt * 1000, 1500))))
        self.update()

    def wheelEvent(self, e):
        if not (self.adb and self.inside(e.position())):
            return
        x, y = self.to_phone(e.position())
        d = int(self.size_phone[1] * 0.16) * (1 if e.angleDelta().y() > 0 else -1)
        self.win.act("swipe", x, y, x, max(0, min(self.size_phone[1] - 1, y + d)), 150)

    # ---- کیبورد ----
    def keyPressEvent(self, e):
        if not self.adb:
            return
        if e.key() in ANDROID_KEYS:
            return self.win.act("key", ANDROID_KEYS[e.key()])
        if e.modifiers() & Qt.KeyboardModifier.ControlModifier:
            return
        t = e.text()
        if t and t.isprintable():
            self.win.send_text_to_phone(t)


# =============================
# اجزای رابط
# =============================
def set_state(w, state):
    w.setProperty("state", state)
    w.style().unpolish(w)
    w.style().polish(w)


def mk_btn(text, cb=None, variant=None, tip=None, name=None):
    b = QPushButton(text)
    if variant:
        b.setProperty("variant", variant)
    if tip:
        b.setToolTip(tip)
    if name:
        b.setObjectName(name)
    b.setCursor(Qt.CursorShape.PointingHandCursor)
    if cb:
        b.clicked.connect(cb)
    return b


def mk_card(title=None):
    f = QFrame()
    f.setObjectName("Card")
    lay = QVBoxLayout(f)
    lay.setContentsMargins(16, 14, 16, 16)
    lay.setSpacing(10)
    if title:
        t = QLabel(title)
        t.setObjectName("CardTitle")
        lay.addWidget(t)
    return f, lay


def mk_label(text, name=None, wrap=True):
    l = QLabel(text)
    if name:
        l.setObjectName(name)
    l.setWordWrap(wrap)
    return l


def ltr(w):
    w.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
    return w


# =============================
# آیکون‌های برداری (جایگزین ایموجی؛ با رنگ تم هماهنگ می‌شوند)
# =============================
def _poly(p, pts, close=False):
    pg = QPolygonF([QPointF(x, y) for x, y in pts])
    p.drawPolygon(pg) if close else p.drawPolyline(pg)


def _speaker(p):
    _poly(p, [(4.5, 10), (8, 10), (12, 6.5), (12, 17.5), (8, 14), (4.5, 14)], True)


def _arrow(p, dx, dy):
    # خط و سر پیکان؛ (dx, dy) جهت
    cx, cy = 12, 12
    p.drawLine(QPointF(cx - dx * 6.5, cy - dy * 6.5), QPointF(cx + dx * 6.5, cy + dy * 6.5))
    tx, ty = cx + dx * 6.5, cy + dy * 6.5
    px, py = -dy, dx
    _poly(p, [(tx - dx * 5 + px * 5, ty - dy * 5 + py * 5), (tx, ty), (tx - dx * 5 - px * 5, ty - dy * 5 - py * 5)])


def _ic_power(p, c):
    p.drawArc(QRectF(5.5, 5.5, 13, 13), 120 * 16, 300 * 16)
    p.drawLine(QPointF(12, 4.5), QPointF(12, 11.5))


def _ic_camera(p, c):
    p.drawRoundedRect(QRectF(3.5, 7.5, 17, 12), 3, 3)
    p.drawEllipse(QPointF(12, 13.5), 3.3, 3.3)
    _poly(p, [(8.5, 7.5), (10, 5), (14, 5), (15.5, 7.5)])


def _ic_record(p, c):
    p.drawEllipse(QPointF(12, 12), 8.2, 8.2)
    p.setBrush(c)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(QPointF(12, 12), 4.2, 4.2)


def _ic_stop(p, c):
    p.setBrush(c)
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(QRectF(6.5, 6.5, 11, 11), 2.5, 2.5)


def _ic_rotate(p, c):
    p.drawArc(QRectF(5, 5, 14, 14), 40 * 16, 280 * 16)
    _poly(p, [(17.8, 3.6), (17.4, 7.6), (21.2, 7.4)])


def _ic_bell(p, c):
    path = QPainterPath()
    path.moveTo(7.5, 16.5)
    path.lineTo(7.5, 11.5)
    path.arcTo(QRectF(7.5, 6.5, 9, 9), 180, -180)
    path.lineTo(16.5, 16.5)
    path.lineTo(18.5, 18.5)
    path.lineTo(5.5, 18.5)
    path.closeSubpath()
    p.drawPath(path)
    p.drawLine(QPointF(10.5, 21), QPointF(13.5, 21))


def _ic_copy(p, c):
    p.drawRoundedRect(QRectF(8.5, 8.5, 11, 11), 2.5, 2.5)
    _poly(p, [(15.5, 8.5), (15.5, 6.5), (13.5, 4.5), (6.5, 4.5), (4.5, 6.5), (4.5, 13.5), (6.5, 15.5), (8.5, 15.5)])


def _ic_sun(p, c):
    p.drawEllipse(QPointF(12, 12), 3.8, 3.8)
    import math
    for i in range(8):
        a = i * math.pi / 4
        p.drawLine(QPointF(12 + 6.4 * math.cos(a), 12 + 6.4 * math.sin(a)),
                   QPointF(12 + 8.6 * math.cos(a), 12 + 8.6 * math.sin(a)))


def _ic_moon(p, c):
    outer, inner = QPainterPath(), QPainterPath()
    outer.addEllipse(QRectF(5, 5, 14, 14))
    inner.addEllipse(QRectF(9.5, 3, 12, 12))
    p.drawPath(outer.subtracted(inner))


def _ic_play(p, c):
    p.setBrush(c)
    p.setPen(Qt.PenStyle.NoPen)
    _poly(p, [(8.5, 6), (8.5, 18), (18, 12)], True)


def _ic_prev(p, c):
    p.drawLine(QPointF(7, 6.5), QPointF(7, 17.5))
    p.setBrush(c)
    _poly(p, [(18, 6.5), (18, 17.5), (10, 12)], True)


def _ic_next(p, c):
    p.drawLine(QPointF(17, 6.5), QPointF(17, 17.5))
    p.setBrush(c)
    _poly(p, [(6, 6.5), (6, 17.5), (14, 12)], True)


def _ic_phone(p, c):
    p.drawRoundedRect(QRectF(6.5, 2.5, 11, 19), 3, 3)
    p.drawLine(QPointF(10.5, 5.5), QPointF(13.5, 5.5))


def _ic_folder(p, c):
    _poly(p, [(3.5, 7.5), (3.5, 18), (20.5, 18), (20.5, 9), (12, 9), (10, 6.5), (3.5, 6.5)], True)


def _ic_send(p, c):
    _poly(p, [(4, 12), (20, 4.5), (15.5, 19.5), (11.5, 13.5)], True)
    p.drawLine(QPointF(11.5, 13.5), QPointF(20, 4.5))


def _ic_globe(p, c):
    p.drawEllipse(QPointF(12, 12), 8, 8)
    p.drawEllipse(QPointF(12, 12), 3.6, 8)
    p.drawLine(QPointF(4, 12), QPointF(20, 12))


ICONS = {
    "back": lambda p, c: _poly(p, [(15.5, 5.5), (7.5, 12), (15.5, 18.5)], True),
    "home": lambda p, c: p.drawEllipse(QPointF(12, 12), 6.6, 6.6),
    "recents": lambda p, c: p.drawRoundedRect(QRectF(6, 6, 12, 12), 3.2, 3.2),
    "power": _ic_power, "camera": _ic_camera, "record": _ic_record, "stop": _ic_stop, "rotate": _ic_rotate,
    "bell": _ic_bell, "copy": _ic_copy, "sun": _ic_sun, "moon": _ic_moon, "play": _ic_play, "prev": _ic_prev,
    "next": _ic_next, "phone": _ic_phone, "folder": _ic_folder, "send": _ic_send, "globe": _ic_globe,
    "vol_up": lambda p, c: (_speaker(p), p.drawArc(QRectF(9.5, 8.5, 7, 7), -55 * 16, 110 * 16),
                            p.drawArc(QRectF(7.5, 5.5, 12, 13), -55 * 16, 110 * 16)),
    "vol_down": lambda p, c: (_speaker(p), p.drawArc(QRectF(9.5, 8.5, 7, 7), -55 * 16, 110 * 16)),
    "mute": lambda p, c: (_speaker(p), p.drawLine(QPointF(15.5, 9.5), QPointF(20.5, 14.5)),
                          p.drawLine(QPointF(20.5, 9.5), QPointF(15.5, 14.5))),
    "up": lambda p, c: _arrow(p, 0, -1), "down": lambda p, c: _arrow(p, 0, 1),
    "left": lambda p, c: _arrow(p, -1, 0), "right": lambda p, c: _arrow(p, 1, 0),
    "dot": lambda p, c: (p.setBrush(c), p.setPen(Qt.PenStyle.NoPen), p.drawEllipse(QPointF(12, 12), 3, 3)),
    "refresh": lambda p, c: (p.drawArc(QRectF(5, 5, 14, 14), 30 * 16, 300 * 16), _poly(p, [(16.5, 2.5), (17.2, 6.8), (21.5, 6)])),
    "plus": lambda p, c: (p.drawLine(QPointF(12, 5.5), QPointF(12, 18.5)), p.drawLine(QPointF(5.5, 12), QPointF(18.5, 12))),
    "check": lambda p, c: _poly(p, [(5.5, 12.5), (10, 17), (18.5, 7)]),
    "file": lambda p, c: (_poly(p, [(6.5, 3.5), (14, 3.5), (18.5, 8), (18.5, 20.5), (6.5, 20.5)], True),
                          _poly(p, [(14, 3.5), (14, 8), (18.5, 8)])),
    "trash": lambda p, c: (p.drawLine(QPointF(5, 7), QPointF(19, 7)), _poly(p, [(9, 7), (9, 4.5), (15, 4.5), (15, 7)]),
                           _poly(p, [(7, 7), (8, 19.5), (16, 19.5), (17, 7)])),
    "save": lambda p, c: (p.drawRoundedRect(QRectF(4.5, 4.5, 15, 15), 2.5, 2.5), p.drawRect(QRectF(8, 4.5, 8, 5)),
                          p.drawRect(QRectF(8, 13.5, 8, 6))),
}
ICON_ROUNDS = []


def icon_round(name, tip, cb):
    """دکمه‌ی گرد کوچک با آیکون برداری."""
    b = mk_btn("", cb, tip=tip, name="Round")
    b.setIconSize(QSize(20, 20))
    b.setProperty("ic", name)
    b.setIcon(make_icon(name, size=20))
    ICON_ROUNDS.append(b)
    return b


def make_icon(name, color=None, size=22):
    col = QColor(color or CUR["text"])
    k = 3
    pm = QPixmap(size * k, size * k)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.scale(size * k / 24.0, size * k / 24.0)
    pen = QPen(col, 1.9)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    ICONS[name](p, col)
    p.end()
    pm.setDevicePixelRatio(k)
    return QIcon(pm)


def app_icon():
    """آیکون برنامه (همان طرح assets/icon.svg)."""
    pm = QPixmap(256, 256)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    g = QLinearGradient(0, 0, 256, 256)
    g.setColorAt(0, QColor("#7C5CFF"))
    g.setColorAt(1, QColor("#4F8CFF"))
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(g)
    p.drawRoundedRect(QRectF(8, 8, 240, 240), 58, 58)
    pen = QPen(QColor("white"), 12)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRoundedRect(QRectF(84, 48, 88, 160), 22, 22)
    p.drawLine(QPointF(112, 68), QPointF(144, 68))
    p.setPen(QPen(QColor(255, 255, 255, 120), 8))
    p.drawEllipse(QPointF(128, 136), 30, 30)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor("white"))
    p.drawEllipse(QPointF(128, 136), 11, 11)
    p.end()
    return QIcon(pm)


class Segmented(QFrame):
    """کنترل بخش‌بندی‌شده‌ی مینیمال (جایگزین تب‌های کوچک)."""
    changed = pyqtSignal(int)

    def __init__(self, labels):
        super().__init__()
        self.setObjectName("Seg")
        lay = QHBoxLayout(self)
        lay.setContentsMargins(3, 3, 3, 3)
        lay.setSpacing(2)
        self.btns = []
        for i, t in enumerate(labels):
            b = QPushButton(t)
            b.setObjectName("SegBtn")
            b.setCheckable(True)
            b.setCursor(Qt.CursorShape.PointingHandCursor)
            b.clicked.connect(lambda _=False, k=i: self.select(k))
            lay.addWidget(b, 1)
            self.btns.append(b)
        self.select(0)

    def select(self, i):
        for j, b in enumerate(self.btns):
            b.setChecked(j == i)
        self.changed.emit(i)


class Root(QWidget):
    """پس‌زمینه با درخشش ملایم آبی/بنفش (aurora)."""

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect(), qc(CUR["bg"]))
        for (cx, cy, col) in ((0.92, 0.0, CUR["a2"]), (0.04, 1.0, CUR["a1"])):
            g = QRadialGradient(self.width() * cx, self.height() * cy, max(self.width(), self.height()) * 0.55)
            g.setColorAt(0, qc(col, CUR["aur"]))
            g.setColorAt(1, qc(col, 0))
            p.fillRect(self.rect(), g)


def shq(s):
    """نقل‌قول امن برای shell اندروید."""
    return "'" + str(s).replace("'", "'\\''") + "'"


def human(n):
    n = float(n)
    for u in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or u == "TB":
            return "%d B" % n if u == "B" else "%.1f %s" % (n, u)
        n /= 1024


def scroll_wrap(inner, width=None):
    sa = QScrollArea()
    sa.setWidgetResizable(True)
    sa.setWidget(inner)
    sa.setFrameShape(QFrame.Shape.NoFrame)
    sa.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
    sa.setStyleSheet("QScrollArea{background:transparent;border:0;} QScrollArea>QWidget>QWidget{background:transparent;}")
    if width:
        sa.setFixedWidth(width)
    return sa


class Gauge(QWidget):
    """گیج دایره‌ای (برای درصد باتری)."""

    def __init__(self):
        super().__init__()
        self.value, self.sub = 0, ""
        self.setMinimumSize(190, 170)

    def set_value(self, v, sub=""):
        self.value, self.sub = max(0, min(100, v)), sub
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        side = min(self.width(), self.height() - 26) - 20
        r = QRectF((self.width() - side) / 2, 10, side, side)
        pen = QPen(qc(CUR["btn"]), 14)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen)
        p.drawArc(r, 225 * 16, -270 * 16)
        g = QLinearGradient(r.topLeft(), r.bottomRight())
        low = self.value <= 20
        g.setColorAt(0, qc(CUR["danger1"] if low else CUR["a1"]))
        g.setColorAt(1, qc(CUR["warn"] if low else CUR["a2"]))
        pen2 = QPen(g, 14)
        pen2.setCapStyle(Qt.PenCapStyle.RoundCap)
        p.setPen(pen2)
        p.drawArc(r, 225 * 16, int(-270 * 16 * self.value / 100))
        p.setPen(qc(CUR["text"]))
        f = QFont(FONT_FAMILY, 22)
        f.setWeight(QFont.Weight.Bold)
        p.setFont(f)
        p.drawText(r, int(Qt.AlignmentFlag.AlignCenter), tr("%d٪") % self.value)
        p.setPen(qc(CUR["muted"]))
        p.setFont(QFont(FONT_FAMILY, 9))
        p.drawText(QRectF(0, r.bottom() + 2, self.width(), 22), int(Qt.AlignmentFlag.AlignCenter), self.sub)


class Sparkline(QWidget):
    """نمودار زنده‌ی چند سری (باتری و RAM)."""

    def __init__(self):
        super().__init__()
        self.series = {tr("باتری"): deque(maxlen=60), "RAM": deque(maxlen=60)}
        self.setMinimumHeight(150)

    def push(self, name, v):
        self.series[name].append(v)
        self.update()

    def clear(self):
        for d in self.series.values():
            d.clear()
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(34, 8, -8, -26)
        p.setPen(QPen(qc(CUR["border"]), 1))
        p.setFont(QFont(FONT_FAMILY, 8))
        for v in (0, 50, 100):
            y = r.bottom() - r.height() * v / 100
            p.drawLine(QPointF(r.left(), y), QPointF(r.right(), y))
            p.setPen(qc(CUR["muted"]))
            p.drawText(QRectF(0, y - 8, 30, 16), int(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter), str(v))
            p.setPen(QPen(qc(CUR["border"]), 1))
        cols = {tr("باتری"): CUR["ok"], "RAM": CUR["a2"]}
        lx = r.left()
        for name, d in self.series.items():
            pen = QPen(qc(cols[name]), 2.4)
            pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            p.setPen(pen)
            if len(d) > 1:
                path = QPainterPath()
                for i, v in enumerate(d):
                    x = r.left() + r.width() * i / 59.0
                    y = r.bottom() - r.height() * max(0, min(100, v)) / 100
                    path.moveTo(x, y) if i == 0 else path.lineTo(x, y)
                p.drawPath(path)
            p.setBrush(qc(cols[name]))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawEllipse(QPointF(lx + 5, r.bottom() + 15), 4, 4)
            p.setPen(qc(CUR["muted"]))
            last = (tr("%d٪") % d[-1]) if d else "—"
            p.drawText(QPointF(lx + 14, r.bottom() + 19), "%s %s" % (name, last))
            lx += 110


class HistLine(QLineEdit):
    """خط فرمان با تاریخچه (بالا/پایین)."""

    def __init__(self):
        super().__init__()
        self.hist, self.pos = [], 0

    def remember(self, t):
        if t and (not self.hist or self.hist[-1] != t):
            self.hist.append(t)
        self.pos = len(self.hist)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Up and self.hist:
            self.pos = max(0, self.pos - 1)
            self.setText(self.hist[self.pos])
        elif e.key() == Qt.Key.Key_Down and self.hist:
            self.pos = min(len(self.hist), self.pos + 1)
            self.setText(self.hist[self.pos] if self.pos < len(self.hist) else "")
        else:
            super().keyPressEvent(e)


LS_RE = re.compile(r"^([\-dlbcps][rwxsStT\-]{9})\s+\d+\s+\S+\s+\S+\s+(\d+)\s+"
                   r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}|[A-Za-z]{3}\s+\d+\s+[\d:]+)\s+(.+)$")


class FileManager(QWidget):
    """مدیر فایل گوشی: مرور، دانلود، ارسال، حذف، پوشه‌ی جدید، تغییر نام."""

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.path = "/sdcard/"
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 4, 0, 0)
        card, cl = mk_card(tr("مدیر فایل گوشی"))
        top = QHBoxLayout()
        top.addWidget(icon_round("up", tr("پوشه‌ی بالاتر"), self.up))
        self.cmb = ltr(QComboBox())
        for lbl, p in ((tr("حافظه‌ی داخلی"), "/sdcard/"), ("Download", "/sdcard/Download/"), ("DCIM", "/sdcard/DCIM/"),
                       ("Pictures", "/sdcard/Pictures/"), ("Documents", "/sdcard/Documents/"),
                       ("Movies", "/sdcard/Movies/"), ("Music", "/sdcard/Music/"), (tr("ریشه /"), "/")):
            self.cmb.addItem(lbl, p)
        self.cmb.activated.connect(lambda i: self.go(self.cmb.itemData(i)))
        top.addWidget(self.cmb)
        self.ed = ltr(QLineEdit(self.path))
        self.ed.returnPressed.connect(lambda: self.go(self.ed.text()))
        top.addWidget(self.ed, 1)
        top.addWidget(icon_round("refresh", tr("تازه‌سازی"), self.refresh))
        cl.addLayout(top)
        self.lst = ltr(QListWidget())
        self.lst.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection)
        self.lst.itemDoubleClicked.connect(self._open)
        cl.addWidget(self.lst, 1)
        row = QHBoxLayout()
        for txt, cb, v in ((tr("دانلود"), self.download, "primary"), (tr("ارسال فایل"), self.upload, None),
                           (tr("پوشه‌ی جدید"), self.mkdir, None), (tr("تغییر نام"), self.rename, None),
                           (tr("حذف"), self.delete, "danger"), (tr("نصب APK"), win.install_apk_dialog, None)):
            row.addWidget(mk_btn(txt, cb, v))
        cl.addLayout(row)
        self.status = mk_label(tr("برای شروع به گوشی وصل شو. فایل‌ها را می‌توانی روی پنجره‌ی برنامه هم رها کنی."), "Muted")
        cl.addWidget(self.status)
        outer.addWidget(card)

    def go(self, path):
        path = (path or "/").strip()
        self.path = path if path.endswith("/") else path + "/"
        self.ed.setText(self.path)
        self.refresh()

    def up(self):
        parent = str(PurePosixPath(self.path.rstrip("/") or "/").parent)
        self.go(parent)

    def refresh(self):
        a = self.win.adb
        if not a:
            self.lst.clear()
            return self.status.setText(tr("گوشی متصل نیست."))
        path = self.path
        self.win.bg(lambda: a.sh("ls -la %s" % shq(path)), lambda out: self._fill(path, out))

    def _fill(self, path, out):
        if path != self.path or isinstance(out, Exception):
            return
        rows = []
        for l in out.splitlines():
            m = LS_RE.match(l.strip())
            if not m:
                continue
            perms, size, date, name = m.groups()
            name = name.split(" -> ")[0]
            if name not in (".", ".."):
                rows.append((perms[0] in "dl", name, int(size), date))
        rows.sort(key=lambda r: (not r[0], r[1].lower()))
        self.lst.clear()
        self.lst.setIconSize(QSize(18, 18))
        for isdir, name, size, date in rows:
            txt = name + ("" if isdir else "      " + human(size)) + "      " + date
            it = QListWidgetItem(make_icon("folder" if isdir else "file", CUR["a1h"] if isdir else CUR["muted"], 18), txt)
            it.setData(Qt.ItemDataRole.UserRole, (name, isdir))
            self.lst.addItem(it)
        bad = ("No such file", "Permission denied", "not found")
        self.status.setText(out.strip()[:120] if (not rows and any(b in out for b in bad)) else tr("%d مورد") % len(rows))

    def selected(self):
        return [(self.path + it.data(Qt.ItemDataRole.UserRole)[0], it.data(Qt.ItemDataRole.UserRole)[1])
                for it in self.lst.selectedItems()]

    def _open(self, it):
        name, isdir = it.data(Qt.ItemDataRole.UserRole)
        if isdir:
            return self.go(self.path + name)
        a = self.win.adb
        tmp = Path(tempfile.gettempdir()) / "phone_bridge_open"
        tmp.mkdir(exist_ok=True)
        dest = tmp / name
        self.status.setText(tr("در حال دانلود برای باز کردن…"))
        self.win.bg(lambda: a.pull(self.path + name, str(dest)),
                    lambda r: (self.status.setText(tr("باز شد")), QDesktopServices.openUrl(QUrl.fromLocalFile(str(dest)))))

    def download(self):
        sel = self.selected()
        if not sel or not self.win.need_phone():
            return self.status.setText(tr("چیزی انتخاب نشده."))
        dest = QFileDialog.getExistingDirectory(self, tr("ذخیره در…"), str(Path.home() / "Downloads"))
        if not dest:
            return
        a = self.win.adb
        self.status.setText(tr("در حال دانلود %d مورد…") % len(sel))

        def work():
            return [a.pull(rp, dest)[0] for rp, _ in sel]

        def done(r):
            ok = not isinstance(r, Exception) and all(x == 0 for x in r)
            self.status.setText((tr("✅ دانلود شد: ") + dest) if ok else tr("دانلود کامل نشد؛ گزارش را در تب اتصال ببین."))
            if ok:
                self.win.open_folder(dest)
        self.win.bg(work, done)

    def upload(self):
        fns, _ = QFileDialog.getOpenFileNames(self, tr("فایل‌ها را انتخاب کن"), str(Path.home() / "Downloads"))
        if fns:
            self.win.push_files(fns, self.path)

    def _simple(self, cmd, msg):
        a = self.win.adb
        self.win.bg(lambda: a.sh(cmd), lambda out: (self.status.setText(msg), self.refresh()))

    def mkdir(self):
        if not self.win.need_phone():
            return
        n, ok = QInputDialog.getText(self, tr("پوشه‌ی جدید"), tr("نام پوشه:"))
        if ok and n.strip():
            self._simple("mkdir -p %s" % shq(self.path + n.strip()), tr("پوشه ساخته شد"))

    def rename(self):
        sel = self.selected()
        if len(sel) != 1:
            return self.status.setText(tr("برای تغییر نام، دقیقاً یک مورد را انتخاب کن."))
        old = sel[0][0]
        n, ok = QInputDialog.getText(self, tr("تغییر نام"), tr("نام جدید:"), text=PurePosixPath(old).name)
        if ok and n.strip():
            self._simple("mv %s %s" % (shq(old), shq(self.path + n.strip())), tr("نام تغییر کرد"))

    def delete(self):
        sel = self.selected()
        if not sel:
            return
        if QMessageBox.question(self, tr("حذف"), tr("%d مورد برای همیشه از گوشی حذف شود؟") % len(sel)) == \
                QMessageBox.StandardButton.Yes:
            self._simple("rm -rf " + " ".join(shq(p) for p, _ in sel), tr("حذف شد"))


class AppManager(QWidget):
    """لیست برنامه‌ها؛ اجرا، توقف، پاک‌کردن داده، حذف، استخراج APK."""

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.pkgs = []
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(14)

        c, cl = mk_card(tr("برنامه‌های نصب‌شده"))
        self.ed = ltr(QLineEdit())
        self.ed.setPlaceholderText(tr("جستجو (مثلاً telegram)…"))
        self.ed.textChanged.connect(self._filter)
        cl.addWidget(self.ed)
        self.chk = QCheckBox(tr("شامل برنامه‌های سیستمی"))
        self.chk.toggled.connect(self.refresh)
        cl.addWidget(self.chk)
        self.lst = ltr(QListWidget())
        self.lst.currentItemChanged.connect(self._select)
        cl.addWidget(self.lst, 1)
        self.lbl_count = mk_label("", "Muted")
        cl.addWidget(self.lbl_count)
        row = QHBoxLayout()
        row.addWidget(mk_btn(tr("تازه‌سازی"), self.refresh))
        row.addWidget(mk_btn(tr("ذخیره‌ی لیست"), self.export))
        cl.addLayout(row)
        lay.addWidget(c, 3)

        c, cl = mk_card(tr("عملیات روی برنامه‌ی انتخاب‌شده"))
        self.lbl_pkg = ltr(mk_label("—", "Url"))
        self.lbl_pkg.setStyleSheet("font-size:10.5pt;")
        cl.addWidget(self.lbl_pkg)
        self.lbl_info = mk_label(tr("یک برنامه را از لیست انتخاب کن."), "Muted")
        cl.addWidget(self.lbl_info)
        for txt, cb, v in ((tr("اجرا"), self.launch, "primary"), (tr("توقف اجباری"), self.stop, None),
                           (tr("تنظیمات برنامه روی گوشی"), self.details, None),
                           (tr("استخراج APK به کامپیوتر"), self.extract, None),
                           (tr("پاک کردن داده‌ها"), self.clear, None), (tr("حذف برنامه"), self.uninstall, "danger"),
                           (tr("نصب APK از کامپیوتر"), win.install_apk_dialog, None)):
            cl.addWidget(mk_btn(txt, cb, v))
        cl.addStretch(1)
        lay.addWidget(c, 2)

    def refresh(self, *_):
        a = self.win.adb
        if not a:
            return self.lbl_count.setText(tr("گوشی متصل نیست."))
        cmd = "pm list packages" if self.chk.isChecked() else "pm list packages -3"
        self.win.bg(lambda: a.sh(cmd, 40), self._got)

    def _got(self, out):
        if isinstance(out, Exception):
            return
        self.pkgs = sorted(l.strip()[8:] for l in out.splitlines() if l.strip().startswith("package:"))
        self._filter()

    def _filter(self, *_):
        q = self.ed.text().strip().lower()
        self.lst.clear()
        shown = [p for p in self.pkgs if q in p.lower()]
        self.lst.addItems(shown)
        self.lbl_count.setText(tr("%d برنامه") % len(shown))

    def cur(self):
        it = self.lst.currentItem()
        if not it:
            self.win.toast(tr("اول یک برنامه را انتخاب کن"))
            return None
        return it.text()

    def _select(self, it, _=None):
        if not it or not self.win.adb:
            return
        pkg, a = it.text(), self.win.adb
        self.lbl_pkg.setText(pkg)
        self.lbl_info.setText(tr("در حال خواندن اطلاعات…"))

        def work():
            return a.sh("dumpsys package %s | grep -E 'versionName|versionCode|firstInstallTime|lastUpdateTime'" % shq(pkg))

        def done(out):
            if isinstance(out, Exception) or self.lbl_pkg.text() != pkg:
                return
            g = lambda k: (re.search(k + r"=([^\s]+(?: [0-9:]+)?)", out) or [None, "—"])[1]
            self.lbl_info.setText(tr("نسخه: %s\nنصب: %s\nآخرین به‌روزرسانی: %s") % (
                g("versionName"), g("firstInstallTime"), g("lastUpdateTime")))
        self.win.bg(work, done)

    def launch(self):
        p = self.cur()
        if p:
            self.win.run_sh("monkey -p %s -c android.intent.category.LAUNCHER 1" % shq(p), tr("اجرا شد: ") + p)

    def stop(self):
        p = self.cur()
        if p:
            self.win.run_sh("am force-stop %s" % shq(p), tr("متوقف شد: ") + p)

    def details(self):
        p = self.cur()
        if p:
            self.win.run_sh("am start -a android.settings.APPLICATION_DETAILS_SETTINGS -d package:%s" % p, tr("باز شد"))

    def clear(self):
        p = self.cur()
        if p and QMessageBox.question(self, tr("پاک کردن داده"), tr("همه‌ی داده‌های %s پاک شود؟") % p) == \
                QMessageBox.StandardButton.Yes:
            self.win.run_sh("pm clear %s" % shq(p), tr("داده‌های برنامه پاک شد"))

    def uninstall(self):
        p = self.cur()
        if p and QMessageBox.question(self, tr("حذف برنامه"), tr("%s حذف شود؟") % p) == QMessageBox.StandardButton.Yes:
            a = self.win.adb
            self.win.bg(lambda: a.sh("pm uninstall %s || pm uninstall --user 0 %s" % (shq(p), shq(p))),
                        lambda out: (self.win.toast(tr("حذف: ") + str(out)[:80]), self.refresh()))

    def extract(self):
        p = self.cur()
        if not p:
            return
        dest = QFileDialog.getExistingDirectory(self, tr("ذخیره‌ی APK در…"), str(Path.home() / "Downloads"))
        if not dest:
            return
        a = self.win.adb

        def work():
            paths = [l.strip()[8:] for l in a.sh("pm path %s" % shq(p)).splitlines() if l.strip().startswith("package:")]
            n = 0
            for rp in paths:
                base = PurePosixPath(rp).name
                name = p + ".apk" if base == "base.apk" else "%s-%s" % (p, base)
                if a.pull(rp, str(Path(dest) / name))[0] == 0:
                    n += 1
            return n, len(paths)

        def done(r):
            if isinstance(r, Exception):
                return self.win.toast(tr("استخراج ناموفق"))
            self.win.toast(tr("✅ %d از %d فایل APK ذخیره شد") % r)
            if r[0]:
                self.win.open_folder(dest)
        self.win.bg(work, done)

    def export(self):
        if not self.pkgs:
            return self.win.toast(tr("لیست خالی است"))
        fn, _ = QFileDialog.getSaveFileName(self, tr("ذخیره"), str(Path.home() / "phone_apps.txt"), "Text (*.txt)")
        if fn:
            Path(fn).write_text("\n".join(self.pkgs), "utf-8")
            self.win.toast(tr("ذخیره شد: ") + fn)


LEVELS = "VDIWEF"


class LogcatPane(QWidget):
    """Logcat زنده با فیلتر سطح و جستجو."""

    def __init__(self, win):
        super().__init__()
        self.win = win
        self.q, self.buf, self.proc = queue.Queue(), deque(maxlen=20000), None
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 8, 0, 0)
        row = QHBoxLayout()
        self.btn = mk_btn(tr("شروع"), self.toggle, "primary")
        row.addWidget(self.btn)
        self.cmb = QComboBox()
        self.cmb.addItems([tr("همه (Verbose)"), tr("Debug به بالا"), tr("Info به بالا"), tr("Warning به بالا"), tr("Error به بالا")])
        self.cmb.currentIndexChanged.connect(self._rerender)
        row.addWidget(self.cmb)
        self.ed = ltr(QLineEdit())
        self.ed.setPlaceholderText(tr("جستجو در لاگ…"))
        self.ed.textChanged.connect(self._rerender)
        row.addWidget(self.ed, 1)
        self.chk_pause = QCheckBox(tr("مکث"))
        row.addWidget(self.chk_pause)
        row.addWidget(icon_round("trash", tr("پاک کردن نمایش"), self.clear))
        row.addWidget(icon_round("save", tr("ذخیره در فایل"), self.save))
        row.addWidget(mk_btn(tr("لاگ گوشی"), self.clear_device, tip="logcat -c"))
        lay.addLayout(row)
        self.out = ltr(QTextEdit())
        self.out.setReadOnly(True)
        self.out.setFont(QFont("Consolas", 9))
        lay.addWidget(self.out, 1)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._drain)
        self.timer.start(150)

    def _lv(self, line):
        return LEVELS.index(line[0]) if line[:2] in [c + "/" for c in LEVELS] else 2

    def _ok(self, line):
        t = self.ed.text().strip().lower()
        return self._lv(line) >= self.cmb.currentIndex() and (not t or t in line.lower())

    def _html(self, line):
        col = {0: CUR["muted"], 1: CUR["muted"], 2: CUR["text"], 3: CUR["warn"], 4: CUR["danger1"], 5: CUR["danger1"]}
        return '<span style="color:%s">%s</span>' % (col[self._lv(line)], html.escape(line))

    def toggle(self):
        if self.proc:
            return self.stop()
        if not self.win.need_phone():
            return
        a = self.win.adb
        try:
            self.proc = subprocess.Popen(a.base + ["logcat", "-v", "brief"], stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT, **NOWIN)
        except Exception as e:
            return self.win.toast(tr("اجرای logcat ناموفق: %s") % e)
        proc = self.proc

        def reader():
            for raw in iter(proc.stdout.readline, b""):
                self.q.put(raw.decode("utf-8", "replace").rstrip())
        threading.Thread(target=reader, daemon=True).start()
        self.btn.setText(tr("توقف"))

    def stop(self):
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass
        self.proc = None
        self.btn.setText(tr("شروع"))

    def _drain(self):
        new = []
        try:
            while len(new) < 600:
                new.append(self.q.get_nowait())
        except queue.Empty:
            pass
        if not new:
            return
        self.buf.extend(new)
        if self.chk_pause.isChecked():
            return
        shown = [self._html(l) for l in new if self._ok(l)]
        if shown:
            c = self.out.textCursor()
            c.movePosition(c.MoveOperation.End)
            c.insertHtml("<br>".join(shown) + "<br>")
            self.out.ensureCursorVisible()
            if self.out.document().characterCount() > 700000:
                self._rerender()

    def _rerender(self, *_):
        self.out.clear()
        lines = [self._html(l) for l in list(self.buf)[-2500:] if self._ok(l)]
        if lines:
            self.out.insertHtml("<br>".join(lines) + "<br>")
            self.out.ensureCursorVisible()

    def clear(self):
        self.buf.clear()
        self.out.clear()

    def clear_device(self):
        if self.win.need_phone():
            self.win.run_sh("logcat -c", tr("لاگ گوشی پاک شد"))

    def save(self):
        fn, _ = QFileDialog.getSaveFileName(self, tr("ذخیره"), str(Path.home() / "logcat.txt"), "Text (*.txt)")
        if fn:
            Path(fn).write_text("\n".join(l for l in self.buf if self._ok(l)), "utf-8")
            self.win.toast(tr("ذخیره شد: ") + fn)


class TerminalPane(QWidget):
    """ترمینال adb shell با تاریخچه."""

    def __init__(self, win):
        super().__init__()
        self.win = win
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 8, 0, 0)
        self.out = ltr(QTextEdit())
        self.out.setReadOnly(True)
        self.out.setFont(QFont("Consolas", 9))
        lay.addWidget(self.out, 1)
        row = QHBoxLayout()
        self.inp = ltr(HistLine())
        self.inp.setPlaceholderText(tr("دستور shell (مثلاً: getprop ro.product.model) — Enter؛ بالا/پایین = تاریخچه"))
        self.inp.returnPressed.connect(self.run)
        row.addWidget(self.inp, 1)
        row.addWidget(mk_btn(tr("اجرا"), self.run, "primary"))
        row.addWidget(icon_round("trash", tr("پاک کردن"), self.out.clear))
        lay.addLayout(row)
        row = QHBoxLayout()
        for txt, cmd in ((tr("مشخصات"), "getprop ro.product.model"), (tr("باتری"), "dumpsys battery"),
                         (tr("برنامه‌ها"), "pm list packages -3"), (tr("شبکه"), "ip addr show wlan0"),
                         (tr("پردازش‌ها"), "top -n 1 -b | head -n 15"), (tr("حافظه"), "df -h"),
                         (tr("برنامه‌ی فعال"), "dumpsys window | grep -E 'mCurrentFocus'")):
            row.addWidget(mk_btn(txt, lambda _=False, c=cmd: self.run(c)))
        lay.addLayout(row)

    def run(self, cmd=None):
        cmd = cmd if isinstance(cmd, str) else self.inp.text().strip()
        if not cmd:
            return
        self.inp.remember(cmd)
        self.inp.clear()
        self.out.append('<span style="color:%s">%s</span>' % (CUR["a1h"], html.escape(cmd)))
        if not self.win.adb:
            return self.out.append(tr("گوشی متصل نیست."))
        a = self.win.adb
        self.win.bg(lambda: a.sh(cmd, 60), lambda o: self.out.append(html.escape(str(o)).replace("\n", "<br>") or tr("(بدون خروجی)")))


class FeaturesMixin:
    """امکانات تازه‌ی پنجره‌ی اصلی."""

    # ------------------------------------------------ زیرساخت
    def _init_features(self):
        self.macro, self.macro_rec, self.macro_t0 = [], None, 0.0
        self._macro_stop, self._macro_thread = threading.Event(), None
        self.rec_proc, self.rec_remote, self.rec_t0 = None, None, 0.0
        self.last_serial, self._reconnecting, self._mon_busy, self._quitting = None, False, False, False
        self._rot, self._bright_val = 0, 128
        self.setAcceptDrops(True)
        self.server.set_clip = lambda t: ui(lambda: QGuiApplication.clipboard().setText(t))
        self.server.get_clip = lambda: ui_get(lambda: QGuiApplication.clipboard().text())
        for attr, ms, fn in (("t_rec", 1000, self._rec_tick), ("t_watch", 5000, self._watchdog),
                             ("t_frame", 350, self._frame_tick), ("t_mon", 3000, self._monitor_tick)):
            t = QTimer(self)
            t.timeout.connect(fn)
            t.start(ms)
            setattr(self, attr, t)
        self.t_rec.stop()
        self._t_bright = QTimer(self)
        self._t_bright.setSingleShot(True)
        self._t_bright.timeout.connect(self._apply_brightness)
        # میانبرهای کیبورد داخل برنامه
        for seq, fn in (("Alt+Left", lambda: self.act("key", 4)), ("Alt+Home", lambda: self.act("key", 3)),
                        ("Alt+Down", lambda: self.act("key", 187)), ("Ctrl+S", self.quick_shot),
                        ("Ctrl+R", self.toggle_record), ("Ctrl+Shift+C", self.copy_shot)):
            QShortcut(QKeySequence(seq), self, activated=fn)
        self._setup_tray()

    def bg(self, fn, cb=None):
        """اجرای fn در نخ پس‌زمینه و فراخوانی cb(نتیجه یا Exception) در نخ اصلی."""
        def run():
            try:
                r = fn()
            except Exception as e:
                r = e
            if cb:
                ui(lambda: cb(r))
        threading.Thread(target=run, daemon=True).start()

    def toast(self, m, ms=5000):
        self.statusBar().showMessage(m, ms)

    def need_phone(self, quiet=False):
        if self.adb:
            return True
        if not quiet:
            self.toast(tr("اول به گوشی وصل شو (تب «اتصال»)"))
        return False

    def pb_dir(self, kind):
        p = Path.home() / kind / "PhoneBridge"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def open_folder(self, p):
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(p)))

    def run_sh(self, cmd, msg=tr("انجام شد")):
        if not self.need_phone():
            return
        a = self.adb
        self.bg(lambda: a.sh(cmd), lambda out: self.toast(msg if isinstance(out, Exception) or not out.strip()
                                                           else msg + "  —  " + out.strip().replace("\n", " ")[:90]))

    def act(self, kind, *a):
        """همه‌ی اعمال لمسی/کیبوردی از این‌جا می‌گذرند (برای ضبط ماکرو)."""
        if not self.adb:
            return
        getattr(self.adb, {"tap": "tap", "swipe": "swipe", "key": "key", "text": "text"}[kind])(*a)
        if self.macro_rec is not None:
            self.macro_rec.append({"t": round(time.time() - self.macro_t0, 3), "k": kind, "a": list(a)})

    # ------------------------------------------------ رویداد اتصال
    def on_phone_connected(self, a):
        self.last_serial = a.serial
        self.refresh_info()
        self.files.go("/sdcard/")
        self.apps.refresh()
        self.spark.clear()

    def on_phone_disconnected(self):
        self.stop_record(fetch=False)
        self._macro_stop.set()
        if hasattr(self, "logcat"):
            self.logcat.stop()

    # ------------------------------------------------ صفحه‌ی کنترل (طراحی مینیمال)
    def icon_btn(self, name, tip, cb, color=None):
        b = QPushButton()
        b.setObjectName("Tool")
        b.setCursor(Qt.CursorShape.PointingHandCursor)
        b.setToolTip(tip)
        b.setIconSize(QSize(22, 22))
        b.setProperty("ic", name)
        b.setProperty("ic_col", color)
        b.setIcon(make_icon(name, color))
        b.clicked.connect(cb)
        self._icon_btns.append(b)
        return b

    def icon_text_btn(self, name, text, cb, variant=None):
        b = mk_btn(text, cb, variant, name="IconText")
        b.setIconSize(QSize(20, 20))
        b.setProperty("ic", name)
        b.setProperty("ic_col", "#FFFFFF" if variant in ("primary", "danger") else None)
        b.setIcon(make_icon(name, "#FFFFFF" if variant in ("primary", "danger") else None, 20))
        self._icon_btns.append(b)
        return b

    def refresh_icons(self):
        for b in ICON_ROUNDS:
            b.setIcon(make_icon(b.property("ic"), size=20))
        for b in self._icon_btns:
            s = b.iconSize().width()
            b.setIcon(make_icon(b.property("ic"), b.property("ic_col"), s))

    def _set_rec_ui(self, on):
        self.btn_rec.setProperty("ic", "stop" if on else "record")
        self.btn_rec.setProperty("ic_col", CUR["danger1"] if on else None)
        self.btn_rec.setToolTip(tr("توقف ضبط  (Ctrl+R)") if on else tr("ضبط ویدیوی صفحه  (Ctrl+R)"))
        self.refresh_icons()

    def _sep(self):
        s = QFrame()
        s.setObjectName("Sep")
        return s

    def _tab_control(self):
        self._icon_btns = []
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 6, 0, 0)
        lay.setSpacing(14)

        # ---- صحنه: نمایشگر + نوار ابزار آیکونی
        stage = QFrame()
        stage.setObjectName("Stage")
        sl = QHBoxLayout(stage)
        sl.setContentsMargins(14, 14, 12, 14)
        sl.setSpacing(10)
        colv = QVBoxLayout()
        colv.setSpacing(6)
        self.view = PhoneView(self)
        self.view.message.connect(self.on_view_message)
        colv.addWidget(self.view, 1)
        self.view_note = mk_label("", "Warn")
        self.view_note.setVisible(False)
        colv.addWidget(self.view_note)
        sl.addLayout(colv, 1)

        bar = QFrame()
        bar.setObjectName("Toolbar")
        bl = QVBoxLayout(bar)
        bl.setContentsMargins(5, 8, 5, 8)
        bl.setSpacing(4)
        bl.addWidget(self.icon_btn("back", tr("برگشت  (Alt+←)"), lambda: self.act("key", 4)))
        bl.addWidget(self.icon_btn("home", tr("خانه  (Alt+Home)"), lambda: self.act("key", 3)))
        bl.addWidget(self.icon_btn("recents", tr("برنامه‌های اخیر  (Alt+↓)"), lambda: self.act("key", 187)))
        bl.addWidget(self._sep())
        bl.addWidget(self.icon_btn("power", tr("روشن/خاموش صفحه"), lambda: self.act("key", 26)))
        bl.addWidget(self.icon_btn("vol_up", tr("صدا بیشتر"), lambda: self.act("key", 24)))
        bl.addWidget(self.icon_btn("vol_down", tr("صدا کمتر"), lambda: self.act("key", 25)))
        bl.addWidget(self._sep())
        bl.addWidget(self.icon_btn("camera", tr("اسکرین‌شات سریع  (Ctrl+S)"), self.quick_shot))
        bl.addWidget(self.icon_btn("copy", tr("کپی تصویر  (Ctrl+Shift+C)"), self.copy_shot))
        self.btn_rec = self.icon_btn("record", tr("ضبط ویدیوی صفحه  (Ctrl+R)"), self.toggle_record)
        bl.addWidget(self.btn_rec)
        bl.addWidget(self.icon_btn("rotate", tr("چرخش صفحه"), self.rotate))
        bl.addWidget(self.icon_btn("bell", tr("باز کردن اعلان‌ها"), lambda: self.phone_cmd("cmd statusbar expand-notifications")))
        bl.addStretch(1)
        bl.addWidget(self.icon_btn("folder", tr("پوشه‌ی تصاویر و ویدیوها"), lambda: self.open_folder(self.pb_dir("Pictures"))))
        sl.addWidget(bar)
        lay.addWidget(stage, 1)

        # ---- پنل کناری با کنترل بخش‌بندی‌شده
        panel = QFrame()
        panel.setObjectName("Panel")
        panel.setFixedWidth(330)
        pl = QVBoxLayout(panel)
        pl.setContentsMargins(14, 14, 14, 14)
        pl.setSpacing(12)
        seg = Segmented([tr("کنترل"), tr("ورودی"), tr("ماکرو")])
        pl.addWidget(seg)
        stack = QStackedWidget()
        stack.addWidget(scroll_wrap(self._pg_controls()))
        stack.addWidget(scroll_wrap(self._pg_input()))
        stack.addWidget(scroll_wrap(self._pg_macro()))
        seg.changed.connect(stack.setCurrentIndex)
        pl.addWidget(stack, 1)
        lay.addWidget(panel)
        return w

    def _caption(self, lay, text):
        lay.addWidget(mk_label(text, "Caption", False))

    def _pg_controls(self):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 4, 0)
        v.setSpacing(8)
        self._caption(v, tr("حرکت‌ها"))
        g = QGridLayout()
        g.setSpacing(6)
        for name, g_, r, c in (("up", "up", 0, 1), ("left", "left", 1, 0), ("right", "right", 1, 2), ("down", "down", 2, 1)):
            b = self.icon_btn(name, {"up": tr("اسکرول به پایین"), "down": tr("اسکرول به بالا"),
                                     "left": tr("swipe به چپ"), "right": tr("swipe به راست")}[name],
                              lambda _=False, k=g_: self.gesture(k))
            b.setObjectName("Dpad")
            b.setMinimumSize(0, 46)
            b.setMaximumSize(16777215, 46)
            b.setMinimumWidth(0)
            b.setMaximumWidth(16777215)
            g.addWidget(b, r, c)
        b = self.icon_btn("dot", tr("دوبار لمس وسط صفحه"), lambda: self.gesture("dbl"))
        b.setObjectName("Dpad")
        b.setMaximumSize(16777215, 46)
        b.setMaximumWidth(16777215)
        g.addWidget(b, 1, 1)
        dp = QWidget()
        dp.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        dp.setLayout(g)
        v.addWidget(dp)

        self._caption(v, tr("صفحه و نور"))
        v.addWidget(self.icon_text_btn("sun", tr("بیدار کردن و باز کردن قفل"), self.wake_unlock, "primary"))
        v.addWidget(self.icon_text_btn("moon", tr("خاموش کردن صفحه"), lambda: self.act("key", 223)))
        self.lbl_bright = mk_label(tr("روشنایی"), "Muted", False)
        v.addWidget(self.lbl_bright)
        self.sl_bright = QSlider(Qt.Orientation.Horizontal)
        self.sl_bright.setRange(1, 255)
        self.sl_bright.setValue(128)
        self.sl_bright.valueChanged.connect(self.set_brightness)
        v.addWidget(self.sl_bright)

        self._caption(v, tr("رسانه"))
        row = QHBoxLayout()
        for name, code in (("prev", 88), ("play", 85), ("next", 87), ("mute", 164)):
            b = self.icon_btn(name, "", lambda _=False, k=code: self.act("key", k))
            b.setObjectName("Dpad")
            b.setMaximumWidth(16777215)
            b.setMaximumHeight(46)
            row.addWidget(b)
        mr = QWidget()
        mr.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        mr.setLayout(row)
        v.addWidget(mr)

        self._caption(v, tr("نمایش"))
        self.chk_live = QCheckBox(tr("نمایش زنده‌ی صفحه"))
        self.chk_live.setChecked(True)
        self.chk_live.toggled.connect(self.on_live)
        v.addWidget(self.chk_live)
        self.cmb_speed = QComboBox()
        self.cmb_speed.addItems([tr("سریع (هر ۰٫۲۵ ثانیه)"), tr("معمولی (هر ۰٫۵ ثانیه)"), tr("کم‌مصرف (هر ۱ ثانیه)")])
        self.cmb_speed.setCurrentIndex(1)
        self.cmb_speed.currentIndexChanged.connect(self.on_speed)
        v.addWidget(self.cmb_speed)
        v.addWidget(mk_btn(tr("ذخیره‌ی اسکرین‌شات به‌صورت دلخواه…"), self.save_shot))
        self.lbl_rec = mk_label(tr("ضبط ویدیو تا ۳ دقیقه؛ بعد از توقف خودکار به کامپیوتر می‌آید."), "Muted")
        v.addWidget(self.lbl_rec)
        v.addStretch(1)
        return w

    def _pg_input(self):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 4, 0)
        v.setSpacing(8)
        self._caption(v, tr("تایپ روی گوشی"))
        self.ed_send = QLineEdit()
        self.ed_send.setPlaceholderText(tr("متن را بنویس و Enter بزن…"))
        self.ed_send.returnPressed.connect(self.send_line)
        v.addWidget(self.ed_send)
        self.chk_adbkb = QCheckBox(tr("فارسی/یونیکد با ADBKeyboard"))
        self.chk_adbkb.setToolTip(tr("برنامه‌ی ADBKeyboard باید روی گوشی نصب و به‌عنوان کیبورد انتخاب شده باشد."))
        v.addWidget(self.chk_adbkb)
        v.addWidget(self.icon_text_btn("send", tr("ارسال"), self.send_line, "primary"))
        self._caption(v, tr("موس روی صفحه"))
        v.addWidget(mk_label(tr("کلیک چپ = لمس\nنگه‌داشتن = لمس طولانی\nکشیدن = swipe\nچرخ موس = اسکرول\nکلیک راست = برگشت\nکلیک وسط = خانه"), "Muted"))
        self._caption(v, tr("کیبورد"))
        v.addWidget(mk_label(tr("روی صفحه‌ی گوشی کلیک کن و با کیبورد کامپیوتر تایپ کن. حروف فارسی فقط با ADBKeyboard "
                                "تایپ می‌شوند؛ یا از تب «کیبورد و ریموت PC» استفاده کن."), "Muted"))
        v.addStretch(1)
        return w

    def _pg_macro(self):
        w = QWidget()
        v = QVBoxLayout(w)
        v.setContentsMargins(0, 0, 4, 0)
        v.setSpacing(8)
        self._caption(v, tr("ضبط"))
        self.btn_mrec = mk_btn(tr("شروع ضبط"), self.macro_toggle_rec, "primary")
        v.addWidget(self.btn_mrec)
        self._caption(v, tr("پخش"))
        row = QHBoxLayout()
        row.addWidget(mk_label(tr("تکرار:"), "Muted", False))
        self.sp_loops = QSpinBox()
        self.sp_loops.setRange(0, 9999)
        self.sp_loops.setValue(1)
        self.sp_loops.setSpecialValueText("∞")
        self.sp_loops.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.sp_loops.setFixedWidth(64)
        row.addWidget(self.sp_loops)
        self.cmb_mspeed = QComboBox()
        self.cmb_mspeed.addItems([tr("۰٫۵×"), tr("۱×"), tr("۲×"), tr("۴×")])
        self.cmb_mspeed.setCurrentIndex(1)
        row.addWidget(self.cmb_mspeed, 1)
        v.addLayout(row)
        v.addWidget(self.icon_text_btn("play", tr("پخش ماکرو"), self.macro_play))
        v.addWidget(mk_btn(tr("توقف"), self.macro_stop))
        self._caption(v, tr("فایل"))
        row = QHBoxLayout()
        row.addWidget(mk_btn(tr("ذخیره"), self.macro_save))
        row.addWidget(mk_btn(tr("باز کردن"), self.macro_load))
        v.addLayout(row)
        self.lbl_macro = mk_label(tr("ماکرویی ضبط نشده. «شروع ضبط» را بزن و کارها را روی صفحه انجام بده."), "Muted")
        v.addWidget(self.lbl_macro)
        v.addStretch(1)
        return w

    # ---- حرکت‌ها و صفحه
    def gesture(self, name):
        if not self.need_phone():
            return
        w, h = self.view.size_phone
        m = {"up": (w // 2, int(h * .7), w // 2, int(h * .3)), "down": (w // 2, int(h * .3), w // 2, int(h * .7)),
             "left": (int(w * .8), h // 2, int(w * .2), h // 2), "right": (int(w * .2), h // 2, int(w * .8), h // 2)}
        if name == "dbl":
            self.act("tap", w // 2, h // 2)
            self.act("tap", w // 2, h // 2)
        else:
            self.act("swipe", *m[name], 300)

    def wake_unlock(self):
        if not self.need_phone():
            return
        w, h = self.view.size_phone
        self.adb.run("input keyevent 224; sleep 0.6; input swipe %d %d %d %d 300" % (w // 2, int(h * .85), w // 2, int(h * .25)))
        self.toast(tr("بیدار شد؛ اگر PIN دارد دستی وارد کن"))

    def rotate(self):
        if self.need_phone():
            self._rot = (self._rot + 1) % 4
            self.adb.run("settings put system accelerometer_rotation 0; settings put system user_rotation %d" % self._rot)

    def set_brightness(self, v):
        self._bright_val = v
        self.lbl_bright.setText(tr("روشنایی: %d٪") % round(v * 100 / 255))
        self._t_bright.start(180)

    def _apply_brightness(self):
        if self.adb:
            self.adb.run("settings put system screen_brightness_mode 0; settings put system screen_brightness %d" % self._bright_val)

    # ---- اسکرین‌شات و ضبط
    def quick_shot(self):
        if not self.view.last_png:
            return self.toast(tr("هنوز تصویری از گوشی نیامده"))
        fn = self.pb_dir("Pictures") / time.strftime("shot_%Y%m%d_%H%M%S.png")
        fn.write_bytes(self.view.last_png)
        self.toast(tr("ذخیره شد: %s") % fn)

    def copy_shot(self):
        if self.view.pix:
            QGuiApplication.clipboard().setPixmap(self.view.pix)
            self.toast(tr("تصویر در کلیپ‌بورد کپی شد"))
        else:
            self.toast(tr("هنوز تصویری نیست"))

    def toggle_record(self):
        if self.rec_proc is None:
            if not self.need_phone():
                return
            self.rec_remote = "/sdcard/pb_rec_%d.mp4" % int(time.time())
            try:
                self.rec_proc = subprocess.Popen(
                    self.adb.base + ["shell", "screenrecord", "--time-limit", "180", self.rec_remote],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **NOWIN)
            except Exception as e:
                return self.toast(tr("شروع ضبط ناموفق: %s") % e)
            self.rec_t0 = time.time()
            self._set_rec_ui(True)
            self.t_rec.start()
        else:
            self.stop_record(fetch=True)

    def _rec_tick(self):
        if self.rec_proc is None:
            return self.t_rec.stop()
        if self.rec_proc.poll() is not None:      # به سقف ۳ دقیقه رسید
            return self.stop_record(fetch=True)
        self.lbl_rec.setText(tr("در حال ضبط… %d ثانیه") % int(time.time() - self.rec_t0))

    def stop_record(self, fetch=True):
        proc, remote, a = self.rec_proc, self.rec_remote, self.adb
        if proc is None:
            return
        self.rec_proc = None
        self.t_rec.stop()
        self._set_rec_ui(False)
        if not (fetch and a):
            try:
                proc.terminate()
            except Exception:
                pass
            return
        self.lbl_rec.setText(tr("در حال پایان ضبط و انتقال به کامپیوتر…"))
        dest = self.pb_dir("Videos") / time.strftime("rec_%Y%m%d_%H%M%S.mp4")

        def work():
            if proc.poll() is None:
                a.sh("pkill -2 screenrecord || killall -2 screenrecord")
                try:
                    proc.wait(10)
                except Exception:
                    proc.kill()
            time.sleep(1.0)
            rc, out = a.pull(remote, str(dest))
            a.sh("rm -f %s" % shq(remote))
            return rc == 0 and dest.exists()

        def done(ok):
            self.lbl_rec.setText((tr("✅ ویدیو ذخیره شد: %s") % dest) if ok is True else tr("ضبط/انتقال ناموفق بود."))
            if ok is True:
                self.open_folder(dest.parent)
        self.bg(work, done)

    # ---- ماکرو
    def macro_toggle_rec(self):
        if self.macro_rec is None:
            if not self.need_phone():
                return
            self.macro_rec, self.macro_t0 = [], time.time()
            self.btn_mrec.setText(tr("پایان ضبط"))
            self.lbl_macro.setText(tr("در حال ضبط… کارها را روی صفحه انجام بده."))
        else:
            self.macro, self.macro_rec = self.macro_rec, None
            self.btn_mrec.setText(tr("شروع ضبط"))
            self.lbl_macro.setText(tr("%d عمل ضبط شد.") % len(self.macro))

    def macro_play(self):
        if not self.need_phone():
            return
        if not self.macro:
            return self.toast(tr("ماکرویی ضبط یا باز نشده"))
        if self._macro_thread and self._macro_thread.is_alive():
            return
        self._macro_stop.clear()
        loops, speed = self.sp_loops.value(), (0.5, 1.0, 2.0, 4.0)[self.cmb_mspeed.currentIndex()]
        evs, a = list(self.macro), self.adb

        def run():
            n = 0
            while not self._macro_stop.is_set():
                last = 0.0
                for e in evs:
                    end = time.time() + max(0.0, (e["t"] - last) / speed)
                    last = e["t"]
                    while time.time() < end and not self._macro_stop.is_set():
                        time.sleep(0.02)
                    if self._macro_stop.is_set():
                        break
                    getattr(a, e["k"])(*e["a"])
                n += 1
                ui(lambda n=n: self.lbl_macro.setText(tr("دور %d تمام شد") % n))
                if loops and n >= loops:
                    break
            ui(lambda: self.lbl_macro.setText(tr("پخش ماکرو تمام شد.")))
        self._macro_thread = threading.Thread(target=run, daemon=True)
        self._macro_thread.start()

    def macro_stop(self):
        self._macro_stop.set()

    def macro_save(self):
        if not self.macro:
            return self.toast(tr("ماکرویی برای ذخیره نیست"))
        fn, _ = QFileDialog.getSaveFileName(self, tr("ذخیره‌ی ماکرو"), str(Path.home() / "macro.json"), "Macro (*.json)")
        if fn:
            Path(fn).write_text(json.dumps(self.macro, ensure_ascii=False), "utf-8")
            self.toast(tr("ماکرو ذخیره شد"))

    def macro_load(self):
        fn, _ = QFileDialog.getOpenFileName(self, tr("باز کردن ماکرو"), str(Path.home()), "Macro (*.json)")
        if fn:
            try:
                self.macro = json.loads(Path(fn).read_text("utf-8"))
                self.lbl_macro.setText(tr("%d عمل بارگذاری شد.") % len(self.macro))
            except Exception as e:
                self.toast(tr("فایل ماکرو معتبر نیست: %s") % e)

    # ------------------------------------------------ تب ابزارها
    def _toggle_row(self, title, on_cmd, off_cmd):
        row = QHBoxLayout()
        lb = QLabel(title)
        lb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(lb, 1)
        row.addWidget(mk_btn(tr("روشن"), lambda: self.run_sh(on_cmd, title + tr(": روشن")), "primary"))
        row.addWidget(mk_btn(tr("خاموش"), lambda: self.run_sh(off_cmd, title + tr(": خاموش"))))
        return row

    def _tab_tools(self):
        inner = QWidget()
        cols = QHBoxLayout(inner)
        cols.setContentsMargins(0, 4, 0, 0)
        cols.setSpacing(14)
        left, right = QVBoxLayout(), QVBoxLayout()
        left.setSpacing(12)
        right.setSpacing(12)

        c, cl = mk_card(tr("تنظیمات سریع"))
        cl.addLayout(self._toggle_row("Wi-Fi", "svc wifi enable", "svc wifi disable"))
        cl.addLayout(self._toggle_row(tr("داده‌ی موبایل"), "svc data enable", "svc data disable"))
        cl.addLayout(self._toggle_row(tr("مزاحم نشوید"), "cmd notification set_dnd priority || settings put global zen_mode 1",
                                      "cmd notification set_dnd off || settings put global zen_mode 0"))
        cl.addLayout(self._toggle_row(tr("حالت تاریک"), "cmd uimode night yes", "cmd uimode night no"))
        cl.addLayout(self._toggle_row(tr("روشن ماندن صفحه (شارژ)"), "svc power stayon true", "svc power stayon false"))
        cl.addLayout(self._toggle_row(tr("نمایش لمس‌ها و مختصات"),
                                      "settings put system show_touches 1; settings put system pointer_location 1",
                                      "settings put system show_touches 0; settings put system pointer_location 0"))
        left.addWidget(c)

        c, cl = mk_card(tr("تنظیمات"))
        self.lbl_font = mk_label(tr("اندازه‌ی فونت: ۱٫۰×"), "Muted", False)
        cl.addWidget(self.lbl_font)
        self.sl_font = QSlider(Qt.Orientation.Horizontal)
        self.sl_font.setRange(8, 20)
        self.sl_font.setValue(10)
        self.sl_font.valueChanged.connect(lambda v: self.lbl_font.setText(tr("اندازه‌ی فونت: %.1f×") % (v / 10)))
        self.sl_font.sliderReleased.connect(
            lambda: self.run_sh("settings put system font_scale %.1f" % (self.sl_font.value() / 10), tr("اندازه‌ی فونت تغییر کرد")))
        cl.addWidget(self.sl_font)
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("خاموشی خودکار صفحه:")), 1)
        self.cmb_timeout = QComboBox()
        for lbl, ms in ((tr("۱۵ ثانیه"), 15000), (tr("۳۰ ثانیه"), 30000), (tr("۱ دقیقه"), 60000), (tr("۲ دقیقه"), 120000),
                        (tr("۵ دقیقه"), 300000), (tr("۱۰ دقیقه"), 600000), (tr("۳۰ دقیقه"), 1800000)):
            self.cmb_timeout.addItem(lbl, ms)
        self.cmb_timeout.activated.connect(lambda i: self.run_sh(
            "settings put system screen_off_timeout %d" % self.cmb_timeout.itemData(i), tr("زمان خاموشی تغییر کرد")))
        row.addWidget(self.cmb_timeout)
        cl.addLayout(row)
        row = QHBoxLayout()
        self.cmb_set = QComboBox()
        for lbl, act in (("Wi-Fi", "WIFI_SETTINGS"), (tr("بلوتوث"), "BLUETOOTH_SETTINGS"), (tr("نمایشگر"), "DISPLAY_SETTINGS"),
                         (tr("صدا"), "SOUND_SETTINGS"), (tr("باتری"), "BATTERY_SAVER_SETTINGS"),
                         (tr("حافظه"), "INTERNAL_STORAGE_SETTINGS"), (tr("برنامه‌ها"), "APPLICATION_SETTINGS"),
                         (tr("گزینه‌های توسعه‌دهنده"), "APPLICATION_DEVELOPMENT_SETTINGS"),
                         (tr("دسترس‌پذیری"), "ACCESSIBILITY_SETTINGS"), (tr("موقعیت مکانی"), "LOCATION_SOURCE_SETTINGS"),
                         (tr("زبان"), "LOCALE_SETTINGS"), (tr("درباره‌ی گوشی"), "DEVICE_INFO_SETTINGS")):
            self.cmb_set.addItem(lbl, act)
        row.addWidget(self.cmb_set, 1)
        row.addWidget(mk_btn(tr("باز کردن تنظیمات"), lambda: self.run_sh(
            "am start -a android.settings.%s" % self.cmb_set.currentData(), tr("تنظیمات باز شد"))))
        cl.addLayout(row)
        left.addWidget(c)

        c, cl = mk_card(tr("نگهداری"))
        cl.addWidget(mk_btn(tr("بستن برنامه‌های پس‌زمینه"), lambda: self.run_sh("am kill-all", tr("برنامه‌های پس‌زمینه بسته شدند"))))
        cl.addWidget(mk_btn(tr("پاک کردن کش همه‌ی برنامه‌ها"), lambda: self.run_sh("pm trim-caches 999999999999",
                                                                          tr("کش پاک شد (روی بعضی گوشی‌ها محدود است)"))))
        left.addWidget(c)
        left.addStretch(1)

        c, cl = mk_card(tr("ارسال به گوشی"))
        self.ed_url = ltr(QLineEdit())
        self.ed_url.setPlaceholderText("https://example.com")
        self.ed_url.returnPressed.connect(self.open_url)
        cl.addWidget(mk_label(tr("باز کردن لینک در مرورگر گوشی:"), "Muted"))
        row = QHBoxLayout()
        row.addWidget(self.ed_url, 1)
        row.addWidget(mk_btn(tr("باز کن"), self.open_url, "primary"))
        cl.addLayout(row)
        cl.addWidget(mk_label(tr("شماره‌گیری / پیامک:"), "Muted"))
        self.ed_tel = ltr(QLineEdit())
        self.ed_tel.setPlaceholderText("0912…")
        cl.addWidget(self.ed_tel)
        self.ed_sms = QLineEdit()
        self.ed_sms.setPlaceholderText(tr("متن پیامک (اختیاری)"))
        cl.addWidget(self.ed_sms)
        row = QHBoxLayout()
        row.addWidget(mk_btn(tr("شماره‌گیری"), self.dial))
        row.addWidget(mk_btn(tr("ساخت پیامک"), self.sms))
        cl.addLayout(row)
        right.addWidget(c)

        c, cl = mk_card(tr("عکس بگیر و بیاور"))
        cl.addWidget(mk_label(tr("دوربین گوشی را باز می‌کند، عکس می‌گیرد و همان لحظه به کامپیوتر می‌آورد. "
                              "اگر عکس نگرفت، شاتر را روی تصویر کلیک کن و «آخرین عکس را بیاور» را بزن."), "Muted"))
        cl.addWidget(mk_btn(tr("عکس بگیر و بیاور"), self.capture_photo, "primary"))
        cl.addWidget(mk_btn(tr("آخرین عکس گوشی را بیاور"), lambda: self.fetch_last_photo(False)))
        right.addWidget(c)
        right.addStretch(1)

        lw, rw = QWidget(), QWidget()
        lw.setLayout(left)
        rw.setLayout(right)
        cols.addWidget(lw, 1)
        cols.addWidget(rw, 1)
        return scroll_wrap(inner)

    def open_url(self):
        u = self.ed_url.text().strip()
        if u:
            if "://" not in u:
                u = "https://" + u
            self.run_sh("am start -a android.intent.action.VIEW -d %s" % shq(u), tr("لینک روی گوشی باز شد"))

    def dial(self):
        n = self.ed_tel.text().strip()
        if n:
            self.run_sh("am start -a android.intent.action.DIAL -d %s" % shq("tel:" + n), tr("شماره‌گیر باز شد"))

    def sms(self):
        n = self.ed_tel.text().strip()
        if n:
            self.run_sh("am start -a android.intent.action.SENDTO -d %s --es sms_body %s" % (
                shq("sms:" + n), shq(self.ed_sms.text())), tr("پیامک آماده شد (ارسال با خودت)"))

    def capture_photo(self):
        self.fetch_last_photo(True)

    def fetch_last_photo(self, shoot):
        if not self.need_phone():
            return
        a = self.adb
        dest_dir = self.pb_dir("Pictures")
        self.toast(tr("در حال گرفتن عکس…") if shoot else tr("در حال آوردن آخرین عکس…"), 8000)

        def newest():
            return a.sh("ls -t /sdcard/DCIM/Camera/ 2>/dev/null | head -n 1").strip()

        def work():
            before = newest()
            if shoot:
                a.sh("am start -a android.media.action.STILL_IMAGE_CAMERA")
                time.sleep(2.5)
                a.sh("input keyevent 27")
                time.sleep(3.5)
            name = newest()
            if not name or (shoot and name == before):
                return None
            dest = dest_dir / name
            return dest if a.pull("/sdcard/DCIM/Camera/" + name, str(dest))[0] == 0 else None

        def done(r):
            if isinstance(r, Path):
                self.toast(tr("عکس آمد: %s") % r)
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(r)))
            else:
                self.toast(tr("عکس جدیدی پیدا نشد؛ شاتر را دستی بزن و «آخرین عکس» را بگیر."))
        self.bg(work, done)

    # ------------------------------------------------ تب اطلاعات
    def _tab_info(self):
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(14)

        c, cl = mk_card(tr("مشخصات دستگاه"))
        g = QGridLayout()
        g.setHorizontalSpacing(14)
        g.setVerticalSpacing(7)
        self.info_vals = {}
        for i, (k, lbl) in enumerate((("model", tr("مدل")), ("brand", tr("سازنده")), ("android", tr("نسخه‌ی اندروید")), ("sdk", "API"),
                                      ("abi", tr("معماری CPU")), ("patch", tr("وصله‌ی امنیتی")), ("res", tr("رزولوشن")),
                                      ("dens", tr("تراکم")), ("ram", "RAM"), ("disk", tr("حافظه‌ی داخلی")), ("ip", "IP"),
                                      ("serial", tr("سریال")), ("build", tr("نسخه‌ی سیستم")))):
            g.addWidget(mk_label(lbl + ":", "Muted", False), i, 0)
            v = ltr(mk_label("—", None, False))
            v.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            g.addWidget(v, i, 1)
            self.info_vals[k] = v
        g.setColumnStretch(1, 1)
        cl.addLayout(g)
        row = QHBoxLayout()
        row.addWidget(mk_btn(tr("تازه‌سازی"), self.refresh_info, "primary"))
        row.addWidget(mk_btn(tr("ذخیره‌ی گزارش"), self.save_info))
        cl.addLayout(row)
        cl.addStretch(1)
        lay.addWidget(c, 1)

        col = QVBoxLayout()
        col.setSpacing(12)
        c, cl = mk_card(tr("باتری"))
        self.gauge = Gauge()
        cl.addWidget(self.gauge)
        col.addWidget(c)
        c, cl = mk_card(tr("پایش زنده (هر ۳ ثانیه)"))
        self.chk_mon = QCheckBox(tr("پایش باتری و RAM"))
        self.chk_mon.setChecked(True)
        cl.addWidget(self.chk_mon)
        self.spark = Sparkline()
        cl.addWidget(self.spark)
        col.addWidget(c)
        c, cl = mk_card(tr("تست اینترنت گوشی (ping)"))
        row = QHBoxLayout()
        self.ed_ping = ltr(QLineEdit("8.8.8.8"))
        row.addWidget(self.ed_ping, 1)
        row.addWidget(mk_btn(tr("تست"), self.ping, "primary"))
        cl.addLayout(row)
        self.lbl_ping = ltr(mk_label("—", "Muted"))
        cl.addWidget(self.lbl_ping)
        col.addWidget(c)
        col.addStretch(1)
        cw = QWidget()
        cw.setLayout(col)
        lay.addWidget(cw, 1)
        return scroll_wrap(w)

    def refresh_info(self):
        if not self.adb:
            return
        a = self.adb
        cmd = ("echo model=$(getprop ro.product.model); echo brand=$(getprop ro.product.manufacturer); "
               "echo android=$(getprop ro.build.version.release); echo sdk=$(getprop ro.build.version.sdk); "
               "echo abi=$(getprop ro.product.cpu.abi); echo patch=$(getprop ro.build.version.security_patch); "
               "echo serial=$(getprop ro.serialno); echo build=$(getprop ro.build.display.id); "
               "wm size; wm density; grep -E 'MemTotal|MemAvailable' /proc/meminfo; echo '==DF'; df /data | tail -n 1; "
               "echo '==IP'; ip route; echo '==BAT'; dumpsys battery")
        self.bg(lambda: a.sh(cmd, 40), self._fill_info)

    def _fill_info(self, out):
        if isinstance(out, Exception):
            return
        v, kv = self.info_vals, {}
        for l in out.splitlines():
            m = re.match(r"^(model|brand|android|sdk|abi|patch|serial|build)=(.*)$", l.strip())
            if m:
                kv[m.group(1)] = m.group(2)
        for k, val in kv.items():
            v[k].setText(val or "—")
        m = re.search(r"Physical size:\s*(\S+)", out)
        v["res"].setText(m.group(1) if m else "—")
        m = re.search(r"Physical density:\s*(\d+)", out)
        v["dens"].setText(m.group(1) + " dpi" if m else "—")
        tot = re.search(r"MemTotal:\s+(\d+)", out)
        av = re.search(r"MemAvailable:\s+(\d+)", out)
        if tot and av:
            t, f = int(tot.group(1)) * 1024, int(av.group(1)) * 1024
            v["ram"].setText(tr("%s  (آزاد: %s)") % (human(t), human(f)))
        m = re.search(r"==DF\s*\n\S+\s+(\d+)\s+(\d+)\s+(\d+)", out)
        if m:
            v["disk"].setText(tr("%s  (استفاده‌شده: %s)") % (human(int(m.group(1)) * 1024), human(int(m.group(2)) * 1024)))
        m = re.search(r"wlan\d.*src (\d+\.\d+\.\d+\.\d+)", out) or re.search(r"src (\d+\.\d+\.\d+\.\d+)", out)
        v["ip"].setText(m.group(1) if m else "—")
        self._fill_battery(out)

    def _fill_battery(self, out):
        lv = re.search(r"level:\s*(\d+)", out)
        if not lv:
            return
        tp = re.search(r"temperature:\s*(\d+)", out)
        st = re.search(r"status:\s*(\d+)", out)
        names = {"2": tr("در حال شارژ "), "3": tr("در حال مصرف"), "4": tr("شارژ نمی‌شود"), "5": tr("پر")}
        sub = ""
        if tp:
            sub += "%.1f°C  " % (int(tp.group(1)) / 10)
        if st:
            sub += names.get(st.group(1), "")
        self.gauge.set_value(int(lv.group(1)), sub)
        return int(lv.group(1))

    def _monitor_tick(self):
        if not (self.adb and self.chk_mon.isChecked() and not self._mon_busy):
            return
        a, self._mon_busy = self.adb, True

        def done(out):
            self._mon_busy = False
            if isinstance(out, Exception):
                return
            lv = self._fill_battery(out)
            if lv is not None:
                self.spark.push(tr("باتری"), lv)
            tot = re.search(r"MemTotal:\s+(\d+)", out)
            av = re.search(r"MemAvailable:\s+(\d+)", out)
            if tot and av:
                self.spark.push("RAM", 100 - int(av.group(1)) * 100 / int(tot.group(1)))
        self.bg(lambda: a.sh("dumpsys battery | grep -E 'level|temperature|status'; grep -E 'MemTotal|MemAvailable' /proc/meminfo"), done)

    def save_info(self):
        fn, _ = QFileDialog.getSaveFileName(self, tr("ذخیره"), str(Path.home() / "phone_info.txt"), "Text (*.txt)")
        if fn:
            Path(fn).write_text("\n".join("%s: %s" % (k, w.text()) for k, w in self.info_vals.items()), "utf-8")
            self.toast(tr("گزارش ذخیره شد: ") + fn)

    def ping(self):
        if not self.need_phone():
            return
        a, host = self.adb, self.ed_ping.text().strip() or "8.8.8.8"
        self.lbl_ping.setText(tr("در حال تست…"))

        def done(out):
            if isinstance(out, Exception):
                return self.lbl_ping.setText(str(out))
            m = re.search(r"=\s*([\d.]+)/([\d.]+)/([\d.]+)", out)
            if m:
                self.lbl_ping.setText(tr("✅ میانگین %s ms   (کمینه %s / بیشینه %s)") % (m.group(2), m.group(1), m.group(3)))
            else:
                self.lbl_ping.setText(tr("❌ پاسخی نیامد:\n") + out[-160:])
        self.bg(lambda: a.sh("ping -c 4 -W 2 %s" % shq(host), 30), done)

    # ------------------------------------------------ تب توسعه
    def _tab_dev(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 4, 0, 0)
        card, cl = mk_card()
        inner = QTabWidget()
        self.logcat, self.terminal = LogcatPane(self), TerminalPane(self)
        inner.addTab(self.logcat, tr("Logcat زنده"))
        inner.addTab(self.terminal, tr("ترمینال adb"))
        cl.addWidget(inner)
        lay.addWidget(card)
        return w

    # ------------------------------------------------ فایل‌ها: ارسال و نصب
    def install_apk_dialog(self):
        fns, _ = QFileDialog.getOpenFileNames(self, tr("APK را انتخاب کن"), str(Path.home() / "Downloads"), "APK (*.apk)")
        if fns:
            self.push_files(fns)

    def push_files(self, paths, remote="/sdcard/Download/"):
        if not self.need_phone():
            return
        paths = [p for p in paths if os.path.exists(p)]
        if not paths:
            return
        a = self.adb
        self.toast(tr("در حال انتقال %d مورد…") % len(paths), 0)

        def work():
            res = []
            for p in paths:
                if p.lower().endswith(".apk"):
                    rc, out = a.install(p)
                    res.append((tr("نصب ") + os.path.basename(p), "success" in out.lower(), out.strip().splitlines()[-1] if out else ""))
                else:
                    rc, out = a.push(p, remote)
                    res.append((tr("ارسال ") + os.path.basename(p), rc == 0, out.strip().splitlines()[-1] if out else ""))
            return res

        def done(r):
            if isinstance(r, Exception):
                return self.toast(tr("انتقال ناموفق: %s") % r)
            ok = sum(1 for x in r if x[1])
            for name, good, msg in r:
                self.adb_log("%s %s  %s" % ("✅" if good else "❌", name, msg))
            self.toast(tr("✅ %d از %d مورد انجام شد") % (ok, len(r)))
            if self.files.path.startswith(remote):
                self.files.refresh()
            self.apps.refresh()
        self.bg(work, done)

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e):
        self.push_files([u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()])

    # ------------------------------------------------ ریموت PC (سرور)
    def _server_cards(self, left):
        c, cl = mk_card(tr("دسترسی‌های ریموت (برای امنیت پیش‌فرض خاموش)"))
        self.chk_scr = QCheckBox(tr("نمایش و کنترل صفحه‌ی کامپیوتر از گوشی"))
        self.chk_scr.toggled.connect(self.on_allow_screen)
        self.chk_sys = QCheckBox(tr("دستورهای سیستمی (قفل / خواب / خاموشی)"))
        self.chk_sys.toggled.connect(lambda v: (setattr(self.server, "allow_system", v),
                                                self.log_server("info", tr("دستورهای سیستمی ") + (tr("فعال شد") if v else tr("غیرفعال شد")))))
        cl.addWidget(self.chk_scr)
        cl.addWidget(self.chk_sys)
        cl.addWidget(mk_label(tr("صفحه‌ی وب گوشی ۸ بخش دارد: تایپ، موس، ارائه، رسانه، میانبر، صفحه‌ی PC، کلیپ‌بورد، سیستم."), "Muted"))
        left.addWidget(c)

        c, cl = mk_card(tr("ارسال متن یا لینک از کامپیوتر به گوشی"))
        self.ed_inbox = QTextEdit()
        self.ed_inbox.setFixedHeight(80)
        self.ed_inbox.setPlaceholderText(tr("متن یا لینک… (در صفحه‌ی وب گوشی نمایش داده می‌شود)"))
        cl.addWidget(self.ed_inbox)
        cl.addWidget(mk_btn(tr("ارسال به صفحه‌ی گوشی"), self.send_inbox, "primary"))
        left.addWidget(c)

    def on_allow_screen(self, v):
        self.server.allow_screen = v
        self.log_server("info", tr("نمایش صفحه‌ی PC ") + (tr("فعال شد") if v else tr("غیرفعال شد")))

    def send_inbox(self):
        t = self.ed_inbox.toPlainText().strip()
        if t and self.server.running:
            self.server.send_to_phone(t)
            self.log_server("ok", tr("متن برای گوشی ارسال شد"))
        else:
            self.toast(tr("سرور روشن نیست یا متن خالی است"))

    def _frame_tick(self):
        s = self.server
        if not (s.running and s.allow_screen and time.time() - s.last_frame_req < 6):
            return
        pm = QGuiApplication.primaryScreen().grabWindow(0)
        if pm.isNull():
            return
        W, H = pm.width(), pm.height()
        small = pm.scaledToWidth(min(1000, W), Qt.TransformationMode.FastTransformation)
        ba = QByteArray()
        buf = QBuffer(ba)
        buf.open(QIODevice.OpenModeFlag.WriteOnly)
        small.save(buf, "JPEG", 55)
        s.frame = (bytes(ba), W, H)

    # ------------------------------------------------ سینی سیستم، اتصال مجدد
    def _setup_tray(self):
        self.tray = None
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(app_icon(), self)
        menu = QMenu()
        menu.addAction(tr("نمایش / مخفی کردن"), lambda: self.setVisible(not self.isVisible()))
        menu.addAction(tr("اسکرین‌شات سریع"), self.quick_shot)
        menu.addSeparator()
        menu.addAction(tr("خروج"), self._quit)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda r: self.setVisible(True) if r == QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.setToolTip(tr("پل گوشی ↔ کامپیوتر"))
        self.tray.show()

    def _quit(self):
        self._quitting = True
        self.close()
        QApplication.quit()

    def _settings_card(self, left):
        c, cl = mk_card(tr("تنظیمات برنامه"))
        self.chk_tray = QCheckBox(tr("هنگام بستن پنجره، در سینی سیستم بماند"))
        self.chk_tray.setChecked(bool(self.cfg.get("tray", False)))
        self.chk_tray.toggled.connect(lambda v: (self.cfg.update(tray=v), save_cfg(self.cfg)))
        self.chk_reco = QCheckBox(tr("اتصال خودکار مجدد وقتی گوشی قطع شد"))
        self.chk_reco.setChecked(bool(self.cfg.get("reconnect", True)))
        self.chk_reco.toggled.connect(lambda v: (self.cfg.update(reconnect=v), save_cfg(self.cfg)))
        cl.addWidget(self.chk_tray)
        cl.addWidget(self.chk_reco)
        cl.addWidget(mk_label("Phone Bridge  v%s  ·  MIT" % __version__, "Muted", False))
        left.addWidget(c)

    def _watchdog(self):
        if self.adb and self.adb.proc.poll() is not None:        # shell گوشی قطع شده
            self.disconnect_phone(silent=True)
            self.adb_log(tr("⚠ ارتباط با گوشی قطع شد."))
            self.toast(tr("ارتباط با گوشی قطع شد") + (tr("؛ تلاش برای اتصال مجدد…") if self.chk_reco.isChecked() else ""))
        if (self.adb is None and self.last_serial is not None and self.adb_path and self.chk_reco.isChecked()
                and not self._reconnecting and self.cmb_dev is not None):
            self._reconnecting = True
            ser, exe = self.last_serial, self.adb_path

            def work():
                if ":" in ser:
                    adb_cmd(exe, ["connect", ser], 10)
                return Adb(exe, ser)

            def done(r):
                self._reconnecting = False
                if isinstance(r, Adb) and self.adb is None:
                    self._connected(r, quiet=True)
                    self.toast(tr("✅ اتصال مجدد برقرار شد"))
                elif isinstance(r, Adb):
                    r.close()
            self.bg(work, done)


def ui_get(fn, timeout=3.0):
    """اجرای fn در نخ اصلی و برگرداندن نتیجه (برای سرور)."""
    ev, box = threading.Event(), [None]

    def run():
        try:
            box[0] = fn()
        finally:
            ev.set()
    ui(run)
    ev.wait(timeout)
    return box[0]


# =============================
# پنجره‌ی اصلی
# =============================
class MainWindow(FeaturesMixin, QMainWindow):
    def __init__(self):
        super().__init__()
        self.cfg = load_cfg()
        self.theme = self.cfg.get("theme", "dark")
        self.adb_path = find_adb(self.cfg.get("adb_path"))
        self.adb = None
        self.grabber = None
        self.server = PhoneKeyboardServer(self.server_event)
        self.setWindowTitle(tr("پل گوشی ↔ کامپیوتر"))
        self.resize(1240, 860)

        root = Root()
        root.setObjectName("Root")
        self.setCentralWidget(root)
        outer = QVBoxLayout(root)
        outer.setContentsMargins(18, 16, 18, 10)
        outer.setSpacing(12)

        # ---- هدر مینیمال ----
        head = QWidget()
        hl = QHBoxLayout(head)
        hl.setContentsMargins(4, 0, 4, 0)
        hl.setSpacing(10)
        tl = QVBoxLayout()
        tl.setSpacing(0)
        tl.addWidget(mk_label(tr("پل گوشی ↔ کامپیوتر"), "Brand", False))
        tl.addWidget(mk_label(tr("موس و کیبورد کامپیوتر برای گوشی، کیبورد گوشی برای کامپیوتر"), "BrandSub", False))
        hl.addLayout(tl, 1)
        self.pill_phone = QLabel(tr("گوشی: قطع"))
        self.pill_phone.setObjectName("Pill")
        self.pill_srv = QLabel(tr("سرور کیبورد: خاموش"))
        self.pill_srv.setObjectName("Pill")
        hl.addWidget(self.pill_phone)
        hl.addWidget(self.pill_srv)
        self.btn_lang = mk_btn("EN" if LANG == "fa" else tr("فا"), self.switch_language, tip=tr("تغییر زبان  /  Language"), name="Round")
        hl.addWidget(self.btn_lang)
        self.btn_theme = mk_btn("", self.toggle_theme, tip=tr("تغییر تم تیره/روشن"), name="Round")
        self.btn_theme.setIconSize(QSize(20, 20))
        hl.addWidget(self.btn_theme)
        outer.addWidget(head)

        # ---- تب‌ها ----
        self.tabs = QTabWidget()
        self.tabs.tabBar().setExpanding(False)
        self.files, self.apps = FileManager(self), AppManager(self)
        self.tab_connect_w = self._tab_connect()
        self.tabs.addTab(self._tab_control(), tr("کنترل"))
        self.tabs.addTab(self._tab_keyboard(), tr("کیبورد و ریموت PC"))
        self.tabs.addTab(self._tab_tools(), tr("ابزارها"))
        self.tabs.addTab(self._tab_info(), tr("اطلاعات"))
        self.tabs.addTab(self.files, tr("فایل‌ها"))
        self.tabs.addTab(self.apps, tr("برنامه‌ها"))
        self.tabs.addTab(self._tab_dev(), tr("توسعه"))
        self.tabs.addTab(self.tab_connect_w, tr("اتصال"))
        outer.addWidget(self.tabs, 1)
        self.statusBar().showMessage(tr("آماده"))

        self.apply_theme()
        self.start_server()
        if self.adb_path:
            self.refresh_devices(auto=True)
        else:
            self.tabs.setCurrentWidget(self.tab_connect_w)
            self.adb_log(tr("ابزار adb پیدا نشد. «دانلود خودکار adb» را بزنید یا adb.exe را دستی انتخاب کنید."))
        self.update_adb_label()
        self._init_features()

    # ================= تب ۲ =================
    def _tab_keyboard(self):
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(14)

        left = QVBoxLayout()
        left.setSpacing(12)
        c, cl = mk_card(tr("آدرس برای مرورگر گوشی"))
        cl.addWidget(mk_label(tr("این آدرس را در مرورگر گوشی (همان وای‌فای) باز کن. هرچه با کیبورد گوشی تایپ کنی، "
                              "روی کامپیوتر — همان‌جا که مکان‌نما هست — تایپ می‌شود."), "Muted"))
        self.lbl_url = ltr(mk_label("—", "Url"))
        self.lbl_url.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.lbl_url.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self.lbl_url)
        row = QHBoxLayout()
        self.btn_srv = mk_btn(tr("روشن/خاموش کردن سرور"), self.toggle_server, "primary")
        row.addWidget(self.btn_srv)
        row.addWidget(mk_btn(tr("کپی آدرس"), self.copy_url))
        row.addWidget(mk_btn(tr("توکن جدید"), self.new_token, tip=tr("آدرس قبلی از کار می‌افتد")))
        cl.addLayout(row)
        row = QHBoxLayout()
        row.addWidget(QLabel(tr("پورت:")))
        self.sp_port = QSpinBox()
        self.sp_port.setRange(1024, 65535)
        self.sp_port.setValue(int(self.cfg.get("port", 8765)))
        self.sp_port.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.sp_port.setFixedWidth(90)
        row.addWidget(self.sp_port)
        row.addStretch(1)
        cl.addLayout(row)
        self.lbl_qr = QLabel()
        self.lbl_qr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cl.addWidget(self.lbl_qr)
        left.addWidget(c)

        c, cl = mk_card(tr("امنیت"))
        cl.addWidget(mk_label(tr("آدرس یک توکن تصادفی دارد و فقط کسی که آن را دارد می‌تواند روی کامپیوتر تایپ کند. "
                              "اگر فایروال ویندوز پرسید، Python را روی «شبکه‌ی خصوصی» مجاز کن."), "Muted"))
        left.addWidget(c)
        self._server_cards(left)
        left.addStretch(1)
        lw = QWidget()
        lw.setLayout(left)
        lay.addWidget(scroll_wrap(lw), 1)

        c, cl = mk_card(tr("رویدادها"))
        self.lst_log = QListWidget()
        cl.addWidget(self.lst_log, 1)
        cl.addWidget(mk_btn(tr("پاک کردن"), self.lst_log.clear))
        lay.addWidget(c, 1)
        return w

    # ================= تب ۳ =================
    def _tab_connect(self):
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 4, 0, 0)
        lay.setSpacing(14)

        left = QVBoxLayout()
        left.setSpacing(12)

        c, cl = mk_card(tr("۱) ابزار adb"))
        self.lbl_adb = ltr(mk_label("", "Muted"))
        cl.addWidget(self.lbl_adb)
        row = QHBoxLayout()
        row.addWidget(mk_btn(tr("پیدا کردن خودکار"), self.auto_find_adb))
        row.addWidget(mk_btn(tr("انتخاب adb.exe"), self.pick_adb))
        cl.addLayout(row)
        cl.addWidget(mk_btn(tr("دانلود خودکار adb (حدود ۷ مگابایت)"), self.download_adb, "primary"))
        self.bar_dl = QProgressBar()
        self.bar_dl.setVisible(False)
        cl.addWidget(self.bar_dl)
        cl.addWidget(mk_btn(tr("باز کردن صفحه‌ی دانلود در مرورگر"), lambda: webbrowser.open(
            "https://developer.android.com/tools/releases/platform-tools")))
        left.addWidget(c)

        c, cl = mk_card(tr("۲) اتصال به گوشی"))
        row = QHBoxLayout()
        self.cmb_dev = ltr(QComboBox())
        self.cmb_dev.setMinimumWidth(180)
        row.addWidget(self.cmb_dev, 1)
        row.addWidget(icon_round("refresh", tr("تازه‌سازی لیست"), self.refresh_devices))
        cl.addLayout(row)
        cl.addWidget(mk_btn(tr("✅ اتصال به دستگاه انتخاب‌شده"), self.connect_selected, "primary"))
        cl.addWidget(mk_btn(tr("قطع اتصال"), self.disconnect_phone))
        cl.addWidget(mk_label(tr("— اتصال بی‌سیم (IP:پورت از Wireless debugging گوشی) —"), "Muted"))
        row = QHBoxLayout()
        self.ed_ip = ltr(QLineEdit(self.cfg.get("last_ip", "")))
        self.ed_ip.setPlaceholderText("192.168.1.20:5555")
        row.addWidget(self.ed_ip, 1)
        row.addWidget(mk_btn(tr("اتصال"), self.wifi_connect))
        cl.addLayout(row)
        row = QHBoxLayout()
        self.ed_pair = ltr(QLineEdit())
        self.ed_pair.setPlaceholderText(tr("IP:پورت جفت‌سازی"))
        self.ed_code = ltr(QLineEdit())
        self.ed_code.setPlaceholderText(tr("کد ۶ رقمی"))
        self.ed_code.setMaximumWidth(110)
        row.addWidget(self.ed_pair, 1)
        row.addWidget(self.ed_code)
        row.addWidget(mk_btn(tr("جفت‌سازی"), self.wifi_pair))
        cl.addLayout(row)
        cl.addWidget(mk_btn(tr("با کابل USB وصل است؛ تبدیل به وای‌فای"), self.usb_to_wifi,
                            tip=tr("یک‌بار با کابل، بعد بی‌سیم")))
        left.addWidget(c)
        self._settings_card(left)
        left.addStretch(1)
        lw = QWidget()
        lw.setLayout(left)
        lay.addWidget(scroll_wrap(lw, 470))

        right = QVBoxLayout()
        right.setSpacing(12)
        c, cl = mk_card(tr("اتصال سریع با QR  (اندروید ۱۱ به بالا)"))
        row = QHBoxLayout()
        row.setSpacing(14)
        self.lbl_pairqr = QLabel(tr("برای شروع «ساخت QR» را بزن"))
        self.lbl_pairqr.setObjectName("Muted")
        self.lbl_pairqr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_pairqr.setFixedSize(250, 250)
        self.lbl_pairqr.setStyleSheet("border:1px dashed #3C4766; border-radius:12px;")
        row.addWidget(self.lbl_pairqr)
        info = QVBoxLayout()
        info.setSpacing(8)
        info.addWidget(mk_label(
            tr("۱. گوشی و کامپیوتر به یک وای‌فای باشند.\n"
            "۲. روی گوشی: تنظیمات ← گزینه‌های توسعه‌دهنده ← Wireless debugging\u200f را روشن کن.\n"
            "۳. گزینه‌ی Pair device with QR code\u200f را بزن و این QR را اسکن کن. "
            "(با دوربین معمولی گوشی کار نمی‌کند.)\n"
            "۴. بقیه خودکار است: جفت‌سازی، اتصال و نمایش صفحه."), "Muted"))
        self.lbl_qr_status = QLabel(tr("آماده"))
        self.lbl_qr_status.setObjectName("Pill")
        self.lbl_qr_status.setWordWrap(True)
        info.addWidget(self.lbl_qr_status)
        self.btn_qr = mk_btn(tr("ساخت QR و شروع"), self.start_qr_pair, "primary")
        info.addWidget(self.btn_qr)
        info.addWidget(mk_btn(tr("لغو"), self.cancel_qr))
        info.addStretch(1)
        row.addLayout(info, 1)
        cl.addLayout(row)
        right.addWidget(c)
        c, cl = mk_card(tr("گزارش adb"))
        self.log_adb = QTextEdit()
        self.log_adb.setReadOnly(True)
        self.log_adb.setMinimumHeight(120)
        ltr(self.log_adb)
        cl.addWidget(self.log_adb, 1)
        right.addWidget(c, 1)
        rw = QWidget()
        rw.setLayout(right)
        lay.addWidget(rw, 5)
        return w

    # ================= تم =================
    def apply_theme(self):
        global CUR
        CUR = THEMES[self.theme]
        QApplication.instance().setStyleSheet(build_qss(CUR, make_icons(CUR)))
        self.btn_theme.setIcon(make_icon("sun" if self.theme == "dark" else "moon", size=20))
        self.refresh_icons()
        self.centralWidget().update()
        self.view.update()
        self.update_pills()

    def switch_language(self):
        """زبان را عوض می‌کند و برنامه را دوباره اجرا می‌کند (همه‌ی متن‌ها از نو ساخته می‌شوند)."""
        self.cfg["lang"] = "en" if LANG == "fa" else "fa"
        save_cfg(self.cfg)
        self._quitting = True
        self.cancel_qr(silent=True)
        self.disconnect_phone(silent=True)
        self.server.stop()
        try:
            subprocess.Popen(_restart_argv(), **NOWIN)
        except Exception as e:
            self.toast("Restart failed: %s" % e)
            return
        QApplication.quit()

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.cfg["theme"] = self.theme
        save_cfg(self.cfg)
        self.apply_theme()

    def update_pills(self):
        ok = self.adb is not None
        self.pill_phone.setText(tr("گوشی: متصل ✓") if ok else tr("گوشی: قطع"))
        set_state(self.pill_phone, "ok" if ok else "warn")
        on = self.server.running
        self.pill_srv.setText(tr("سرور کیبورد: روشن ✓") if on else tr("سرور کیبورد: خاموش"))
        set_state(self.pill_srv, "ok" if on else "warn")

    # ================= اعمال گوشی =================
    def phone_cmd(self, cmd):
        if self.adb:
            self.adb.run(cmd)

    def send_text_to_phone(self, t):
        if not self.adb:
            return
        if all(ord(ch) < 128 for ch in t):
            self.act("text", t)
        elif self.chk_adbkb.isChecked():
            self.adb.text_unicode(t)
        else:
            self.statusBar().showMessage(
                tr("حروف غیرانگلیسی با adb تایپ نمی‌شود؛ ADBKeyboard را نصب و تیک گزینه را بزن، یا از تب «کیبورد گوشی» استفاده کن."),
                7000)

    def send_line(self):
        t = self.ed_send.text()
        if t:
            self.send_text_to_phone(t)
            self.ed_send.clear()

    def on_live(self, v):
        if self.grabber:
            self.grabber.live = v

    def on_speed(self, i):
        if self.grabber:
            self.grabber.interval = (0.25, 0.5, 1.0)[i]

    def on_view_message(self, m):
        self.view_note.setText(m if self.view.pix else "")
        self.view_note.setVisible(bool(m) and bool(self.view.pix))
        if m and not self.view.pix:
            self.statusBar().showMessage(m.replace("\n", " "), 6000)

    def save_shot(self):
        if not self.view.last_png:
            return self.statusBar().showMessage(tr("هنوز تصویری نیست"), 3000)
        fn, _ = QFileDialog.getSaveFileName(self, tr("ذخیره"), str(Path.home() / "phone_screenshot.png"), "PNG (*.png)")
        if fn:
            Path(fn).write_bytes(self.view.last_png)
            self.statusBar().showMessage(tr("ذخیره شد: ") + fn, 4000)

    # ================= adb =================
    def adb_log(self, s):
        self.log_adb.append(s)

    def update_adb_label(self):
        self.lbl_adb.setText(("✅ " + self.adb_path) if self.adb_path else tr("❌ adb پیدا نشد"))

    def auto_find_adb(self):
        p = find_adb(self.cfg.get("adb_path"))
        if p:
            self.set_adb_path(p)
            self.refresh_devices()
        else:
            self.adb_log(tr("adb پیدا نشد. دانلود خودکار را بزنید یا adb.exe را دستی انتخاب کنید."))

    def pick_adb(self):
        fn, _ = QFileDialog.getOpenFileName(self, tr("adb.exe را انتخاب کنید"), str(Path.home() / "Downloads"),
                                            tr("adb (adb.exe adb);;همه (*)"))
        if fn:
            self.set_adb_path(fn)
            self.refresh_devices()

    def set_adb_path(self, p):
        self.adb_path = p
        self.cfg["adb_path"] = p
        save_cfg(self.cfg)
        self.update_adb_label()
        self.adb_log("adb: " + p)

    def download_adb(self):
        url = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
        self.bar_dl.setVisible(True)
        self.bar_dl.setValue(0)
        self.adb_log(tr("در حال دانلود از dl.google.com …"))

        def work():
            try:
                tmp = Path(tempfile.gettempdir()) / "platform-tools.zip"

                def hook(b, bs, total):
                    if total > 0:
                        ui(lambda v=int(b * bs * 100 / total): self.bar_dl.setValue(min(100, v)))
                urllib.request.urlretrieve(url, str(tmp), hook)
                with zipfile.ZipFile(tmp) as z:
                    z.extractall(APP_DIR)
                exe = APP_DIR / "platform-tools" / ("adb.exe" if sys.platform == "win32" else "adb")
                if not exe.is_file():
                    raise RuntimeError(tr("adb داخل فایل دانلودشده نبود"))
                ui(lambda: (self.set_adb_path(str(exe)), self.bar_dl.setVisible(False), self.refresh_devices()))
            except Exception as e:
                ui(lambda m=str(e): (self.bar_dl.setVisible(False), self.adb_log(
                    tr("دانلود نشد: %s\nصفحه‌ی دانلود را در مرورگر باز کنید، zip را استخراج کنید و «انتخاب adb.exe» را بزنید.") % m)))
        threading.Thread(target=work, daemon=True).start()

    def _need_adb(self):
        if not self.adb_path:
            self.adb_log(tr("ابتدا adb را پیدا یا دانلود کنید."))
            return False
        return True

    def refresh_devices(self, auto=False):
        if not self._need_adb():
            return

        def work():
            adb_cmd(self.adb_path, ["start-server"], 20)
            rc, out = adb_cmd(self.adb_path, ["devices"], 15)
            devs = []
            for l in out.splitlines()[1:]:
                parts = l.split()
                if len(parts) >= 2 and "daemon" not in l and not l.startswith("*"):
                    devs.append((parts[0], parts[1]))
            ui(lambda: self._show_devices(devs, out, auto))
        threading.Thread(target=work, daemon=True).start()

    def _show_devices(self, devs, raw, auto):
        self.cmb_dev.clear()
        for s, st in devs:
            self.cmb_dev.addItem("%s  [%s]" % (s, st), s)
        self.adb_log(tr("دستگاه‌ها:\n") + (raw or tr("(خالی)")))
        if any(st == "unauthorized" for _, st in devs):
            self.adb_log(tr("⚠ پنجره‌ی «Allow USB debugging» را روی گوشی تأیید کنید و دوباره تازه‌سازی بزنید."))
        good = [s for s, st in devs if st == "device"]
        if auto and len(good) == 1 and not self.adb:
            self.cmb_dev.setCurrentIndex([s for s, _ in devs].index(good[0]))
            self.connect_selected()

    def connect_selected(self):
        self.connect_serial(self.cmb_dev.currentData())

    def connect_serial(self, serial):
        if not self._need_adb():
            return
        self.statusBar().showMessage(tr("در حال اتصال…"))

        def work():
            try:
                a = Adb(self.adb_path, serial)
                ui(lambda: self._connected(a))
            except Exception as e:
                ui(lambda m=str(e): (self.adb_log(tr("اتصال ناموفق: ") + m), self.statusBar().showMessage(tr("اتصال ناموفق"), 4000)))
        threading.Thread(target=work, daemon=True).start()

    def _connected(self, a, quiet=False):
        self.disconnect_phone(silent=True)
        self.adb = a
        self.view.set_adb(a)
        self.grabber = Grabber(a, self.view)
        self.grabber.live = self.chk_live.isChecked()
        self.grabber.interval = (0.25, 0.5, 1.0)[self.cmb_speed.currentIndex()]
        self.grabber.start()
        self.adb_log(tr("✅ وصل شد: %s (%dx%d)") % (a.serial or tr("پیش‌فرض"), *a.size))
        self.statusBar().showMessage(tr("گوشی متصل شد"), 4000)
        self.update_pills()
        if not quiet:
            self.tabs.setCurrentIndex(0)
            self.view.setFocus()
        self.on_phone_connected(a)

    def disconnect_phone(self, silent=False):
        if self.grabber:
            self.grabber.stop_ev.set()
            self.grabber = None
        if self.adb:
            self.on_phone_disconnected()
            self.adb.close()
            self.adb = None
        self.view.set_adb(None)
        self.update_pills()
        if not silent:
            self.adb_log(tr("اتصال قطع شد."))

    def _bg_adb(self, steps_fn):
        threading.Thread(target=steps_fn, daemon=True).start()

    def wifi_connect(self):
        if not self._need_adb():
            return
        addr = self.ed_ip.text().strip()
        if not addr:
            return self.adb_log(tr("IP:پورت را بنویسید."))
        if ":" not in addr:
            addr += ":5555"
        self.cfg["last_ip"] = addr
        save_cfg(self.cfg)

        def work():
            rc, out = adb_cmd(self.adb_path, ["connect", addr], 20)
            ui(lambda: (self.adb_log(out), self.refresh_devices()))
        self._bg_adb(work)

    def wifi_pair(self):
        if not self._need_adb():
            return
        addr, code = self.ed_pair.text().strip(), self.ed_code.text().strip()
        if not addr or not code:
            return self.adb_log(tr("IP:پورت جفت‌سازی و کد را بنویسید."))

        def work():
            rc, out = adb_cmd(self.adb_path, ["pair", addr, code], 25)
            ui(lambda: self.adb_log(out))
        self._bg_adb(work)

    def usb_to_wifi(self):
        if not self._need_adb():
            return

        def work():
            rc, out = adb_cmd(self.adb_path, ["devices"], 15)
            usb = [l.split()[0] for l in out.splitlines()[1:] if l.strip().endswith("device") and ":" not in l.split()[0]]
            if not usb:
                return ui(lambda: self.adb_log(tr("دستگاه USB پیدا نشد. کابل را وصل و USB debugging را روشن کنید.")))
            s = usb[0]
            rc, route = adb_cmd(self.adb_path, ["-s", s, "shell", "ip", "route"], 15)
            m = re.search(r"src (\d+\.\d+\.\d+\.\d+)", route)
            if not m:
                return ui(lambda: self.adb_log(tr("IP گوشی پیدا نشد؛ گوشی را به همان وای‌فای وصل کنید.\n") + route))
            ip = m.group(1)
            rc, o1 = adb_cmd(self.adb_path, ["-s", s, "tcpip", "5555"], 15)
            time.sleep(1.5)
            rc, o2 = adb_cmd(self.adb_path, ["connect", ip + ":5555"], 20)
            ui(lambda: (self.adb_log(o1 + "\n" + o2 + tr("\nحالا کابل را می‌توانید جدا کنید.")),
                        self.ed_ip.setText(ip + ":5555"), self.refresh_devices()))
        self._bg_adb(work)

    # ================= اتصال با QR =================
    def qr_status(self, text, state="warn"):
        self.lbl_qr_status.setText(text)
        set_state(self.lbl_qr_status, state)

    def start_qr_pair(self):
        if not self._need_adb():
            return
        self.cancel_qr(silent=True)
        alpha = string.ascii_letters + string.digits
        name = "studio-" + "".join(secrets.choice(alpha) for _ in range(10))
        pw = "".join(secrets.choice(alpha) for _ in range(12))
        self.qr_name = name
        self.lbl_pairqr.setPixmap(qr_pixmap("WIFI:T:ADB;S:%s;P:%s;;" % (name, pw), 250))
        ev = threading.Event()
        self.qr_cancel = ev
        self.qr_status(tr("منتظر اسکن QR توسط گوشی…"), "warn")
        threading.Thread(target=self._qr_worker, args=(name, pw, ev), daemon=True).start()

    def cancel_qr(self, silent=False):
        ev = getattr(self, "qr_cancel", None)
        if ev:
            ev.set()
        self.lbl_pairqr.clear()
        self.lbl_pairqr.setText(tr("برای شروع «ساخت QR» را بزن"))
        if not silent:
            self.qr_status(tr("لغو شد"), "warn")

    def _qr_worker(self, name, pw, ev):
        exe = self.adb_path

        def st(t, s="warn"):
            ui(lambda: None if ev.is_set() else self.qr_status(t, s))

        def log(t):
            ui(lambda: self.adb_log(t))

        def mdns_ok():
            rc, out = adb_cmd(exe, ["mdns", "check"], 10)
            log("mdns: " + out)
            return rc == 0 and "unavailable" not in out.lower() and "error" not in out.lower()
        adb_cmd(exe, ["start-server"], 20)
        if not mdns_ok():
            log(tr("راه‌اندازی مجدد adb با mDNS…"))
            adb_cmd(exe, ["kill-server"], 10)
            adb_cmd(exe, ["start-server"], 20)
            if not mdns_ok():
                return st(tr("این نسخه‌ی adb از mDNS پشتیبانی نمی‌کند؛ از «جفت‌سازی با کد» استفاده کن."))
        pair_addr, deadline = None, time.time() + 150
        while time.time() < deadline and not ev.is_set():
            _, out = adb_cmd(exe, ["mdns", "services"], 10)
            for n, t, a in parse_mdns(out):
                if t.startswith("_adb-tls-pairing") and n == name:
                    pair_addr = a
            if pair_addr:
                break
            time.sleep(1.2)
        if ev.is_set():
            return
        if not pair_addr:
            log(tr("گوشی QR را اسکن نکرد (یا mDNS در این شبکه مسدود است)."))
            return st(tr("زمان تمام شد؛ گوشی QR را اسکن نکرد. دوباره امتحان کن."))
        st(tr("گوشی پیدا شد؛ در حال جفت‌سازی…"))
        rc, out = adb_cmd(exe, ["pair", pair_addr, pw], 25)
        log(out)
        if "successfully paired" not in out.lower():
            return st(tr("جفت‌سازی ناموفق بود (گزارش را ببین)."))
        st(tr("جفت شد؛ در حال اتصال…"))
        host, addr = pair_addr.rsplit(":", 1)[0], None
        for _ in range(30):
            if ev.is_set():
                return
            _, out = adb_cmd(exe, ["mdns", "services"], 10)
            for n, t, a in parse_mdns(out):
                if t.startswith("_adb-tls-connect") and a.rsplit(":", 1)[0] == host:
                    addr = a
            if addr:
                break
            time.sleep(1)
        if not addr:
            log(tr("جفت شد ولی پورت اتصال پیدا نشد. IP:پورت صفحه‌ی Wireless debugging را در «اتصال بی‌سیم» بزن."))
            return st(tr("جفت شد؛ ولی آدرس اتصال پیدا نشد (راهنما در گزارش)."))
        rc, out = adb_cmd(exe, ["connect", addr], 20)
        log(out)
        ui(lambda: self._qr_done(addr))

    def _qr_done(self, addr):
        self.qr_status(tr("✅ وصل شد"), "ok")
        self.lbl_pairqr.clear()
        self.lbl_pairqr.setText(tr("✅\nگوشی وصل شد"))
        self.ed_ip.setText(addr)
        self.cfg["last_ip"] = addr
        save_cfg(self.cfg)
        self.refresh_devices()
        self.connect_serial(addr)

    # ================= سرور کیبورد =================
    def server_event(self, kind, msg):
        ui(lambda: self.log_server(kind, msg))

    def log_server(self, kind, msg):
        icon = {"ok": "✅", "warn": "⚠", "info": "•"}.get(kind, "•")
        self.lst_log.addItem("%s  %s   —   %s" % (icon, msg, time.strftime("%H:%M:%S")))
        self.lst_log.scrollToBottom()
        while self.lst_log.count() > 300:
            self.lst_log.takeItem(0)

    def start_server(self):
        try:
            self.server.start(self.sp_port.value())
        except ImportError:
            self.lbl_url.setText(tr("pynput نصب نیست"))
            self.log_server("warn", tr("کتابخانه‌ی pynput نصب نیست:  py -m pip install pynput"))
        except OSError as e:
            self.lbl_url.setText(tr("پورت اشغال است"))
            self.log_server("warn", tr("سرور روشن نشد (پورت اشغال؟): %s") % e)
        except Exception as e:
            self.log_server("warn", tr("سرور روشن نشد: %s") % e)
        self.cfg["port"] = self.sp_port.value()
        save_cfg(self.cfg)
        self.refresh_url()

    def toggle_server(self):
        if self.server.running:
            self.server.stop()
            self.log_server("info", tr("سرور خاموش شد"))
        else:
            self.start_server()
        self.refresh_url()

    def new_token(self):
        self.server.token = secrets.token_urlsafe(6)
        self.server.seen.clear()
        self.refresh_url()
        self.log_server("info", tr("توکن جدید ساخته شد"))

    def refresh_url(self):
        if self.server.running:
            u = self.server.url()
            self.lbl_url.setText(u)
            self.make_qr(u)
        else:
            self.lbl_url.setText(tr("سرور خاموش است"))
            self.lbl_qr.clear()
        self.update_pills()

    def copy_url(self):
        if self.server.running:
            QGuiApplication.clipboard().setText(self.server.url())
            self.statusBar().showMessage(tr("آدرس کپی شد"), 3000)

    def make_qr(self, url):
        try:
            self.lbl_qr.setPixmap(qr_pixmap(url, 210))
        except Exception:
            self.lbl_qr.clear()

    def closeEvent(self, e):
        if self.cfg.get("tray") and self.tray and not self._quitting:
            e.ignore()
            self.hide()
            self.tray.showMessage(tr("پل گوشی"), tr("برنامه در سینی سیستم در حال اجراست."))
            return
        self.cfg["theme"] = self.theme
        save_cfg(self.cfg)
        self.cancel_qr(silent=True)
        self.disconnect_phone(silent=True)
        self.server.stop()
        super().closeEvent(e)


def _restart_argv():
    """فرمان اجرای دوباره‌ی برنامه، بدون --lang قدیمی."""
    args, skip = [], False
    for a in sys.argv[1:]:
        if skip:
            skip = False
        elif a == "--lang":
            skip = True
        elif not a.startswith("--lang="):
            args.append(a)
    base = [sys.executable] if getattr(sys, "frozen", False) else [sys.executable, os.path.abspath(sys.argv[0])]
    return base + args


def parse_args(argv):
    import argparse
    ap = argparse.ArgumentParser(prog="phone-bridge", description="Phone Bridge — PC ↔ Android remote control.")
    ap.add_argument("--version", action="version", version="Phone Bridge %s" % __version__)
    ap.add_argument("--lang", choices=("fa", "en"), help="interface language (saved for next runs)")
    return ap.parse_known_args(argv[1:])


def main():
    global BUS, LANG
    args, qt_args = parse_args(sys.argv)
    cfg = load_cfg()
    if args.lang:
        cfg["lang"] = args.lang
        save_cfg(cfg)
    LANG = cfg.get("lang", "fa")
    app = QApplication([sys.argv[0]] + qt_args)
    app.setWindowIcon(app_icon())
    if sys.platform == "win32":      # آیکون درست در نوار وظیفه
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("PhoneBridge.App")
        except Exception:
            pass
    app.setStyle("Fusion")
    app.setLayoutDirection(Qt.LayoutDirection.RightToLeft if LANG == "fa" else Qt.LayoutDirection.LeftToRight)
    BUS = Bus()
    have_font = setup_fonts()
    app.setFont(QFont(FONT_FAMILY, 10))
    w = MainWindow()
    w.show()
    if not have_font:
        def get_font():
            if fetch_fonts():
                def apply():
                    if setup_fonts():
                        app.setFont(QFont(FONT_FAMILY, 10))
                        w.apply_theme()
                ui(apply)
        threading.Thread(target=get_font, daemon=True).start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
