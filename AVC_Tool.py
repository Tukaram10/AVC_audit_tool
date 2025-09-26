import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import logging

# ---------------- LOGGING SETUP ----------------
LOG_FILE = r"D:\VehicleAuditTool.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Application started")

# ---------------- RESOURCE HELPER ----------------
def resource_path(relative_path):
    """Get absolute path to resource (works for .py, .pyc, and PyInstaller .exe)"""
    try:
        base_path = sys._MEIPASS  # PyInstaller temp dir
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class VehicleAuditTool:
    def __init__(self, root):
        self.root = root
        self.root.title("AVC Vehicle Audit Tool")
        self.root.configure(bg="black")

        self.image_dir = ""
        self.labels_file = ""
        self.image_files = []
        self.labels = []
        self.current_index = 0
        self.selected_class = tk.StringVar()

        # --- Top Frame ---
        top_frame = tk.Frame(root, bg="black")
        top_frame.pack(fill="x", pady=5)

        tk.Label(top_frame, text="Image Dir:", fg="orange", bg="black").grid(row=0, column=0, sticky="w")
        self.image_dir_entry = tk.Entry(top_frame, width=50)
        self.image_dir_entry.grid(row=0, column=1)
        self.create_button(top_frame, "Browse", self.browse_image_dir).grid(row=0, column=2, padx=5)

        tk.Label(top_frame, text="Labels File:", fg="orange", bg="black").grid(row=1, column=0, sticky="w")
        self.labels_file_entry = tk.Entry(top_frame, width=50)
        self.labels_file_entry.grid(row=1, column=1)
        self.create_button(top_frame, "Browse", self.browse_labels_file).grid(row=1, column=2, padx=5)

        self.create_button(top_frame, "Load", self.load_data).grid(row=2, column=1, pady=5)
        self.create_button(top_frame, "Save", self.save_labels).grid(row=2, column=2, pady=5)

        # --- Main Frame ---
        main_frame = tk.Frame(root, bg="black")
        main_frame.pack(fill="both", expand=True)

        self.listbox = tk.Listbox(main_frame, width=30, bg="black", fg="orange")
        self.listbox.pack(side="left", fill="y", padx=5, pady=5)
        self.listbox.bind("<<ListboxSelect>>", self.on_select_image)

        self.image_label = tk.Label(main_frame, bg="black")
        self.image_label.pack(side="left", expand=True, padx=5, pady=5)

        self.labels_frame = tk.Frame(main_frame, bg="black")
        self.labels_frame.pack(side="right", fill="y", padx=5, pady=5)

        tk.Label(self.labels_frame, text="Select Class", fg="orange", bg="black").pack(pady=2)
        self.radio_buttons = {}

        # --- Navigation ---
        nav_frame = tk.Frame(root, bg="black")
        nav_frame.pack(fill="x", pady=5)
        self.create_button(nav_frame, "Prev", self.prev_image).pack(side="left", padx=10)
        self.create_button(nav_frame, "Next", self.next_image).pack(side="left", padx=10)
        self.create_button(nav_frame, "Delete", self.delete_image).pack(side="left", padx=10)

    # ---------------- BUTTON CREATION ----------------
    def create_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command, bg="#1a1a1a", fg="orange",
                        activebackground="orange", activeforeground="black", relief="flat", bd=1)
        btn.bind("<Enter>", lambda e: btn.config(bg="orange", fg="black"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#1a1a1a", fg="orange"))
        return btn

    # ---------------- FILE SELECTION ----------------
    def browse_image_dir(self):
        self.image_dir = filedialog.askdirectory()
        self.image_dir_entry.delete(0, tk.END)
        self.image_dir_entry.insert(0, self.image_dir)
        logging.info(f"Selected image directory: {self.image_dir}")

    def browse_labels_file(self):
        self.labels_file = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        self.labels_file_entry.delete(0, tk.END)
        self.labels_file_entry.insert(0, self.labels_file)
        logging.info(f"Selected labels file: {self.labels_file}")

    # ---------------- LOAD DATA ----------------
    def load_data(self):
        if not self.image_dir or not self.labels_file:
            messagebox.showerror("Error", "Select image directory and labels file.")
            return
        self.image_files = [f for f in os.listdir(self.image_dir) if f.lower().endswith((".jpg", ".png"))]
        self.labels = [line.strip() for line in open(self.labels_file, "r")]

        self.listbox.delete(0, tk.END)
        for f in self.image_files:
            self.listbox.insert(tk.END, f)

        for widget in self.labels_frame.winfo_children()[1:]:
            widget.destroy()
        self.radio_buttons.clear()
        for lbl in self.labels:
            rb = tk.Radiobutton(self.labels_frame, text=lbl, variable=self.selected_class, value=lbl,
                                fg="orange", bg="black", selectcolor="black", command=self.select_class_animation)
            rb.pack(anchor="w")
            self.radio_buttons[lbl] = rb

        logging.info("Data loaded successfully")

    # ---------------- CLASS SELECTION ----------------
    def select_class_animation(self):
        selected = self.selected_class.get()
        for lbl, rb in self.radio_buttons.items():
            if lbl == selected:
                rb.config(bg="orange", fg="black")
            else:
                rb.config(bg="black", fg="orange")
        logging.info(f"Selected class: {selected}")

    # ---------------- IMAGE DISPLAY ----------------
    def show_image(self, index):
        if not self.image_files:
            return
        file_path = os.path.join(self.image_dir, self.image_files[index])
        img = Image.open(file_path)
        img.thumbnail((600, 600))
        img_tk = ImageTk.PhotoImage(img)
        self.image_label.config(image=img_tk)
        self.image_label.image = img_tk
        logging.info(f"Displayed image: {file_path}")

    def on_select_image(self, event):
        if not self.listbox.curselection():
            return
        self.current_index = self.listbox.curselection()[0]
        self.show_image(self.current_index)

    # ---------------- NAVIGATION ----------------
    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image(self.current_index)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.current_index)

    def next_image(self):
        if self.current_index < len(self.image_files) - 1:
            self.current_index += 1
            self.show_image(self.current_index)
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.current_index)

    def delete_image(self):
        if not self.image_files:
            return
        try:
            file_to_delete = os.path.join(self.image_dir, self.image_files[self.current_index])
            os.remove(file_to_delete)
            logging.info(f"Deleted image: {file_to_delete}")
            del self.image_files[self.current_index]
            self.listbox.delete(self.current_index)
            if self.image_files:
                self.current_index = max(0, self.current_index - 1)
                self.show_image(self.current_index)
        except Exception as e:
            logging.error(f"Error deleting image: {e}")

    # ---------------- SAVE LABELS ----------------
    def save_labels(self):
        if not self.labels_file:
            messagebox.showerror("Error", "No labels file to save.")
            return
        try:
            with open(self.labels_file, "w") as f:
                for lbl in self.labels:
                    f.write(lbl + "\n")
            messagebox.showinfo("Saved", "Labels saved successfully.")
            logging.info("Labels saved successfully")
        except Exception as e:
            logging.error(f"Error saving labels: {e}")


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = VehicleAuditTool(root)
        root.mainloop()
    except Exception as e:
        logging.critical(f"Fatal error: {e}")
