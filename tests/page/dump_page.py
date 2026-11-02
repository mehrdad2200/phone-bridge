"""Write the phone remote page (both languages) to a folder so page_test.js can load it in jsdom.

    python tests/page/dump_page.py OUT_DIR
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import phone_bridge as pb  # noqa: E402

out = Path(sys.argv[1] if len(sys.argv) > 1 else ".")
out.mkdir(parents=True, exist_ok=True)
for lang in ("fa", "en"):
    html = pb.PAGE.replace("__T__", "TOKEN123").replace("__LANG__", lang).replace("__DIR__", "rtl" if lang == "fa" else "ltr")
    (out / ("page_%s.html" % lang)).write_text(html, encoding="utf-8")
print("wrote", out)
