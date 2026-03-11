#!/usr/bin/env python3
"""
===============================================================================
🚀 PROJECT      : BeUlta Satellite Suite
📦 MODULE       : gibs_explorer.py
👤 AUTHOR        : Reza / BeUlta Suite
🔖 VERSION       : 1.9.0
📅 LAST UPDATE  : 2026-03-11
⚖️ COPYRIGHT     : (c) 2026 ParkCircus Productions
📜 LICENSE       : MIT License
===============================================================================

📑 VERSION HISTORY:
    - 1.8.0: Deep Sweep Metadata Parser with Regex date extraction.
    - 1.9.0: Active-Only Filter. Suppressed [HISTORIC] layers. Refined Status
             column to icon-only (⭐/⏳). Updated stats to show Active/Recent.

📝 DESCRIPTION:
    A high-precision discovery tool for NASA GIBS. This version filters out
    legacy data to show only contemporary 2025-2026 satellite streams.
===============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import requests
import xml.etree.ElementTree as ET
import threading
import re


class GIBSExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("NASA GIBS 2026 Discovery (v1.9.0 Active-Only)")
        self.root.geometry("1200x900")

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.tree_font = tkfont.Font(family="Helvetica", size=10)
        self.style.configure("Treeview", rowheight=32, font=self.tree_font)

        self.layers_data = {}
        self.xml_url = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/all/1.0.0/WMTSCapabilities.xml"

        self.setup_ui()
        threading.Thread(target=self.fetch_layers, daemon=True).start()

    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(header_frame, text="🔍 Search: ").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_list)

        self.search_entry = ttk.Entry(header_frame, textvariable=self.search_var, width=35)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        # Updated Eye-Candy: Shows counts for the two visible categories
        self.stats_label = ttk.Label(header_frame, text="0 ⭐ | 0 ⏳", font=("Helvetica", 10, "bold"))
        self.stats_label.pack(side=tk.LEFT, padx=15)

        self.status = ttk.Label(header_frame, text="⏳ Analyzing Live Streams...", foreground="orange")
        self.status.pack(side=tk.RIGHT)

        # --- Table Configuration ---
        columns = ("status", "id", "title", "data_range")
        self.tree = ttk.Treeview(main_frame, columns=columns, show='headings')

        self.tree.heading("status", text="")
        self.tree.heading("id", text="NASA Identifier")
        self.tree.heading("title", text="Description")
        self.tree.heading("data_range", text="Temporal Metadata")

        self.tree.column("status", width=35, anchor="center")
        self.tree.column("id", width=380)
        self.tree.column("title", width=420)
        self.tree.column("data_range", width=260)

        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, in_=self.tree)

        self.details = tk.Text(main_frame, height=5, state='disabled', background="#fdfdfd", font=("Courier", 10))
        self.details.pack(fill=tk.X, pady=(10, 0))
        self.tree.bind("<<TreeviewSelect>>", self.handle_selection)

    def fetch_layers(self):
        try:
            response = requests.get(self.xml_url, timeout=60)
            response.raise_for_status()
            root = ET.fromstring(response.content)

            ns = {'wmts': 'http://www.opengis.net/wmts/1.0', 'owc': 'http://www.opengis.net/ows/1.1'}

            for layer in root.findall('.//wmts:Layer', ns):
                lid = layer.find('owc:Identifier', ns).text
                title = layer.find('owc:Title', ns).text

                layer_xml_str = ET.tostring(layer, encoding='unicode')
                dates = re.findall(r'\d{4}-\d{2}-\d{2}', layer_xml_str)
                latest = max(dates) if dates else "N/A"

                # Check for Continuous markers
                if "9999-12-31" in layer_xml_str:
                    latest = "2026 (NRT)"
                    display_range = "Continuous / 2026 NRT"
                elif len(dates) >= 2:
                    display_range = f"{min(dates)} TO {max(dates)}"
                elif len(dates) == 1:
                    display_range = f"Active since {dates[0]}"
                else:
                    display_range = "N/A"

                # Logic: Only keep it if it's 2025 or 2026
                if "2026" in latest or "2025" in latest or "nrt" in latest.lower():
                    self.layers_data[lid] = {
                        'title': title,
                        'range': display_range,
                        'latest': latest,
                        'raw': layer_xml_str.lower()
                    }

            self.root.after(0, self.update_list, sorted(self.layers_data.keys()))
            self.root.after(0, lambda: self.status.config(text="✅ Sync Ready", foreground="green"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("NASA Error", str(e)))

    def update_list(self, keys):
        self.tree.delete(*self.tree.get_children())
        star_count = 0
        hour_count = 0

        for k in keys:
            d = self.layers_data[k]

            if "2026" in d['latest'] or "nrt" in d['latest'].lower():
                status_icon = "⭐"
                star_count += 1
            else:
                status_icon = "⏳"
                hour_count += 1

            self.tree.insert("", tk.END, values=(status_icon, k, d['title'], d['range']))

        self.stats_label.config(text=f"📊 {star_count} ⭐ | {hour_count} ⏳")

    def filter_list(self, *args):
        query = self.search_var.get().lower().strip()
        tokens = query.split()

        if not tokens:
            self.update_list(sorted(self.layers_data.keys()))
            return

        matches = []
        for lid, meta in self.layers_data.items():
            if all(t in meta['raw'] or t in lid.lower() or t in meta['title'].lower() for t in tokens):
                matches.append(lid)

        self.update_list(sorted(matches))

    def handle_selection(self, event):
        sel = self.tree.selection()
        if not sel: return
        lid = self.tree.item(sel[0], "values")[1]
        meta = self.layers_data[lid]

        info = f"🚀 ID: {lid}\n📅 TEMPORAL: {meta['range']}\n"
        info += "-" * 60 + "\n[ID COPIED TO CLIPBOARD]"

        self.details.config(state='normal')
        self.details.delete('1.0', tk.END)
        self.details.insert(tk.END, info)
        self.details.config(state='disabled')

        self.root.clipboard_clear()
        self.root.clipboard_append(lid)


if __name__ == "__main__":
    root = tk.Tk()
    app = GIBSExplorer(root)
    root.mainloop()
