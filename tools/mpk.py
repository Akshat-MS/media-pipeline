#!/usr/bin/env python3
"""
mpk — Media Pipeline Kit

Command-line utilities for the Lecture Alive AI workflow. Deterministic work
lives here; judgement lives in the layer prompts.

    mpk --help
    mpk deck --help
    mpk deck extract --help
"""
from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

__version__ = "0.1.0"

A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
EMU_PER_INCH = 914400


# ════════════════════════════════════════════════════════════ helpers
def die(msg: str, code: int = 1):
    print(f"mpk: error: {msg}", file=sys.stderr)
    sys.exit(code)


def need(mod: str):
    try:
        return __import__(mod)
    except ImportError:
        die(f"{mod} is required — pip install {mod.replace('_','-')}")


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def safe(fn, default=None):
    """python-pptx raises rather than returning None for several properties
    (auto_shape_type on a non-autoshape, colour on an inherited fill). Probing
    is normal here, so an exception is a fact about the shape, not an error."""
    try:
        return fn()
    except Exception:
        return default


def emit(data, out: str | None):
    text = json.dumps(data, indent=2, ensure_ascii=False)
    if out:
        Path(out).write_text(text, encoding="utf-8")
        print(f"wrote {out}  ({len(text):,} bytes)", file=sys.stderr)
    else:
        print(text)


def slide_id(deck_id: str, n: int) -> str:
    return f"{deck_id}_s{n:02d}"


def open_deck(path: str):
    """Open a .pptx. A file that is not a PowerPoint package is a normal
    mistake, not a crash — python-pptx raises PackageNotFoundError, which says
    nothing useful about what went wrong."""
    need("pptx")
    from pptx import Presentation
    from pptx.exc import PackageNotFoundError
    try:
        return Presentation(path)
    except PackageNotFoundError:
        die(f"not a PowerPoint file: {path}\n"
            f"       mpk deck commands need a .pptx. If this is a .ppt, open it "
            f"in PowerPoint or LibreOffice and save as .pptx.")
    except Exception as exc:
        die(f"could not open {path}: {type(exc).__name__}: {exc}")


# ════════════════════════════════════════════════════════════ deck extract
def _lines_of(tf) -> list[str]:
    """Visual lines. Splits paragraphs on <a:br/> soft breaks, which PowerPoint
    uses freely and which paragraph.text silently joins with \\x0b — merging
    what a viewer sees as separate lines. Layer 8 reveals visual lines, so this
    is the list that matters."""
    out = []
    for para in tf.paragraphs:
        for piece in para.text.split("\x0b"):
            out.append(piece)
    return out


def _colour(obj, kind: str) -> dict | None:
    """Best-effort colour read. Records the token as well as the resolved RGB,
    because a theme reference and a literal hex are different facts."""
    try:
        src = getattr(obj, kind)
        col = src.fore_color if kind == "fill" else src.color
        t = str(col.type).split(".")[-1].split(" ")[0] if col.type is not None else None
        d = {"type": t}
        try:
            d["rgb"] = str(col.rgb)
        except Exception:
            pass
        try:
            d["theme_color"] = str(col.theme_color).split(".")[-1].split(" ")[0]
        except Exception:
            pass
        return d if len(d) > 1 else None
    except Exception:
        return None


def _connector_facts(sh) -> dict:
    """Direction is the highest-error field in this layer, so read it from the
    XML rather than inferring it: a:stCxn / a:endCxn give the connected shapes,
    a:tailEnd / a:headEnd give which end carries the arrowhead."""
    el = sh._element
    out = {"start_cxn": None, "end_cxn": None,
           "head_end": None, "tail_end": None, "direction_verified": False}

    nv = el.find(f"{P}nvCxnSpPr/{P}cNvCxnSpPr")
    if nv is not None:
        for tag, key in (("stCxn", "start_cxn"), ("endCxn", "end_cxn")):
            n = nv.find(f"{A}{tag}")
            if n is not None:
                out[key] = {"shape_id": int(n.get("id")), "site_idx": int(n.get("idx"))}

    ln = el.find(f"{P}spPr/{A}ln")
    if ln is not None:
        for tag, key in (("headEnd", "head_end"), ("tailEnd", "tail_end")):
            n = ln.find(f"{A}{tag}")
            if n is not None:
                out[key] = n.get("type")

    arrow = (out["tail_end"] and out["tail_end"] != "none") or \
            (out["head_end"] and out["head_end"] != "none")
    if out["start_cxn"] and out["end_cxn"] and arrow:
        out["direction_verified"] = True
        out["direction_basis"] = (
            "a:stCxn/a:endCxn give both connected shapes; "
            f"a:tailEnd type={out['tail_end']!r} head={out['head_end']!r} "
            "identifies the arrowhead end")
    else:
        missing = []
        if not out["start_cxn"] or not out["end_cxn"]:
            missing.append("connection sites not declared in XML")
        if not arrow:
            missing.append("no arrowhead on either end")
        out["direction_basis"] = "NOT VERIFIED — " + "; ".join(missing)
    return out


def _table_of(sh) -> dict | None:
    if not getattr(sh, "has_table", False):
        return None
    t = sh.table
    return {
        "rows": len(t.rows), "cols": len(t.columns),
        "cells": [[c.text for c in row.cells] for row in t.rows],
    }


def _walk(shapes, sid: str, parent=None, group_off=(0, 0), depth=0) -> list[dict]:
    out = []
    for sh in shapes:
        eid = f"{sid}_{sh.shape_id}"
        raw = {"x": sh.left, "y": sh.top, "cx": sh.width, "cy": sh.height}
        absbox = dict(raw)
        if parent is not None:
            absbox = {"x": (sh.left or 0) + group_off[0], "y": (sh.top or 0) + group_off[1],
                      "cx": sh.width, "cy": sh.height}

        st = str(safe(lambda: sh.shape_type) or "")
        is_group = "GROUP" in st.upper()
        is_conn = sh._element.tag.endswith("}cxnSp")
        is_pic = "PICTURE" in st.upper()
        is_tbl = getattr(sh, "has_table", False)

        a = {
            "element_id": eid,
            "ooxml_shape_id": sh.shape_id,
            "ooxml_name": sh.name,
            "type": ("connector" if is_conn else "group" if is_group
                     else "table" if is_tbl else "picture" if is_pic
                     else "text" if safe(lambda: bool(sh.text_frame.text.strip()), False)
                     else "shape"),
            "shape_type": st,
            "shape_kind": safe(lambda: str(sh.auto_shape_type).split(" ")[0]),
            "parent_id": parent,
            "bounding_box": absbox,
            "properties": {},
            "flags": [],
        }
        if parent is not None:
            a["bounding_box_raw"] = raw
            a["flags"].append({
                "code": "group_relative_geometry", "severity": "info",
                "note": "inside a group — raw offsets are relative to the group transform; "
                        "bounding_box is the resolved absolute box",
                "needs_eye_check": False})

        if safe(lambda: sh.rotation):
            a["bounding_box"]["rot"] = sh.rotation
            a["flags"].append({"code": "rotated", "severity": "info",
                               "note": f"rotation {sh.rotation}° — resolve before "
                                       "concluding anything about geometry",
                               "needs_eye_check": False})

        p = a["properties"]
        if safe(lambda: sh.has_text_frame, False):
            tf = sh.text_frame
            p["text"] = tf.text
            p["paragraphs"] = [{"level": q.level, "text": q.text} for q in tf.paragraphs]
            p["lines"] = _lines_of(tf)
            if len(p["lines"]) > len(p["paragraphs"]):
                a["flags"].append({
                    "code": "soft_line_breaks", "severity": "info",
                    "note": f"{len(p['lines'])} visual lines across "
                            f"{len(p['paragraphs'])} paragraphs — <a:br/> soft breaks "
                            "present; use lines[] for per-line reveal",
                    "needs_eye_check": False})
            szs = {r.font.size.pt for q in tf.paragraphs for r in q.runs
                   if r.font.size is not None}
            if szs:
                p["font_sizes_pt"] = sorted(szs)
            if not tf.text.strip():
                p["empty"] = True
                a["flags"].append({"code": "empty_text_box", "severity": "info",
                                   "note": "no text runs — contributes no content",
                                   "needs_eye_check": False})
            if re.search(r"</?a:fld", sh._element.xml):
                p["is_field"] = True
                a["flags"].append({"code": "rendered_field", "severity": "info",
                                   "note": "contains a field (e.g. slide number) — "
                                           "the value is rendered, not literal",
                                   "needs_eye_check": False})

        for k, kind in (("fill", "fill"), ("line", "line")):
            c = _colour(sh, kind)
            if c:
                p[f"{k}_colour"] = c

        if is_pic:
            p["descr"] = safe(lambda: sh._element.find(
                ".//{http://schemas.openxmlformats.org/drawingml/2006/main}"
                "..").get("descr")) or sh.name
            p["image_name"] = safe(lambda: sh.image.filename)
            p["image_ext"] = safe(lambda: sh.image.ext)
            p["raster_content_unread"] = True
            a["flags"].append({"code": "raster_content_unread", "severity": "warn",
                               "note": "opaque raster — the XML cannot say what is "
                                       "drawn inside it",
                               "needs_eye_check": True})

        if is_conn:
            cf = _connector_facts(sh)
            a["endpoints"] = {
                "start": ({"anchor_shape_id": cf["start_cxn"]["shape_id"],
                           "anchor_element_id": f"{sid}_{cf['start_cxn']['shape_id']}",
                           "site_idx": cf["start_cxn"]["site_idx"], "inferred": False}
                          if cf["start_cxn"] else None),
                "end": ({"anchor_shape_id": cf["end_cxn"]["shape_id"],
                         "anchor_element_id": f"{sid}_{cf['end_cxn']['shape_id']}",
                         "site_idx": cf["end_cxn"]["site_idx"], "inferred": False}
                        if cf["end_cxn"] else None)}
            p.update({k: cf[k] for k in
                      ("head_end", "tail_end", "direction_verified", "direction_basis")})
            if not cf["direction_verified"]:
                a["flags"].append({"code": "direction_unverified", "severity": "error",
                                   "note": cf["direction_basis"],
                                   "needs_eye_check": True})

        if is_tbl:
            p["table"] = _table_of(sh)

        out.append(a)

        if is_group:
            off = (absbox["x"], absbox["y"])
            out.extend(_walk(sh.shapes, sid, parent=eid, group_off=off, depth=depth + 1))
    return out


def cmd_deck_extract(args):
    prs = open_deck(args.file)
    deck_id = args.deck_id or Path(args.file).stem.lower()[:16]

    slides, coverage = [], []
    for n, s in enumerate(prs.slides, 1):
        if args.slide and n != args.slide:
            continue
        sid = slide_id(deck_id, n)
        assets = _walk(s.shapes, sid)
        ids = sorted(a["ooxml_shape_id"] for a in assets)
        gaps = [i for i in range(min(ids), max(ids) + 1) if i not in ids] if ids else []
        coverage.append({"slide_id": sid, "captured_ids": ids, "gaps": gaps,
                         "reading": ("no shapes at these ids in spTree — consistent with "
                                     "deleted shapes or non-spTree parts"
                                     if gaps else "contiguous, no gaps")})
        notes = None
        if s.has_notes_slide and s.notes_slide.notes_text_frame is not None:
            t = s.notes_slide.notes_text_frame.text.strip()
            notes = t or None
        slides.append({"slide_id": sid, "slide_number": n,
                       "notes": notes, "assets": assets})

    out = {
        "deck_id": deck_id,
        "metadata": {
            "source_file": Path(args.file).name,
            "slide_count": len(prs.slides),
            "slides_extracted": len(slides),
            "canvas_dimensions": {"width": prs.slide_width, "height": prs.slide_height,
                                  "units": "EMU",
                                  "inches": [round(prs.slide_width / EMU_PER_INCH, 3),
                                             round(prs.slide_height / EMU_PER_INCH, 3)],
                                  "aspect": round(prs.slide_width / prs.slide_height, 4)},
            "extraction_path": "mpk_deck_extract",
            "mpk_version": __version__,
        },
        "id_coverage": coverage,
        "slides": slides,
    }
    if args.expect and args.expect != len(prs.slides):
        out["metadata"]["slide_count_mismatch"] = {
            "expected": args.expect, "found": len(prs.slides)}
        print(f"mpk: WARNING expected {args.expect} slides, found {len(prs.slides)}",
              file=sys.stderr)
    emit(out, args.out)


def cmd_deck_info(args):
    prs = open_deck(args.file)
    w, h = prs.slide_width, prs.slide_height
    print(f"{Path(args.file).name}")
    print(f"  slides : {len(prs.slides)}")
    print(f"  canvas : {w} x {h} EMU  "
          f"({w/EMU_PER_INCH:.2f} x {h/EMU_PER_INCH:.2f} in, "
          f"aspect {w/h:.4f})")
    for n, s in enumerate(prs.slides, 1):
        kinds: dict[str, int] = {}
        for sh in s.shapes:
            k = str(safe(lambda: sh.shape_type) or "?").split(" ")[0]
            kinds[k] = kinds.get(k, 0) + 1
        title = next((sh.text_frame.text.split("\n")[0][:48]
                      for sh in s.shapes
                      if safe(lambda: bool(sh.text_frame.text.strip()), False)
                      and not sh.text_frame.text.strip().isdigit()), "")
        bits = " ".join(f"{k}×{v}" for k, v in sorted(kinds.items()))
        print(f"  s{n:02d}  {len(s.shapes):2d} shapes  {bits:<48} {title}")


# ════════════════════════════════════════════════════════════ deck normalize
def cmd_deck_normalize(args):
    src = open_deck(args.file)
    if args.like:
        ref = open_deck(args.like)
        tw, th = ref.slide_width, ref.slide_height
    else:
        tw, th = args.width, args.height
    if not tw or not th:
        die("give --like <deck.pptx> or both --width and --height")

    sw, sh_ = src.slide_width, src.slide_height
    fx, fy = tw / sw, th / sh_
    if abs((sw / sh_) - (tw / th)) > 0.01:
        print(f"mpk: WARNING aspect differs ({sw/sh_:.4f} vs {tw/th:.4f}) — "
              "scaling will distort", file=sys.stderr)

    def scale(shapes):
        for s in shapes:
            for attr, f in (("left", fx), ("top", fy), ("width", fx), ("height", fy)):
                v = getattr(s, attr)
                if v is not None:
                    setattr(s, attr, int(round(v * f)))
            if str(safe(lambda: s.shape_type) or "").upper().startswith("GROUP"):
                scale(s.shapes)
            if safe(lambda: s.has_text_frame, False):
                for para in s.text_frame.paragraphs:
                    for r in para.runs:
                        if r.font.size is not None:
                            r.font.size = int(round(r.font.size * min(fx, fy)))

    for s in src.slides:
        scale(s.shapes)
    src.slide_width, src.slide_height = int(tw), int(th)
    src.save(args.out)
    print(f"normalized {sw}x{sh_} -> {int(tw)}x{int(th)}  "
          f"(x{fx:.4f}, y{fy:.4f})  -> {args.out}", file=sys.stderr)


# ════════════════════════════════════════════════════════════ deck merge
def cmd_deck_merge(args):
    base = open_deck(args.into)
    add = open_deck(args.file)

    if (base.slide_width, base.slide_height) != (add.slide_width, add.slide_height):
        die(f"canvas mismatch: {args.into} is {base.slide_width}x{base.slide_height}, "
            f"{args.file} is {add.slide_width}x{add.slide_height}. "
            f"Run 'mpk deck normalize {args.file} --like {args.into}' first — merging "
            f"decks of different sizes puts every coordinate in the wrong frame.")

    layout = base.slide_layouts[args.layout] if args.layout is not None \
        else base.slides[0].slide_layout

    inserted = []
    for s in add.slides:
        new = base.slides.add_slide(layout)
        for shp in list(new.shapes):          # start from a clean slide
            shp._element.getparent().remove(shp._element)
        for shp in s.shapes:
            new.shapes._spTree.append(copy.deepcopy(shp._element))
        inserted.append(new)

    if args.at:
        sldIdLst = base.slides._sldIdLst
        ids = list(sldIdLst)
        for k, new in enumerate(inserted):
            el = ids[len(ids) - len(inserted) + k]
            sldIdLst.remove(el)
            sldIdLst.insert(args.at - 1 + k, el)

    base.save(args.out)
    print(f"merged {len(inserted)} slide(s) from {Path(args.file).name} into "
          f"{Path(args.into).name}"
          + (f" at position {args.at}" if args.at else " (appended)")
          + f"  -> {args.out}", file=sys.stderr)
    print("mpk: NOTE images and theme parts are not re-linked by a raw spTree copy — "
          "run 'mpk deck render' and check the result before trusting it.",
          file=sys.stderr)


# ════════════════════════════════════════════════════════════ deck render
def cmd_deck_render(args):
    soffice = next((c for c in ("soffice", "libreoffice") if have(c)), None)
    if not soffice:
        die("LibreOffice not found — install it, or skip rendering")
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    pdf = outdir / (Path(args.file).stem + ".pdf")
    subprocess.run([soffice, "--headless", "--convert-to", "pdf",
                    "--outdir", str(outdir), args.file], check=True,
                   stdout=subprocess.DEVNULL)
    if not have("pdftoppm"):
        print(f"wrote {pdf} — install poppler-utils (pdftoppm) for PNGs",
              file=sys.stderr)
        return
    subprocess.run(["pdftoppm", "-png", "-r", str(args.dpi),
                    str(pdf), str(outdir / Path(args.file).stem)], check=True)
    pngs = sorted(outdir.glob(f"{Path(args.file).stem}*.png"))
    print(f"rendered {len(pngs)} page(s) at {args.dpi} dpi -> {outdir}", file=sys.stderr)
    for p in pngs:
        print(p)


# ════════════════════════════════════════════════════════════ review build
TEMPLATE_DIR = Path(__file__).parent / "templates"
DEFAULT_TEMPLATE = "slide-review"
_DATA_BLOCK = re.compile(
    r'(<script type="application/json" id="manifest">\n).*?(\n</script>)', re.DOTALL)


def resolve_template(name: str) -> Path:
    """Accept a bare template name or an explicit path.

    Bare names resolve against tools/templates/ so callers say
    `--template slide-review` rather than carrying a path around. Later layers
    add their own pages here — a sequence player for Layer 8, a transcript
    table for Layer 4 — and each is a template, not a new renderer."""
    p = Path(name)
    if p.suffix and p.exists():
        return p
    cand = TEMPLATE_DIR / (name if name.endswith(".html") else f"{name}.html")
    if cand.exists():
        return cand
    have_names = ", ".join(sorted(t.stem for t in TEMPLATE_DIR.glob("*.html"))) or "none"
    die(f"no template {name!r} — available: {have_names}")


def cmd_review_templates(args):
    if not TEMPLATE_DIR.is_dir():
        die(f"no templates directory at {TEMPLATE_DIR}")
    rows = sorted(TEMPLATE_DIR.glob("*.html"))
    if not rows:
        print("no templates found")
        return
    print(f"templates in {TEMPLATE_DIR}:")
    for t in rows:
        m = re.search(r"<title>(.*?)</title>", t.read_text(encoding="utf-8"))
        mark = "  (default)" if t.stem == DEFAULT_TEMPLATE else ""
        print(f"  {t.stem:<20} {m.group(1) if m else '':<40}{mark}")


def cmd_review_build(args):
    """Inject the manifest into a review template.

    The template owns the page — its embedded JavaScript renders every row,
    flag, prior and connector sentence from the manifest at load time. This
    command only substitutes the data block, so there is exactly one
    implementation of the page, shared by the tool and by the prompt."""
    tpl_path = resolve_template(args.template or DEFAULT_TEMPLATE)
    tpl = tpl_path.read_text(encoding="utf-8")
    raw = Path(args.file).read_text(encoding="utf-8")
    try:
        json.loads(raw)                  # fail loudly, and readably
    except json.JSONDecodeError as exc:
        die(f"{args.file} is not valid JSON: {exc}")
    html, n = _DATA_BLOCK.subn(
        lambda m: m.group(1) + raw.strip() + m.group(2), tpl)
    if n != 1:
        die(f'expected exactly one manifest block in {tpl_path}, found {n}')
    Path(args.out).write_text(html, encoding="utf-8")
    print(f"wrote {args.out}  ({len(html):,} bytes) — {tpl_path.name}, "
          f"rendering from the embedded manifest", file=sys.stderr)


# ════════════════════════════════════════════════════════════ audio / video
def _ff(cmd: list[str]) -> str:
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def cmd_audio_extract(args):
    if not have("ffmpeg"):
        die("ffmpeg not found")
    # RC-003: the delivery master is 48 kHz stereo and must never be the
    # 16 kHz copy that speech recognition wants.
    subprocess.run(["ffmpeg", "-y", "-i", args.file, "-vn",
                    "-ar", "48000", "-ac", "2", "-c:a", "pcm_s16le", args.out],
                   check=True, stderr=subprocess.DEVNULL)
    print(f"wrote {args.out} — 48 kHz stereo master (RC-003 delivery path)",
          file=sys.stderr)


def cmd_audio_asr(args):
    if not have("ffmpeg"):
        die("ffmpeg not found")
    subprocess.run(["ffmpeg", "-y", "-i", args.file, "-vn",
                    "-ar", "16000", "-ac", "1", "-c:a", "pcm_s16le", args.out],
                   check=True, stderr=subprocess.DEVNULL)
    print(f"wrote {args.out} — 16 kHz mono ASR copy. Never ship this as the "
          f"master (RC-003).", file=sys.stderr)


def cmd_audio_probe(args):
    if not have("ffmpeg"):
        die("ffmpeg not found")
    j = json.loads(_ff(["ffprobe", "-v", "quiet", "-print_format", "json",
                        "-show_streams", "-show_format", args.file]) or "{}")
    a = next((s for s in j.get("streams", []) if s.get("codec_type") == "audio"), {})
    vd = subprocess.run(["ffmpeg", "-i", args.file, "-af", "volumedetect",
                         "-f", "null", "-"], capture_output=True, text=True).stderr
    mean = re.search(r"mean_volume:\s*(-?[\d.]+) dB", vd)
    peak = re.search(r"max_volume:\s*(-?[\d.]+) dB", vd)
    emit({"file": Path(args.file).name,
          "codec": a.get("codec_name"), "sample_rate_hz": a.get("sample_rate"),
          "channels": a.get("channels"), "bitrate_bps": a.get("bit_rate"),
          "duration_s": j.get("format", {}).get("duration"),
          "mean_volume_db": float(mean.group(1)) if mean else None,
          "peak_volume_db": float(peak.group(1)) if peak else None,
          "note": "Layer 7 input. Cite TGT-005…010 rather than repeating these numbers."},
         args.out)


def cmd_video_probe(args):
    if not have("ffprobe"):
        die("ffprobe not found")
    j = json.loads(_ff(["ffprobe", "-v", "quiet", "-print_format", "json",
                        "-show_streams", "-show_format", args.file]) or "{}")
    v = next((s for s in j.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in j.get("streams", []) if s.get("codec_type") == "audio"), {})
    fr = v.get("avg_frame_rate", "0/1")
    try:
        n, d = fr.split("/"); fps = round(int(n) / int(d), 3) if int(d) else None
    except Exception:
        fps = None
    emit({"file": Path(args.file).name,
          "resolution": f"{v.get('width')}x{v.get('height')}",
          "declared_fps": fps, "video_codec": v.get("codec_name"),
          "profile": v.get("profile"),
          "video_bitrate_mbps": (round(int(v["bit_rate"]) / 1e6, 2)
                                 if v.get("bit_rate") else None),
          "audio_codec": a.get("codec_name"), "audio_channels": a.get("channels"),
          "audio_sample_rate_hz": a.get("sample_rate"),
          "duration_s": j.get("format", {}).get("duration"),
          "note": "declared_fps is what the container reports. It does NOT prove the "
                  "picture changes that often — see 'mpk video uniquefps' (TGT-013)."},
         args.out)


def cmd_video_uniquefps(args):
    """TGT-013. A 30 fps file made of 8 unique frames per second reports 30 to
    ffprobe and passes TGT-002, while still looking choppy — because encoding
    cannot add motion that was never rendered (RC-001)."""
    if not have("ffmpeg"):
        die("ffmpeg not found")
    dur = _ff(["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
               "-of", "csv=p=0", args.file]).strip()
    err = subprocess.run(["ffmpeg", "-i", args.file, "-vf",
                          f"mpdecimate=hi={args.hi}:lo={args.lo}",
                          "-loglevel", "info", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = re.search(r"frame=\s*(\d+)", err[::-1][:400][::-1]) or \
        re.findall(r"frame=\s*(\d+)", err)
    kept = int(m[-1]) if isinstance(m, list) and m else (int(m.group(1)) if m else None)
    d = float(dur) if dur else None
    eff = round(kept / d, 2) if kept and d else None
    emit({"file": Path(args.file).name, "duration_s": d,
          "unique_frames": kept, "effective_unique_fps": eff,
          "threshold": args.threshold,
          "verdict": (None if eff is None else
                      "PASS" if eff >= args.threshold else "FAIL"),
          "enforcement": "advisory",
          "note": "TGT-013 — measured over the whole file here. The target is "
                  "measured over ACTIVE BEAT WINDOWS, so deliberately still "
                  "content is not penalised; a whole-file figure is a floor, "
                  "not the gate."},
         args.out)


# ════════════════════════════════════════════════════════════ check manifest
def cmd_check_manifest(args):
    try:
        m = json.loads(Path(args.file).read_text())
    except json.JSONDecodeError as exc:
        die(f"{args.file} is not valid JSON: {exc}")
    m = m.get("payload", m)
    slides = m.get("slides") or [m]
    problems, notes = [], []

    for s in slides:
        sid = s.get("slide_id", "?")
        for a in s.get("assets", []):
            eid = a.get("element_id", "?")
            if not eid or not re.match(r".+_\d+$", str(eid)):
                problems.append(f"{sid}: element_id {eid!r} does not look "
                                f"OOXML-derived (<slide>_<shape_id>)")
            if a.get("tag") not in ("STATIC", "DYNAMIC"):
                problems.append(f"{eid}: tag {a.get('tag')!r} is not STATIC/DYNAMIC")
            if a.get("semantic_type") is None and not a.get("semantic_type_prior"):
                notes.append(f"{eid}: semantic_type null with no prior recorded")
            if a.get("type") == "connector":
                if not (a.get("properties") or {}).get("direction_verified"):
                    notes.append(f"{eid}: connector direction unverified")
    d = m.get("deck") or {}
    for k in ("entity_inventory", "chrome_pattern", "colour_convention"):
        if k not in d:
            notes.append(f"deck.{k} missing — Layer 6 reads entity_inventory")

    print(f"slides: {len(slides)}  assets: "
          f"{sum(len(s.get('assets', [])) for s in slides)}")
    for p in problems:
        print(f"  FAIL  {p}")
    for n in notes:
        print(f"  note  {n}")
    print(f"\n{len(problems)} failure(s), {len(notes)} note(s)")
    sys.exit(1 if problems else 0)


# ════════════════════════════════════════════════════════════ CLI
def build_parser():
    ap = argparse.ArgumentParser(
        prog="mpk", description="mpk — Media Pipeline Kit. Deterministic utilities "
                                "for the Lecture Alive AI workflow.",
        epilog="Try: mpk deck --help  ·  mpk deck extract --help",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--version", action="version", version=f"mpk {__version__}")
    groups = ap.add_subparsers(dest="group", metavar="<group>")

    # ---- deck
    g = groups.add_parser("deck", help="PowerPoint decks: inspect, extract, reshape")
    gs = g.add_subparsers(dest="cmd", metavar="<command>")

    c = gs.add_parser("info", help="one-line summary per slide")
    c.add_argument("file"); c.set_defaults(fn=cmd_deck_info)

    c = gs.add_parser("extract", help="OOXML shape tree -> raw JSON (Layer 3 step 1)")
    c.add_argument("file")
    c.add_argument("--out", "-o", help="write JSON here (default stdout)")
    c.add_argument("--deck-id", help="id prefix for element ids (default: filename stem)")
    c.add_argument("--slide", type=int, help="extract one slide only")
    c.add_argument("--expect", type=int, help="warn if the slide count differs")
    c.set_defaults(fn=cmd_deck_extract)

    c = gs.add_parser("normalize", help="rescale a deck to another canvas size")
    c.add_argument("file")
    c.add_argument("--like", help="copy the canvas size from this deck")
    c.add_argument("--width", type=int); c.add_argument("--height", type=int)
    c.add_argument("--out", "-o", required=True)
    c.set_defaults(fn=cmd_deck_normalize)

    c = gs.add_parser("merge", help="splice slides from one deck into another")
    c.add_argument("file", help="deck whose slides are inserted")
    c.add_argument("--into", required=True, help="base deck")
    c.add_argument("--at", type=int, help="1-based position (default: append)")
    c.add_argument("--layout", type=int, help="layout index for inserted slides")
    c.add_argument("--out", "-o", required=True)
    c.set_defaults(fn=cmd_deck_merge)

    c = gs.add_parser("render", help="slides -> PNG via LibreOffice")
    c.add_argument("file")
    c.add_argument("--outdir", "-d", default="render")
    c.add_argument("--dpi", type=int, default=150)
    c.set_defaults(fn=cmd_deck_render)

    # ---- review
    g = groups.add_parser("review", help="review pages built from templates")
    gs = g.add_subparsers(dest="cmd", metavar="<command>")
    c = gs.add_parser("build", help="manifest JSON -> self-contained review HTML")
    c.add_argument("file"); c.add_argument("--out", "-o", required=True)
    c.add_argument("--template", "-t", default=None,
                   help=f"template name or path (default: {DEFAULT_TEMPLATE})")
    c.set_defaults(fn=cmd_review_build)
    c = gs.add_parser("templates", help="list available review templates")
    c.set_defaults(fn=cmd_review_templates)

    # ---- audio
    g = groups.add_parser("audio", help="audio extraction and measurement")
    gs = g.add_subparsers(dest="cmd", metavar="<command>")
    c = gs.add_parser("extract", help="video -> 48 kHz stereo master (RC-003)")
    c.add_argument("file"); c.add_argument("--out", "-o", required=True)
    c.set_defaults(fn=cmd_audio_extract)
    c = gs.add_parser("asr", help="video -> 16 kHz mono copy for alignment")
    c.add_argument("file"); c.add_argument("--out", "-o", required=True)
    c.set_defaults(fn=cmd_audio_asr)
    c = gs.add_parser("probe", help="loudness and format measurements (Layer 7)")
    c.add_argument("file"); c.add_argument("--out", "-o")
    c.set_defaults(fn=cmd_audio_probe)

    # ---- video
    g = groups.add_parser("video", help="video measurement")
    gs = g.add_subparsers(dest="cmd", metavar="<command>")
    c = gs.add_parser("probe", help="resolution/fps/codec/bitrate (TGT-001…008)")
    c.add_argument("file"); c.add_argument("--out", "-o")
    c.set_defaults(fn=cmd_video_probe)
    c = gs.add_parser("uniquefps", help="unique frames per second (TGT-013)")
    c.add_argument("file"); c.add_argument("--out", "-o")
    c.add_argument("--threshold", type=float, default=24.0)
    c.add_argument("--hi", type=int, default=768); c.add_argument("--lo", type=int, default=320)
    c.set_defaults(fn=cmd_video_uniquefps)

    # ---- check
    g = groups.add_parser("check", help="validate artifacts")
    gs = g.add_subparsers(dest="cmd", metavar="<command>")
    c = gs.add_parser("manifest", help="validate a Layer 3 manifest")
    c.add_argument("file"); c.set_defaults(fn=cmd_check_manifest)

    return ap


def main(argv=None):
    ap = build_parser()
    args = ap.parse_args(argv)
    for attr in ("file", "into", "like"):
        v = getattr(args, attr, None)
        if isinstance(v, str) and not Path(v).exists():
            die(f"{attr}: no such file: {v}")
    if not getattr(args, "fn", None):
        (ap if not args.group else
         ap.parse_args([args.group, "--help"]))
        ap.print_help()
        return 2
    return args.fn(args)


if __name__ == "__main__":
    try:
        sys.exit(main() or 0)
    except BrokenPipeError:
        # `mpk deck info deck.pptx | head` is normal usage; SIGPIPE is not an error.
        try:
            sys.stdout.close()
        finally:
            sys.exit(0)
    except KeyboardInterrupt:
        sys.exit(130)
