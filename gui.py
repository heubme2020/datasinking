# -*- coding: utf-8 -*-
"""DataSinking Report Downloader (tkinter GUI)

No-code tool: enter key -> pick exchange -> pick stock -> set filters -> download Markdown.
Requires: pip install datasinking
"""
import os
import sys
import json
import threading
import webbrowser
import requests
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from datasinking import DataSinking

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

EXCHANGES = {"SSE (Shanghai)": "sse", "SZSE (Shenzhen)": "szse", "BSE (Beijing)": "bj"}
DOC_TYPES = {"All": None, "Annual": "annual", "Semi-annual": "semiannual", "Q1": "q1", "Q3": "q3"}


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("DataSinking Report Downloader")
        self.root.geometry("720x680")
        self.ds = None
        self.stocks = []  # [{stock_code, stock_name, report_count}]

        self._load_config()
        self._build_ui()

    # ---- config ----
    def _load_config(self):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            self.saved_key = cfg.get("key", "")
        except Exception:
            self.saved_key = ""

    def _save_config(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump({"key": self.key_var.get().strip()}, f)
        except Exception:
            pass

    def _open_get_key(self):
        webbrowser.open("https://datasink.ing/pricing")

    # ---- UI ----
    def _build_ui(self):
        # 1. key
        key_frame = ttk.LabelFrame(self.root, text="1. API Key")
        key_frame.pack(fill="x", padx=10, pady=6)
        self.key_var = tk.StringVar(value=self.saved_key)
        ttk.Entry(key_frame, textvariable=self.key_var, width=60).pack(side="left", padx=6, pady=6)
        ttk.Button(key_frame, text="Get key", command=self._open_get_key).pack(side="left", padx=4)
        ttk.Button(key_frame, text="Connect", command=self._connect).pack(side="left", padx=4)

        # 2. select stock
        exch_frame = ttk.LabelFrame(self.root, text="2. Select a stock")
        exch_frame.pack(fill="x", padx=10, pady=6)
        self.exch_var = tk.StringVar(value=list(EXCHANGES.keys())[0])
        ttk.Combobox(exch_frame, textvariable=self.exch_var, values=list(EXCHANGES.keys()), state="readonly", width=22).pack(side="left", padx=6, pady=6)
        ttk.Button(exch_frame, text="Refresh stocks", command=self._load_stocks).pack(side="left", padx=4)

        search_frame = ttk.Frame(exch_frame)
        search_frame.pack(fill="x", padx=6, pady=2)
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", lambda *_: self._filter_stocks())
        ttk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side="left", padx=4)

        list_frame = ttk.Frame(exch_frame)
        list_frame.pack(fill="both", expand=True, padx=6, pady=4)
        self.stock_list = tk.Listbox(list_frame, height=10)
        scroll = ttk.Scrollbar(list_frame, orient="vertical", command=self.stock_list.yview)
        self.stock_list.configure(yscrollcommand=scroll.set)
        self.stock_list.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        # 3. download options
        cond_frame = ttk.LabelFrame(self.root, text="3. Download options")
        cond_frame.pack(fill="x", padx=10, pady=6)

        row1 = ttk.Frame(cond_frame)
        row1.pack(fill="x", padx=6, pady=4)
        ttk.Label(row1, text="Report type:").pack(side="left")
        self.doc_type_var = tk.StringVar(value=list(DOC_TYPES.keys())[0])
        ttk.Combobox(row1, textvariable=self.doc_type_var, values=list(DOC_TYPES.keys()), state="readonly", width=18).pack(side="left", padx=4)
        ttk.Label(row1, text="Count:").pack(side="left", padx=(20, 0))
        self.limit_var = tk.StringVar(value="7")
        ttk.Entry(row1, textvariable=self.limit_var, width=8).pack(side="left", padx=4)
        ttk.Label(row1, text="(-1 = all)").pack(side="left", padx=4)

        row2 = ttk.Frame(cond_frame)
        row2.pack(fill="x", padx=6, pady=4)
        ttk.Label(row2, text="Report period (optional):").pack(side="left")
        self.period_from_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.period_from_var, width=12).pack(side="left", padx=4)
        ttk.Label(row2, text="~").pack(side="left")
        self.period_to_var = tk.StringVar()
        ttk.Entry(row2, textvariable=self.period_to_var, width=12).pack(side="left", padx=4)
        ttk.Label(row2, text="format YYYY-MM-DD").pack(side="left", padx=6)

        row3 = ttk.Frame(cond_frame)
        row3.pack(fill="x", padx=6, pady=4)
        ttk.Label(row3, text="Save to:").pack(side="left")
        self.out_dir_var = tk.StringVar(value=os.path.join(os.path.expanduser("~"), "Downloads", "finreport"))
        ttk.Entry(row3, textvariable=self.out_dir_var, width=40).pack(side="left", padx=4)
        ttk.Button(row3, text="Browse", command=self._browse_dir).pack(side="left", padx=4)

        ttk.Button(cond_frame, text="Download Markdown", command=self._download).pack(padx=6, pady=8)

        # 4. log
        log_frame = ttk.LabelFrame(self.root, text="4. Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=6)
        self.log_text = tk.Text(log_frame, height=8, state="disabled")
        self.log_text.pack(fill="both", expand=True, padx=6, pady=4)

    def _log(self, msg):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")

    # ---- actions ----
    def _connect(self):
        key = self.key_var.get().strip()
        if not key:
            messagebox.showwarning("Notice", "Please enter your API key")
            return
        ds = DataSinking(key)
        try:
            ds.list_exchanges()  # 验证 key 是否有效
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code == 401:
                messagebox.showerror("Error", "Invalid API key — click 'Get key' to get one.")
            else:
                messagebox.showerror("Error", f"Connection failed: {e}")
            return
        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}")
            return
        self.ds = ds
        self._save_config()  # 验证通过后自动记住
        self._log("Connected — key is valid")

    def _ensure_ds(self):
        if not self.ds:
            self._connect()
        return self.ds is not None

    def _load_stocks(self):
        if not self._ensure_ds():
            return
        exch = EXCHANGES[self.exch_var.get()]
        self._log(f"Loading {exch} stocks...")
        try:
            self.stocks = self.ds.list_stocks(exch)
            self._log(f"{len(self.stocks)} stocks")
            self._filter_stocks()
        except Exception as e:
            self._log(f"Failed to load: {e}")
            messagebox.showerror("Error", str(e))

    def _filter_stocks(self):
        kw = self.search_var.get().strip()
        self.stock_list.delete(0, "end")
        for s in self.stocks:
            code = s.get("stock_code", "")
            name = s.get("stock_name") or ""
            if kw and kw not in code and kw not in name:
                continue
            self.stock_list.insert("end", f"{code}  {name}")

    def _get_selected_code(self):
        sel = self.stock_list.curselection()
        if not sel:
            messagebox.showwarning("Notice", "Select a stock first")
            return None
        return self.stock_list.get(sel[0]).split()[0]

    def _browse_dir(self):
        d = filedialog.askdirectory()
        if d:
            self.out_dir_var.set(d)

    def _download(self):
        code = self._get_selected_code()
        if not code or not self._ensure_ds():
            return
        doc_type = DOC_TYPES[self.doc_type_var.get()]
        try:
            limit = int(self.limit_var.get().strip())
        except ValueError:
            messagebox.showwarning("Notice", "Count must be an integer (e.g. 7, or -1 for all)")
            return
        period_from = self.period_from_var.get().strip() or None
        period_to = self.period_to_var.get().strip() or None
        out_dir = self.out_dir_var.get().strip()
        if not out_dir:
            messagebox.showwarning("Notice", "Choose a save directory")
            return

        self._log(f"Downloading {code}: type={doc_type}, limit={limit}, period={period_from}~{period_to}")
        threading.Thread(
            target=self._do_download,
            args=(code, doc_type, limit, period_from, period_to, out_dir),
            daemon=True,
        ).start()

    def _do_download(self, code, doc_type, limit, period_from, period_to, out_dir):
        def log(msg):
            self.root.after(0, self._log, msg)
        try:
            reports = self.ds.get_stock_reports(code, period_from=period_from, period_to=period_to, limit=limit, doc_type=doc_type)
            os.makedirs(out_dir, exist_ok=True)
            n = 0
            for r in reports:
                r_code = r["stock_code"]
                r_type = r["doc_type"]
                period = r.get("report_period") or "unknown"
                year = str(period)[:4] if period else "unknown"
                ann = r.get("announcement_time")
                date = datetime.fromtimestamp(ann / 1000).strftime("%Y%m%d") if ann else "unknown"
                fname = f"{r_code}_{year}_{r_type}_{date}.md"
                with open(os.path.join(out_dir, fname), "w", encoding="utf-8") as f:
                    f.write(r.get("content", ""))
                n += 1
                log(f"  downloaded: {fname}")
            log(f"Done: {n} files -> {out_dir}")
        except Exception as e:
            log(f"Download failed: {e}")


def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, rel)


def main():
    root = tk.Tk()
    try:
        root.iconbitmap(resource_path("graham.ico"))
    except Exception:
        pass
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
