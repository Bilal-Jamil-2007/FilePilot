import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import threading
import time
import string

# ----------------------------
# Global Variables
# ----------------------------
searching = False
search_thread = None
drive_vars = {}   # dynamically populated { "C:\\": BooleanVar(), ... }

# ----------------------------
# Drive Detection
# ----------------------------
def get_drives():
    drives = []
    for letter in string.ascii_uppercase:
        d = f"{letter}:\\"
        if os.path.exists(d):
            drives.append(d)
    return drives

# ----------------------------
# Search Function
# ----------------------------
def search_operation(target, mode, drives):
    global searching
    start_time = time.time()
    found_items = []

    status_label.config(text="🔍 Searching...")

    try:
        for drive in drives:
            for root, dirs, files in os.walk(drive, topdown=True):
                if not searching:
                    status_label.config(text="⏹ Search stopped.")
                    return
                if mode == "file":
                    for file_name in files:
                        if target.lower() in file_name.lower():
                            found_items.append(os.path.join(root, file_name))
                elif mode == "folder":
                    for dir_name in dirs:
                        if target.lower() in dir_name.lower():
                            found_items.append(os.path.join(root, dir_name))
    except Exception as e:
        found_items.append(f"Error accessing {drive}: {e}")

    end_time = time.time()

    if found_items:
        result_box.insert(tk.END, f"🔍 Found {len(found_items)} result(s):\n", "highlight")
        for item in found_items:
            result_box.insert(tk.END, item + "\n")
        status_label.config(text=f"✅ Done - {len(found_items)} result(s) found.")
    else:
        result_box.insert(tk.END, "❌ No matches found.\n")
        status_label.config(text="❌ No matches found.")

    result_box.insert(tk.END, f"\n⏱ Time taken: {end_time - start_time:.2f} seconds\n")
    result_box.see(tk.END)

# ----------------------------
# Start Search
# ----------------------------
def start_search(mode, entry_widget):
    global searching, search_thread
    target = entry_widget.get().strip()

    # collect selected drives from dynamic checkboxes
    drives = [d for d, var in drive_vars.items() if var.get()]

    if not target:
        messagebox.showwarning("Input Error", "Please enter a search term.")
        return
    if not drives:
        messagebox.showwarning("Drive Error", "Please select at least one drive.")
        return

    # Clear old results
    result_box.delete(1.0, tk.END)

    searching = True
    status_label.config(text="🔎 Searching...")
    search_thread = threading.Thread(target=search_operation, args=(target, mode, drives))
    search_thread.start()

# ----------------------------
# Stop Search
# ----------------------------
def stop_search():
    global searching
    searching = False
    result_box.insert(tk.END, "\n⏹ Search stopped by user.\n", "stop")
    status_label.config(text="⏹ Search stopped by user.")
    result_box.see(tk.END)

# ----------------------------
# Clear Results
# ----------------------------
def clear_results():
    result_box.delete(1.0, tk.END)
    status_label.config(text="🧹 Results cleared.")

# ----------------------------
# Helpers to render drive checkboxes
# ----------------------------
def render_drive_checkboxes(parent_frame):
    """Populate drive checkboxes dynamically into parent_frame and update global drive_vars."""
    # clear previous (if switching between File/Folder screens)
    for w in parent_frame.winfo_children():
        w.destroy()

    tk.Label(parent_frame, text="Select Drives:", font=("Arial", 12), bg="#f0f8ff").pack(anchor="w")

    # (re)build drive_vars
    drive_vars.clear()
    row_frame = tk.Frame(parent_frame, bg="#f0f8ff")
    row_frame.pack(anchor="w", pady=2)

    for idx, d in enumerate(get_drives()):
        var = tk.BooleanVar()
        # auto-check C:\ for convenience (optional)
        if d.upper().startswith("C"):
            var.set(True)
        cb = tk.Checkbutton(row_frame, text=d, variable=var, bg="#f0f8ff")
        cb.grid(row=0, column=idx, padx=6, pady=2, sticky="w")
        drive_vars[d] = var

# ----------------------------
# File Search Window
# ----------------------------
def file_window():
    clear_frame()
    heading = tk.Label(main_frame, text="📄 File Search", font=("Arial", 16, "bold"), bg="#f0f8ff")
    heading.pack(pady=10)

    entry = tk.Entry(main_frame, width=40, font=("Arial", 12))
    entry.pack(pady=5)

    drive_frame = tk.Frame(main_frame, bg="#f0f8ff")
    drive_frame.pack(pady=5)
    render_drive_checkboxes(drive_frame)

    button_frame = tk.Frame(main_frame, bg="#f0f8ff")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="🔍 Search", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
              command=lambda: start_search("file", entry)).pack(side="left", padx=5)

    tk.Button(button_frame, text="⏹ Stop", font=("Arial", 12, "bold"), bg="#FF6347", fg="white",
              command=stop_search).pack(side="left", padx=5)

    tk.Button(button_frame, text="⬅ Back", font=("Arial", 12), command=main_window).pack(side="left", padx=5)

# ----------------------------
# Folder Search Window
# ----------------------------
def folder_window():
    clear_frame()
    heading = tk.Label(main_frame, text="📁 Folder Search", font=("Arial", 16, "bold"), bg="#f0f8ff")
    heading.pack(pady=10)

    entry = tk.Entry(main_frame, width=40, font=("Arial", 12))
    entry.pack(pady=5)

    drive_frame = tk.Frame(main_frame, bg="#f0f8ff")
    drive_frame.pack(pady=5)
    render_drive_checkboxes(drive_frame)

    button_frame = tk.Frame(main_frame, bg="#f0f8ff")
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="🔍 Search", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white",
              command=lambda: start_search("folder", entry)).pack(side="left", padx=5)

    tk.Button(button_frame, text="⏹ Stop", font=("Arial", 12, "bold"), bg="#FF6347", fg="white",
              command=stop_search).pack(side="left", padx=5)

    tk.Button(button_frame, text="⬅ Back", font=("Arial", 12), command=main_window).pack(side="left", padx=5)

# ----------------------------
# Main Menu
# ----------------------------
def main_window():
    clear_frame()
    heading = tk.Label(main_frame, text="🔎 Search App", font=("Arial", 18, "bold"), bg="#f0f8ff")
    heading.pack(pady=15)

    tk.Label(main_frame, text="What do you want to search?", font=("Arial", 12), bg="#f0f8ff").pack(pady=5)

    tk.Button(main_frame, text="📄 File", font=("Arial", 12, "bold"), width=15, bg="#2196F3", fg="white",
              command=file_window).pack(pady=5)

    tk.Button(main_frame, text="📁 Folder", font=("Arial", 12, "bold"), width=15, bg="#9C27B0", fg="white",
              command=folder_window).pack(pady=5)

# ----------------------------
# Utility Function
# ----------------------------
def clear_frame():
    for widget in main_frame.winfo_children():
        widget.destroy()

# ----------------------------
# Main App Setup
# ----------------------------
root = tk.Tk()
root.title("Search App")
root.geometry("700x650")
root.configure(bg="#f0f8ff")

# Main frame
main_frame = tk.Frame(root, bg="#f0f8ff")
main_frame.pack(fill="both", expand=True)

# Results box
result_box = scrolledtext.ScrolledText(root, width=80, height=15, font=("Consolas", 10))
result_box.pack(pady=10, padx=10)

# Clear button
clear_btn = tk.Button(root, text="🧹 Clear Results", font=("Arial", 12, "bold"), bg="#808080", fg="white",
                      command=clear_results)
clear_btn.pack(pady=5)

# Status Label
status_label = tk.Label(root, text="Ready", font=("Arial", 12), bg="#f0f8ff", fg="blue")
status_label.pack(pady=5)

# Text styling
result_box.tag_config("highlight", foreground="green", font=("Consolas", 10, "bold"))
result_box.tag_config("stop", foreground="red", font=("Consolas", 10, "italic"))

# Show main window
main_window()
root.mainloop()
