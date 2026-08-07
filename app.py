import io
from pathlib import Path

import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np

try:
    import cairosvg
    from PIL import Image, ImageTk
except ImportError:
    cairosvg = None
    Image = None
    ImageTk = None

from analytics.butterfly import calculate as butterfly_score
from analytics.canopy import build_density_grid
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
        self.logo_image = self._load_brand_logo()

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

        if self.logo_image is not None:
            logo_label = tk.Label(header, image=self.logo_image, bg="#07111f")
            logo_label.image = self.logo_image
            logo_label.pack(anchor="w", pady=(0, 8))
        else:
            tk.Label(header, text="🌎 BioSphereAI", bg="#07111f", fg="#f8fafc", font=("Segoe UI", 28, "bold")).pack(anchor="w")

        tk.Label(header, text="A modern ecological dashboard from live weather conditions", bg="#07111f", fg="#93c5fd", font=("Segoe UI", 11)).pack(anchor="w", pady=(4, 0))

        # Search / refresh area for ZIP-based weather lookup.
        search_frame = tk.Frame(self.content_frame, bg="#0f172a", padx=14, pady=14)
        search_frame.pack(fill="x", pady=(0, 16))

        tk.Label(search_frame, text="ZIP Code", bg="#0f172a", fg="#e2e8f0", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 12))

        self.zip_entry = ttk.Entry(search_frame, width=12, style="Search.TEntry")
        self.zip_entry.insert(0, "13760")
        self.zip_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12))

        tk.Label(search_frame, text="Latitude", bg="#0f172a", fg="#e2e8f0", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, sticky="w", padx=(0, 12))
        self.lat_entry = ttk.Entry(search_frame, width=10, style="Search.TEntry")
        self.lat_entry.grid(row=0, column=3, sticky="ew", padx=(0, 12))

        tk.Label(search_frame, text="Longitude", bg="#0f172a", fg="#e2e8f0", font=("Segoe UI", 11, "bold")).grid(row=0, column=4, sticky="w", padx=(0, 12))
        self.lon_entry = ttk.Entry(search_frame, width=10, style="Search.TEntry")
        self.lon_entry.grid(row=0, column=5, sticky="ew", padx=(0, 12))

        self.search_button = ttk.Button(search_frame, text="Refresh forecast", style="Primary.TButton", command=self.load_location_data)
        self.search_button.grid(row=0, column=6, sticky="w")

        self.status_label = tk.Label(search_frame, text="Loading live forecast…", bg="#0f172a", fg="#a7f3d0", font=("Segoe UI", 10, "bold"))
        self.status_label.grid(row=0, column=7, sticky="w", padx=(18, 0))

        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(3, weight=1)
        search_frame.columnconfigure(5, weight=1)

        # Weather summary card that updates whenever the ZIP code changes.
        self.weather_card, self.weather_body = self.create_card(self.content_frame, "Current Weather")
        self.weather_card.pack(fill="x", pady=(0, 12))

        # Grid of score cards for plant, bee, butterfly, habitat, and canopy health.
        metrics_grid = tk.Frame(self.content_frame, bg="#07111f")
        metrics_grid.pack(fill="both", expand=True)

        self.metric_cards = {
            "plant": self.create_metric_card(metrics_grid, "🌱 Plant Health", "0%"),
            "bee": self.create_metric_card(metrics_grid, "🐝 Bee Activity", "0%"),
            "butterfly": self.create_metric_card(metrics_grid, "🦋 Butterfly Activity", "0%"),
            "habitat": self.create_metric_card(metrics_grid, "🌳 Habitat Health", "0%"),
            "canopy": self.create_metric_card(metrics_grid, "🌲 Canopy Cover", "0%"),
        }

        self.metric_cards["plant"].grid(row=0, column=0, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.metric_cards["bee"].grid(row=0, column=1, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.metric_cards["butterfly"].grid(row=0, column=2, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.metric_cards["habitat"].grid(row=1, column=0, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.metric_cards["canopy"].grid(row=1, column=1, pady=(0, 12), sticky="nsew")

        metrics_grid.columnconfigure((0, 1, 2), weight=1)
        metrics_grid.rowconfigure((0, 1), weight=1)

        # AI recommendation panel that displays practical suggestions from the live score data.
        self.canopy_card, self.canopy_body = self.create_card(self.content_frame, "Canopy & Throughfall")
        self.canopy_card.pack(fill="both", expand=True, pady=(0, 12))

        self.canopy_summary = tk.Label(
            self.canopy_body,
            text="Sampling canopy cover and throughfall for the selected site.",
            bg="#0f172a",
            fg="#cbd5e1",
            font=("Segoe UI", 10),
            justify="left",
            wraplength=920,
        )
        self.canopy_summary.pack(fill="x", pady=(0, 12))

        self.canopy_chart_frame = tk.Frame(self.canopy_body, bg="#0f172a")
        self.canopy_chart_frame.pack(fill="both", expand=True)
        self.canopy_canvas = None

    def _load_brand_logo(self):
        icon_path = Path(__file__).resolve().parent / "Graphics" / "biosphere logo.svg"
        if cairosvg is None or Image is None or ImageTk is None or not icon_path.exists():
            return None

        try:
            png_bytes = cairosvg.svg2png(url=str(icon_path), output_width=240)
            image = Image.open(io.BytesIO(png_bytes))
            photo = ImageTk.PhotoImage(image)
            return photo
        except Exception:
            return None

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
            ("Canopy Cover", f"{weather.get('canopy_cover', 0)}%"),
            ("Throughfall", f"{weather.get('throughfall_mm', 0)} mm"),
            ("Interception Loss", f"{weather.get('interception_loss_mm', 0)} mm"),
        ]

        for i, (key, value) in enumerate(details, start=2):
            tk.Label(weather_grid, text=f"{key}:", bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 10, "bold")).grid(row=i, column=0, sticky="w", pady=(10, 0))
            tk.Label(weather_grid, text=value, bg="#0f172a", fg="#f8fafc", font=("Segoe UI", 11, "bold")).grid(row=i, column=1, sticky="w", padx=(12, 0), pady=(10, 0))

        self.render_canopy_chart(weather)

    def render_canopy_chart(self, weather):
        # Display canopy density as a map-like surface with throughfall and interception labels.
        canopy = weather.get("canopy_cover", 0)
        rain_chance = weather.get("precipitation_probability", 0)
        throughfall_mm = weather.get("throughfall_mm", 0)
        interception_mm = weather.get("interception_loss_mm", 0)

        self.canopy_summary.config(
            text=(
                f"Site canopy cover is estimated at {canopy}%. "
                f"With a {rain_chance}% rain chance, the model predicts {throughfall_mm} mm of throughfall and "
                f"{interception_mm} mm lost to interception."
            )
        )

        if self.canopy_canvas is not None:
            self.canopy_canvas.get_tk_widget().destroy()

        density_grid = np.array(build_density_grid(canopy, size=14))

        fig, ax = plt.subplots(figsize=(8.5, 3.2), dpi=100)
        fig.patch.set_facecolor("#07111f")
        ax.set_facecolor("#0f172a")

        image = ax.imshow(density_grid, cmap="Greens", origin="lower", aspect="auto")
        ax.scatter([density_grid.shape[1] // 2], [density_grid.shape[0] // 2], color="#166534", s=50, marker="o")
        ax.set_title("Canopy density map", color="#f8fafc", pad=10)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.text(
            0.5,
            0.02,
            f"Throughfall: {throughfall_mm} mm  |  Interception: {interception_mm} mm",
            transform=ax.transAxes,
            ha="center",
            va="bottom",
            color="#93c5fd",
            fontsize=9,
        )

        cbar = fig.colorbar(image, ax=ax, pad=0.02, shrink=0.85)
        cbar.ax.yaxis.set_tick_params(color="#f8fafc")
        cbar.outline.set_edgecolor("#334155")
        cbar.ax.set_ylabel("Canopy density", color="#f8fafc", rotation=90)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["bottom"].set_visible(False)
        ax.spines["left"].set_visible(False)

        self.canopy_canvas = FigureCanvasTkAgg(fig, master=self.canopy_chart_frame)
        self.canopy_canvas.draw()
        self.canopy_canvas.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def update_scores(self, weather):
        # Recalculate all ecosystem scores and refresh the UI tiles and AI advice.
        plant = plant_score(weather)
        bee = bee_score(weather)
        butterfly = butterfly_score(weather)
        habitat = habitat_score(plant, bee, butterfly)
        canopy_value = weather.get("canopy_cover", 0)

        self.metric_cards["plant"].winfo_children()[1].configure(text=f"{plant}%")
        self.metric_cards["bee"].winfo_children()[1].configure(text=f"{bee}%")
        self.metric_cards["butterfly"].winfo_children()[1].configure(text=f"{butterfly}%")
        self.metric_cards["habitat"].winfo_children()[1].configure(text=f"{habitat}%")
        self.metric_cards["canopy"].winfo_children()[1].configure(text=f"{canopy_value}%")


    def load_default_data(self):
        # Load the default ZIP code when the app first opens.
        self.load_location_data()

    def load_location_data(self):
        # Fetch weather data for the entered ZIP code or coordinates and update the dashboard.
        zipcode = self.zip_entry.get().strip()
        lat_value = self.lat_entry.get().strip()
        lon_value = self.lon_entry.get().strip()

        if zipcode:
            fetch_method = lambda: self.service.get_by_zip(zipcode)
        elif lat_value and lon_value:
            try:
                lat = float(lat_value)
                lon = float(lon_value)
            except ValueError:
                messagebox.showwarning("Input needed", "Please enter valid numeric latitude and longitude values.")
                return
            fetch_method = lambda: self.service.get_by_coords(lat, lon)
        else:
            messagebox.showwarning("Input needed", "Please enter either a ZIP code or latitude/longitude coordinates.")
            return

        self.status_label.config(text="Fetching live weather…")
        self.update_idletasks()

        try:
            weather = fetch_method()
            self.render_weather(weather)
            self.update_scores(weather)
            self.status_label.config(text=f"Loaded forecast for {weather.get('city', '')}, {weather.get('state', '')}")
        except Exception as exc:
            messagebox.showerror("Forecast Error", f"Unable to load weather data:\n{exc}")
            self.status_label.config(text="Unable to refresh forecast")


if __name__ == "__main__":
    app = BioSphereAIApp()
    app.mainloop()
