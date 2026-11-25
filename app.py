import os, sys, json, subprocess
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QListWidget, QListWidgetItem, QScrollArea,
                             QStackedWidget, QFileDialog)

BASE = os.path.dirname(os.path.abspath(__file__))
W = subprocess.Popen(["python3", os.path.join(BASE, "worker.py")], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
def ask(d): W.stdin.write(json.dumps(d)+"\n"); W.stdin.flush(); return json.loads(W.stdout.readline())
class CutefishBooks(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cutefish Books"); self.setWindowIcon(QIcon(os.path.join(BASE, "icon.svg")))
        self.resize(1050, 720)
        self.bp, self.pg, self.zm, self.dk = "", 0, 1.5, False
        self.sf = os.path.expanduser("~/.cf_books.json")
        self.st = json.load(open(self.sf)) if os.path.exists(self.sf) else {}
        self.apply_theme(); self.tm = QTimer(self); self.tm.timeout.connect(self.apply_theme); self.tm.start(1500)

        cw = QWidget(); self.setCentralWidget(cw); ml = QVBoxLayout(cw)
        tb = QHBoxLayout(); ml.addLayout(tb)
        self.btn_act = QPushButton("Klasör Seç"); self.btn_act.clicked.connect(self.on_act); tb.addWidget(self.btn_act)
        tb.addStretch(); self.lbl_title = QLabel("<b>Cutefish Books</b>"); tb.addWidget(self.lbl_title); tb.addStretch()
        self.btn_zm_out = QPushButton("-"); self.btn_zm_out.clicked.connect(lambda: self.set_zoom(-0.25)); tb.addWidget(self.btn_zm_out)
        self.btn_zm_in = QPushButton("+"); self.btn_zm_in.clicked.connect(lambda: self.set_zoom(0.25)); tb.addWidget(self.btn_zm_in)
        self.btn_dk = QPushButton("Gece Modu"); self.btn_dk.clicked.connect(self.toggle_dark); tb.addWidget(self.btn_dk)
        self.lbl_pg = QLabel(""); tb.addWidget(self.lbl_pg)
        self.stack = QStackedWidget(); ml.addWidget(self.stack)
        self.shelf = QListWidget(); self.shelf.setViewMode(QListWidget.IconMode); self.shelf.setIconSize(QSize(130, 180)); self.shelf.setResizeMode(QListWidget.Adjust); self.shelf.setSpacing(16); self.shelf.itemClicked.connect(self.open_item); self.stack.addWidget(self.shelf)
        self.scroll = QScrollArea(); self.scroll.setAlignment(Qt.AlignCenter); self.page_lbl = QLabel(); self.scroll.setWidget(self.page_lbl); self.stack.addWidget(self.scroll)
        nav = QHBoxLayout(); ml.addLayout(nav)
        self.btn_prev = QPushButton("‹ Önceki Sayfa"); self.btn_prev.clicked.connect(lambda: self.render(self.pg - 1)); nav.addWidget(self.btn_prev)
        self.btn_next = QPushButton("Sonraki Sayfa ›"); self.btn_next.clicked.connect(lambda: self.render(self.pg + 1)); nav.addWidget(self.btn_next)
        self.set_read_ui(False)

    def apply_theme(self):
        cfg = os.path.expanduser("~/.config/cutefish/services.conf")
        txt = open(cfg).read().lower().replace(" ", "") if os.path.exists(cfg) else ""
        dark = ("darkmode=true" in txt) or (QApplication.palette().window().color().lightness() < 128)
        if getattr(self, "_last_dk", None) == dark: return
        self._last_dk = dark
        if dark: self.setStyleSheet("QMainWindow,QWidget,QScrollArea,QListWidget{background:#1C1C1E;color:#F5F5F7;border:none;} QPushButton{background:#2C2C2E;color:#FFF;border:1px solid #3A3A3C;border-radius:6px;padding:6px 12px;} QPushButton:hover{background:#3A3A3C;} QLabel{color:#F5F5F7;}")
        else: self.setStyleSheet("QMainWindow,QWidget,QScrollArea,QListWidget{background:#F5F5F7;color:#1D1D1F;border:none;} QPushButton{background:#FFF;color:#1D1D1F;border:1px solid #DDD;border-radius:6px;padding:6px 12px;} QPushButton:hover{background:#EAEAEA;} QLabel{color:#1D1D1F;}")
    def set_read_ui(self, r):
        self.stack.setCurrentIndex(1 if r else 0); self.btn_act.setText("← Kütüphane" if r else "Klasör Seç")
        for w in (self.btn_zm_out, self.btn_zm_in, self.btn_dk, self.lbl_pg, self.btn_prev, self.btn_next): w.setVisible(r)

    def on_act(self):
        if self.stack.currentIndex() == 1: self.set_read_ui(False); return
        p = QFileDialog.getExistingDirectory(self, "Kitap Klasörü Seç", os.path.expanduser("~"))
        if p:
            self.shelf.clear()
            for b in ask({"cmd":"scan","dir":p}):
                it = QListWidgetItem(b["title"]); it.setData(Qt.UserRole, b["path"])
                if b["cover"]: it.setIcon(QIcon(b["cover"]))
                self.shelf.addItem(it)

    def open_item(self, it): self.bp = it.data(Qt.UserRole); self.pg = self.st.get(self.bp, 0); self.set_read_ui(True); self.render(self.pg)
    def set_zoom(self, d): self.zm = max(0.75, min(3.5, self.zm + d)); self.render(self.pg)
    def toggle_dark(self): self.dk = not self.dk; self.render(self.pg)
    def keyPressEvent(self, e):
        if self.stack.currentIndex() == 1:
            if e.key() == Qt.Key_Right: self.render(self.pg + 1)
            elif e.key() == Qt.Key_Left: self.render(self.pg - 1)
    def render(self, n):
        if not self.bp or n < 0: return
        d = ask({"cmd":"page","path":self.bp,"pg":n,"zm":self.zm,"dk":self.dk})
        self.pg = d["page"]; self.st[self.bp] = self.pg; json.dump(self.st, open(self.sf, "w"))
        pix = QPixmap(); pix.loadFromData(__import__("base64").b64decode(d["b64"])); self.page_lbl.setPixmap(pix); self.page_lbl.resize(pix.size()); self.lbl_pg.setText(f"  {self.pg + 1} / {d['total']}")

app = QApplication(sys.argv); w = CutefishBooks(); w.show(); sys.exit(app.exec_())
