import tkinter as tk
from tkinter import ttk


class ResponsiveApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Responsive Design dengan ttk")
        self.root.geometry("800x600")
        # minsize dibuat kecil agar simulasi mobile (lebar 400) benar-benar bisa tercapai
        self.root.minsize(350, 300)

        # Variabel untuk tracking ukuran window
        self.current_width = 800
        self.current_height = 600
        self.current_mode = None

        self._setup_styles()
        self._buat_interface()
        self._bind_events()

    def _setup_styles(self):
        self.style = ttk.Style()

        # Style untuk desktop (default)
        self.style.configure('Desktop.TLabel', font=('Arial', 12), padding=(10, 5))
        # Style untuk tablet
        self.style.configure('Tablet.TLabel', font=('Arial', 10), padding=(8, 4))
        # Style untuk mobile
        self.style.configure('Mobile.TLabel', font=('Arial', 9), padding=(5, 3))

        # Button styles
        self.style.configure('Desktop.TButton', padding=(15, 8), font=('Arial', 11))
        self.style.configure('Tablet.TButton', padding=(12, 6), font=('Arial', 10))
        self.style.configure('Mobile.TButton', padding=(8, 4), font=('Arial', 9))

    def _buat_interface(self):
        # Main container dengan scrollable frame
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        # Lebar frame di dalam canvas mengikuti lebar canvas
        self.canvas.bind(
            "<Configure>",
            lambda e: self.canvas.itemconfigure(self.canvas_window, width=e.width)
        )

        # Header section
        self.header_frame = ttk.Frame(self.scrollable_frame)
        self.header_frame.pack(fill='x', padx=20, pady=20)

        self.title_label = ttk.Label(self.header_frame, text="Responsive Design Demo",
                                     style='Desktop.TLabel')
        self.title_label.pack()

        self.size_label = ttk.Label(self.header_frame,
                                    text=f"Window Size: {self.current_width}x{self.current_height}",
                                    style='Desktop.TLabel')
        self.size_label.pack(pady=(5, 0))

        # Content grid yang akan berubah layout
        self.content_frame = ttk.Frame(self.scrollable_frame)
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 20))

        # Cards yang akan di-reposition berdasarkan ukuran window
        self.cards = []
        for i in range(6):
            card = ttk.LabelFrame(self.content_frame, text=f"Card {i + 1}", padding="15")

            ttk.Label(card, text=f"Content untuk card {i + 1}",
                      style='Desktop.TLabel').pack()
            ttk.Button(card, text=f"Action {i + 1}",
                       style='Desktop.TButton').pack(pady=(10, 0))

            self.cards.append(card)

        # Control panel
        self.control_frame = ttk.LabelFrame(self.scrollable_frame, text="Controls", padding="15")
        self.control_frame.pack(fill='x', padx=20, pady=(0, 20))

        ttk.Button(self.control_frame, text="Simulate Mobile (400x600)",
                   command=lambda: self.resize_window(400, 600),
                   style='Desktop.TButton').pack(side='left', padx=(0, 10))

        ttk.Button(self.control_frame, text="Simulate Tablet (600x800)",
                   command=lambda: self.resize_window(600, 800),
                   style='Desktop.TButton').pack(side='left', padx=(0, 10))

        ttk.Button(self.control_frame, text="Simulate Desktop (800x600)",
                   command=lambda: self.resize_window(800, 600),
                   style='Desktop.TButton').pack(side='left')

        # Pack canvas dan scrollbar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Initial layout
        self._update_layout()

    def _bind_events(self):
        self.root.bind('<Configure>', self._on_window_resize)

    def _on_window_resize(self, event):
        if event.widget == self.root:
            self.current_width = self.root.winfo_width()
            self.current_height = self.root.winfo_height()
            self.size_label.config(text=f"Window Size: {self.current_width}x{self.current_height}")
            self._update_layout()

    def _update_layout(self):
        # Tentukan mode berdasarkan lebar window
        if self.current_width < 500:
            mode = 'Mobile'
        elif self.current_width < 700:
            mode = 'Tablet'
        else:
            mode = 'Desktop'

        # Susun ulang hanya jika mode berubah
        if mode == self.current_mode:
            return
        self.current_mode = mode

        for card in self.cards:
            card.grid_forget()

        if mode == 'Mobile':
            self._apply_grid_layout(1, 'Mobile')    # 1 kolom
        elif mode == 'Tablet':
            self._apply_grid_layout(2, 'Tablet')    # 2 kolom
        else:
            self._apply_grid_layout(3, 'Desktop')   # 3 kolom

    def _apply_grid_layout(self, columns, size):
        # Reset bobot kolom, lalu aktifkan sebanyak kolom yang dipakai
        for c in range(3):
            self.content_frame.columnconfigure(c, weight=1 if c < columns else 0, uniform='kolom')

        for i, card in enumerate(self.cards):
            row, col = divmod(i, columns)
            card.grid(row=row, column=col, sticky='nsew', padx=5, pady=(0, 10))

        self._update_styles(size)

    def _update_styles(self, size):
        label_style = f'{size}.TLabel'
        button_style = f'{size}.TButton'

        self.title_label.config(style=label_style)
        self.size_label.config(style=label_style)

        # Update semua label dan button di dalam card
        for card in self.cards:
            for child in card.winfo_children():
                if isinstance(child, ttk.Label):
                    child.config(style=label_style)
                elif isinstance(child, ttk.Button):
                    child.config(style=button_style)

    def resize_window(self, width, height):
        self.root.geometry(f"{width}x{height}")

    def run(self):
        self.root.mainloop()


# Jalankan aplikasi
if __name__ == "__main__":
    app = ResponsiveApp()
    app.run()