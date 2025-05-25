# Setup Instructions
# Install dependencies:

# bash
# Copy
# Edit
# pip install tkinterdnd2
# tkinter comes with Python, but tkinterdnd2 is needed for drag-and-drop.

# Save the script as convert_links_gui_dnd.py.

# Run with:

# bash
# Copy
# Edit
# python3 convert_links_gui_dnd.py


import os
import configparser
import tkinter as tk
from tkinter import filedialog, messagebox
import xml.etree.ElementTree as ET
import json
from tkinterdnd2 import DND_FILES, TkinterDnD

CONFIG_FILE = os.path.expanduser("~/.convert_links_config.json")

def extract_url_from_url_file(path):
    config = configparser.ConfigParser()
    config.read(path)
    try:
        return config["InternetShortcut"]["URL"]
    except Exception:
        return None

def extract_url_from_desktop_file(path):
    try:
        with open(path, "r") as f:
            for line in f:
                if line.startswith("Exec="):
                    url = line.strip().split("Exec=")[1]
                    if url.startswith("http"):
                        return url
    except Exception:
        pass
    return None

def extract_url_from_webloc_file(path):
    try:
        tree = ET.parse(path)
        dict_elem = tree.find(".//dict")
        key_elems = list(dict_elem)
        for i in range(len(key_elems)):
            if key_elems[i].tag == "key" and key_elems[i].text == "URL":
                url_elem = key_elems[i + 1]
                return url_elem.text
    except Exception:
        pass
    return None

def create_html_file(name, url, output_dir):
    safe_name = os.path.splitext(name)[0].replace(" ", "_") + ".html"
    path = os.path.join(output_dir, safe_name)
    html = f"""<!DOCTYPE html>
<html>
  <head>
    <meta http-equiv="refresh" content="0; url={url}">
    <title>{safe_name}</title>
  </head>
  <body>
    <p><a href="{url}">Click here if not redirected</a></p>
  </body>
</html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

def convert_links_to_html(folder):
    count = 0
    for root, _, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            url = None
            if file.endswith(".url"):
                url = extract_url_from_url_file(path)
            elif file.endswith(".desktop"):
                url = extract_url_from_desktop_file(path)
            elif file.endswith(".webloc"):
                url = extract_url_from_webloc_file(path)

            if url:
                create_html_file(file, url, root)
                count += 1
    return count

def load_last_folder():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("last_folder", os.path.expanduser("~"))
    return os.path.expanduser("~")

def save_last_folder(folder):
    with open(CONFIG_FILE, "w") as f:
        json.dump({"last_folder": folder}, f)

def process_folder(folder):
    if not os.path.isdir(folder):
        messagebox.showerror("Error", f"{folder} is not a valid directory.")
        return
    save_last_folder(folder)
    count = convert_links_to_html(folder)
    messagebox.showinfo("Done", f"{count} shortcut(s) converted to HTML in:\n{folder}")

def select_folder_gui():
    folder = filedialog.askdirectory(title="Select folder to scan", initialdir=load_last_folder())
    if folder:
        process_folder(folder)

def on_drop(event):
    path = event.data.strip().strip("{}")  # Handles spaces in folder names on Windows
    process_folder(path)

def main_gui():
    root = TkinterDnD.Tk()
    root.title("Convert .url/.desktop/.webloc to HTML")
    root.geometry("400x200")
    root.resizable(False, False)

    label = tk.Label(root, text="Drag folder here or click button below", font=("Arial", 12))
    label.pack(pady=20)

    drop_area = tk.Label(root, text="⬇️ Drop Folder Here ⬇️", relief="ridge", bd=2, width=30, height=4, bg="#f0f0f0")
    drop_area.pack(pady=10)
    drop_area.drop_target_register(DND_FILES)
    drop_area.dnd_bind("<<Drop>>", on_drop)

    btn = tk.Button(root, text="Choose Folder...", command=select_folder_gui)
    btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    try:
        from tkinterdnd2 import DND_FILES, TkinterDnD
    except ImportError:
        print("Please install tkinterdnd2 with: pip install tkinterdnd2")
        exit(1)
    main_gui()
