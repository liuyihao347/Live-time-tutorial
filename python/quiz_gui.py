import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import sys
from pathlib import Path
import ctypes

# Enable high DPI awareness for Windows (reduces graininess)
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)  # PROCESS_PER_MONITOR_DPI_AWARE
except Exception:
    pass

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
except Exception:
    A4 = None

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


def _build_demo_steps(explanation: str, selected_text: str, correct_text: str) -> list[str]:
    steps = []
    if explanation:
        sentences = [s.strip() for s in explanation.replace("\n", " ").split(".") if s.strip()]
        for sentence in sentences[:3]:
            steps.append(sentence)

    if not steps:
        steps = [
            "Understand what the question is really asking.",
            "Compare each option with the required time complexity.",
            "Choose the option that satisfies both correctness and efficiency.",
        ]

    steps.append(f"Your selected option: {selected_text}")
    steps.append(f"Best option: {correct_text}")
    return steps


def _build_note_payload(quiz_data: dict, selected_index: int) -> dict:
    correct_index = int(quiz_data.get("correctIndex", 0))
    is_correct = selected_index == correct_index
    knowledge = quiz_data.get("knowledgeSummary", "") or ""
    points = _extract_points(knowledge)

    correct_text = quiz_data.get("options", [""])[correct_index]
    selected_text = quiz_data.get("options", [""])[selected_index]

    title = quiz_data.get("category") or "Notebook"
    topic = quiz_data.get("question", "").strip()
    explanation = (quiz_data.get("explanation", "") or "").strip()

    demo_steps = _build_demo_steps(explanation, selected_text, correct_text)
    score = 100 if is_correct else 35

    return {
        "title": title,
        "topic": topic,
        "summary": "Correct" if is_correct else "Incorrect",
        "sections": [
            {
                "heading": "Question",
                "body": topic,
            },
            {
                "heading": "Your Answer",
                "body": f"{chr(65 + selected_index)}. {selected_text}",
            },
            {
                "heading": "Correct Answer",
                "body": f"{chr(65 + correct_index)}. {correct_text}",
            },
            {
                "heading": "Explanation",
                "body": explanation if explanation else "(No explanation provided)",
            },
            {
                "heading": "Quick Walkthrough",
                "body": "\n".join([f"{i + 1}. {step}" for i, step in enumerate(demo_steps)]),
            },
        ],
        "key_points": points,
        "table": {
            "headers": ["Option", "Content", "Evaluation"],
            "rows": [
                [
                    chr(65 + i),
                    opt,
                    "Correct" if i == correct_index else ("Selected" if i == selected_index else "Not selected"),
                ]
                for i, opt in enumerate(quiz_data.get("options", []))
            ],
        },
        "chart": {
            "title": "Answer Quality",
            "labels": ["Your Score", "Perfect Score"],
            "values": [score, 100],
        },
    }


def _write_notebook_pdf(notebook_dir: Path, payload: dict) -> Path:
    if A4 is None:
        raise RuntimeError("reportlab is required. Install with: pip install reportlab")

    notebook_dir.mkdir(parents=True, exist_ok=True)

    filename = _sanitize_filename(payload.get("topic") or "note") + ".pdf"
    pdf_path = notebook_dir / filename

    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=payload.get("topic") or "Notebook",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0E1A2B"),
        spaceAfter=10,
    )
    h_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#111827"),
        spaceBefore=10,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#111827"),
    )
    meta_style = ParagraphStyle(
        "MetaStyle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor("#475569"),
        spaceAfter=8,
    )

    story = []
    story.append(Paragraph(payload.get("topic") or "Notebook", title_style))
    story.append(Paragraph(f"Status: {payload.get('summary', '')}", meta_style))

    for sec in payload.get("sections", []):
        story.append(Paragraph(sec.get("heading", ""), h_style))
        body = (sec.get("body") or "").replace("\n", "<br/>")
        story.append(Paragraph(body, body_style))

    key_points = payload.get("key_points", [])
    if key_points:
        story.append(Paragraph("Key Points", h_style))
        kp_html = "<br/>".join([f"• {p}" for p in key_points])
        story.append(Paragraph(kp_html, body_style))

    table_data = payload.get("table")
    if table_data and table_data.get("headers") and table_data.get("rows"):
        story.append(Paragraph("Options Table", h_style))
        data = [table_data["headers"]] + table_data["rows"]
        t = Table(data, colWidths=[24 * mm, 110 * mm, 44 * mm])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#EEF2FF")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(Spacer(1, 6))
        story.append(t)

    chart_data = payload.get("chart")
    if chart_data and chart_data.get("labels") and chart_data.get("values"):
        labels = list(chart_data.get("labels") or [])
        values = list(chart_data.get("values") or [])
        if len(labels) == len(values) and labels:
            story.append(Paragraph(chart_data.get("title") or "Chart", h_style))
            drawing = Drawing(170 * mm, 62 * mm)
            chart = VerticalBarChart()
            chart.x = 10
            chart.y = 8
            chart.height = 52 * mm
            chart.width = 160 * mm
            chart.data = [values]
            chart.categoryAxis.categoryNames = labels
            chart.valueAxis.valueMin = 0
            chart.valueAxis.valueMax = max(100, max(values))
            chart.valueAxis.valueStep = 20
            chart.bars[0].fillColor = colors.HexColor("#2563EB")
            chart.strokeColor = colors.HexColor("#CBD5E1")
            chart.valueAxis.strokeColor = colors.HexColor("#CBD5E1")
            chart.categoryAxis.labels.angle = 20
            chart.categoryAxis.labels.dy = -10
            drawing.add(chart)
            story.append(Spacer(1, 6))
            story.append(drawing)

    doc.build(story)
    return pdf_path

class QuizWindow:
    def __init__(self, quiz_data):
        self.quiz_data = quiz_data
        self.answered = False
        self.selected_index = None
        self.option_rows = []

        self.config = _load_config()
        self.notebook_dir = Path(self.config.get("notebookPath") or str(_default_notebook_dir()))

        self.root = tk.Tk()
        self.root.title(f"Live-time-tutorial")
        
        # Get actual screen dimensions (accounting for DPI scaling)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size to 85% of screen or max 1400x900
        width = min(int(screen_width * 0.85), 1400)
        height = min(int(screen_height * 0.85), 900)
        
        self.root.geometry(f"{width}x{height}")
        self.root.minsize(800, 600)
        self.root.configure(bg="#F8FAFC")

        # Center window after a short delay to ensure proper sizing
        def center_window():
            x = (self.root.winfo_screenwidth() - width) // 2
            y = (self.root.winfo_screenheight() - height) // 2
            self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.after(50, center_window)
        
        self._setup_style()
        self.setup_ui()
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(100, lambda: self.root.attributes('-topmost', False))
        self.root.mainloop()

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure("App.TFrame", background="#F8FAFC")
        style.configure("Card.TFrame", background="#FFFFFF")
        style.configure("Title.TLabel", background="#FFFFFF", foreground="#0F172A", font=("Segoe UI", 22, "bold"))
        style.configure("H2.TLabel", background="#FFFFFF", foreground="#334155", font=("Segoe UI", 14, "bold"))
        style.configure("Muted.TLabel", background="#FFFFFF", foreground="#64748B", font=("Segoe UI", 11))
        style.configure("Pill.TLabel", background="#DBEAFE", foreground="#1E40AF", font=("Segoe UI", 11, "bold"))
        style.configure("Success.TLabel", background="#FFFFFF", foreground="#059669", font=("Segoe UI", 13, "bold"))
        style.configure("Danger.TLabel", background="#FFFFFF", foreground="#DC2626", font=("Segoe UI", 13, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 12, "bold"), padding=(18, 12))
        style.configure("Secondary.TButton", font=("Segoe UI", 11), padding=(14, 10))
    
    def setup_ui(self):
        app = ttk.Frame(self.root, padding=24, style="App.TFrame")
        app.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(app, padding=0, style="App.TFrame")
        header.pack(fill=tk.X)

        title_card = ttk.Frame(header, padding=20, style="Card.TFrame")
        title_card.pack(fill=tk.X)

        ttk.Label(title_card, text="Live-time-tutorial", style="Title.TLabel").pack(anchor=tk.W)
        ttk.Label(title_card, text="Click any option card to submit instantly.", style="Muted.TLabel").pack(anchor=tk.W, pady=(4, 0))

        notebook_row = ttk.Frame(title_card, style="Card.TFrame")
        notebook_row.pack(fill=tk.X, pady=(14, 0))

        self.notebook_path_label = ttk.Label(
            notebook_row,
            text=f"Notebook: {self.notebook_dir}",
            style="Muted.TLabel",
        )
        self.notebook_path_label.pack(side=tk.LEFT, anchor=tk.W)

        ttk.Button(
            notebook_row,
            text="Change...",
            style="Secondary.TButton",
            command=self.change_notebook_path,
        ).pack(side=tk.RIGHT)

        content = ttk.Frame(app, padding=(0, 20, 0, 0), style="App.TFrame")
        content.pack(fill=tk.BOTH, expand=True)

        # Left panel - Question and Options (60% width)
        left = ttk.Frame(content, style="App.TFrame")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 12))

        # Right panel - Result (40% width, min 380px)
        right = ttk.Frame(content, style="App.TFrame")
        right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=False, padx=(12, 0))
        right.config(width=420)
        right.pack_propagate(False)

        q_card = ttk.Frame(left, padding=20, style="Card.TFrame")
        q_card.pack(fill=tk.BOTH, expand=True)
        ttk.Label(q_card, text="Question", style="H2.TLabel").pack(anchor=tk.W)

        self.question_text = tk.Text(
            q_card,
            height=3,
            wrap=tk.WORD,
            font=("Segoe UI", 13),
            bg="#F1F5F9",
            fg="#1E293B",
            relief=tk.FLAT,
            padx=16,
            pady=16,
            highlightthickness=1,
            highlightbackground="#E2E8F0",
            insertbackground="#1E293B",
        )
        self.question_text.insert("1.0", self.quiz_data.get("question", ""))
        self.question_text.config(state=tk.DISABLED)
        self.question_text.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        opt_card = ttk.Frame(left, padding=20, style="Card.TFrame")
        opt_card.pack(fill=tk.X, pady=(16, 0))
        ttk.Label(opt_card, text="Options", style="H2.TLabel").pack(anchor=tk.W)

        options_wrap = tk.Frame(opt_card, bg="#FFFFFF", highlightthickness=0)
        options_wrap.pack(fill=tk.X, pady=(10, 0))

        for i, option in enumerate(self.quiz_data.get("options", [])):
            row = tk.Frame(
                options_wrap,
                bg="#FFFFFF",
                highlightthickness=1,
                highlightbackground="#E2E8F0",
                cursor="hand2",
                padx=16,
                pady=14,
            )
            row.pack(fill=tk.X, pady=8)

            index_label = tk.Label(
                row,
                text=chr(65 + i),
                width=3,
                bg="#3B82F6",
                fg="#FFFFFF",
                font=("Segoe UI", 11, "bold"),
                relief=tk.FLAT,
                padx=6,
                pady=5,
            )
            index_label.pack(side=tk.LEFT)

            text_label = tk.Label(
                row,
                text=option,
                bg="#FFFFFF",
                fg="#1E293B",
                justify=tk.LEFT,
                wraplength=600,
                anchor=tk.W,
                font=("Segoe UI", 12),
                padx=14,
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

        self.hint_label = ttk.Label(opt_card, text="", style="Muted.TLabel")
        self.hint_label.pack(anchor=tk.W, pady=(6, 0))

        result_card = ttk.Frame(right, padding=20, style="Card.TFrame")
        result_card.pack(fill=tk.BOTH, expand=True)
        ttk.Label(result_card, text="Result", style="H2.TLabel").pack(anchor=tk.W)

        self.result_badge = ttk.Label(result_card, text="Waiting for answer", style="Pill.TLabel")
        self.result_badge.pack(anchor=tk.W, pady=(10, 0))

        self.result_status = ttk.Label(result_card, text="", style="Muted.TLabel")
        self.result_status.pack(anchor=tk.W, pady=(6, 0))

        self.result_text = tk.Text(
            result_card,
            height=1,
            wrap=tk.WORD,
            font=("Segoe UI", 12),
            bg="#F1F5F9",
            fg="#1E293B",
            relief=tk.FLAT,
            padx=16,
            pady=16,
            highlightthickness=1,
            highlightbackground="#E2E8F0",
            insertbackground="#1E293B",
        )
        self.result_text.insert("1.0", "Click an option to see instant feedback and explanation.")
        self.result_text.config(state=tk.DISABLED)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

        self.add_btn = ttk.Button(
            result_card,
            text="Add to My Notebook (PDF)",
            style="Primary.TButton",
            command=self.add_to_notebook,
            state=tk.DISABLED,
        )
        self.add_btn.pack(fill=tk.X, pady=(14, 0))

        self.note_status = ttk.Label(result_card, text="", style="Muted.TLabel")
        self.note_status.pack(anchor=tk.W, pady=(8, 0))

    def _hover_option(self, row: tk.Frame, entering: bool):
        if self.answered:
            return
        row.configure(bg="#EFF6FF" if entering else "#FFFFFF")

    def _set_option_style(self, idx: int, state: str):
        cfg = self.option_rows[idx]
        row = cfg["row"]
        dot = cfg["index_label"]
        text = cfg["text_label"]

        palette = {
            "idle": ("#FFFFFF", "#3B82F6", "#1E293B", "#FFFFFF", "#E2E8F0"),
            "selected": ("#EFF6FF", "#2563EB", "#1E40AF", "#FFFFFF", "#3B82F6"),
            "correct": ("#ECFDF5", "#059669", "#065F46", "#FFFFFF", "#10B981"),
            "wrong": ("#FEF2F2", "#DC2626", "#991B1B", "#FFFFFF", "#F87171"),
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
        knowledge = (self.quiz_data.get("knowledgeSummary") or "").strip()
        points = _extract_points(knowledge)

        correct_answer = self.quiz_data.get("options", [""])[correct]
        selected_answer = self.quiz_data.get("options", [""])[selected]

        badge = "Correct" if is_correct else "Incorrect"
        self.result_badge.config(text=badge)
        self.result_status.config(
            text="Excellent choice. You can now export the note to Notebook."
            if is_correct
            else "Not the best choice. Review the walkthrough and save notes to reinforce learning."
        )

        demo_steps = _build_demo_steps(explanation, selected_answer, correct_answer)

        lines = [
            f"Result: {badge}",
            "",
            f"Your answer: {chr(65 + selected)}. {selected_answer}",
            f"Correct answer: {chr(65 + correct)}. {correct_answer}",
            "",
            "Clear Explanation",
            explanation if explanation else "(No explanation provided)",
            "",
            "Walkthrough Demo",
        ]

        for i, step in enumerate(demo_steps, start=1):
            lines.append(f"{i}. {step}")

        if points:
            lines.append("")
            lines.append("Key Points")
            for p in points:
                lines.append(f"- {p}")

        text = "\n".join(lines)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete("1.0", tk.END)
        self.result_text.insert("1.0", text)
        self.result_text.config(state=tk.DISABLED)

        self.add_btn.config(state=tk.NORMAL)
        self.note_status.config(text="Ready. Click 'Add to My Notebook (PDF)' to save a polished note.")

    def add_to_notebook(self):
        if not self.answered or self.selected_index is None:
            return

        try:
            # Save quiz data with answer for agent to process
            pending_data = {
                "quiz": self.quiz_data,
                "selectedIndex": int(self.selected_index),
                "isCorrect": int(self.selected_index) == int(self.quiz_data.get("correctIndex", 0)),
                "timestamp": __import__("datetime").datetime.now().isoformat(),
            }
            
            pending_dir = Path.home() / ".live-time-tutorial"
            pending_dir.mkdir(parents=True, exist_ok=True)
            pending_path = pending_dir / "pending_quiz.json"
            
            with open(pending_path, "w", encoding="utf-8") as f:
                json.dump(pending_data, f, ensure_ascii=False, indent=2)
            
            self.note_status.config(text="Quiz saved! Tell the agent: 'Generate notebook PDF'")
            messagebox.showinfo(
                "Ready for Agent",
                f"Quiz data saved to:\n{pending_path}\n\n"
                "Tell the agent: \"Generate notebook PDF for this quiz\"\n"
                "The agent will execute the full knowledge expansion workflow."
            )
        except Exception as e:
            messagebox.showerror("Failed", str(e))

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
        return json.loads(quiz_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to parse file: {quiz_file}")
        sys.exit(1)

if __name__ == "__main__":
    quiz_data = load_quiz_from_args()
    QuizWindow(quiz_data)
