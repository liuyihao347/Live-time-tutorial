import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { writeFileSync, mkdirSync, existsSync, readFileSync } from "fs";
import { join, resolve, dirname } from "path";
import { homedir } from "os";
import { spawn } from "child_process";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

interface QuizData {
  id: string;
  question: string;
  options: string[];
  correctIndex: number;
  explanation: string;
  knowledgeSummary: string;
  createdAt: number;
  category?: string;
}

interface NotebookConfig {
  notebookPath: string;
}

interface NotebookNotePayload {
  topic: string;
  summary?: string;
  contentMarkdown?: string;
  tags?: string[];
  sections?: Array<{ heading: string; body: string }>;
  keyPoints?: string[];
  table?: { headers: string[]; rows: string[][] };
  chart?: { title?: string; labels: string[]; values: number[] };
  design?: {
    theme?: "clean" | "warm" | "forest";
    accentColor?: string;
  };
}

function sanitizeFilename(name: string): string {
  return name.replace(/[<>:"/\\|?*]/g, "").trim().substring(0, 40);
}

function generateQuizFilename(quiz: QuizData): string {
  const category = quiz.category || "Uncategorized";
  const questionPreview = sanitizeFilename(quiz.question.split(/[,.?!]/)[0]);
  const shortDate = new Date(quiz.createdAt).toISOString().slice(0, 10).replace(/-/g, "");
  return `${shortDate}_${category}_${questionPreview}.json`;
}

class QuizMCPServer {
  private server: Server;
  private config: NotebookConfig;
  private configPath: string;
  private tempDir: string;

  constructor() {
    this.server = new Server(
      {
        name: "live-time-tutorial-mcp",
        version: "4.0.0",
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.configPath = join(homedir(), ".live-time-tutorial", "config.json");
    this.tempDir = join(homedir(), ".live-time-tutorial", "temp");
    this.config = this.loadConfig();
    this.setupToolHandlers();

    this.server.onerror = (error) => {
      console.error("[MCP Error]", error);
    };
  }

  private loadConfig(): NotebookConfig {
    try {
      if (existsSync(this.configPath)) {
        const configData = readFileSync(this.configPath, "utf-8");
        return { ...{ notebookPath: join(homedir(), "Desktop", "Notebook") }, ...JSON.parse(configData) };
      }
    } catch (error) {
      console.error("Failed to load config:", error);
    }
    return {
      notebookPath: join(homedir(), "Desktop", "Notebook"),
    };
  }

  private saveConfig(): void {
    try {
      const configDir = join(homedir(), ".live-time-tutorial");
      if (!existsSync(configDir)) {
        mkdirSync(configDir, { recursive: true });
      }
      writeFileSync(this.configPath, JSON.stringify(this.config, null, 2));
    } catch (error) {
      console.error("Failed to save config:", error);
    }
  }

  private ensureNotebookDir(): string {
    if (!existsSync(this.config.notebookPath)) {
      mkdirSync(this.config.notebookPath, { recursive: true });
    }
    return this.config.notebookPath;
  }

  private ensureTempDir(): string {
    if (!existsSync(this.tempDir)) {
      mkdirSync(this.tempDir, { recursive: true });
    }
    return this.tempDir;
  }

  private sanitizeNoteFilename(topic: string): string {
    const base = (topic || "note").replace(/[<>:"/\\|?*]/g, "").trim().replace(/\s+/g, " ");
    const shortened = base.length > 80 ? base.slice(0, 80) : base;
    return shortened || "note";
  }

  private setupToolHandlers(): void {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: "generate_quiz",
            description: "Generate a knowledge quiz and open the Live-time-tutorial GUI window.",
            inputSchema: {
              type: "object",
              properties: {
                question: { type: "string", description: "Quiz question" },
                options: { type: "array", items: { type: "string" }, description: "Answer options" },
                correctIndex: { type: "number", description: "Correct option index (0-based)" },
                explanation: { type: "string", description: "Short explanation" },
                knowledgeSummary: { type: "string", description: "Key points separated by |" },
                category: { type: "string", description: "Category" },
              },
              required: ["question", "options", "correctIndex", "explanation"],
            },
          },
          {
            name: "set_notebook_path",
            description: "Set Notebook storage path (default: Desktop/Notebook).",
            inputSchema: {
              type: "object",
              properties: {
                path: { type: "string", description: "New path, supports ~/" },
              },
              required: ["path"],
            },
          },
          {
            name: "get_pending_quiz",
            description: "Get the pending quiz data from GUI (saved when user clicked 'Add to Notebook'). Use this to start the agent-first notebook PDF workflow.",
            inputSchema: {
              type: "object",
              properties: {},
            },
          },
          {
            name: "save_notebook_note_pdf",
            description: "Save a Notebook note as a beautiful PDF (LLM-driven).",
            inputSchema: {
              type: "object",
              properties: {
                topic: { type: "string", description: "Note topic (also used as filename)" },
                summary: { type: "string", description: "Short summary/status line" },
                contentMarkdown: {
                  type: "string",
                  description: "Flexible markdown body generated by agent skills (preferred for non-rigid layouts)",
                },
                tags: { type: "array", items: { type: "string" }, description: "Optional tags" },
                sections: {
                  type: "array",
                  description: "Sections in reading order",
                  items: {
                    type: "object",
                    properties: {
                      heading: { type: "string" },
                      body: { type: "string" },
                    },
                    required: ["heading", "body"],
                  },
                },
                keyPoints: { type: "array", items: { type: "string" }, description: "Key points" },
                table: {
                  type: "object",
                  properties: {
                    headers: { type: "array", items: { type: "string" } },
                    rows: { type: "array", items: { type: "array", items: { type: "string" } } },
                  },
                },
                chart: {
                  type: "object",
                  description: "Simple bar chart",
                  properties: {
                    title: { type: "string" },
                    labels: { type: "array", items: { type: "string" } },
                    values: { type: "array", items: { type: "number" } },
                  },
                  required: ["labels", "values"],
                },
                design: {
                  type: "object",
                  description: "Optional visual style options",
                  properties: {
                    theme: {
                      type: "string",
                      enum: ["clean", "warm", "forest"],
                      description: "Preset visual theme",
                    },
                    accentColor: {
                      type: "string",
                      description: "Hex color like #2563EB; overrides theme accent",
                    },
                  },
                },
              },
              required: ["topic"],
            },
          },
        ],
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case "generate_quiz":
            return await this.handleGenerateQuiz(args as any);
          case "set_notebook_path":
            return await this.handleSetNotebookPath(args as any);
          case "get_pending_quiz":
            return await this.handleGetPendingQuiz();
          case "save_notebook_note_pdf":
            return await this.handleSaveNotebookNotePdf(args as any);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : String(error);
        return {
          content: [{ type: "text", text: `Error: ${errorMessage}` }],
          isError: true,
        };
      }
    });
  }

  private async handleGenerateQuiz(args: {
    question: string;
    options: string[];
    correctIndex: number;
    explanation: string;
    knowledgeSummary?: string;
    category?: string;
  }) {
    const sessionId = `${Date.now()}_${Math.random().toString(36).substring(2, 7)}`;

    const knowledgePoints = args.knowledgeSummary
      ? args.knowledgeSummary.split(/[|\n]/).map(s => s.trim()).filter(s => s)
      : [];

    const quiz: QuizData = {
      id: sessionId,
      question: args.question,
      options: args.options,
      correctIndex: args.correctIndex,
      explanation: args.explanation,
      knowledgeSummary: knowledgePoints.join("|"),
      createdAt: Date.now(),
      category: args.category || "Uncategorized",
    };

    const notebookDir = this.ensureNotebookDir();
    const quizDir = join(notebookDir, "quizzes");
    if (!existsSync(quizDir)) {
      mkdirSync(quizDir, { recursive: true });
    }

    const filename = generateQuizFilename(quiz);
    const quizDataPath = join(quizDir, filename);
    writeFileSync(quizDataPath, JSON.stringify(quiz, null, 2), "utf-8");

    this.launchPythonGui(quizDataPath);

    return {
      content: [
        {
          type: "text",
          text: `Quiz generated. A GUI window should appear shortly.\n\nCategory: ${quiz.category}\nQuestion: ${quiz.question.substring(0, 70)}${quiz.question.length > 70 ? "..." : ""}\nSaved: ${filename}\n\nTip: Quiz data is stored as JSON and rendered by python/quiz_gui.py.`,
        },
      ],
    };
  }

  private launchPythonGui(quizPath: string): void {
    const pythonExe = process.platform === "win32" ? "python" : "python3";
    const guiScriptPath = resolve(__dirname, "..", "python", "quiz_gui.py");

    if (!existsSync(guiScriptPath)) {
      throw new Error(`Python GUI script not found: ${guiScriptPath}`);
    }

    const child = spawn(pythonExe, [guiScriptPath, quizPath], {
      detached: true,
      stdio: "ignore",
      shell: false,
    });

    child.unref();
    console.error(`[MCP] Launched Python GUI: ${guiScriptPath} ${quizPath}`);
  }

  private async handleSetNotebookPath(args: { path: string }) {
    let newPath = args.path.trim();
    if (newPath.startsWith("~/") || newPath === "~") {
      newPath = newPath.replace("~", homedir());
    }
    newPath = resolve(newPath);

    try {
      if (!existsSync(newPath)) {
        mkdirSync(newPath, { recursive: true });
      }

      this.config.notebookPath = newPath;
      this.saveConfig();

      return {
        content: [{ type: "text", text: `Notebook path updated:\n${newPath}` }],
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: `Failed to set path: ${error instanceof Error ? error.message : String(error)}` }],
        isError: true,
      };
    }
  }

  private async handleGetPendingQuiz() {
    const pendingPath = join(homedir(), ".live-time-tutorial", "pending_quiz.json");
    
    if (!existsSync(pendingPath)) {
      return {
        content: [{ type: "text", text: "No pending quiz found. Click 'Add to Notebook' in the quiz GUI first." }],
        isError: true,
      };
    }

    try {
      const data = JSON.parse(readFileSync(pendingPath, "utf-8"));
      return {
        content: [
          {
            type: "text",
            text: `Pending quiz loaded:\n${JSON.stringify(data, null, 2)}\n\nNow use the agent-first-notebook-pdf skill to generate rich content, then call save_notebook_note_pdf.`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [{ type: "text", text: `Failed to read pending quiz: ${error instanceof Error ? error.message : String(error)}` }],
        isError: true,
      };
    }
  }

  private async handleSaveNotebookNotePdf(args: NotebookNotePayload) {
    const notebookDir = this.ensureNotebookDir();
    const tempDir = this.ensureTempDir();

    const topic = (args.topic || "note").trim();
    if (!topic) {
      return { content: [{ type: "text", text: "topic is required" }], isError: true };
    }

    const filenameBase = this.sanitizeNoteFilename(topic);
    const payload: NotebookNotePayload = {
      topic,
      summary: args.summary,
      contentMarkdown: args.contentMarkdown,
      tags: args.tags || [],
      sections: args.sections || [],
      keyPoints: args.keyPoints || [],
      table: args.table,
      chart: args.chart,
      design: args.design,
    };

    const payloadPath = join(tempDir, `note_payload_${Date.now()}.json`);
    const outPath = join(notebookDir, `${filenameBase}.pdf`);

    mkdirSync(notebookDir, { recursive: true });
    writeFileSync(payloadPath, JSON.stringify(payload, null, 2), "utf-8");

    const pyScriptPath = join(tempDir, "notebook_pdf_writer.py");
    const script = `# -*- coding: utf-8 -*-
import json
import sys
import re
from pathlib import Path

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


def _safe_hex_color(value: str | None, fallback: str) -> str:
    if not isinstance(value, str):
        return fallback
    text = value.strip()
    if re.fullmatch(r"#[0-9A-Fa-f]{6}", text):
        return text
    return fallback


def _render_markdown(story, markdown_text: str, h_style, h3_style, body_style, quote_style, code_style):
    if not markdown_text.strip():
        return

    fence = chr(96) * 3
    in_code = False

    for raw in markdown_text.splitlines():
        line = raw.rstrip("\n")
        stripped = line.strip()

        if stripped.startswith(fence):
            in_code = not in_code
            continue

        if in_code:
            safe = (
                line.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace(" ", "&nbsp;")
            )
            story.append(Paragraph(safe or "&nbsp;", code_style))
            continue

        if not stripped:
            story.append(Spacer(1, 4))
            continue

        if stripped.startswith("### "):
            story.append(Paragraph(stripped[4:], h3_style))
            continue

        if stripped.startswith("## "):
            story.append(Paragraph(stripped[3:], h_style))
            continue

        if stripped.startswith("# "):
            story.append(Paragraph(stripped[2:], h_style))
            continue

        if stripped.startswith("> "):
            story.append(Paragraph(stripped[2:], quote_style))
            continue

        if stripped.startswith("- ") or stripped.startswith("* "):
            story.append(Paragraph(f"• {stripped[2:]}", body_style))
            continue

        ordered = re.match(r"^\d+[\.)]\s+(.*)$", stripped)
        if ordered:
            story.append(Paragraph(stripped, body_style))
            continue

        story.append(Paragraph(stripped, body_style))


def _write_pdf(out_path: Path, payload: dict) -> None:
    if A4 is None:
        raise RuntimeError("reportlab is required. Install with: pip install reportlab")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=payload.get("topic") or "Notebook",
    )

    styles = getSampleStyleSheet()
    design = payload.get("design") or {}
    theme = str(design.get("theme") or "clean").lower()
    default_accent = "#2563EB"
    if theme == "warm":
        default_accent = "#C2410C"
    elif theme == "forest":
        default_accent = "#0F766E"

    accent = _safe_hex_color(design.get("accentColor"), default_accent)
    heading_color = colors.HexColor(accent)
    table_header_bg = colors.HexColor("#EEF2FF") if theme == "clean" else (
        colors.HexColor("#FFF1E6") if theme == "warm" else colors.HexColor("#E6F7F1")
    )

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=heading_color,
        spaceAfter=10,
    )
    h_style = ParagraphStyle(
        "HeadingStyle",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=heading_color,
        spaceBefore=10,
        spaceAfter=6,
    )
    h3_style = ParagraphStyle(
        "Heading3Style",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.8,
        leading=14,
        textColor=colors.HexColor("#1F2937"),
        spaceBefore=6,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#111827"),
    )
    quote_style = ParagraphStyle(
        "QuoteStyle",
        parent=styles["BodyText"],
        fontName="Helvetica-Oblique",
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        leftIndent=10,
        borderPadding=6,
    )
    code_style = ParagraphStyle(
        "CodeStyle",
        parent=styles["BodyText"],
        fontName="Courier",
        fontSize=9.2,
        leading=12,
        textColor=colors.HexColor("#0F172A"),
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
    summary = (payload.get("summary") or "").strip()
    if summary:
        story.append(Paragraph(summary, meta_style))

    tags = [str(tag).strip() for tag in (payload.get("tags") or []) if str(tag).strip()]
    if tags:
        story.append(Paragraph("Tags: " + "  |  ".join(tags), meta_style))

    content_markdown = (payload.get("contentMarkdown") or "").strip()
    if content_markdown:
        _render_markdown(story, content_markdown, h_style, h3_style, body_style, quote_style, code_style)

    for sec in payload.get("sections", []) or []:
        story.append(Paragraph(sec.get("heading", ""), h_style))
        body = (sec.get("body") or "").replace("\n", "<br/>")
        story.append(Paragraph(body, body_style))

    key_points = payload.get("keyPoints") or []
    if key_points:
        story.append(Paragraph("Key Points", h_style))
        kp_html = "<br/>".join([f"• {p}" for p in key_points if str(p).strip()])
        story.append(Paragraph(kp_html, body_style))

    table_data = payload.get("table")
    if table_data and table_data.get("headers") and table_data.get("rows"):
        story.append(Paragraph("Table", h_style))
        data = [table_data["headers"]] + table_data["rows"]
        t = Table(data, hAlign="LEFT")
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), table_header_bg),
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

    chart = payload.get("chart")
    if chart and chart.get("labels") and chart.get("values"):
        labels = list(chart.get("labels") or [])
        values = list(chart.get("values") or [])
        if len(labels) == len(values) and len(labels) > 0:
            story.append(Paragraph(chart.get("title") or "Chart", h_style))

            w = 170 * mm
            h = 60 * mm
            d = Drawing(w, h)
            bc = VerticalBarChart()
            bc.x = 10
            bc.y = 10
            bc.height = h - 20
            bc.width = w - 20
            bc.data = [values]
            bc.categoryAxis.categoryNames = labels
            bc.valueAxis.forceZero = True
            bc.bars[0].fillColor = heading_color
            bc.strokeColor = colors.HexColor("#CBD5E1")
            bc.valueAxis.strokeColor = colors.HexColor("#CBD5E1")
            bc.categoryAxis.labels.angle = 30
            bc.categoryAxis.labels.dy = -12
            d.add(bc)
            story.append(Spacer(1, 6))
            story.append(d)

    doc.build(story)


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python notebook_pdf_writer.py <payload.json> <out.pdf>")
        return 1
    payload_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    _write_pdf(out_path, payload)
    print(str(out_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
`;
    writeFileSync(pyScriptPath, script, "utf-8");

    const pythonExe = process.platform === "win32" ? "python" : "python3";
    const child = spawn(pythonExe, [pyScriptPath, payloadPath, outPath], {
      stdio: ["ignore", "pipe", "pipe"],
      shell: false,
    });

    const out = await new Promise<{ code: number; stdout: string; stderr: string }>((resolvePromise) => {
      let stdout = "";
      let stderr = "";
      child.stdout?.on("data", (d) => (stdout += d.toString()));
      child.stderr?.on("data", (d) => (stderr += d.toString()));
      child.on("close", (code) => resolvePromise({ code: code ?? 1, stdout, stderr }));
    });

    if (out.code !== 0) {
      const msg = (out.stderr || out.stdout || "Failed to generate PDF").trim();
      return { content: [{ type: "text", text: msg }], isError: true };
    }

    return {
      content: [{ type: "text", text: `Saved Notebook PDF:\n${outPath}` }],
    };
  }

  async run(): Promise<void> {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error("Live-time-tutorial MCP server running on stdio");
    console.error(`Notebook: ${this.config.notebookPath}`);
  }
}

const server = new QuizMCPServer();
server.run().catch(console.error);
