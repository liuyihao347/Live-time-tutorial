import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import sys
from pathlib import Path
from datetime import datetime
import ctypes  # For Windows DPI awareness

# Set Windows DPI awareness for crisp rendering on high-DPI displays
if sys.platform == "win32":
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # Per-monitor DPI aware
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()  # Fallback
        except Exception:
            pass

try:
    from PIL import ImageGrab
    HAS_PIL = True
except Exception:
    HAS_PIL = False

def _default_notebook_dir() -> Path:
    return Path.home() / "Desktop" / "Notebook"


def _config_path() -> Path:
    return Path.home() / ".live-time-tutorial" / "config.json"


def _load_config() -> dict:
    cfg_path = _config_path()
    try:
        if cfg_path.exists():
            return json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {"notebookPath": str(_default_notebook_dir())}


def _save_config(cfg: dict) -> None:
    cfg_path = _config_path()
    cfg_path.parent.mkdir(parents=True, exist_ok=True)
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")


def _sanitize_filename(name: str) -> str:
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "")
    name = " ".join(name.split()).strip()
    return name[:80] if len(name) > 80 else name


def _extract_points(text: str) -> list[str]:
    if not text:
        return []
    return [p.strip() for p in text.replace("\n", "|").split("|") if p.strip()]


def _capture_gui_screenshot(root: tk.Tk, notebook_dir: Path, topic: str) -> Path:
    """Capture GUI screenshot and save as PNG."""
    if not HAS_PIL:
        raise RuntimeError("Pillow is required for screenshot. Install with: pip install Pillow")
    
    # Ensure window is fully rendered
    root.update_idletasks()
    root.update()
    
    # Get window geometry
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    width = root.winfo_width()
    height = root.winfo_height()
    
    # Capture screenshot
    screenshot = ImageGrab.grab(bbox=(x, y, x + width, y + height))
    
    # Save as PNG directly to notebook_dir
    filename = _sanitize_filename(topic) + ".png"
    png_path = notebook_dir / filename
    screenshot.save(str(png_path), "PNG", dpi=(144, 144))
    
    return png_path


class QuizWindow:
    def __init__(self, quiz_data):
        self.quiz_data = quiz_data
        self.answered = False
        self.selected_index = None
        self.is_correct = False
        self.saved_to_notebook = False
        self.screenshot_path = None
        self.option_rows = []
        self._density_job = None
        self.user_feedback = ""

        self.config = _load_config()
        self.notebook_dir = Path(self.config.get("notebookPath") or str(_default_notebook_dir()))

        self.root = tk.Tk()
        self.root.title(f"Live-time-tutorial - {quiz_data.get('category', 'Quiz')}")
        self.root.configure(bg="#0A1220")

        # Size window near-fullscreen so quiz is fully visible on first pop-up.
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        width = min(int(sw * 0.98), 2400)
        height = min(int(sh * 0.98), 1800)  # Increased from 0.96 and 1600
        x = (sw - width) // 2
        y = max(0, (sh - height) // 2 - 10)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        self.root.minsize(1024, 1024)  # Increased min height from 940
        
        self._setup_style()
        self.setup_ui()
        self.root.update_idletasks()
        self._update_option_density()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Signal that the window is ready
        print("WINDOW_READY", flush=True)
        
        self.root.mainloop()

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("App.TFrame", background="#0A1220")
        style.configure("Card.TFrame", background="#101B2D")
        style.configure("Title.TLabel", background="#101B2D", foreground="#F8FAFC", font=("Segoe UI", 15, "bold"))
        style.configure("H2.TLabel", background="#101B2D", foreground="#E2E8F0", font=("Segoe UI", 11, "bold"))
        style.configure("Muted.TLabel", background="#101B2D", foreground="#9FB0CB", font=("Segoe UI", 9))
        style.configure("MutedBg.TLabel", background="#0A1220", foreground="#9FB0CB", font=("Segoe UI", 9))
        style.configure("Pill.TLabel", background="#1A2A44", foreground="#93C5FD", font=("Segoe UI", 9, "bold"))
        style.configure("Success.TLabel", background="#101B2D", foreground="#34D399", font=("Segoe UI", 11, "bold"))
        style.configure("Danger.TLabel", background="#101B2D", foreground="#F87171", font=("Segoe UI", 11, "bold"))
        
        style.configure("Primary.TButton", 
                        background="#F8FAFC", 
                        foreground="#0A1220", 
                        font=("Segoe UI", 10, "bold"), 
                        padding=(14, 8))
        style.map("Primary.TButton", 
                  background=[("active", "#E2E8F0"), ("disabled", "#334155")],
                  foreground=[("disabled", "#9FB0CB")])

        style.configure("Secondary.TButton", 
                        background="#F8FAFC", 
                        foreground="#0A1220", 
                        font=("Segoe UI", 10, "bold"), 
                        padding=(10, 6))
        style.map("Secondary.TButton", 
                  background=[("active", "#E2E8F0")])
    
    def setup_ui(self):
        app = ttk.Frame(self.root, padding=(16, 10), style="App.TFrame")
        app.pack(fill=tk.BOTH, expand=True)

        # ── Compact header bar ──
        header = ttk.Frame(app, padding=(14, 8), style="Card.TFrame")
        header.pack(fill=tk.X)

        hdr_left = ttk.Frame(header, style="Card.TFrame")
        hdr_left.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(hdr_left, text="Live-time-tutorial", style="Title.TLabel").pack(side=tk.LEFT)
        ttk.Label(hdr_left, text="  Interactive knowledge quiz with instant feedback", style="Muted.TLabel").pack(side=tk.LEFT, padx=(8, 0))

        ttk.Button(
            header,
            text="Change...",
            style="Secondary.TButton",
            command=self.change_notebook_path,
        ).pack(side=tk.RIGHT)

        self.notebook_path_label = ttk.Label(
            header,
            text=f"Notebook: {self.notebook_dir}",
            style="Muted.TLabel",
        )
        self.notebook_path_label.pack(side=tk.RIGHT, padx=(0, 10))

        # ── Two-column content using PanedWindow for flexible split ──
        content = ttk.Frame(app, padding=(0, 10, 0, 6), style="App.TFrame")
        content.pack(fill=tk.BOTH, expand=True)

        content.columnconfigure(0, weight=2)
        content.columnconfigure(1, weight=3)
        content.rowconfigure(0, weight=5)
        content.rowconfigure(1, weight=1)

        # ── Left column: Question + Options (fills vertically) ──
        left = ttk.Frame(content, style="Card.TFrame", padding=14)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left.rowconfigure(1, weight=1)   # question area gets some stretch
        left.rowconfigure(2, weight=3)   # options area gets more stretch

        ttk.Label(left, text="Question", style="H2.TLabel").grid(row=0, column=0, sticky="w")

        self.question_text = tk.Text(
            left,
            height=4,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#0A1220",
            fg="#E2E8F0",
            relief=tk.FLAT,
            padx=10,
            pady=8,
            highlightthickness=1,
            highlightbackground="#2D3B56",
            insertbackground="#E2E8F0",
        )
        self.question_text.insert("1.0", self.quiz_data.get("question", ""))
        self.question_text.config(state=tk.DISABLED)
        self.question_text.grid(row=1, column=0, sticky="nsew", pady=(6, 10))

        left.columnconfigure(0, weight=1)

        opt_section = ttk.Frame(left, style="Card.TFrame")
        opt_section.grid(row=2, column=0, sticky="nsew", pady=(0, 0))
        opt_section.rowconfigure(1, weight=1)
        opt_section.columnconfigure(0, weight=1)
        opt_section.bind("<Configure>", self._update_option_density)

        ttk.Label(opt_section, text="Select an option", style="H2.TLabel").grid(row=0, column=0, sticky="w", pady=(0, 6))

        options_wrap = tk.Frame(opt_section, bg="#101B2D", highlightthickness=0)
        options_wrap.grid(row=1, column=0, sticky="nsew")
        options_wrap.pack_propagate(False)
        self.options_wrap = options_wrap

        self.hint_label = ttk.Label(
            opt_section,
            text="Choose one option, then review the explanation or enter feedback below.",
            style="Muted.TLabel",
        )
        self.hint_label.grid(row=2, column=0, sticky="ew", pady=(6, 0))

        for i, option in enumerate(self.quiz_data.get("options", [])):
            row = tk.Frame(
                options_wrap,
                bg="#15233A",
                highlightthickness=1,
                highlightbackground="#2E3F60",
                cursor="hand2",
                padx=10,
                pady=8,
            )
            row.pack(fill=tk.X, pady=4)

            index_label = tk.Label(
                row,
                text=chr(65 + i),
                width=3,
                bg="#203554",
                fg="#DBEAFE",
                font=("Segoe UI", 10, "bold"),
                relief=tk.FLAT,
                padx=4,
                pady=3,
            )
            index_label.pack(side=tk.LEFT)

            text_label = tk.Label(
                row,
                text=option,
                bg="#15233A",
                fg="#E2E8F0",
                justify=tk.LEFT,
                wraplength=400,
                anchor=tk.W,
                font=("Segoe UI", 11),
                padx=8,
            )
            text_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

            row.bind("<Button-1>", lambda _e, idx=i: self.submit_answer(idx))
            index_label.bind("<Button-1>", lambda _e, idx=i: self.submit_answer(idx))
            text_label.bind("<Button-1>", lambda _e, idx=i: self.submit_answer(idx))
            row.bind("<Enter>", lambda _e, widget=row: self._hover_option(widget, True))
            row.bind("<Leave>", lambda _e, widget=row: self._hover_option(widget, False))
            index_label.bind("<Enter>", lambda _e, widget=row: self._hover_option(widget, True))
            index_label.bind("<Leave>", lambda _e, widget=row: self._hover_option(widget, False))
            text_label.bind("<Enter>", lambda _e, widget=row: self._hover_option(widget, True))
            text_label.bind("<Leave>", lambda _e, widget=row: self._hover_option(widget, False))

            self.option_rows.append({"row": row, "index_label": index_label, "text_label": text_label})

        # ── Right column: Result panel (expands to fill) ──
        right = ttk.Frame(content, style="Card.TFrame", padding=14)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right.rowconfigure(3, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(right, text="Result", style="H2.TLabel").grid(row=0, column=0, sticky="w")

        self.result_badge = ttk.Label(right, text="Waiting for answer", style="Pill.TLabel")
        self.result_badge.grid(row=1, column=0, sticky="w", pady=(8, 0))

        self.result_status = ttk.Label(right, text="", style="Muted.TLabel")
        self.result_status.grid(row=2, column=0, sticky="w", pady=(4, 0))

        self.result_text = tk.Text(
            right,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#0A1220",
            fg="#E2E8F0",
            relief=tk.FLAT,
            padx=10,
            pady=10,
            highlightthickness=1,
            highlightbackground="#2D3B56",
            insertbackground="#E2E8F0",
        )
        self.result_text.insert("1.0", "Your result and explanation will appear here after answering.")
        self.result_text.config(state=tk.DISABLED)
        self.result_text.grid(row=3, column=0, sticky="nsew", pady=(8, 0))

        # Bottom bar for save button and status
        bottom = ttk.Frame(right, style="Card.TFrame")
        bottom.grid(row=4, column=0, sticky="ew", pady=(10, 0))
        bottom.columnconfigure(1, weight=1)

        self.add_btn = ttk.Button(
            bottom,
            text="Save to Notebook",
            style="Primary.TButton",
            command=self.save_screenshot,
            state=tk.NORMAL,  # Button is always normal to capture click
        )
        self.add_btn.grid(row=0, column=0, sticky="w")

        self.note_status = ttk.Label(bottom, text="Close the window to continue", style="Muted.TLabel")
        self.note_status.grid(row=0, column=1, sticky="w", padx=(12, 0))

        # ── Feedback section spanning both columns ──
        feedback_frame = ttk.Frame(content, style="Card.TFrame", padding=(14, 10))
        feedback_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(8, 0))
        feedback_frame.columnconfigure(0, weight=1)
        feedback_frame.rowconfigure(1, weight=1)

        fb_header = ttk.Frame(feedback_frame, style="Card.TFrame")
        fb_header.grid(row=0, column=0, sticky="ew", pady=(0, 6))
        fb_header.columnconfigure(0, weight=1)

        ttk.Label(fb_header, text="Feedback to Agent", style="H2.TLabel").grid(row=0, column=0, sticky="w")
        
        # Action button container
        btn_frame = ttk.Frame(fb_header, style="Card.TFrame")
        btn_frame.grid(row=0, column=1, sticky="e")
        
        self.submit_fb_btn = ttk.Button(
            btn_frame,
            text="Enter",
            style="Primary.TButton",
            command=self._on_close
        )
        self.submit_fb_btn.pack(side=tk.RIGHT)

        ttk.Label(
            fb_header,
            text="Optional: Enter a follow-up prompt for the agent.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(2, 0))

        self.feedback_text = tk.Text(
            feedback_frame,
            height=3,
            wrap=tk.WORD,
            font=("Segoe UI", 11),
            bg="#0A1220",
            fg="#E2E8F0",
            relief=tk.FLAT,
            padx=10,
            pady=8,
            highlightthickness=1,
            highlightbackground="#2D3B56",
            insertbackground="#E2E8F0",
        )
        self.feedback_text.grid(row=1, column=0, sticky="nsew")
        self.feedback_text.bind("<FocusIn>", self._on_feedback_focus_in)
        self.feedback_text.bind("<FocusOut>", self._on_feedback_focus_out)
        self.feedback_text.bind("<Return>", self._on_feedback_enter)
        self.feedback_text.bind("<Shift-Return>", lambda e: None) # Allow shift-enter for newlines
        
        self._feedback_placeholder = ""
        self._feedback_placeholder_active = True
        self.feedback_text.insert("1.0", self._feedback_placeholder)
        self.feedback_text.config(fg="#5A6F8A")


    def _on_feedback_focus_in(self, _event=None):
        if self._feedback_placeholder_active:
            self.feedback_text.delete("1.0", tk.END)
            self.feedback_text.config(fg="#E2E8F0")
            self._feedback_placeholder_active = False

    def _on_feedback_focus_out(self, _event=None):
        content = self.feedback_text.get("1.0", tk.END).strip()
        if not content:
            self.feedback_text.insert("1.0", self._feedback_placeholder)
            self.feedback_text.config(fg="#5A6F8A")
            self._feedback_placeholder_active = True

    def _on_feedback_enter(self, event):
        if not event.state & 0x0001: # Not holding shift
            self._on_close()
            return "break" # Prevent default newline
        return None

    def _update_option_density(self, _event=None):
        if self._density_job is not None:
            self.root.after_cancel(self._density_job)
        self._density_job = self.root.after(50, self._do_update_option_density)

    def _do_update_option_density(self):
        self._density_job = None
        count = len(self.option_rows)
        if count == 0 or not hasattr(self, "options_wrap"):
            return

        # Always update geometry synchronously
        self.options_wrap.update_idletasks()
        
        available_height = self.options_wrap.winfo_height()
        available_width = self.options_wrap.winfo_width()
        if available_height <= 1:
            return

        # Check if available dimensions haven't changed much to prevent oscillation
        if hasattr(self, "_last_aw") and abs(self._last_aw - available_width) < 5 and abs(self._last_ah - available_height) < 5:
            return
            
        self._last_aw = available_width
        self._last_ah = available_height

        base_rows_height = sum(max(44, cfg["row"].winfo_reqheight()) for cfg in self.option_rows)
        hint_height = self.hint_label.winfo_reqheight() + 8
        free_height = max(0, available_height - base_rows_height - hint_height)

        gap = max(8, min(64, free_height // (count + 1)))
        inner_y_pad = max(12, min(32, 10 + gap // 2))
        wrap_length = max(260, available_width - 120)

        for i, cfg in enumerate(self.option_rows):
            top_gap = gap if i == 0 else gap // 2 + 4
            bottom_gap = gap // 2 + 4
            cfg["row"].pack_configure(pady=(top_gap, bottom_gap))
            cfg["row"].configure(pady=inner_y_pad)
            cfg["text_label"].configure(wraplength=wrap_length)

        self.hint_label.grid_configure(pady=(max(6, gap // 2), 0))

    def _hover_option(self, row: tk.Frame, entering: bool):
        if self.answered:
            return
        row.configure(bg="#1D2F4E" if entering else "#15233A")

    def _set_option_style(self, idx: int, state: str):
        cfg = self.option_rows[idx]
        row = cfg["row"]
        dot = cfg["index_label"]
        text = cfg["text_label"]

        palette = {
            "idle": ("#15233A", "#203554", "#E2E8F0", "#DBEAFE", "#2E3F60"),
            "selected": ("#2A4062", "#355C8D", "#F8FAFC", "#DBEAFE", "#4A6999"),
            "correct": ("#0F3A2F", "#166543", "#ECFDF5", "#D1FAE5", "#21825A"),
            "wrong": ("#4A1E2A", "#7F1D1D", "#FEE2E2", "#FECACA", "#9F3131"),
        }
        bg, dot_bg, text_fg, dot_fg, border = palette[state]
        row.configure(bg=bg, highlightbackground=border, cursor="arrow")
        dot.configure(bg=dot_bg, fg=dot_fg)
        text.configure(bg=bg, fg=text_fg)
    
    def change_notebook_path(self):
        chosen = filedialog.askdirectory(title="Select Notebook folder")
        if not chosen:
            return
        self.notebook_dir = Path(chosen)
        self.config["notebookPath"] = str(self.notebook_dir)
        try:
            _save_config(self.config)
        except Exception:
            pass
        self.notebook_path_label.config(text=f"Notebook: {self.notebook_dir}")
        self.note_status.config(text=f"Notebook path updated: {self.notebook_dir}")
    
    def submit_answer(self, selected: int):
        if self.answered:
            return

        self.selected_index = selected
        self.answered = True
        correct = int(self.quiz_data.get("correctIndex", 0))
        is_correct = selected == correct

        for i in range(len(self.option_rows)):
            self._set_option_style(i, "idle")

        self._set_option_style(selected, "selected")
        self._set_option_style(correct, "correct")
        if selected != correct:
            self._set_option_style(selected, "wrong")

        explanation = (self.quiz_data.get("explanation") or "").strip()
        terminology = (self.quiz_data.get("terminology") or "").strip()
        knowledge = (self.quiz_data.get("knowledgeSummary") or "").strip()
        points = _extract_points(knowledge)

        badge = "Correct" if is_correct else "Incorrect"
        self.result_badge.config(text=badge)
        self.result_status.config(
            text="Correct! Review the explanation below."
            if is_correct
            else "Review the explanation to understand the correct approach."
        )

        lines = []
        
        if terminology:
            lines.extend([
                "Terminology & Definitions",
                terminology,
                ""
            ])
            
        if explanation:
            lines.extend([
                "Clear Explanation",
                explanation,
                ""
            ])

        if points:
            lines.append("Key Points")
            for p in points:
                lines.append(f"- {p}")

        text = "\n".join(lines).strip()
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", text)
        self.result_text.config(state=tk.DISABLED)

        self.is_correct = is_correct
        self.note_status.config(text="Close the window if you don't need notes", foreground="#9FB0CB")

    def _on_close(self):
        """Handle window close: always save quiz result if user answered."""
        if not self._feedback_placeholder_active:
            self.user_feedback = self.feedback_text.get("1.0", tk.END).strip()
        else:
            self.user_feedback = ""
        if self.answered and self.selected_index is not None:
            self._save_quiz_result()
        elif self.user_feedback:
            self._save_quiz_result()
        self.root.destroy()

    def _save_quiz_result(self):
        """Save quiz result to file for MCP to read."""
        try:
            quiz_file = Path(sys.argv[1]) if len(sys.argv) > 1 else None
            if quiz_file:
                if len(sys.argv) > 2:
                    result_path = Path(sys.argv[2]).expanduser().resolve()
                else:
                    result_path = quiz_file.parent / f"{quiz_file.stem}.result.json"
                selected = self.selected_index
                correct = int(self.quiz_data.get("correctIndex", 0))
                options = self.quiz_data.get("options", [])
                result = {
                    "quizId": self.quiz_data.get("id"),
                    "question": self.quiz_data.get("question"),
                    "options": options,
                    "selectedIndex": selected,
                    "selectedAnswer": options[selected] if selected is not None and 0 <= selected < len(options) else None,
                    "correctIndex": correct,
                    "correctAnswer": options[correct] if 0 <= correct < len(options) else None,
                    "isCorrect": self.is_correct,
                    "explanation": self.quiz_data.get("explanation"),
                    "knowledgeSummary": self.quiz_data.get("knowledgeSummary"),
                    "category": self.quiz_data.get("category"),
                    "savedToNotebook": self.saved_to_notebook,
                    "screenshotPath": str(self.screenshot_path) if self.screenshot_path else None,
                    "userFeedback": self.user_feedback,
                    "answeredAt": datetime.now().isoformat(),
                }
                result_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            print(f"Failed to save result: {e}", file=sys.stderr)

    def save_screenshot(self):
        if not self.answered or self.selected_index is None:
            self.note_status.config(text="Please answer the quiz first :)", foreground="#F87171")
            return

        try:
            topic = self.quiz_data.get("question", "quiz_result").strip()
            png_path = _capture_gui_screenshot(self.root, self.notebook_dir, topic)
            self.saved_to_notebook = True
            self.screenshot_path = png_path
            self.note_status.config(text=f"Great! Check {self.notebook_dir} later.")
            self.add_btn.config(state=tk.DISABLED)
        except Exception as e:
            self.note_status.config(text=f"Failed: {e}")

def load_quiz_from_args():
    """Load quiz data from command line args."""
    if len(sys.argv) < 2:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", "Usage:\npython quiz_gui.py <quiz file path>")
        sys.exit(1)

    quiz_file = Path(sys.argv[1]).expanduser().resolve()

    if not quiz_file.exists():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"File not found: {quiz_file}")
        sys.exit(1)

    try:
        return json.loads(quiz_file.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to parse file: {quiz_file}")
        sys.exit(1)

if __name__ == "__main__":
    quiz_data = load_quiz_from_args()
    QuizWindow(quiz_data)
