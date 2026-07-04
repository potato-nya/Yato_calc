import os
import tkinter as tk
from tkinter import filedialog

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None
    ImageTk = None


class BackgroundDebugWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("背景图调试窗口 v4.0")
        self.geometry("1000x700")
        self.configure(bg="#f5f5f5")

        self.background_label = tk.Label(self, bg="#f5f5f5")
        self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.background_label.lower()

        self.controls = tk.Frame(self, bg="#f5f5f5")
        self.controls.pack(side=tk.TOP, fill=tk.X, padx=12, pady=12)

        tk.Button(self.controls, text="上传图片", command=self.choose_background).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(self.controls, text="清除背景", command=self.clear_background).pack(side=tk.LEFT)

        self.bind("<Configure>", self.refresh_background)
        self.refresh_background()

    def _load_background(self, path, size=None):
        if not path or not os.path.exists(path):
            return None
        if Image is not None and ImageTk is not None:
            try:
                image = Image.open(path)
                if image.mode != "RGBA":
                    image = image.convert("RGBA")
                if size:
                    image = image.resize(size, Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS)
                return ImageTk.PhotoImage(image)
            except Exception:
                pass
        try:
            return tk.PhotoImage(file=path)
        except Exception:
            return None

    def refresh_background(self, event=None):
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        photo = self._load_background(self.current_path, size=(width, height)) if hasattr(self, "current_path") else None
        if photo is None:
            return
        self.background_label.configure(image=photo)
        self.background_label.image = photo

    def choose_background(self):
        path = filedialog.askopenfilename(
            title="选择背景图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp *.gif"), ("所有文件", "*.*")],
        )
        if path:
            self.current_path = path
            self.refresh_background()

    def clear_background(self):
        if hasattr(self, "current_path"):
            del self.current_path
        self.background_label.configure(image="")


if __name__ == "__main__":
    app = BackgroundDebugWindow()
    app.mainloop()
