import tkinter as tk
from tkinter import ttk
from datetime import datetime, time
from zoneinfo import ZoneInfo

ROME_TZ = ZoneInfo("Europe/Rome")
BUCHAREST_TZ = ZoneInfo("Europe/Bucharest")
ISTANBUL_TZ = ZoneInfo("Europe/Istanbul")

WORK_START_MORNING = time(9, 0)
WORK_END_MORNING = time(12, 0)
WORK_START_AFTERNOON = time(13, 0)
WORK_END_AFTERNOON = time(17, 30)


class WorldClockApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Orologi mondiali")
        self.configure(padx=24, pady=24, background="#f5f7fb")

        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Card.TFrame",
            background="#ffffff",
            relief="flat",
        )
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), background="#ffffff")
        style.configure("Subtitle.TLabel", font=("Segoe UI", 11), background="#ffffff", foreground="#5a667a")
        style.configure("CityName.TLabel", font=("Segoe UI", 11, "bold"), background="#eef2f9")
        style.configure("CityTime.TLabel", font=("Segoe UI", 11, "bold"), background="#eef2f9", foreground="#1a69d5")
        style.configure("Section.TLabel", font=("Segoe UI", 12, "bold"), background="#ffffff")
        style.configure("StatusOk.TLabel", font=("Segoe UI", 11, "bold"), foreground="#1f7a1f", background="#ffffff")
        style.configure("StatusAlert.TLabel", font=("Segoe UI", 11, "bold"), foreground="#c62828", background="#ffffff")
        style.configure("StatusNeutral.TLabel", font=("Segoe UI", 11), foreground="#5a667a", background="#ffffff")

        card = ttk.Frame(self, padding=24, style="Card.TFrame")
        card.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        title = ttk.Label(card, text="Orario attuale", style="Title.TLabel")
        title.grid(row=0, column=0, sticky="w")
        subtitle = ttk.Label(
            card,
            text="Fusi orari di Roma, Bucarest e Istanbul.",
            style="Subtitle.TLabel",
        )
        subtitle.grid(row=1, column=0, pady=(4, 16), sticky="w")

        self.clock_frame = ttk.Frame(card, padding=0, style="Card.TFrame")
        self.clock_frame.grid(row=2, column=0, sticky="ew")
        self.clock_frame.columnconfigure(1, weight=1)

        self.city_labels = {}
        for idx, (city, zone) in enumerate(
            (
                ("Roma", ROME_TZ),
                ("Bucarest", BUCHAREST_TZ),
                ("Istanbul", ISTANBUL_TZ),
            )
        ):
            row_frame = ttk.Frame(self.clock_frame)
            row_frame.grid(row=idx, column=0, sticky="ew", pady=4)
            row_frame.columnconfigure(1, weight=1)
            row_frame.configure(style="Card.TFrame")

            pill = tk.Frame(row_frame, bg="#eef2f9", padx=16, pady=10)
            pill.grid(row=0, column=0, sticky="ew")
            pill.columnconfigure(1, weight=1)

            name_label = ttk.Label(pill, text=city, style="CityName.TLabel")
            name_label.grid(row=0, column=0, sticky="w")

            time_label = ttk.Label(pill, text="--:--:--", style="CityTime.TLabel")
            time_label.grid(row=0, column=1, sticky="e")
            self.city_labels[zone] = time_label

        separator = ttk.Separator(card, orient="horizontal")
        separator.grid(row=3, column=0, sticky="ew", pady=20)

        meeting_label = ttk.Label(card, text="Verifica orario riunione", style="Section.TLabel")
        meeting_label.grid(row=4, column=0, sticky="w")

        form_frame = ttk.Frame(card, padding=(0, 12, 0, 0), style="Card.TFrame")
        form_frame.grid(row=5, column=0, sticky="ew")
        form_frame.columnconfigure(1, weight=1)
        form_frame.columnconfigure(3, weight=1)

        ttk.Label(form_frame, text="Inizio (Roma):", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        self.start_var = tk.StringVar()
        start_entry = ttk.Entry(form_frame, textvariable=self.start_var, width=10)
        start_entry.grid(row=0, column=1, sticky="w", padx=(8, 16))
        start_entry.insert(0, "09:00")

        ttk.Label(form_frame, text="Fine (Roma):", style="Subtitle.TLabel").grid(
            row=0, column=2, sticky="w"
        )
        self.end_var = tk.StringVar()
        end_entry = ttk.Entry(form_frame, textvariable=self.end_var, width=10)
        end_entry.grid(row=0, column=3, sticky="w", padx=(8, 0))
        end_entry.insert(0, "10:00")

        hint = ttk.Label(
            form_frame,
            text="Formato HH:MM (ora di Roma)",
            style="Subtitle.TLabel",
        )
        hint.grid(row=1, column=0, columnspan=4, sticky="w", pady=(6, 0))

        self.status_label = ttk.Label(card, text="", style="StatusNeutral.TLabel")
        self.status_label.grid(row=6, column=0, sticky="w", pady=(12, 0))

        self.start_var.trace_add("write", lambda *_: self.evaluate_meeting())
        self.end_var.trace_add("write", lambda *_: self.evaluate_meeting())

        self.update_times()
        self.evaluate_meeting()

    def update_times(self) -> None:
        now_rome = datetime.now(tz=ROME_TZ)
        for zone, label in self.city_labels.items():
            local_time = now_rome.astimezone(zone)
            label.config(text=local_time.strftime("%H:%M:%S"))
        self.after(1000, self.update_times)

    def evaluate_meeting(self) -> None:
        start_time = self._parse_time(self.start_var.get())
        end_time = self._parse_time(self.end_var.get())

        if not start_time or not end_time:
            self._set_status("Inserisci un orario valido.", "neutral")
            return

        if end_time <= start_time:
            self._set_status("L'orario di fine deve essere dopo l'inizio.", "alert")
            return

        today = datetime.now(tz=ROME_TZ).date()
        start_dt = datetime.combine(today, start_time, tzinfo=ROME_TZ)
        end_dt = datetime.combine(today, end_time, tzinfo=ROME_TZ)

        bucharest_ok = self._is_within_working_hours(start_dt.astimezone(BUCHAREST_TZ), end_dt.astimezone(BUCHAREST_TZ))
        istanbul_ok = self._is_within_working_hours(start_dt.astimezone(ISTANBUL_TZ), end_dt.astimezone(ISTANBUL_TZ))

        if bucharest_ok and istanbul_ok:
            self._set_status("OK", "ok")
        else:
            self._set_status("L'orario proposto non rientra negli slot orari locali", "alert")

    @staticmethod
    def _parse_time(value: str) -> time | None:
        try:
            parsed = datetime.strptime(value.strip(), "%H:%M").time()
        except ValueError:
            return None
        return parsed

    @staticmethod
    def _is_within_working_hours(start_dt: datetime, end_dt: datetime) -> bool:
        start_local = start_dt.timetz().replace(tzinfo=None)
        end_local = end_dt.timetz().replace(tzinfo=None)
        in_morning = start_local >= WORK_START_MORNING and end_local <= WORK_END_MORNING
        in_afternoon = start_local >= WORK_START_AFTERNOON and end_local <= WORK_END_AFTERNOON
        return in_morning or in_afternoon

    def _set_status(self, message: str, status: str) -> None:
        styles = {
            "ok": "StatusOk.TLabel",
            "alert": "StatusAlert.TLabel",
            "neutral": "StatusNeutral.TLabel",
        }
        self.status_label.configure(text=message, style=styles.get(status, "StatusNeutral.TLabel"))


if __name__ == "__main__":
    app = WorldClockApp()
    app.mainloop()
