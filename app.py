import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import numpy as np

from utils.landcover_map import build_hls_landcover_comparison, fetch_hls_comparison_images
from analytics.butterfly import calculate as butterfly_score
from analytics.canopy import build_density_grid
from analytics.conservation import (
    calculate_habitat_quality,
    calculate_connectivity,
    calculate_restoration_potential,
    calculate_pollinator_suitability,
    calculate_native_plant_support,
)
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

        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill="both", expand=True)

        self.overview_tab = tk.Frame(self.notebook, bg="#07111f")
        self.conservation_tab = tk.Frame(self.notebook, bg="#07111f")
        self.notebook.add(self.overview_tab, text="Overview")
        self.notebook.add(self.conservation_tab, text="Conservation")

        # Header area for the app title and subtitle.
        header = tk.Frame(self.overview_tab, bg="#07111f")
        header.pack(fill="x", pady=(0, 18))

        tk.Label(header, text="🌎 BioSphereAI", bg="#07111f", fg="#f8fafc", font=("Segoe UI", 28, "bold")).pack(anchor="w")
        tk.Label(header, text="A modern ecological dashboard from live weather conditions", bg="#07111f", fg="#93c5fd", font=("Segoe UI", 11)).pack(anchor="w", pady=(4, 0))

        # Search / refresh area for ZIP-based weather lookup.
        search_frame = tk.Frame(self.overview_tab, bg="#0f172a", padx=14, pady=14)
        search_frame.pack(fill="x", pady=(0, 16))

        tk.Label(search_frame, text="ZIP Code", bg="#0f172a", fg="#e2e8f0", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 12))

        self.zip_entry = ttk.Entry(search_frame, width=12, style="Search.TEntry")
        self.zip_entry.insert(0, "13760")
        self.zip_entry.grid(row=0, column=1, sticky="ew", padx=(0, 12))

        tk.Label(search_frame, text="Latitude", bg="#0f172a", fg="#e2e8f0", font=("Segoe UI", 11, "bold")).grid(row=0, column=2, sticky="w", padx=(0, 12))
        self.lat_entry = ttk.Entry(search_frame, width=10, style="Search.TEntry")
        self.lat_entry.insert(0, "42.10")
        self.lat_entry.grid(row=0, column=3, sticky="ew", padx=(0, 12))

        tk.Label(search_frame, text="Longitude", bg="#0f172a", fg="#e2e8f0", font=("Segoe UI", 11, "bold")).grid(row=0, column=4, sticky="w", padx=(0, 12))
        self.lon_entry = ttk.Entry(search_frame, width=10, style="Search.TEntry")
        self.lon_entry.insert(0, "-76.05")
        self.lon_entry.grid(row=0, column=5, sticky="ew", padx=(0, 12))

        self.search_button = ttk.Button(search_frame, text="Refresh forecast", style="Primary.TButton", command=self.load_location_data)
        self.search_button.grid(row=0, column=6, sticky="w")

        self.status_label = tk.Label(search_frame, text="Loading live forecast…", bg="#0f172a", fg="#a7f3d0", font=("Segoe UI", 10, "bold"))
        self.status_label.grid(row=0, column=7, sticky="w", padx=(18, 0))

        search_frame.columnconfigure(1, weight=1)
        search_frame.columnconfigure(3, weight=1)
        search_frame.columnconfigure(5, weight=1)

        # Weather summary card that updates whenever the ZIP code changes.
        self.weather_card, self.weather_body = self.create_card(self.overview_tab, "Current Weather")
        self.weather_card.pack(fill="x", pady=(0, 12))

        # Grid of score cards for plant, bee, butterfly, habitat, and canopy health.
        metrics_grid = tk.Frame(self.overview_tab, bg="#07111f")
        metrics_grid.pack(fill="both", expand=True)

        self.metric_cards = {
            "plant": self.create_metric_card(metrics_grid, "🌱 Plant Health", "0%", "Plant vigor and growth potential driven by local weather, moisture, and canopy cover."),
            "bee": self.create_metric_card(metrics_grid, "🐝 Bee Activity", "0%", "Pollinator activity potential based on current temperature, wind, and floral conditions."),
            "butterfly": self.create_metric_card(metrics_grid, "🦋 Butterfly Activity", "0%", "Butterfly habitat suitability estimated from temperature, humidity, and bloom support."),
            "habitat": self.create_metric_card(metrics_grid, "🌳 Habitat Health", "0%", "Overall ecological wellness combining plant, pollinator, and canopy condition."),
            "canopy": self.create_metric_card(metrics_grid, "🌲 Canopy Cover", "0%", "Estimated tree and foliage coverage from the local canopy model."),
        }

        self.metric_cards["plant"].grid(row=0, column=0, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.metric_cards["bee"].grid(row=0, column=1, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.metric_cards["butterfly"].grid(row=0, column=2, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.metric_cards["habitat"].grid(row=1, column=0, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.metric_cards["canopy"].grid(row=1, column=1, pady=(0, 12), sticky="nsew")

        metrics_grid.columnconfigure((0, 1, 2), weight=1)
        metrics_grid.rowconfigure((0, 1), weight=1)

        # AI recommendation panel that displays practical suggestions from the live score data.
        self.canopy_card, self.canopy_body = self.create_card(self.overview_tab, "Canopy & Throughfall")
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

        self.hls_card, self.hls_body = self.create_card(self.overview_tab, "5-Mile Canopy Comparison")
        self.hls_card.pack(fill="both", expand=True, pady=(0, 12))
        self.hls_summary = tk.Label(
            self.hls_body,
            text="Comparing canopy conditions at 2015, 2020, and 2026 for the selected location.",
            bg="#0f172a",
            fg="#cbd5e1",
            font=("Segoe UI", 10),
            justify="left",
            wraplength=920,
        )
        self.hls_summary.pack(fill="x", pady=(0, 12))
        self.hls_chart_frame = tk.Frame(self.hls_body, bg="#0f172a")
        self.hls_chart_frame.pack(fill="both", expand=True)
        self.hls_canvas = None

        conservation_header = tk.Label(self.conservation_tab, text="Conservation insights", bg="#07111f", fg="#f8fafc", font=("Segoe UI", 18, "bold"))
        conservation_header.pack(anchor="w", pady=(0, 12), padx=16)

        conservation_grid = tk.Frame(self.conservation_tab, bg="#07111f")
        conservation_grid.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        self.conservation_cards = {
            "habitat_quality": self.create_metric_card(conservation_grid, "Habitat Quality", "0%", "Evaluates local habitat condition using canopy structure, weather, and ecological balance."),
            "connectivity": self.create_metric_card(conservation_grid, "Connectivity", "0%", "Measures landscape linkage and how easily wildlife can move between habitat patches."),
            "restoration_potential": self.create_metric_card(conservation_grid, "Restoration Potential", "0%", "Estimates opportunities for improving habitat value through restoration actions."),
            "pollinator": self.create_metric_card(conservation_grid, "Pollinator Habitat", "0%", "Shows how suitable the site is for bees and other pollinators based on weather and vegetation."),
            "native_support": self.create_metric_card(conservation_grid, "Native Plant Support", "0%", "Reflects how favorable conditions are for supporting native plant communities."),
        }

        self.conservation_cards["habitat_quality"].grid(row=0, column=0, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.conservation_cards["connectivity"].grid(row=0, column=1, padx=(0, 12), pady=(0, 12), sticky="nsew")
        self.conservation_cards["restoration_potential"].grid(row=0, column=2, pady=(0, 12), sticky="nsew")
        self.conservation_cards["pollinator"].grid(row=1, column=0, padx=(0, 12), sticky="nsew")
        self.conservation_cards["native_support"].grid(row=1, column=1, sticky="nsew")

        conservation_grid.columnconfigure((0, 1, 2), weight=1)
        conservation_grid.rowconfigure((0, 1), weight=1)

        self.conservation_summary = tk.Label(
            self.conservation_tab,
            text="Conservation metrics reflect habitat structure, species support, and restoration potential.",
            bg="#07111f",
            fg="#cbd5e1",
            font=("Segoe UI", 10),
            justify="left",
            wraplength=920,
        )
        self.conservation_summary.pack(fill="x", pady=(0, 12), padx=16)

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

    def create_metric_card(self, parent, title, value, description="Live environmental score"):
        # Build the compact score tiles shown in the dashboard grid.
        frame = ttk.Frame(parent, style="Card.TFrame", padding=(16, 14))
        ttk.Label(frame, text=title, style="CardTitle.TLabel").pack(anchor="w")
        ttk.Label(frame, text=value, style="Value.TLabel").pack(anchor="w", pady=(10, 0))
        ttk.Label(frame, text=description, style="Body.TLabel", wraplength=220, justify="left").pack(anchor="w", pady=(4, 0))
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

        self.render_hls_year_comparison(weather)

    def render_hls_year_comparison(self, weather):
        # Show a 5-mile canopy comparison for the selected site across HLS years.
        try:
            lon = float(self.lon_entry.get().strip()) if self.lon_entry.get().strip() else -88.6
            lat = float(self.lat_entry.get().strip()) if self.lat_entry.get().strip() else 26.4
        except ValueError:
            lon = -88.6
            lat = 26.4

        specs = build_hls_landcover_comparison(center_lon=lon, center_lat=lat, years=(2015, 2020, 2026), tile_size_miles=5.0)
        if self.hls_canvas is not None:
            self.hls_canvas.get_tk_widget().destroy()

        try:
            image_records = fetch_hls_comparison_images(center_lon=lon, center_lat=lat, years=(2015, 2020, 2026), tile_size_miles=5.0)
        except Exception:
            image_records = []

        fig, axes = plt.subplots(1, 3, figsize=(12, 4.5), dpi=100)
        fig.patch.set_facecolor("#07111f")

        rendered_any = False
        for axis, spec in zip(axes, specs):
            record = next((item for item in image_records if item["year"] == spec["year"]), None)
            image = record["image"] if record else None
            axis.set_facecolor("#0f172a")

            if image is not None:
                axis.imshow(np.asarray(image))
                axis.set_title(f"{spec['year']} - {spec['dataset'].split('/')[-2]}", color="#f8fafc", fontsize=10)
                rendered_any = True
            else:
                year_shift = spec["year"] - 2020
                year_canopy = max(0.0, min(100.0, float(weather.get("canopy_cover", 55)) + (year_shift * 2.0)))
                year_grid = np.linspace(-1.0, 1.0, 28)
                xx, yy = np.meshgrid(year_grid, year_grid)
                distance = np.sqrt(xx ** 2 + yy ** 2)
                canopy_surface = np.clip(1.0 - distance * 1.2, 0.0, 1.0)
                canopy_surface = canopy_surface * (year_canopy / 100.0)
                axis.imshow(canopy_surface, cmap="Greens", origin="lower", vmin=0.0, vmax=1.0)
                axis.set_title(f"{spec['year']} - fallback", color="#f8fafc", fontsize=10)

            axis.set_xticks([])
            axis.set_yticks([])
            axis.text(
                0.5,
                0.02,
                "5-mi window",
                transform=axis.transAxes,
                ha="center",
                va="bottom",
                color="#bfdbfe",
                fontsize=8,
            )

        fig.suptitle(f"Canopy comparison for {lat:.2f}, {lon:.2f}", color="#f8fafc", fontsize=12)
        fig.tight_layout(rect=(0, 0, 1, 0.96))

        self.hls_canvas = FigureCanvasTkAgg(fig, master=self.hls_chart_frame)
        self.hls_canvas.draw()
        self.hls_canvas.get_tk_widget().pack(fill="both", expand=True)
        if rendered_any:
            summary = "Real NASA HLS satellite imagery for the selected 5-mile area across years 2015, 2020, and 2026."
        else:
            summary = f"Showing synthetic canopy model (Earth Engine unavailable). To use real satellite imagery: install Python from python.org, then run 'pip install earthengine-api' and 'python -m earthengine authenticate'."
        
        self.hls_summary.config(text=summary)
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

    def render_conservation_tab(self, weather):
        habitat_quality = calculate_habitat_quality(weather)
        connectivity = calculate_connectivity(weather)
        restoration = calculate_restoration_potential(weather)
        pollinator = calculate_pollinator_suitability(weather)
        native_support = calculate_native_plant_support(weather)

        self.conservation_cards["habitat_quality"].winfo_children()[1].configure(text=f"{habitat_quality}%")
        self.conservation_cards["connectivity"].winfo_children()[1].configure(text=f"{connectivity}%")
        self.conservation_cards["restoration_potential"].winfo_children()[1].configure(text=f"{restoration}%")
        self.conservation_cards["pollinator"].winfo_children()[1].configure(text=f"{pollinator}%")
        self.conservation_cards["native_support"].winfo_children()[1].configure(text=f"{native_support}%")

        self.conservation_summary.config(
            text=(
                f"Habitat quality is {habitat_quality}%. Connectivity is {connectivity}%. "
                f"Restoration potential is {restoration}%. Pollinator habitat is {pollinator}% and "
                f"native plant support is {native_support}%.")
        )


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
            if 'latitude' in weather and 'longitude' in weather:
                self.lat_entry.delete(0, tk.END)
                self.lat_entry.insert(0, f"{weather['latitude']:.4f}")
                self.lon_entry.delete(0, tk.END)
                self.lon_entry.insert(0, f"{weather['longitude']:.4f}")
                
            self.render_weather(weather)
            self.update_scores(weather)
            self.render_conservation_tab(weather)
            self.status_label.config(text=f"Loaded forecast for {weather.get('city', '')}, {weather.get('state', '')}")
        except Exception as exc:
            messagebox.showerror("Forecast Error", f"Unable to load weather data:\n{exc}")
            self.status_label.config(text="Unable to refresh forecast")

        except Exception as e:
            print(f"Error occurred while fetching weather data: {e}")

if __name__ == "__main__":
    app = BioSphereAIApp()
    app.mainloop()
