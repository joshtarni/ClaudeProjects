import json
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from config import ConfigurationError, load_config, save_config
from launcher import LaunchError, launch_local


TITLE_NAMES = {
    "nfsu2_revived": "NFSU2 Revived",
    "vice_city_web": "Vice City Web Edition",
}


def integration_record_path() -> Path:
    return Path(__file__).resolve().parent / "offline_integrations.json"


def load_integration_records(path: Path | None = None) -> dict[str, dict]:
    record_path = path or integration_record_path()
    if not record_path.exists():
        return {}
    try:
        data = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def title_is_ready(title: str, records: dict[str, dict]) -> bool:
    record = records.get(title)
    if not isinstance(record, dict):
        return False
    return bool(
        record.get("authorized_source_build")
        and record.get("rights_evidence")
        and record.get("passed_TEST_003") is True
    )


class LauncherApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Offline Game Launcher")
        self.root.resizable(False, False)
        self.config_path = None
        self.records = load_integration_records()

        try:
            self.paths = load_config()
        except ConfigurationError as exc:
            self.paths = {title: None for title in TITLE_NAMES}
            messagebox.showerror("Configuration Error", str(exc), parent=root)

        frame = ttk.Frame(root, padding=20)
        frame.grid(sticky="nsew")

        ttk.Label(
            frame,
            text="Offline NFSU2 Revived and Vice City Launcher",
            font=("Segoe UI", 14, "bold"),
        ).grid(row=0, column=0, columnspan=3, pady=(0, 12))

        self.status_labels: dict[str, ttk.Label] = {}
        self.path_labels: dict[str, ttk.Label] = {}
        self.configure_buttons: dict[str, ttk.Button] = {}
        self.launch_buttons: dict[str, ttk.Button] = {}

        for row, title in enumerate(TITLE_NAMES, start=1):
            ttk.Label(frame, text=TITLE_NAMES[title], font=("Segoe UI", 11)).grid(
                row=row, column=0, sticky="w", padx=(0, 12)
            )
            status = "OFFLINE READY" if title_is_ready(title, self.records) else "UNAVAILABLE - NOT VERIFIED"
            self.status_labels[title] = ttk.Label(frame, text=status)
            self.status_labels[title].grid(row=row, column=1, sticky="w", padx=(0, 12))

            path = self.paths.get(title)
            self.path_labels[title] = ttk.Label(
                frame, text=path if path else "No local executable configured", width=48
            )
            self.path_labels[title].grid(row=row + 2, column=0, columnspan=2, sticky="w")

            self.configure_buttons[title] = ttk.Button(
                frame, text="Choose executable", command=lambda t=title: self.configure(t)
            )
            self.configure_buttons[title].grid(row=row, column=2)
            self.launch_buttons[title] = ttk.Button(
                frame, text="Launch", command=lambda t=title: self.launch(t)
            )
            self.launch_buttons[title].grid(row=row + 2, column=2)

            if not title_is_ready(title, self.records):
                self.launch_buttons[title].state(["disabled"])

    def configure(self, title: str) -> None:
        selected = filedialog.askopenfilename(
            title=f"Choose authorized local executable for {TITLE_NAMES[title]}",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
            parent=self.root,
        )
        if not selected:
            return
        self.paths[title] = selected
        try:
            save_config(self.paths)
        except (ConfigurationError, OSError) as exc:
            messagebox.showerror("Configuration Error", str(exc), parent=self.root)
            return
        self.path_labels[title].configure(text=selected)

    def launch(self, title: str) -> None:
        if not title_is_ready(title, self.records):
            messagebox.showerror(
                "Edition Unavailable",
                f"{TITLE_NAMES[title]} is unavailable offline until an authorized build "
                "has a complete integration record and passes TEST-003.",
                parent=self.root,
            )
            return

        target = self.paths.get(title)
        if not target:
            messagebox.showerror(
                "Build Not Configured",
                f"Choose a local executable for {TITLE_NAMES[title]}.",
                parent=self.root,
            )
            return
        try:
            launch_local(target)
        except LaunchError as exc:
            messagebox.showerror("Launch Failed", str(exc), parent=self.root)


def main() -> None:
    root = tk.Tk()
    LauncherApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
