import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont
import requests
import xml.etree.ElementTree as ET
import threading
from datetime import datetime, timedelta


class GIBSExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("NASA GIBS 2026 High-Density Discovery")
        self.root.geometry("1200x950")

        # --- Dynamic Style Configuration ---
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Measure font to prevent overlapping rows
        self.tree_font = tkfont.Font(family="Helvetica", size=10)
        row_pad = self.tree_font.metrics("linespace") + 12  # Extra padding for Linux/Ubuntu

        self.style.configure("Treeview", rowheight=row_pad, font=self.tree_font)
        self.style.configure("Treeview.Heading", font=(self.tree_font.actual("family"), 10, "bold"))

        self.layers_data = {}
        # Using the /all/ endpoint to ensure we catch every 2026 heartbeat
        self.xml_url = "https://gibs.earthdata.nasa.gov/wmts/epsg4326/all/1.0.0/WMTSCapabilities.xml"
        self.freshness_threshold = datetime.now() - timedelta(days=30)

        self.setup_ui()
        threading.Thread(target=self.fetch_layers, daemon=True).start()

    def setup_ui(self):
        top = ttk.Frame(self.root, padding="10")
        top.pack(fill=tk.X)

        ttk.Label(top, text="🔍 Filter (ID or Title):").pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_list)
        ttk.Entry(top, textvariable=self.search_var, width=50).pack(side=tk.LEFT, padx=10)

        self.status = ttk.Label(top, text="🛰️ Parsing NASA Manifest...", foreground="orange")
        self.status.pack(side=tk.RIGHT)

        paned = ttk.PanedWindow(self.root, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Main List (25 rows)
        tree_frame = ttk.Frame(paned)
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Title", "Pulse"), show='headings', height=25)
        self.tree.heading("ID", text="Identifier")
        self.tree.heading("Title", text="Descriptive Title")
        self.tree.heading("Pulse", text="Latest Update")

        self.tree.column("ID", width=350)
        self.tree.column("Title", width=450)
        self.tree.column("Pulse", width=120, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        paned.add(tree_frame, weight=4)

        # Details
        self.details = tk.Text(paned, height=8, state='disabled', bg="#1a1a1a", fg="#00ff41",
                               font=('Courier New', 11), padx=15, pady=15)
        paned.add(self.details, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.handle_selection)

    def fetch_layers(self):
        try:
            r = requests.get(self.xml_url, timeout=45)
            root_xml = ET.fromstring(r.content)
            ns = {'w': 'http://www.opengis.net/wmts/1.0', 'o': 'http://www.opengis.net/ows/1.1'}

            valid = 0
            for layer in root_xml.findall(".//w:Layer", ns):
                ident = layer.find("o:Identifier", ns).text
                title = layer.find("o:Title", ns).text if layer.find("o:Title", ns) is not None else "N/A"
                time_node = layer.find(".//w:Dimension[o:Identifier='Time']/w:Value", ns)

                if time_node is not None:
                    try:
                        # Fixed Logic for end date extraction
                        full_text = time_node.text
                        end_date_str = full_text.split('/')[-2] if '/' in full_text else full_text
                        end_dt = datetime.strptime(end_date_str, "%Y-%m-%d")

                        if end_dt >= self.freshness_threshold:
                            self.layers_data[ident] = {
                                'end': end_date_str,
                                'range': full_text,
                                'title': title
                            }
                            valid += 1
                    except:
                        continue

            self.root.after(0, self.update_list, sorted(self.layers_data.keys()))
            self.root.after(0, lambda: self.status.config(text=f"✅ {valid} Live Layers Found", foreground="green"))
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("NASA Error", str(e)))

    def update_list(self, keys):
        self.tree.delete(*self.tree.get_children())
        for k in keys:
            d = self.layers_data[k]
            self.tree.insert("", tk.END, values=(k, d['title'], d['end']))

    def filter_list(self, *args):
        term = self.search_var.get().lower()
        keys = [k for k in self.layers_data.keys() if term in k.lower() or term in self.layers_data[k]['title'].lower()]
        self.update_list(sorted(keys))

    def handle_selection(self, event):
        sel = self.tree.selection()
        if not sel: return
        layer_id = self.tree.item(sel[0], "values")[0]
        d = self.layers_data[layer_id]

        info = f"🚀 IDENTIFIER : {layer_id}\n📝 TITLE      : {d['title']}\n📅 DATA RANGE : {d['range'].replace('/', '  TO  ')}\n"
        info += "=" * 70 + "\nCOPIED TO CLIPBOARD"

        self.details.config(state='normal')
        self.details.delete('1.0', tk.END);
        self.details.insert(tk.END, info)
        self.details.config(state='disabled')

        self.root.clipboard_clear();
        self.root.clipboard_append(layer_id)


if __name__ == "__main__":
    root = tk.Tk()
    GIBSExplorer(root)
    root.mainloop()
