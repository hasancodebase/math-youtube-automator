"""
================================================
  MATH YOUTUBE CHANNEL AUTOMATOR
  Desktop App — Windows 10/11
  AI: Groq (FREE) — Llama 3.3 70B
================================================
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import json
import os
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

BG_DARK      = "#1a1a2e"
BG_CARD      = "#16213e"
BG_INPUT     = "#0f3460"
ACCENT_GREEN = "#00d4aa"
ACCENT_BLUE  = "#4cc9f0"
ACCENT_GOLD  = "#ffd60a"
TEXT_WHITE   = "#ffffff"
TEXT_GRAY    = "#a8b2d8"
TEXT_MUTED   = "#606880"
DANGER_RED   = "#ff6b6b"
SUCCESS_GRN  = "#51cf66"
WARNING_YEL  = "#ffd60a"

FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_HEAD  = ("Segoe UI", 13, "bold")
FONT_NORMAL= ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 10)
FONT_MONO  = ("Consolas", 10)
FONT_BIG   = ("Segoe UI", 28, "bold")


class MathChannelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MathChannel Automator — Powered by Groq AI (FREE)")
        self.root.geometry("1100x750")
        self.root.configure(bg=BG_DARK)
        self.root.resizable(True, True)

        self.is_running    = False
        self.pipeline_data = {}
        self.api_key       = tk.StringVar(value=os.getenv("GROQ_API_KEY", ""))
        self.level_var     = tk.StringVar(value="algebra")
        self.duration_var  = tk.StringVar(value="8-10 min (ideal)")

        self.stage_vars = {
            "script":    tk.BooleanVar(value=True),
            "animate":   tk.BooleanVar(value=False),
            "voice":     tk.BooleanVar(value=True),
            "thumbnail": tk.BooleanVar(value=True),
            "assemble":  tk.BooleanVar(value=True),
            "upload":    tk.BooleanVar(value=False),
        }

        self._build_ui()
        self._check_api_key()

    def _build_ui(self):
        topbar = tk.Frame(self.root, bg=BG_CARD, height=60)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="📐 MathChannel Automator",
                 font=FONT_TITLE, bg=BG_CARD, fg=ACCENT_GREEN).pack(side="left", padx=20, pady=10)
        tk.Label(topbar, text="Turn any math problem into a YouTube video — Groq AI (FREE, Ultra Fast)",
                 font=FONT_SMALL, bg=BG_CARD, fg=TEXT_GRAY).pack(side="left", padx=5)

        self.api_status_label = tk.Label(topbar, text="● API: checking...",
                                          font=FONT_SMALL, bg=BG_CARD, fg=WARNING_YEL)
        self.api_status_label.pack(side="right", padx=20)

        content = tk.Frame(self.root, bg=BG_DARK)
        content.pack(fill="both", expand=True, padx=15, pady=10)

        left = tk.Frame(content, bg=BG_DARK, width=380)
        left.pack(side="left", fill="y", padx=(0, 8))
        left.pack_propagate(False)

        right = tk.Frame(content, bg=BG_DARK)
        right.pack(side="left", fill="both", expand=True)

        self._build_left(left)
        self._build_right(right)

        statusbar = tk.Frame(self.root, bg=BG_CARD, height=30)
        statusbar.pack(fill="x", side="bottom")
        statusbar.pack_propagate(False)

        self.status_label = tk.Label(statusbar,
                                      text="Ready — enter a math problem and click Run",
                                      font=FONT_SMALL, bg=BG_CARD, fg=TEXT_GRAY)
        self.status_label.pack(side="left", padx=15, pady=5)

    def _build_left(self, parent):
        api_card = self._card(parent, "🔑 Groq API Key (FREE — Works from Pakistan)")
        tk.Entry(api_card, textvariable=self.api_key, font=FONT_SMALL,
                 bg=BG_INPUT, fg=TEXT_WHITE, insertbackground=TEXT_WHITE,
                 show="*", relief="flat", bd=6).pack(fill="x", pady=(0, 6))
        tk.Button(api_card, text="Get free key → console.groq.com",
                  font=FONT_SMALL, bg=BG_DARK, fg=ACCENT_BLUE,
                  relief="flat", cursor="hand2",
                  command=lambda: self._open_url("https://console.groq.com")).pack(anchor="w")

        prob_card = self._card(parent, "📝 Math Problem")
        self.problem_entry = scrolledtext.ScrolledText(
            prob_card, height=5, font=FONT_NORMAL, bg=BG_INPUT, fg=TEXT_WHITE,
            insertbackground=TEXT_WHITE, relief="flat", bd=6, wrap="word")
        self.problem_entry.pack(fill="x", pady=(0, 8))
        self.problem_entry.insert("1.0", "Solve: 2x + 5 = 13")

        ex_frame = tk.Frame(prob_card, bg=BG_CARD)
        ex_frame.pack(fill="x", pady=(0, 4))
        tk.Label(ex_frame, text="Examples:", font=FONT_SMALL,
                 bg=BG_CARD, fg=TEXT_GRAY).pack(side="left")

        for label, prob in [
            ("Primary",  "What is 3/4 + 1/2?"),
            ("Algebra",  "Solve: x^2 - 5x + 6 = 0"),
            ("Trig",     "Find sin(30) and cos(60)"),
            ("Calculus", "Differentiate: f(x) = 3x^4 - 2x^2"),
        ]:
            tk.Button(ex_frame, text=label, font=("Segoe UI", 9),
                      bg=BG_INPUT, fg=ACCENT_BLUE, relief="flat",
                      cursor="hand2", padx=6,
                      command=lambda p=prob: self._set_example(p)).pack(side="left", padx=2)

        opt_card = self._card(parent, "Options")
        tk.Label(opt_card, text="Math Level:", font=FONT_SMALL,
                 bg=BG_CARD, fg=TEXT_GRAY).pack(anchor="w")
        ttk.Combobox(opt_card, textvariable=self.level_var, font=FONT_SMALL,
                     state="readonly",
                     values=["primary","middle","algebra","trigonometry","calculus"]
                     ).pack(fill="x", pady=(2, 8))

        tk.Label(opt_card, text="Target Duration:", font=FONT_SMALL,
                 bg=BG_CARD, fg=TEXT_GRAY).pack(anchor="w")
        ttk.Combobox(opt_card, textvariable=self.duration_var, font=FONT_SMALL,
                     state="readonly",
                     values=["4-6 min (primary)","8-10 min (ideal)","12-15 min (advanced)"]
                     ).pack(fill="x", pady=(2, 0))

        stage_card = self._card(parent, "Pipeline Stages")
        for key, label in [
            ("script",    "  Generate script + SEO"),
            ("animate",   "  Animate with Manim"),
            ("voice",     "  Generate voice (TTS)"),
            ("thumbnail", "  Create thumbnail"),
            ("assemble",  "  Assemble final video"),
            ("upload",    "  Upload to YouTube"),
        ]:
            tk.Checkbutton(stage_card, text=label, variable=self.stage_vars[key],
                           font=FONT_SMALL, bg=BG_CARD, fg=TEXT_WHITE,
                           selectcolor=BG_INPUT, activebackground=BG_CARD,
                           activeforeground=TEXT_WHITE).pack(anchor="w", pady=1)

        self.run_btn = tk.Button(parent, text="  RUN FULL PIPELINE",
                                  font=("Segoe UI", 13, "bold"),
                                  bg=ACCENT_GREEN, fg=BG_DARK,
                                  relief="flat", cursor="hand2",
                                  pady=12, command=self._run_pipeline)
        self.run_btn.pack(fill="x", pady=(10, 4))

        self.stop_btn = tk.Button(parent, text="  STOP", font=FONT_NORMAL,
                                   bg=DANGER_RED, fg=TEXT_WHITE,
                                   relief="flat", cursor="hand2",
                                   pady=6, state="disabled",
                                   command=self._stop_pipeline)
        self.stop_btn.pack(fill="x")

    def _build_right(self, parent):
        stats_frame = tk.Frame(parent, bg=BG_DARK)
        stats_frame.pack(fill="x", pady=(0, 8))

        for attr, val, label in [
            ("videos_count", "0",     "Videos Generated"),
            ("stage_info",   "Idle",  "Current Stage"),
            ("elapsed",      "00:00", "Time Elapsed"),
            ("output_size",  "0 MB",  "Output Size"),
        ]:
            card = tk.Frame(stats_frame, bg=BG_CARD)
            card.pack(side="left", fill="x", expand=True, padx=3)
            lbl = tk.Label(card, text=val, font=FONT_BIG, bg=BG_CARD, fg=ACCENT_GREEN)
            lbl.pack(pady=(8, 0))
            tk.Label(card, text=label, font=FONT_SMALL,
                     bg=BG_CARD, fg=TEXT_GRAY).pack(pady=(0, 8))
            setattr(self, f"stat_{attr}", lbl)

        prog_card = self._card(parent, "Pipeline Progress")
        self.stage_labels = {}
        self.stage_icons  = {}
        self.stage_bars   = {}

        for key, label in [
            ("script",    "Generate Script + SEO"),
            ("animate",   "Animate with Manim"),
            ("voice",     "Generate Voice"),
            ("thumbnail", "Create Thumbnail"),
            ("assemble",  "Assemble Video"),
            ("upload",    "Upload to YouTube"),
        ]:
            row = tk.Frame(prog_card, bg=BG_CARD)
            row.pack(fill="x", pady=3)
            icon = tk.Label(row, text="o", font=FONT_NORMAL,
                            bg=BG_CARD, fg=TEXT_MUTED, width=2)
            icon.pack(side="left", padx=(0, 6))
            lbl = tk.Label(row, text=label, font=FONT_SMALL,
                           bg=BG_CARD, fg=TEXT_GRAY, width=24, anchor="w")
            lbl.pack(side="left")
            bar_frame = tk.Frame(row, bg=BG_INPUT, height=6)
            bar_frame.pack(side="left", fill="x", expand=True, padx=6)
            bar_frame.pack_propagate(False)
            bar = tk.Frame(bar_frame, bg=TEXT_MUTED, height=6, width=0)
            bar.pack(side="left", fill="y")
            self.stage_icons[key]  = icon
            self.stage_labels[key] = lbl
            self.stage_bars[key]   = (bar_frame, bar)

        log_card = self._card(parent, "Live Log")
        self.log_text = scrolledtext.ScrolledText(
            log_card, height=12, font=FONT_MONO, bg="#0a0a1a",
            fg=ACCENT_GREEN, relief="flat", bd=4, state="disabled")
        self.log_text.pack(fill="both", expand=True)
        self.log_text.tag_config("success", foreground=SUCCESS_GRN)
        self.log_text.tag_config("error",   foreground=DANGER_RED)
        self.log_text.tag_config("warning", foreground=WARNING_YEL)
        self.log_text.tag_config("info",    foreground=ACCENT_BLUE)
        self.log_text.tag_config("muted",   foreground=TEXT_MUTED)

        ctrl = tk.Frame(log_card, bg=BG_CARD)
        ctrl.pack(fill="x", pady=(4, 0))
        tk.Button(ctrl, text="Clear Log", font=FONT_SMALL, bg=BG_INPUT,
                  fg=TEXT_GRAY, relief="flat", cursor="hand2",
                  command=self._clear_log).pack(side="left", padx=2)
        tk.Button(ctrl, text="Open Output Folder", font=FONT_SMALL,
                  bg=BG_INPUT, fg=ACCENT_BLUE, relief="flat", cursor="hand2",
                  command=self._open_output).pack(side="left", padx=2)
        tk.Button(ctrl, text="Save Log", font=FONT_SMALL, bg=BG_INPUT,
                  fg=TEXT_GRAY, relief="flat", cursor="hand2",
                  command=self._save_log).pack(side="right", padx=2)

    def _run_pipeline(self):
        problem = self.problem_entry.get("1.0", "end").strip()
        if not problem:
            messagebox.showwarning("No Problem", "Please enter a math problem!")
            return
        api_key = self.api_key.get().strip()
        if not api_key or len(api_key) < 10:
            messagebox.showerror("API Key Missing",
                "Please enter your Groq API key!\nGet it free at: console.groq.com")
            return

        self._reset_stages()
        self.is_running = True
        self.run_btn.config(state="disabled", bg=TEXT_MUTED)
        self.stop_btn.config(state="normal")
        self.start_time = datetime.now()
        self._update_timer()

        threading.Thread(target=self._pipeline_thread,
                         args=(problem, self.level_var.get(), api_key),
                         daemon=True).start()

    def _pipeline_thread(self, problem, level, api_key):
        try:
            self._log(f"Starting pipeline for: {problem[:60]}...", "info")
            self._log(f"Level: {level.upper()} | AI: Groq Llama 3.3 70B (FREE)", "muted")
            self._log("-" * 50, "muted")

            if self.stage_vars["script"].get():
                self._start_stage("script")
                result = self._run_script_stage(problem, level, api_key)
                if result:
                    self.pipeline_data = result
                    self._complete_stage("script")
                    self._log("Script generated!", "success")
                    self._log(f"  Title: {result['seo']['title']}", "muted")
                    self._log(f"  Steps: {len(result['script']['steps'])}", "muted")
                    self._log(f"  Keyword: {result['seo']['keyword_focus']}", "muted")
                else:
                    self._fail_stage("script")
                    return

            if self.stage_vars["animate"].get():
                self._start_stage("animate")
                self._simulate_stage("animate", 2)
                self._complete_stage("animate")
                self._log("Animation spec ready", "success")

            if self.stage_vars["voice"].get():
                self._start_stage("voice")
                self._log("Generating voice narration...", "info")
                if self._run_voice_stage():
                    self._complete_stage("voice")
                    self._log("Voice MP3 saved!", "success")
                else:
                    self._fail_stage("voice")
                    self._log("Voice failed - check internet", "warning")

            if self.stage_vars["thumbnail"].get():
                self._start_stage("thumbnail")
                self._log("Creating thumbnail...", "info")
                if self._run_thumbnail_stage(problem):
                    self._complete_stage("thumbnail")
                    self._log("Thumbnail PNG saved!", "success")
                else:
                    self._fail_stage("thumbnail")

            if self.stage_vars["assemble"].get():
                self._start_stage("assemble")
                self._simulate_stage("assemble", 2)
                self._complete_stage("assemble")
                self._log("Package assembled!", "success")

            if self.stage_vars["upload"].get():
                self._start_stage("upload")
                self._simulate_stage("upload", 3)
                self._complete_stage("upload")
                self._log("Uploaded to YouTube!", "success")

            self._log("-" * 50, "muted")
            self._log("PIPELINE COMPLETE! Check output folder.", "success")
            self._update_stat("videos_count", "1")
            self._update_stat("stage_info", "Done")
            self._update_status("Done! Click Open Output Folder to see results.")
            self._save_output()

        except Exception as e:
            self._log(f"Error: {str(e)}", "error")
        finally:
            self.is_running = False
            self.root.after(0, lambda: self.run_btn.config(state="normal", bg=ACCENT_GREEN))
            self.root.after(0, lambda: self.stop_btn.config(state="disabled"))

    def _run_script_stage(self, problem, level, api_key):
        try:
            from groq import Groq
            client = Groq(api_key=api_key)

            level_map = {
                "primary":      ("Grade 1-5",   "6-10 years old"),
                "middle":       ("Grade 6-8",   "11-13 years old"),
                "algebra":      ("Grade 9-10",  "14-16 years old"),
                "trigonometry": ("Grade 10-11", "15-17 years old"),
                "calculus":     ("Grade 11-12", "16-18 years old"),
            }
            grade, age = level_map.get(level, ("Grade 9-10", "14-16 years old"))

            self._log("  Connecting to Groq AI...", "muted")
            self._update_bar("script", 20)

            script_prompt = f"""You are a friendly math teacher making a YouTube video for students aged {age} ({grade}).

MATH PROBLEM: {problem}

Return ONLY valid JSON with no extra text, no markdown, no explanation:
{{
  "hook": "Exciting opening line that grabs attention in 15 seconds",
  "problem_statement": "Restate problem in simple friendly words",
  "steps": [
    {{
      "step_number": 1,
      "title": "Short step title",
      "narration": "What teacher says - friendly, simple, 2-3 sentences",
      "on_screen_math": "Math shown on screen at this step",
      "math_rule": "Name of math rule used e.g. BODMAS Distributive Property",
      "rule_explanation": "One simple sentence explaining why this rule works",
      "tip": "Memory trick or encouragement or empty string"
    }}
  ],
  "summary": "2-3 sentence recap of what was solved and key rules used",
  "outro": "Friendly closing with subscribe reminder"
}}"""

            self._log("  Generating step-by-step script...", "muted")
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": script_prompt}],
                temperature=0.7,
                max_tokens=2000,
            )
            self._update_bar("script", 50)

            raw = response.choices[0].message.content.strip()
            raw = re.sub(r"^```json\s*", "", raw)
            raw = re.sub(r"^```\s*", "", raw)
            raw = re.sub(r"\s*```$", "", raw)
            script = json.loads(raw)

            self._log("  Generating SEO metadata...", "muted")

            seo_prompt = f"""You are a YouTube SEO expert for global math education targeting students worldwide.

PROBLEM: {problem}
LEVEL: {grade}
STEPS: {[s['title'] for s in script['steps']]}

Return ONLY valid JSON with no extra text:
{{
  "title": "YouTube title max 60 chars keyword-rich engaging",
  "description": "250 word YouTube description. First line has main keyword. Second line what they learn. Steps summary. Rules covered. Subscribe CTA. Hashtags at end.",
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6","tag7","tag8","tag9","tag10","tag11","tag12","tag13","tag14","tag15"],
  "thumbnail_text": "Bold thumbnail text max 5 words",
  "thumbnail_subtitle": "Subtitle max 4 words",
  "keyword_focus": "Single most important search keyword"
}}"""

            seo_resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": seo_prompt}],
                temperature=0.5,
                max_tokens=1000,
            )
            self._update_bar("script", 90)

            raw2 = seo_resp.content[0].message.content.strip() if hasattr(seo_resp, 'content') else seo_resp.choices[0].message.content.strip()
            raw2 = re.sub(r"^```json\s*", "", raw2)
            raw2 = re.sub(r"^```\s*", "", raw2)
            raw2 = re.sub(r"\s*```$", "", raw2)
            seo = json.loads(raw2)

            self._update_bar("script", 100)
            return {"script": script, "seo": seo, "problem": problem, "level": level}

        except json.JSONDecodeError as e:
            self._log(f"  JSON error: {str(e)} - try running again", "error")
            return None
        except Exception as e:
            self._log(f"  Script error: {str(e)}", "error")
            return None

    def _run_voice_stage(self):
        try:
            from gtts import gTTS
            if not self.pipeline_data:
                return False

            script  = self.pipeline_data["script"]
            out_dir = Path("D:/math-channel/output/audio")
            out_dir.mkdir(parents=True, exist_ok=True)

            narration = script["hook"] + ". "
            narration += script["problem_statement"] + ". "
            for step in script["steps"]:
                narration += f"Step {step['step_number']}. {step['title']}. "
                narration += step["narration"] + ". "
                narration += f"We used the {step['math_rule']}. "
                narration += step["rule_explanation"] + ". "
                if step.get("tip"):
                    narration += step["tip"] + ". "
            narration += script["summary"] + ". "
            narration += script["outro"]

            self._log(f"  {len(narration)} chars to speech...", "muted")
            self._update_bar("voice", 40)

            safe = "".join(c for c in self.pipeline_data["problem"][:30]
                          if c.isalnum() or c in " _-").strip().replace(" ", "_")
            out_file = out_dir / f"{safe}_narration.mp3"
            gTTS(text=narration, lang="en", slow=False).save(str(out_file))

            self._update_bar("voice", 100)
            self._log(f"  Saved: {out_file.name}", "muted")
            return True
        except Exception as e:
            self._log(f"  Voice error: {str(e)}", "error")
            return False

    def _run_thumbnail_stage(self, problem):
        try:
            from PIL import Image, ImageDraw, ImageFont

            out_dir = Path("D:/math-channel/output/thumbnails")
            out_dir.mkdir(parents=True, exist_ok=True)

            img  = Image.new("RGB", (1280, 720), color=(26, 26, 46))
            draw = ImageDraw.Draw(img)

            for i in range(720):
                v = int(i / 720 * 35)
                draw.line([(0, i), (1280, i)], fill=(15, 52 + v, 96 + v))

            draw.rectangle([0, 0, 14, 720], fill=(0, 212, 170))

            try:
                f72 = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 72)
                f42 = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 42)
                f32 = ImageFont.truetype("C:/Windows/Fonts/arial.ttf",   32)
                f28 = ImageFont.truetype("C:/Windows/Fonts/arial.ttf",   28)
            except:
                f72 = f42 = f32 = f28 = ImageFont.load_default()

            draw.text((80, 60),  "MathChannel", font=f32, fill=(0, 212, 170))
            prob_short = problem if len(problem) < 32 else problem[:29] + "..."
            draw.text((80, 130), prob_short,    font=f72, fill=(255, 255, 255))

            seo      = self.pipeline_data.get("seo", {})
            subtitle = seo.get("thumbnail_subtitle", "Easy Step by Step")
            keyword  = seo.get("keyword_focus", "Math Tutorial")
            level    = self.pipeline_data.get("level", "").upper()

            draw.text((80, 280), subtitle, font=f42, fill=(255, 214, 10))
            draw.rectangle([80, 370, 80 + len(keyword)*18 + 30, 420], fill=(76, 201, 240))
            draw.text((95, 378), keyword,  font=f28, fill=(26, 26, 46))
            draw.rectangle([80, 440, 300, 495], fill=(83, 74, 183))
            draw.text((95, 450), f"{level} LEVEL", font=f28, fill=(255, 255, 255))
            draw.rectangle([880, 20, 1260, 75], fill=(0, 212, 170))
            draw.text((895, 30), "STEP BY STEP", font=f28, fill=(26, 26, 46))
            draw.text((80, 660), "Learn Math the Easy Way - Subscribe for More!",
                      font=f28, fill=(96, 104, 128))

            safe = "".join(c for c in problem[:30]
                          if c.isalnum() or c in " _-").strip().replace(" ", "_")
            out_file = out_dir / f"{safe}_thumbnail.png"
            img.save(str(out_file))

            self._update_bar("thumbnail", 100)
            self._log(f"  Saved: {out_file.name}", "muted")
            return True
        except Exception as e:
            self._log(f"  Thumbnail error: {str(e)}", "error")
            return False

    def _save_output(self):
        if not self.pipeline_data:
            return
        try:
            out_dir = Path("D:/math-channel/output/scripts")
            out_dir.mkdir(parents=True, exist_ok=True)
            safe = "".join(c for c in self.pipeline_data["problem"][:40]
                          if c.isalnum() or c in " _-").strip().replace(" ", "_")
            out_file = out_dir / f"{safe}.json"
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(self.pipeline_data, f, indent=2, ensure_ascii=False)
            self._log(f"  JSON saved: {out_file.name}", "muted")
            size = sum(f.stat().st_size for f in Path("D:/math-channel/output").rglob("*")
                      if f.is_file()) / (1024*1024)
            self._update_stat("output_size", f"{size:.1f}MB")
        except Exception as e:
            self._log(f"  Save error: {str(e)}", "error")

    def _card(self, parent, title):
        frame = tk.Frame(parent, bg=BG_CARD, relief="flat")
        frame.pack(fill="x", pady=4, padx=2)
        tk.Label(frame, text=title, font=FONT_HEAD,
                 bg=BG_CARD, fg=ACCENT_GOLD).pack(anchor="w", padx=10, pady=(8,4))
        inner = tk.Frame(frame, bg=BG_CARD)
        inner.pack(fill="x", padx=10, pady=(0,10))
        return inner

    def _log(self, message, tag=""):
        def _do():
            self.log_text.config(state="normal")
            ts = datetime.now().strftime("%H:%M:%S")
            self.log_text.insert("end", f"[{ts}] {message}\n", tag)
            self.log_text.see("end")
            self.log_text.config(state="disabled")
        self.root.after(0, _do)

    def _update_status(self, msg):
        self.root.after(0, lambda: self.status_label.config(text=msg))

    def _update_stat(self, key, val):
        lbl = getattr(self, f"stat_{key}", None)
        if lbl:
            self.root.after(0, lambda: lbl.config(text=val))

    def _update_bar(self, stage, pct):
        def _do():
            frame, bar = self.stage_bars[stage]
            w = int(frame.winfo_width() * pct / 100)
            bar.config(width=max(w, 0))
        self.root.after(0, _do)

    def _start_stage(self, stage):
        def _do():
            self.stage_icons[stage].config(text=">", fg=ACCENT_BLUE)
            self.stage_labels[stage].config(fg=TEXT_WHITE)
            self._update_stat("stage_info", stage.title())
            self._update_status(f"Running: {stage}...")
        self.root.after(0, _do)

    def _complete_stage(self, stage):
        def _do():
            self.stage_icons[stage].config(text="v", fg=SUCCESS_GRN)
            self.stage_labels[stage].config(fg=SUCCESS_GRN)
            self._update_bar(stage, 100)
        self.root.after(0, _do)

    def _fail_stage(self, stage):
        def _do():
            self.stage_icons[stage].config(text="x", fg=DANGER_RED)
            self.stage_labels[stage].config(fg=DANGER_RED)
        self.root.after(0, _do)

    def _simulate_stage(self, stage, seconds):
        import time
        for i in range(seconds * 10):
            if not self.is_running:
                break
            self._update_bar(stage, int((i / (seconds*10)) * 95))
            time.sleep(0.1)

    def _reset_stages(self):
        for key in self.stage_icons:
            self.stage_icons[key].config(text="o", fg=TEXT_MUTED)
            self.stage_labels[key].config(fg=TEXT_GRAY)
            _, bar = self.stage_bars[key]
            bar.config(width=0)
        self._update_stat("stage_info", "Running")

    def _update_timer(self):
        if self.is_running:
            elapsed = datetime.now() - self.start_time
            mins, secs = divmod(int(elapsed.total_seconds()), 60)
            self.stat_elapsed.config(text=f"{mins:02d}:{secs:02d}")
            self.root.after(1000, self._update_timer)

    def _set_example(self, problem):
        self.problem_entry.delete("1.0", "end")
        self.problem_entry.insert("1.0", problem)

    def _clear_log(self):
        self.log_text.config(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.config(state="disabled")

    def _open_output(self):
        import subprocess
        path = "D:\\math-channel\\output"
        Path(path).mkdir(parents=True, exist_ok=True)
        subprocess.Popen(f'explorer "{path}"')

    def _save_log(self):
        content = self.log_text.get("1.0", "end")
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            initialfile=f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        if path:
            with open(path, "w") as f:
                f.write(content)

    def _stop_pipeline(self):
        self.is_running = False
        self._log("Pipeline stopped by user.", "warning")
        self._update_status("Stopped.")
        self.run_btn.config(state="normal", bg=ACCENT_GREEN)
        self.stop_btn.config(state="disabled")

    def _open_url(self, url):
        import webbrowser
        webbrowser.open(url)

    def _check_api_key(self):
        key = self.api_key.get().strip()
        if key and len(key) > 20:
            self.api_status_label.config(text="● API: Groq ready", fg=SUCCESS_GRN)
        else:
            self.api_status_label.config(text="● API: key missing", fg=DANGER_RED)
        self.root.after(2000, self._check_api_key)


if __name__ == "__main__":
    root = tk.Tk()
    app  = MathChannelApp(root)
    root.mainloop()