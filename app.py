import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from ai.ai import RecommendationAssistant
from analytics.butterfly import calculate as butterfly_score
from analytics.habitat import calculate as habitat_score
from analytics.plant import calculate as plant_score
from analytics.pollinator import calculate as bee_score
from services.weather_service import WeatherService


class BioSphereAIApp(tk.Tk):
    # Main desktop window for the BioSphereAI dashboard.
    def __init__(self):
        super().__init__()
        self.title("BioSphereAI")
        self.geometry("980x700")
        self.minsize(900, 620)
        self.configure(bg="#07111f")

        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.style.configure("Header.TLabel", background="#07111f", foreground="#f8fafc", font=("Segoe UI", 22, "bold"))
        self.style.configure("Subtitle.TLabel", background="#07111f", foreground="#93c5fd", font=("Segoe UI", 11))
        self.style.configure("Card.TFrame", background="#0f172a")
        self.style.configure("CardTitle.TLabel", background="#0f172a", foreground="#e2e8f0", font=("Segoe UI", 13, "bold"))
        self.style.configure("Value.TLabel", background="#0f172a", foreground="#f8fafc", font=("Segoe UI", 20, "bold"))
        self.style.configure("Body.TLabel", background="#0f172a", foreground="#cbd5e1", font=("Segoe UI", 10))
        self.style.configure("Accent.TLabel", background="#0f172a", foreground="#34d399", font=("Segoe UI", 11, "bold"))

        self.style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(16, 8))
        self.style.map("Primary.TButton", background=[("active", "#1d4ed8")])

        self.style.configure("Search.TEntry", fieldbackground="#0b1220", foreground="#f8fafc", borderwidth=0)
        self.style.configure("Search.TFrame", background="#0f172a")

        self.service = WeatherService()
        self.assistant = RecommendationAssistant()

        self.build_layout()
        self.load_default_data()

    def build_layout(self):
        # Create a scrollable canvas so the window can be moved vertically.
        self.canvas = tk.Canvas(self, bg="#07111f", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True, padx=(18, 0), pady=18)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.content_frame = tk.Frame(self.canvas, bg="#07111f")
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")
        self.content_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Header area for the app title and subtitle.
        header = tk.Frame(self.content_frame, bg="#07111f")
        header.pack(fill="x", pady=(0, 18))

        tk.Label(header, text="🌎 BioSphereAI", bg="#07111f", fg="#f8fafc", font=("Segoe UI", 28, "bold")).pack(anchor="w")
        tk.Label(header, text="A modern ecological dashboard from live weather conditions", bg="#07111f", fg="#93c5fd", font=("Segoe UI", 11)).pack(anchor="w", pady=(4, 0))

        # Search / refresh area for ZIP-based weather lookup.
        search_frame = tk.Frame(self.content_frame, bg="#0f172a", padx=14, pady=14)
        search_frame.pack(fill="x", pady=(0, 16))

        tk.Label(search_frame, text="ZIP Code", bg="#0f172a", fg="#e2e8f0", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 12))

        self.zip_entry = ttk.Entry(search_frame, width=16, style="Search.TEntry")
        self.zip_entry.insert(0, "13760")
        self.zip_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12))

        self.search_button = ttk.Button(search_frame, text="Refresh forecast", style="Primary.TButton", command=self.load_location_data)
        self.search_button.grid(row=0, column=2, sticky="w")

        self.status_label = tk.Label(search_frame, text="Loading live forecast…", bg="#0f172a", fg="#a7f3d0", font=("Segoe UI", 10, "bold"))
        self.status_label.grid(row=0, column=3, sticky="w", padx=(18, 0))

        search_frame.columnconfigure(1, weight=1)

        # Weather summary card that updates whenever the ZIP code changes.
        self.weather_card, self.weather_body = self.create_card(self.content_frame, "Current Weather")
        self.weather_card.pack(fill="x", pady=(0, 12))

        # Grid of score cards for plant, bee, butterfly, and habitat health.
        metrics_grid = tk.Frame(self.content_frame, bg="#07111f")
        metrics_grid.pack(fill="both", expand=True)

        self.metric_cards = {
            "plant": self.create_metric_card(metrics_grid, "🌱 Plant Health", "0%"),
            "bee": self.create_metric_card(metrics_grid, "🐝 Bee Activity", "0%"),
            "butterfly": self.create_metric_card(metrics_grid, "🦋 Butterfly Activity", "0%"),
            "habitat": self.create_metric_card(metrics_grid, "🌳 Habitat Health", "0%"),
        }

        self.metric_cards["plant"].grid(row=0, column=0, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.metric_cards["bee"].grid(row=0, column=1, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.metric_cards["butterfly"].grid(row=0, column=2, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.metric_cards["habitat"].grid(row=0, column=3, pady=(0, 12), sticky="nsew")

        metrics_grid.columnconfigure((0, 1, 2, 3), weight=1)

        # AI recommendation panel that displays practical suggestions from the live score data.
        self.recommendation_card, self.recommendation_body = self.create_card(self.content_frame, "AI Assistant Recommendations")
        self.recommendation_card.pack(fill="both", expand=True)

        self.recommendations_box = scrolledtext.ScrolledText(
            self.recommendation_body,
            wrap=tk.WORD,
            bg="#0b1220",
            fg="#f8fafc",
            insertbackground="#f8fafc",
            relief="flat",
            padx=12,
            pady=10,
            font=("Segoe UI", 10),
            height=12,
        )
        self.recommendations_box.pack(fill="both", expand=True, pady=(10, 0))

    def create_card(self, parent, title):
        # Shared helper for producing a styled card with a title and content body.
        frame = ttk.Frame(parent, style="Card.TFrame", padding=(16, 14))
        title_label = ttk.Label(frame, text=title, style="CardTitle.TLabel")
        title_label.pack(anchor="w")

        body = tk.Frame(frame, bg="#0f172a")
        body.pack(fill="both", expand=True, pady=(8, 0))
        return frame, body

    def _on_mousewheel(self, event):
        # Scroll the dashboard vertically when the user spins the mouse wheel.
        self.canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    def create_metric_card(self, parent, title, value):
        # Build the compact score tiles shown in the dashboard grid.
        frame = ttk.Frame(parent, style="Card.TFrame", padding=(16, 14))
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(frame, text=value, style="Value.TLabel").pack(anchor="w", pady=(10, 0))
        ttk.Label(frame, text="Live environmental score", style="Body.TLabel").pack(anchor="w", pady=(4, 0))
        return frame

    def clear_weather_card(self):
        for widget in self.weather_body.winfo_children():
            widget.destroy()

    def render_weather(self, weather):
        # Paint the current weather summary using the live weather payload.
        self.clear_weather_card()

        weather_grid = tk.Frame(self.weather_body, bg="#0f172a")
        weather_grid.pack(fill="x", pady=(10, 0))

        location = f"{weather['city']}, {weather['state']}"
        tk.Label(weather_grid, text=location, bg="#0f172a", fg="#f8fafc", font=("Segoe UI", 16, "bold")).grid(row=0, column=0, sticky="w")
        tk.Label(weather_grid, text=weather['forecast'], bg="#0f172a", fg="#93c5fd", font=("Segoe UI", 10)).grid(row=1, column=0, sticky="w", pady=(4, 0))

        details = [
            ("Temperature", f"{weather['temperature']}°F"),
            ("Rain Chance", f"{weather['precipitation_probability']}%"),
            ("Wind", weather['wind_speed']),
            ("Humidity", f"{weather['humidity']}%"),
        ]

        for i, (key, value) in enumerate(details, start=2):
            tk.Label(weather_grid, text=f"{key}:", bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 10, "bold")).grid(row=i, column=0, sticky="w", pady=(10, 0))
            tk.Label(weather_grid, text=value, bg="#0f172a", fg="#f8fafc", font=("Segoe UI", 11, "bold")).grid(row=i, column=1, sticky="w", padx=(12, 0), pady=(10, 0))

    def update_scores(self, weather):
        # Recalculate all ecosystem scores and refresh the UI tiles and AI advice.
        plant = plant_score(weather)
        bee = bee_score(weather)
        butterfly = butterfly_score(weather)
        habitat = habitat_score(plant, bee, butterfly)

        self.metric_cards["plant"].winfo_children()[1].configure(text=f"{plant}%")
        self.metric_cards["bee"].winfo_children()[1].configure(text=f"{bee}%")
        self.metric_cards["butterfly"].winfo_children()[1].configure(text=f"{butterfly}%")
        self.metric_cards["habitat"].winfo_children()[1].configure(text=f"{habitat}%")

        scores = {
            "plant": plant,
            "bee": bee,
            "butterfly": butterfly,
            "habitat": habitat,
        }
        self.recommendations_box.delete("1.0", tk.END)
        self.recommendations_box.insert("1.0", self.assistant.summarize(weather, scores))

    def load_default_data(self):
        # Load the default ZIP code when the app first opens.
        self.load_location_data()

    def load_location_data(self):
        # Fetch weather data for the entered ZIP code and update the dashboard.
        zipcode = self.zip_entry.get().strip()

        if not zipcode:
            messagebox.showwarning("Input needed", "Please enter a ZIP code before refreshing the forecast.")
            return

        self.status_label.config(text="Fetching live weather…")
        self.update_idletasks()

        try:
            weather = self.service.get_by_zip(zipcode)
            self.render_weather(weather)
            self.update_scores(weather)
            self.status_label.config(text=f"Loaded forecast for {weather['city']}, {weather['state']}")
        except Exception as exc:
            messagebox.showerror("Forecast Error", f"Unable to load weather data:\n{exc}")
            self.status_label.config(text="Unable to refresh forecast")


if __name__ == "__main__":
    app = BioSphereAIApp()
    app.mainloop()
