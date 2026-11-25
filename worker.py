import sys, os, json, base64, hashlib, tempfile, subprocess, fitz
try:
    from docx import Document
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    HAS_DOCX = True
except Exception:
    HAS_DOCX = False

DIRECT = (".pdf", ".epub", ".xps", ".fb2", ".cbz")
TEXT_LIKE = (".docx", ".txt", ".rtf", ".odt")
DJVU = (".djvu", ".djv")
CACHE = os.path.join(tempfile.gettempdir(), "cf_books")
os.makedirs(CACHE, exist_ok=True)
doc_cache, page_cache = {}, {}

def ext_of(p): return ("." + p.rsplit(".", 1)[-1].lower()) if "." in os.path.basename(p) else ""
def name_of(p): return os.path.basename(p).rsplit(".", 1)[0]
def text_to_pdf(src, dst):
    if not HAS_DOCX: return
    lines = [p.text for p in Document(src).paragraphs] if ext_of(src) == ".docx" else open(src, errors="ignore").read().splitlines()
    c = canvas.Canvas(dst, pagesize=A4); y = 800
    for ln in lines:
        for i in range(0, max(1, len(ln)), 85):
            if y < 50: c.showPage(); y = 800
            c.drawString(40, y, ln[i:i+85]); y -= 15
    c.save()

def get_doc(p):
    if p in doc_cache: return doc_cache[p]
    e = ext_of(p)
    pdf = p if e in DIRECT else os.path.join(CACHE, hashlib.md5(p.encode()).hexdigest() + ".pdf")
    if not os.path.exists(pdf):
        if e in TEXT_LIKE: text_to_pdf(p, pdf)
        elif e in DJVU: subprocess.run(["ddjvu", "-format=pdf", p, pdf], check=True)
    doc_cache[p] = fitz.open(pdf); return doc_cache[p]

def render_b64(d, pg, zm, dk):
    key = (id(d), pg, zm, dk)
    if key not in page_cache:
        pix = d[pg].get_pixmap(matrix=fitz.Matrix(zm, zm), alpha=False)
        if dk: pix.invert_irect(pix.irect)
        page_cache[key] = base64.b64encode(pix.tobytes("jpg")).decode()
    return page_cache[key]

for line in sys.stdin:
    req = json.loads(line)
    if req["cmd"] == "scan":
        res = []
        for f in sorted(os.listdir(req["dir"])):
            e = ext_of(f)
            if e in DIRECT + TEXT_LIKE + DJVU:
                fp = os.path.join(req["dir"], f); cov = ""
                if e in DIRECT:
                    try:
                        cp = os.path.join(CACHE, "c_" + hashlib.md5(fp.encode()).hexdigest() + ".png")
                        if not os.path.exists(cp): d = fitz.open(fp); d[0].get_pixmap(matrix=fitz.Matrix(0.3, 0.3)).save(cp); d.close()
                        cov = cp
                    except Exception: pass
                res.append({"title": name_of(f), "path": fp, "cover": cov})
        print(json.dumps(res), flush=True)
    elif req["cmd"] == "page":
        d = get_doc(req["path"]); pg = max(0, min(req["pg"], len(d) - 1))
        b64 = render_b64(d, pg, req["zm"], req["dk"])
        if pg + 1 < len(d): render_b64(d, pg + 1, req["zm"], req["dk"])
        print(json.dumps({"b64": b64, "page": pg, "total": len(d)}), flush=True)
