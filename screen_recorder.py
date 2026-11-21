import ctypes
import json
import os
import queue
import shutil
import subprocess
import tempfile
import threading
import time
import tkinter as tk
import wave
from tkinter import filedialog, messagebox, ttk

import imageio_ffmpeg
import mss
import numpy as np
import soundcard


FPS = 20
AUDIO_SAMPLE_RATE = 48000
AUDIO_CHANNELS = 2
AUDIO_BLOCK_SIZE = 2048
MIN_WIDTH = 160
MIN_HEIGHT = 90
HANDLE_SIZE = 30
TRANSPARENT_COLOR = "#ff00ff"


def record_system_audio(path, stop_event, resume_event, ready_event, errors):
    try:
        speaker = soundcard.default_speaker()
        if speaker is None:
            raise RuntimeError("No default audio output device is available.")
        loopback = soundcard.get_microphone(
            id=str(speaker.name),
            include_loopback=True,
        )
        with loopback.recorder(
            samplerate=AUDIO_SAMPLE_RATE,
            channels=AUDIO_CHANNELS,
        ) as recorder, wave.open(path, "wb") as output:
            output.setnchannels(AUDIO_CHANNELS)
            output.setsampwidth(2)
            output.setframerate(AUDIO_SAMPLE_RATE)
            ready_event.set()
            first_read = True
            while not stop_event.is_set() or first_read:
                if not resume_event.wait(timeout=0.1):
                    continue
                samples = recorder.record(numframes=AUDIO_BLOCK_SIZE)
                first_read = False
                if samples.size and resume_event.is_set():
                    pcm = np.clip(samples, -1.0, 1.0)
                    output.writeframesraw((pcm * 32767).astype("<i2").tobytes())
    except Exception as error:
        errors.append(str(error))
    finally:
        ready_event.set()


def mux_video_with_audio(video_path, audio_path):
    directory = os.path.dirname(os.path.abspath(video_path))
    descriptor, muxed_path = tempfile.mkstemp(
        prefix=".screen-recording-mux-",
        suffix=".mp4",
        dir=directory,
    )
    os.close(descriptor)
    try:
        command = [
            imageio_ffmpeg.get_ffmpeg_exe(),
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            video_path,
            "-i",
            audio_path,
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-shortest",
            "-movflags",
            "+faststart",
            muxed_path,
        ]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(
                f"Could not add system audio to the recording: {result.stderr.strip()}"
            )
        os.replace(muxed_path, video_path)
    finally:
        if os.path.exists(muxed_path):
            os.remove(muxed_path)


class ScreenRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Area Recorder")
        self.root.geometry("390x335")
        self.root.resizable(False, False)
        self.root.configure(bg="#0b1120")
        self._configure_theme()
        self._user32 = ctypes.windll.user32
        self._hotkey_path = os.path.join(
            os.environ.get("APPDATA", os.path.expanduser("~")),
            "ScreenAreaRecorder",
            "hotkeys.json",
        )
        self._hotkeys = {
            "Start": "Ctrl+Shift+F8",
            "Pause/Resume": "Ctrl+Shift+F9",
            "Stop": "Ctrl+Shift+F10",
        }
        self._hotkey_load_error = self._load_hotkeys()
        self._hotkey_pressed = {action: False for action in self._hotkeys}
        self._hotkeys_enabled = True

        self.capture_box = tk.Toplevel(root)
        self.capture_box.overrideredirect(True)
        self.capture_box.attributes("-topmost", True)
        self.capture_box.geometry("640x360+80+80")

        self.canvas = tk.Canvas(
            self.capture_box,
            bg=TRANSPARENT_COLOR,
            highlightthickness=0,
            bd=0,
        )
        self.canvas.pack(fill="both", expand=True)
        self.capture_box.bind("<Configure>", self._draw_capture_box)
        self.canvas.bind("<ButtonPress-1>", self._begin_box_drag)
        self.canvas.bind("<B1-Motion>", self._move_or_resize_box)

        try:
            self.capture_box.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
        except tk.TclError:
            self.capture_box.attributes("-alpha", 0.25)

        self._drag_mode = "move"
        self._drag_start = (0, 0)
        self._box_start = (0, 0, 0, 0)
        self._recording = False
        self._paused = False
        self._stop_event = threading.Event()
        self._resume_event = threading.Event()
        self._messages = queue.Queue()
        self._worker = None
        self._temporary_path = None
        self._audio_temporary_path = None

        self.status = tk.StringVar(value="Ready")
        self._build_controls()
        self.root.protocol("WM_DELETE_WINDOW", self.close)
        self.root.after(200, self._check_worker_messages)
        self.root.after(50, self._check_hotkeys)
        if self._hotkey_load_error:
            self.root.after(
                100,
                lambda: messagebox.showwarning(
                    "Hotkeys could not be loaded",
                    self._hotkey_load_error,
                    parent=self.root,
                ),
            )

    def _configure_theme(self):
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("App.TFrame", background="#0b1120")
        style.configure("Card.TFrame", background="#151e2f")
        style.configure(
            "Title.TLabel",
            background="#0b1120",
            foreground="#f1f5f9",
            font=("Segoe UI", 18, "bold"),
        )
        style.configure(
            "Subtitle.TLabel",
            background="#0b1120",
            foreground="#94a3b8",
            font=("Segoe UI", 9),
        )
        style.configure(
            "CardTitle.TLabel",
            background="#151e2f",
            foreground="#e2e8f0",
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "CardText.TLabel",
            background="#151e2f",
            foreground="#94a3b8",
            font=("Segoe UI", 9),
        )
        style.configure(
            "Status.TLabel",
            background="#151e2f",
            foreground="#cbd5e1",
            font=("Segoe UI", 9, "bold"),
        )
        style.configure(
            "Primary.TButton",
            background="#2563eb",
            foreground="#ffffff",
            borderwidth=0,
            padding=(16, 10),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Primary.TButton",
            background=[("disabled", "#26344b"), ("active", "#3b82f6")],
            foreground=[("disabled", "#718096"), ("active", "#ffffff")],
        )
        style.configure(
            "Secondary.TButton",
            background="#263449",
            foreground="#e2e8f0",
            borderwidth=0,
            padding=(16, 10),
            font=("Segoe UI", 9, "bold"),
        )
        style.map(
            "Secondary.TButton",
            background=[("disabled", "#1a2434"), ("active", "#35465f")],
            foreground=[("disabled", "#64748b"), ("active", "#ffffff")],
        )

    def _build_controls(self):
        shell = ttk.Frame(self.root, style="App.TFrame", padding=(24, 20, 24, 18))
        shell.pack(fill="both", expand=True)

        ttk.Label(shell, text="Screen Recorder", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            shell,
            text="Capture just the part of your screen you need.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", pady=(2, 16))

        card = ttk.Frame(shell, style="Card.TFrame", padding=(16, 13))
        card.pack(fill="x")
        ttk.Label(card, text="CAPTURE AREA", style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(
            card,
            text="Drag the outline to move it and use the bottom-right handle to resize. "
            "The area is locked while recording.",
            style="CardText.TLabel",
            wraplength=310,
            justify="left",
        ).pack(anchor="w", pady=(5, 10))

        status_row = ttk.Frame(card, style="Card.TFrame")
        status_row.pack(fill="x")
        self.status_dot = tk.Canvas(
            status_row,
            width=10,
            height=10,
            bg="#151e2f",
            highlightthickness=0,
        )
        self.status_dot.pack(side="left", padx=(0, 8))
        self.status_dot.create_oval(1, 1, 9, 9, fill="#64748b", outline="")
        ttk.Label(status_row, textvariable=self.status, style="Status.TLabel").pack(
            side="left", fill="x", expand=True
        )

        controls = ttk.Frame(shell, style="App.TFrame")
        controls.pack(fill="x", pady=(15, 0))
        self.start_button = ttk.Button(
            controls,
            text="Start recording",
            style="Primary.TButton",
            command=self.start_recording,
        )
        self.start_button.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.pause_button = ttk.Button(
            controls,
            text="Pause",
            style="Secondary.TButton",
            command=self.pause_recording,
            state="disabled",
        )
        self.pause_button.pack(side="left", fill="x", expand=True, padx=6)
        self.stop_button = ttk.Button(
            controls,
            text="Stop",
            style="Secondary.TButton",
            command=self.stop_recording,
            state="disabled",
        )
        self.stop_button.pack(side="left", fill="x", expand=True, padx=(6, 0))

        ttk.Button(
            shell,
            text="Set up hotkeys…",
            style="Secondary.TButton",
            command=self.open_hotkey_settings,
        ).pack(fill="x", pady=(10, 0))

    def _set_status(self, text, recording=False):
        self.status.set(text)
        color = "#ef4444" if recording else "#64748b"
        self.status_dot.itemconfigure(1, fill=color)

    def _draw_capture_box(self, _event=None):
        width = self.capture_box.winfo_width()
        height = self.capture_box.winfo_height()
        self.canvas.delete("overlay")
        self.canvas.create_rectangle(
            2,
            2,
            width - 2,
            height - 2,
            outline="#00e5ff",
            width=4,
            tags="overlay",
        )
        self.canvas.create_text(
            12,
            12,
            anchor="nw",
            text="CAPTURE AREA",
            fill="white",
            font=("Segoe UI", 10, "bold"),
            tags="overlay",
        )
        self.canvas.create_rectangle(
            width - HANDLE_SIZE,
            height - HANDLE_SIZE,
            width - 3,
            height - 3,
            fill="#00e5ff",
            outline="white",
            width=1,
            tags="overlay",
        )

    def _begin_box_drag(self, event):
        width = self.capture_box.winfo_width()
        height = self.capture_box.winfo_height()
        self._drag_mode = (
            "resize"
            if event.x >= width - HANDLE_SIZE and event.y >= height - HANDLE_SIZE
            else "move"
        )
        self._drag_start = (event.x_root, event.y_root)
        self._box_start = (
            self.capture_box.winfo_x(),
            self.capture_box.winfo_y(),
            width,
            height,
        )

    def _move_or_resize_box(self, event):
        start_x, start_y = self._drag_start
        left, top, width, height = self._box_start
        delta_x = event.x_root - start_x
        delta_y = event.y_root - start_y
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        if self._drag_mode == "resize":
            width = max(MIN_WIDTH, min(width + delta_x, screen_width - left))
            height = max(MIN_HEIGHT, min(height + delta_y, screen_height - top))
            self.capture_box.geometry(f"{width}x{height}+{left}+{top}")
        else:
            left = max(0, min(left + delta_x, screen_width - width))
            top = max(0, min(top + delta_y, screen_height - height))
            self.capture_box.geometry(f"{width}x{height}+{left}+{top}")

    def start_recording(self):
        if self._recording:
            return

        try:
            descriptor, path = tempfile.mkstemp(
                prefix=".screen-recording-",
                suffix=".mp4",
                dir=os.path.dirname(os.path.abspath(__file__)),
            )
            os.close(descriptor)
        except OSError as error:
            messagebox.showerror("Could not start recording", str(error), parent=self.root)
            return

        region = {
            "left": self.capture_box.winfo_x(),
            "top": self.capture_box.winfo_y(),
            "width": self.capture_box.winfo_width(),
            "height": self.capture_box.winfo_height(),
        }
        self.capture_box.withdraw()
        self._stop_event.clear()
        self._resume_event.set()
        self._recording = True
        self._paused = False
        self._temporary_path = path
        self._audio_temporary_path = os.path.splitext(path)[0] + ".wav"
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal", text="Pause")
        self.stop_button.config(state="normal")
        self._set_status("Recording…", recording=True)
        self._worker = threading.Thread(
            target=self._record,
            args=(region, path, self._audio_temporary_path),
            daemon=True,
        )
        self._worker.start()

    def pause_recording(self):
        if not self._recording or self.stop_button.instate(["disabled"]):
            return
        if self._paused:
            self._paused = False
            self._resume_event.set()
            self.pause_button.config(text="Pause")
            self._set_status("Recording…", recording=True)
        else:
            self._paused = True
            self._resume_event.clear()
            self.pause_button.config(text="Resume")
            self._set_status("Paused")

    def stop_recording(self):
        if self._recording:
            self._paused = False
            self._resume_event.set()
            self._set_status("Finishing video…", recording=True)
            self.stop_button.config(state="disabled")
            self.pause_button.config(state="disabled")
            self._stop_event.set()

    def _record(self, region, path, audio_path):
        process = None
        audio_thread = None
        audio_errors = []
        audio_ready = threading.Event()
        frame_count = 0
        started = None
        next_frame_at = None
        paused_at = None
        paused_duration = 0
        try:
            audio_thread = threading.Thread(
                target=record_system_audio,
                args=(
                    audio_path,
                    self._stop_event,
                    self._resume_event,
                    audio_ready,
                    audio_errors,
                ),
                daemon=True,
            )
            audio_thread.start()
            if not audio_ready.wait(timeout=10):
                raise RuntimeError("Timed out while opening the system audio capture device.")
            if audio_errors:
                raise RuntimeError(f"Could not capture system audio: {audio_errors[0]}")

            ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
            width = region["width"]
            height = region["height"]
            command = [
                ffmpeg,
                "-y",
                "-hide_banner",
                "-loglevel",
                "error",
                "-f",
                "rawvideo",
                "-vcodec",
                "rawvideo",
                "-pix_fmt",
                "rgb24",
                "-s",
                f"{width}x{height}",
                "-r",
                str(FPS),
                "-i",
                "-",
                "-c:v",
                "libx264",
                "-preset",
                "veryfast",
                "-crf",
                "28",
                "-vf",
                "pad=ceil(iw/2)*2:ceil(ih/2)*2",
                "-pix_fmt",
                "yuv420p",
                "-movflags",
                "+faststart",
                path,
            ]
            process = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            with mss.mss() as screen:
                started = time.monotonic()
                next_frame_at = started
                while not self._stop_event.is_set() or frame_count == 0:
                    if not self._resume_event.wait(timeout=0.1):
                        if paused_at is None:
                            paused_at = time.monotonic()
                        continue
                    now = time.monotonic()
                    if paused_at is not None:
                        paused_duration += now - paused_at
                        paused_at = None
                        next_frame_at = now
                    if audio_errors:
                        raise RuntimeError(f"System audio capture failed: {audio_errors[0]}")
                    if process.poll() is not None:
                        raise RuntimeError(
                            f"FFmpeg stopped unexpectedly (exit code {process.returncode})."
                        )
                    frame = screen.grab(region)
                    if not self._resume_event.is_set():
                        continue
                    process.stdin.write(frame.rgb)
                    frame_count += 1
                    if frame_count % FPS == 0 and not self._paused:
                        elapsed = max(now - started - paused_duration, 0.1)
                        self._messages.put(
                            ("status", f"Recording… {frame_count / elapsed:.0f} FPS")
                        )
                    next_frame_at += 1 / FPS
                    delay = next_frame_at - time.monotonic()
                    if delay > 0:
                        self._stop_event.wait(min(delay, 0.02))

            process.stdin.close()
            return_code = process.wait(timeout=15)
            if return_code != 0:
                raise RuntimeError(f"FFmpeg could not finish the video (exit code {return_code}).")
            audio_thread.join(timeout=5)
            if audio_thread.is_alive():
                raise RuntimeError("System audio capture did not stop cleanly.")
            if audio_errors:
                raise RuntimeError(f"System audio capture failed: {audio_errors[0]}")
            if not os.path.exists(audio_path) or os.path.getsize(audio_path) <= 44:
                raise RuntimeError("System audio capture produced an empty audio track.")
            mux_video_with_audio(path, audio_path)
            os.remove(audio_path)
            self._messages.put(("done", (path, audio_path)))
        except Exception as error:
            self._stop_event.set()
            if audio_thread is not None:
                audio_thread.join(timeout=5)
            if process is not None and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
            self._messages.put(("error", (path, audio_path, str(error))))
        finally:
            if process is not None and process.stdin and not process.stdin.closed:
                process.stdin.close()

    def _check_worker_messages(self):
        try:
            while True:
                kind, detail = self._messages.get_nowait()
                if kind == "status":
                    if not self._paused:
                        self._set_status(detail, recording=True)
                    continue
                self._recording = False
                self._paused = False
                self._resume_event.set()
                self.pause_button.config(state="disabled", text="Pause")
                self.stop_button.config(state="disabled")
                self.start_button.config(state="normal")
                if kind == "done":
                    self.capture_box.withdraw()
                    video_path, _audio_path = detail
                    self._save_recording(video_path)
                    self.capture_box.deiconify()
                    self.capture_box.lift()
                else:
                    temporary_path, audio_path, error = detail
                    self._discard_recording(temporary_path)
                    self._discard_recording(audio_path)
                    self.capture_box.deiconify()
                    self.capture_box.lift()
                    self._set_status("Recording failed")
                    messagebox.showerror("Recording failed", error, parent=self.root)
        except queue.Empty:
            pass
        self.root.after(200, self._check_worker_messages)

    def _save_recording(self, temporary_path):
        while True:
            destination = filedialog.asksaveasfilename(
                parent=self.root,
                title="Save screen recording",
                defaultextension=".mp4",
                filetypes=[("MP4 video", "*.mp4")],
                initialfile="screen-recording.mp4",
                initialdir=os.path.dirname(os.path.abspath(__file__)),
            )
            if not destination:
                self._discard_recording(temporary_path)
                self._set_status("Recording discarded")
                return

            if os.path.exists(destination) and not messagebox.askyesno(
                "Overwrite file?",
                f"{destination} already exists. Replace it?",
                parent=self.root,
            ):
                continue

            try:
                if os.path.abspath(destination) != os.path.abspath(temporary_path):
                    shutil.move(temporary_path, destination)
                self._temporary_path = None
                self._audio_temporary_path = None
                self._set_status(f"Saved: {destination}")
            except OSError as error:
                self._set_status("Could not save recording")
                messagebox.showerror(
                    "Could not save recording",
                    f"{error}\n\nThe temporary video is still available at:\n{temporary_path}",
                    parent=self.root,
                )
            return

    def _discard_recording(self, path):
        if not path:
            return
        try:
            if os.path.exists(path):
                os.remove(path)
            if self._temporary_path == path:
                self._temporary_path = None
            if self._audio_temporary_path == path:
                self._audio_temporary_path = None
        except OSError as error:
            messagebox.showerror(
                "Could not remove temporary recording",
                f"{error}\n\nTemporary video location:\n{path}",
                parent=self.root,
            )

    def close(self):
        if self._recording:
            self._resume_event.set()
            self._stop_event.set()
            if self._worker is not None:
                self._worker.join(timeout=2)
        self.root.destroy()

    def _load_hotkeys(self):
        if not os.path.exists(self._hotkey_path):
            return None
        try:
            with open(self._hotkey_path, "r", encoding="utf-8") as settings:
                hotkeys = json.load(settings)
            if not isinstance(hotkeys, dict) or set(hotkeys) != set(self._hotkeys):
                raise ValueError("The hotkey settings file has an invalid format.")
            if any(not self._parse_hotkey(value) for value in hotkeys.values()):
                raise ValueError("The hotkey settings file contains an unsupported shortcut.")
            if len(set(hotkeys.values())) != len(hotkeys):
                raise ValueError("Each action must have a different shortcut.")
            self._hotkeys = hotkeys
        except (OSError, ValueError, json.JSONDecodeError) as error:
            return f"{error}\nDefault hotkeys will be used."
        return None

    @staticmethod
    def _parse_hotkey(shortcut):
        if not isinstance(shortcut, str):
            return None
        parts = shortcut.split("+")
        if not parts or any(not part for part in parts):
            return None
        modifiers = set()
        for part in parts[:-1]:
            normalized = part.strip().lower()
            modifier = {
                "ctrl": "ctrl",
                "control": "ctrl",
                "alt": "alt",
                "shift": "shift",
            }.get(normalized)
            if modifier is None or modifier in modifiers:
                return None
            modifiers.add(modifier)

        key = parts[-1].strip()
        key_name = key.lower()
        special_keys = {
            "backspace": 0x08,
            "tab": 0x09,
            "clear": 0x0C,
            "return": 0x0D,
            "enter": 0x0D,
            "pause": 0x13,
            "caps_lock": 0x14,
            "escape": 0x1B,
            "space": 0x20,
            "page_up": 0x21,
            "page_down": 0x22,
            "end": 0x23,
            "home": 0x24,
            "left": 0x25,
            "up": 0x26,
            "right": 0x27,
            "down": 0x28,
            "insert": 0x2D,
            "delete": 0x2E,
        }
        if key_name in special_keys:
            key_code = special_keys[key_name]
        elif key_name.startswith("f") and key_name[1:].isdigit():
            number = int(key_name[1:])
            if not 1 <= number <= 24:
                return None
            key_code = 0x6F + number
        elif len(key) == 1 and key.isprintable():
            key_code = key.upper()
            key_code = ord(key_code)
            if key_code > 0x7F:
                return None
        else:
            return None
        return key_code, frozenset(modifiers)

    def _check_hotkeys(self):
        if self._hotkeys_enabled:
            modifier_keys = {
                "ctrl": 0x11,
                "alt": 0x12,
                "shift": 0x10,
            }
            for action, shortcut in self._hotkeys.items():
                parsed = self._parse_hotkey(shortcut)
                pressed = False
                if parsed:
                    key_code, modifiers = parsed
                    pressed = bool(self._user32.GetAsyncKeyState(key_code) & 0x8000)
                    for modifier, modifier_key in modifier_keys.items():
                        modifier_pressed = bool(
                            self._user32.GetAsyncKeyState(modifier_key) & 0x8000
                        )
                        if modifier_pressed != (modifier in modifiers):
                            pressed = False
                            break
                if pressed and not self._hotkey_pressed[action]:
                    {
                        "Start": self.start_recording,
                        "Pause/Resume": self.pause_recording,
                        "Stop": self.stop_recording,
                    }[action]()
                self._hotkey_pressed[action] = pressed
        else:
            self._hotkey_pressed = {action: False for action in self._hotkeys}
        self.root.after(50, self._check_hotkeys)

    def open_hotkey_settings(self):
        if hasattr(self, "_hotkey_window") and self._hotkey_window.winfo_exists():
            self._hotkey_window.lift()
            return

        window = tk.Toplevel(self.root)
        self._hotkey_window = window
        window.title("Set up hotkeys")
        window.geometry("360x290")
        window.minsize(360, 290)
        window.resizable(False, False)
        window.configure(bg="#0b1120")
        window.transient(self.root)
        window.grab_set()
        self._hotkeys_enabled = False
        pending_hotkeys = dict(self._hotkeys)
        buttons = {}

        ttk.Label(
            window,
            text="Choose a shortcut for each action.",
            style="Subtitle.TLabel",
        ).pack(anchor="w", padx=18, pady=(16, 10))

        rows = ttk.Frame(window, style="App.TFrame", padding=(18, 0))
        rows.pack(fill="x")
        for action in self._hotkeys:
            row = ttk.Frame(rows, style="App.TFrame")
            row.pack(fill="x", pady=4)
            ttk.Label(row, text=action, style="Subtitle.TLabel", width=14).pack(
                side="left"
            )
            button = ttk.Button(
                row,
                text=pending_hotkeys[action],
                style="Secondary.TButton",
            )
            button.pack(side="right", fill="x", expand=True)
            buttons[action] = button

        def capture_shortcut(action):
            buttons[action].config(text="Press a shortcut…")

            def on_key(event):
                if event.keysym in (
                    "Shift_L",
                    "Shift_R",
                    "Control_L",
                    "Control_R",
                    "Alt_L",
                    "Alt_R",
                ):
                    return "break"
                modifiers = []
                if event.state & 0x0004:
                    modifiers.append("Ctrl")
                if event.state & 0x0008 or event.state & 0x20000:
                    modifiers.append("Alt")
                if event.state & 0x0001:
                    modifiers.append("Shift")
                key = event.keysym
                key = {
                    "Prior": "Page_Up",
                    "Next": "Page_Down",
                    "Return": "Enter",
                    "Escape": "Escape",
                    "space": "Space",
                    "BackSpace": "Backspace",
                }.get(key, key)
                candidate = "+".join(modifiers + [key])
                if not self._parse_hotkey(candidate):
                    buttons[action].config(text="Unsupported key")
                    return "break"
                pending_hotkeys[action] = candidate
                buttons[action].config(text=candidate)
                window.unbind("<KeyPress>")
                return "break"

            window.bind("<KeyPress>", on_key)
            window.focus_force()

        for action, button in buttons.items():
            button.config(command=lambda name=action: capture_shortcut(name))

        footer = ttk.Frame(window, style="App.TFrame", padding=(18, 12, 18, 14))
        footer.pack(fill="x", side="bottom")

        def close_settings():
            self._hotkeys_enabled = True
            window.grab_release()
            window.destroy()

        def save_settings():
            if len(set(pending_hotkeys.values())) != len(pending_hotkeys):
                messagebox.showerror(
                    "Duplicate hotkeys",
                    "Each action must have a different shortcut.",
                    parent=window,
                )
                return
            try:
                os.makedirs(os.path.dirname(self._hotkey_path), exist_ok=True)
                with open(self._hotkey_path, "w", encoding="utf-8") as settings:
                    json.dump(pending_hotkeys, settings, indent=2)
            except OSError as error:
                messagebox.showerror(
                    "Could not save hotkeys",
                    str(error),
                    parent=window,
                )
                return
            self._hotkeys = pending_hotkeys
            self._hotkey_pressed = {action: False for action in self._hotkeys}
            close_settings()

        ttk.Button(
            footer,
            text="Cancel",
            style="Secondary.TButton",
            command=close_settings,
        ).pack(side="right", padx=(8, 0))
        ttk.Button(
            footer,
            text="Save",
            style="Primary.TButton",
            command=save_settings,
        ).pack(side="right")
        window.protocol("WM_DELETE_WINDOW", close_settings)


def main():
    root = tk.Tk()
    ScreenRecorder(root)
    root.mainloop()


if __name__ == "__main__":
    main()
