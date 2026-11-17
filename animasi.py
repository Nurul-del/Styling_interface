import tkinter as tk
from tkinter import ttk
import threading
import time


def blend(c1, c2, t):
    """Campur dua warna hex (#rrggbb). t=0 -> c1, t=1 -> c2."""
    a = [int(c1[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(c2[i:i + 2], 16) for i in (1, 3, 5)]
    r = [round(x + (y - x) * t) for x, y in zip(a, b)]
    return '#%02x%02x%02x' % tuple(r)


class AnimatedApp:
    PANEL_BG = '#2d2d2d'
    TITLE_FG = '#00ff88'
    TEXT_FG = '#ffffff'

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Animasi dan Transisi dengan ttk")
        self.root.geometry("800x700")
        self.root.configure(bg='#1a1a1a')

        # Animation variables
        self.animation_running = False
        self.progress_value = 0
        self.sliding = False
        self.fading = False

        self._setup_styles()
        self._buat_interface()

    # Tkinter tidak thread-safe: semua perubahan widget dari thread
    # dijadwalkan ke thread utama lewat root.after(0, ...).
    def _ui(self, func, *args):
        try:
            self.root.after(0, func, *args)
        except (RuntimeError, tk.TclError):
            pass  # jendela sudah ditutup

    def _setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')  # agar warna custom tampil di Windows

        # Dark theme styles
        self.style.configure('Dark.TFrame', background=self.PANEL_BG, relief='flat')

        self.style.configure('Dark.TLabel', background=self.PANEL_BG,
                             foreground=self.TEXT_FG, font=('Arial', 11))

        self.style.configure('Title.TLabel', background=self.PANEL_BG,
                             foreground=self.TITLE_FG, font=('Arial', 16, 'bold'))

        # Style khusus untuk konten yang di-fade (warna teksnya dianimasikan)
        self.style.configure('FadeTitle.TLabel', background=self.PANEL_BG,
                             foreground=self.TITLE_FG, font=('Arial', 16, 'bold'))
        self.style.configure('FadeText.TLabel', background=self.PANEL_BG,
                             foreground=self.TEXT_FG, font=('Arial', 11))

        self.style.configure('TLabelframe', background=self.PANEL_BG)
        self.style.configure('TLabelframe.Label', background=self.PANEL_BG,
                             foreground=self.TEXT_FG)

        self.style.configure('Animated.TButton', background='#00ff88',
                             foreground='#1a1a1a', borderwidth=0, focuscolor='none',
                             padding=(20, 10), font=('Arial', 10, 'bold'))
        self.style.map('Animated.TButton',
                       background=[('pressed', '#009954'), ('active', '#00cc6a')])

    def _buat_interface(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Header
        self.header_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
        self.header_frame.pack(fill='x', pady=(0, 20))

        self.title_label = ttk.Label(self.header_frame, text="🎬 Animation Demo",
                                     style='Title.TLabel')
        self.title_label.pack()

        # Progress animation section
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="Progress Animation", padding="20")
        self.progress_frame.pack(fill='x', pady=(0, 15))

        ttk.Label(self.progress_frame, text="Animated Progress Bar:",
                  style='Dark.TLabel').pack(anchor='w', pady=(0, 10))

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate',
                                            length=400, style='TProgressbar')
        self.progress_bar.pack(fill='x', pady=(0, 15))

        progress_controls = ttk.Frame(self.progress_frame, style='Dark.TFrame')
        progress_controls.pack(fill='x')

        ttk.Button(progress_controls, text="Start Animation", style='Animated.TButton',
                   command=self.start_progress_animation).pack(side='left', padx=(0, 10))
        ttk.Button(progress_controls, text="Stop Animation", style='Animated.TButton',
                   command=self.stop_animation).pack(side='left', padx=(0, 10))
        ttk.Button(progress_controls, text="Reset", style='Animated.TButton',
                   command=self.reset_progress).pack(side='left')

        # Sliding panel animation
        self.slide_frame = ttk.LabelFrame(self.main_frame, text="Sliding Panel", padding="20")
        self.slide_frame.pack(fill='x', pady=(0, 15))

        self.slide_container = ttk.Frame(self.slide_frame, style='Dark.TFrame', height=200)
        self.slide_container.pack(fill='x', pady=(0, 15))
        self.slide_container.pack_propagate(False)

        self.sliding_panel = ttk.Frame(self.slide_container, style='Dark.TFrame')
        self.sliding_panel.place(x=-300, y=0, width=300, height=200)

        panel_content = ttk.Frame(self.sliding_panel, style='Dark.TFrame')
        panel_content.pack(fill='both', expand=True, padx=20, pady=20)

        ttk.Label(panel_content, text="🎯 Sliding Panel Content",
                  style='Title.TLabel').pack()
        ttk.Label(panel_content, text="Panel ini dapat slide masuk dan keluar",
                  style='Dark.TLabel').pack(pady=(10, 0))

        slide_controls = ttk.Frame(self.slide_frame, style='Dark.TFrame')
        slide_controls.pack(fill='x')

        ttk.Button(slide_controls, text="Slide In", style='Animated.TButton',
                   command=self.slide_in).pack(side='left', padx=(0, 10))
        ttk.Button(slide_controls, text="Slide Out", style='Animated.TButton',
                   command=self.slide_out).pack(side='left')

        # Fade animation section
        self.fade_frame = ttk.LabelFrame(self.main_frame, text="Fade Animation", padding="20")
        self.fade_frame.pack(fill='both', expand=True)

        self.fade_content = ttk.Frame(self.fade_frame, style='Dark.TFrame')
        self.fade_content.pack(fill='both', expand=True, pady=(0, 15))

        ttk.Label(self.fade_content, text="✨ Fade Content",
                  style='FadeTitle.TLabel').pack(pady=20)
        ttk.Label(self.fade_content, text="Content ini dapat fade in/out dengan smooth transition",
                  style='FadeText.TLabel').pack()

        fade_controls = ttk.Frame(self.fade_frame, style='Dark.TFrame')
        fade_controls.pack(fill='x')

        ttk.Button(fade_controls, text="Fade Out", style='Animated.TButton',
                   command=self.fade_out).pack(side='left', padx=(0, 10))
        ttk.Button(fade_controls, text="Fade In", style='Animated.TButton',
                   command=self.fade_in).pack(side='left')

    # ---------- Progress ----------
    def start_progress_animation(self):
        if not self.animation_running:
            self.animation_running = True
            threading.Thread(target=self._animate_progress, daemon=True).start()

    def _animate_progress(self):
        while self.animation_running and self.progress_value < 100:
            self.progress_value += 1
            self._ui(self._set_progress, self.progress_value)
            time.sleep(0.05)  # 50ms per langkah

        if self.progress_value >= 100:
            self.animation_running = False

    def _set_progress(self, value):
        self.progress_bar['value'] = value

    def stop_animation(self):
        self.animation_running = False

    def reset_progress(self):
        self.animation_running = False
        self.progress_value = 0
        self.progress_bar['value'] = 0

    # ---------- Sliding ----------
    def slide_in(self):
        self._start_slide(-300, 0)

    def slide_out(self):
        self._start_slide(0, -300)

    def _start_slide(self, start_x, end_x):
        if self.sliding:
            return
        self.sliding = True
        threading.Thread(target=self._animate_slide, args=(start_x, end_x), daemon=True).start()

    def _animate_slide(self, start_x, end_x):
        steps = 30
        for i in range(steps + 1):
            current_x = start_x + (end_x - start_x) * (i / steps)
            self._ui(self._place_panel, current_x)
            time.sleep(0.02)  # 20ms per langkah
        self.sliding = False

    def _place_panel(self, x):
        self.sliding_panel.place(x=x, y=0, width=300, height=200)

    # ---------- Fade ----------
    def fade_out(self):
        if self.fading:
            return
        self.fading = True
        threading.Thread(target=self._animate_fade, args=(0.0, 1.0, True), daemon=True).start()

    def fade_in(self):
        if self.fading:
            return
        self.fading = True
        # Tampilkan lagi (warna teks masih menyatu dengan latar), lalu munculkan perlahan
        self.fade_content.pack(fill='both', expand=True, pady=(0, 15))
        threading.Thread(target=self._animate_fade, args=(1.0, 0.0, False), daemon=True).start()

    def _animate_fade(self, t_start, t_end, hide_at_end):
        steps = 20
        for i in range(steps + 1):
            t = t_start + (t_end - t_start) * (i / steps)
            self._ui(self._set_fade, t)
            time.sleep(0.05)
        if hide_at_end:
            self._ui(self.fade_content.pack_forget)
        self.fading = False

    def _set_fade(self, t):
        """t=0: warna asli, t=1: menyatu dengan latar (hilang)."""
        self.style.configure('FadeTitle.TLabel', foreground=blend(self.TITLE_FG, self.PANEL_BG, t))
        self.style.configure('FadeText.TLabel', foreground=blend(self.TEXT_FG, self.PANEL_BG, t))

    def run(self):
        self.root.mainloop()


# Jalankan aplikasi
if __name__ == "__main__":
    app = AnimatedApp()
    app.run()