"""Fast unit tests (no phone, no window). Run:  python -m pytest -q"""
import ast
import os
import re
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault("PHONE_BRIDGE_HOME", str(ROOT / ".test-data"))

import phone_bridge as pb  # noqa: E402

SRC = (ROOT / "phone_bridge.py").read_text(encoding="utf-8")
TREE = ast.parse(SRC)
FA = re.compile(r"[\u0600-\u06FF]")


# ---------------------------------------------------------------- helpers
def test_version_is_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", pb.__version__)


@pytest.mark.parametrize("n,out", [(0, "0 B"), (1023, "1023 B"), (2048, "2.0 KB"), (1234567, "1.2 MB"), (5 * 1024 ** 3, "5.0 GB")])
def test_human_sizes(n, out):
    assert pb.human(n) == out


def test_shell_quoting_is_safe():
    assert pb.shq("a b") == "'a b'"
    assert pb.shq("it's") == "'it'\\''s'"          # embedded quote survives a POSIX shell
    assert pb.shq("; rm -rf /") == "'; rm -rf /'"


def test_parse_mdns():
    out = ("List of discovered mdns services\n"
           "studio-AbC123\t_adb-tls-pairing._tcp.\t192.168.1.5:37123\n"
           "adb-XYZ\t_adb-tls-connect._tcp.\t192.168.1.5:41999\n"
           "noise line\n")
    assert pb.parse_mdns(out) == [("studio-AbC123", "_adb-tls-pairing._tcp.", "192.168.1.5:37123"),
                                  ("adb-XYZ", "_adb-tls-connect._tcp.", "192.168.1.5:41999")]


@pytest.mark.parametrize("line,expect", [
    ("drwxrwx--x 2 root sdcard_rw 3452 2026-10-02 11:30 DCIM", ("d", "DCIM")),
    ("-rw-rw---- 1 root sdcard_rw 2048 2026-10-04 08:00 my notes.txt", ("-", "my notes.txt")),
    ("-rw-rw---- 1 u0_a1 media_rw 99 Jan 5 10:22 old style.jpg", ("-", "old style.jpg")),
])
def test_ls_parser(line, expect):
    m = pb.LS_RE.match(line)
    assert m and (m.group(1)[0], m.group(4)) == expect


def test_restart_argv_drops_stale_lang(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["phone_bridge.py", "--lang", "en", "--other"])
    assert "--lang" not in pb._restart_argv() and "en" not in pb._restart_argv()[2:]
    monkeypatch.setattr(sys, "argv", ["phone_bridge.py", "--lang=fa"])
    assert not any(a.startswith("--lang") for a in pb._restart_argv())


def test_data_dir_env_override(monkeypatch, tmp_path):
    monkeypatch.setenv("PHONE_BRIDGE_HOME", str(tmp_path / "x"))
    assert pb._data_dir() == tmp_path / "x" and (tmp_path / "x").is_dir()


# ---------------------------------------------------------------- QR code
def test_qr_geometry_and_finders():
    m = pb.qr_matrix("hello")
    n = len(m)
    assert n == 21                                   # version 1
    for (r, c) in ((0, 0), (0, n - 7), (n - 7, 0)):  # three 7x7 finder patterns
        assert all(m[r][c + i] for i in range(7)) and all(m[r + 6][c + i] for i in range(7))
        assert m[r + 3][c + 3] and not m[r + 1][c + 1]


def test_qr_versions_grow_with_payload():
    sizes = [len(pb.qr_matrix("x" * k)) for k in (5, 40, 100, 200)]
    assert sizes == sorted(sizes) and len(set(sizes)) == 4
    with pytest.raises(ValueError):
        pb.qr_matrix("x" * 400)


@pytest.fixture(scope="session")
def qapp():
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication([])
    yield app                                        # keep a reference alive for the whole session


def _gray(pixmap):
    import numpy as np
    from PyQt6.QtGui import QImage
    img = pixmap.toImage().convertToFormat(QImage.Format.Format_Grayscale8)
    w, h = img.width(), img.height()
    ptr = img.constBits()
    ptr.setsize(h * img.bytesPerLine())
    return np.frombuffer(ptr, np.uint8).reshape(h, img.bytesPerLine())[:, :w].copy()


def test_qr_roundtrip_with_opencv(qapp):
    cv2 = pytest.importorskip("cv2")
    pytest.importorskip("numpy")
    for text in ("WIFI:T:ADB;S:studio-abcdEFGH12;P:Zy9xQ3mL8pRt;;", "http://192.168.1.9:8765/?t=tIqeDlR9", "سلام"):
        # OpenCV's detector is picky about scale; the code must decode at (at least) one of several sizes
        found = [cv2.QRCodeDetector().detectAndDecode(_gray(pb.qr_pixmap(text, size)))[0] for size in (300, 420, 520)]
        assert text in found, found


def test_icons_render(qapp):
    for name in pb.ICONS:
        assert not pb.make_icon(name).isNull(), name
    assert not pb.app_icon().isNull()


# ---------------------------------------------------------------- translations
def _tr_strings():
    out = {}
    for n in ast.walk(TREE):
        if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "tr" and n.args
                and isinstance(n.args[0], ast.Constant) and isinstance(n.args[0].value, str)):
            out[n.args[0].value] = n.lineno
    return out


def test_every_tr_string_has_an_english_translation():
    missing = {k: v for k, v in _tr_strings().items() if k not in pb.EN}
    assert not missing, "add these to EN: %s" % missing


def test_translations_keep_format_placeholders():
    ph = lambda s: sorted(re.findall(r"%[sdf.0-9]*[sdf]", s))
    bad = [k for k, v in pb.EN.items() if ph(k) != ph(v)]
    assert not bad, bad


def test_no_orphan_translations():
    used = set(_tr_strings())
    assert not [k for k in pb.EN if k not in used], "EN has entries nothing uses"


def test_no_untranslated_persian_literal_in_ui_code():
    """Every Persian string must go through tr() — otherwise English mode would show Persian."""
    docs = set()
    for n in ast.walk(TREE):
        if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body and isinstance(n.body[0], ast.Expr):
            docs.add(id(n.body[0].value))
    parents = {c: p for p in ast.walk(TREE) for c in ast.iter_child_nodes(p)}
    en_dict = next(n for n in TREE.body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "EN")
    inside_en = {id(x) for x in ast.walk(en_dict)}
    bad = []
    for n in ast.walk(TREE):
        if not (isinstance(n, ast.Constant) and isinstance(n.value, str) and FA.search(n.value)):
            continue
        if id(n) in docs or id(n) in inside_en or len(n.value) > 3000:      # docstrings, EN table, the web page
            continue
        p = parents[n]
        if isinstance(p, ast.Call) and isinstance(p.func, ast.Name) and p.func.id == "tr":
            continue
        bad.append((n.lineno, n.value[:40]))
    assert not bad, "wrap with tr(): %s" % bad


# ---------------------------------------------------------------- web page
def test_page_has_placeholders_and_no_external_resources():
    page = pb.PAGE
    for token in ("__T__", "__LANG__", "__DIR__"):
        assert token in page
    assert not re.search(r"(src|href)=[\"']https?://", page), "the remote page must work offline (LAN only)"
    assert "cdn." not in page and "googleapis" not in page


def test_page_i18n_tables_are_in_sync():
    fa = set(re.findall(r"(\w+):'", pb.PAGE.split("const L={fa:{")[1].split("en:{")[0]))
    en = set(re.findall(r"(\w+):'", pb.PAGE.split("en:{")[1].split("const KEYS")[0]))
    assert fa == en and len(fa) > 40, (fa ^ en)
