import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import mplcursors
import serial
import serial.tools.list_ports
import threading
from datetime import datetime
import csv
import re

class CubeMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📡 CubeMonitor - LoRa Telemetría")
        self.root.geometry("1200x800")
        self.paused = False

        self.ser = None
        self.read_thread = None
        self.data_log = []
        self.realtime_labels = {}
        self.selected_fields = ["Temp", "Alt", "Volt"]
        self.update_interval = 5000
        self.max_points = 100

        self.fields = [
            "Volt", "Descent", "Temp", "BMP_T", "Pres", "Hum",
            "GyX", "GyY", "GyZ", "AccX", "AccY", "AccZ",
            "MagX", "MagY", "MagZ", "Head", "Alt", "Lat", "Lon", "AltGPS"
        ]

        self.unit_map = {
            "Volt": "V", "Descent": "m/s", "Temp": "°C", "BMP_T": "°C", "Pres": "hPa",
            "Hum": "%", "GyX": "°/s", "GyY": "°/s", "GyZ": "°/s", "AccX": "m/s²", "AccY": "m/s²",
            "AccZ": "m/s²", "MagX": "uT", "MagY": "uT", "MagZ": "uT", "Head": "°",
            "Alt": "m", "Lat": "", "Lon": "", "AltGPS": "m"
        }

        self.setup_ui()
        self.root.after(self.update_interval, self.update_graphs)

    def setup_ui(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True)

        self.tab_realtime = ttk.Frame(notebook)
        self.tab_history = ttk.Frame(notebook)
        self.tab_graphs = ttk.Frame(notebook)

        notebook.add(self.tab_realtime, text="📡 Tiempo Real")
        notebook.add(self.tab_history, text="📄 Historial")
        notebook.add(self.tab_graphs, text="📊 Gráficas")

        port_frame = ttk.Frame(self.root)
        port_frame.pack(pady=5)
        ttk.Label(port_frame, text="Puerto COM:").pack(side='left', padx=5)
        self.port_combobox = ttk.Combobox(port_frame, width=30, state="readonly")
        self.port_combobox.pack(side='left')
        self.refresh_ports()
        ttk.Button(port_frame, text="Actualizar", command=self.refresh_ports).pack(side='left', padx=5)
        ttk.Button(port_frame, text="Conectar", command=self.connect_serial).pack(side='left', padx=5)

        for i, field in enumerate(self.fields):
            ttk.Label(self.tab_realtime, text=f"{field}:", font=("Arial", 12, "bold")).grid(row=i, column=0, sticky="e", padx=10, pady=3)
            self.realtime_labels[field] = ttk.Label(self.tab_realtime, text="—", font=("Arial", 12))
            self.realtime_labels[field].grid(row=i, column=1, sticky="w", padx=10, pady=3)

        self.text_area = scrolledtext.ScrolledText(self.tab_history, wrap=tk.WORD, font=("Courier", 10))
        self.text_area.pack(expand=True, fill='both', padx=10, pady=10)
        ttk.Button(self.tab_history, text="💾 Guardar CSV", command=self.save_csv).pack(pady=10)

        self.graph_fig = Figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.graph_fig, master=self.tab_graphs)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=10)

        options_frame = ttk.Frame(self.tab_graphs)
        options_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(options_frame, text="Campos a graficar:").pack(side='left')
        self.check_vars = {}
        for field in self.fields:
            var = tk.BooleanVar(value=field in self.selected_fields)
            cb = ttk.Checkbutton(options_frame, text=field, variable=var, command=self.update_selected_fields)
            cb.pack(side='left')
            self.check_vars[field] = var

        control_frame = ttk.Frame(self.tab_graphs)
        control_frame.pack(pady=5)
        ttk.Label(control_frame, text="Máx puntos visibles:").pack(side='left')
        self.limit_spinbox = ttk.Spinbox(control_frame, from_=10, to=500, increment=10, width=5, command=self.update_limits)
        self.limit_spinbox.set(self.max_points)
        self.limit_spinbox.pack(side='left', padx=5)
        self.pause_button = ttk.Button(control_frame, text="⏸ Pausar", command=self.toggle_pause)
        self.pause_button.pack(side='left', padx=10)

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_button.config(text="▶ Reanudar" if self.paused else "⏸ Pausar")

    def update_selected_fields(self):
        self.selected_fields = [f for f, var in self.check_vars.items() if var.get()]

    def update_limits(self):
        try:
            self.max_points = int(self.limit_spinbox.get())
        except:
            self.max_points = 100

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combobox['values'] = [port.device for port in ports]
        if ports:
            self.port_combobox.current(0)
        else:
            self.port_combobox.set("No hay puertos")

    def connect_serial(self):
        selected_port = self.port_combobox.get()
        if not selected_port:
            messagebox.showwarning("Puerto no seleccionado", "Selecciona un puerto COM válido.")
            return
        try:
            self.ser = serial.Serial(selected_port, 115200, timeout=1)
            self.read_thread = threading.Thread(target=self.read_serial_data, daemon=True)
            self.read_thread.start()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def read_serial_data(self):
        while True:
            if self.ser and self.ser.in_waiting:
                try:
                    line = self.ser.readline().decode(errors='ignore').strip()
                    if line.startswith("🔹"):
                        clean = line.replace("🔹", "").strip()
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        self.update_fields(clean)
                        self.text_area.insert(tk.END, f"[{timestamp}] {clean}\n")
                        self.text_area.see(tk.END)
                        self.data_log.append((timestamp, clean))
                except Exception as e:
                    print("Lectura fallida:", e)

    def update_fields(self, line):
        alias = {
            "Volt": "Volt", "Descent": "Descent", "Temp": "Temp", "BMP_T": "BMP_T",
            "Pres": "Pres", "Hum": "Hum", "GyX": "GyX", "GyY": "GyY", "GyZ": "GyZ",
            "AccX": "AccX", "AccY": "AccY", "AccZ": "AccZ",
            "MagX": "MagX", "MagY": "MagY", "MagZ": "MagZ",
            "Head": "Head", "Alt": "Alt", "Lat": "Lat", "Lon": "Lon", "AltGPS": "AltGPS"
        }
        parts = line.split()
        for p in parts:
            if ":" in p:
                try:
                    k, v = p.split(":", 1)
                    key_gui = alias.get(k.strip())
                    if key_gui in self.realtime_labels:
                        self.realtime_labels[key_gui].config(text=v.strip())
                except Exception as e:
                    print("Error al procesar campo:", p, "->", e)

    def save_csv(self):
        if not self.data_log:
            messagebox.showinfo("Sin datos", "No hay datos para guardar.")
            return
        filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not filename:
            return
        try:
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["Datetime"] + self.fields)
                for timestamp, line in self.data_log:
                    row = [timestamp]
                    for key in self.fields:
                        val = ""
                        for part in line.split():
                            if part.startswith(key + ":"):
                                val = part.split(":", 1)[1]
                        row.append(val)
                    writer.writerow(row)
            messagebox.showinfo("Éxito", f"Datos guardados en: {filename}")
        except Exception as e:
            messagebox.showerror("Error al guardar CSV", str(e))

    def update_graphs(self):
        if self.paused or not self.data_log or not self.selected_fields:
            self.root.after(self.update_interval, self.update_graphs)
            return

        self.graph_fig.clf()
        timestamps = []
        values_dict = {f: [] for f in self.selected_fields}

        for timestamp, line in self.data_log[-self.max_points:]:
            timestamps.append(datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S"))
            for f in self.selected_fields:
                val = ""
                for part in line.split():
                    if part.startswith(f + ":"):
                        val = part.split(":", 1)[1].replace(",", ".")
                try:
                    match = re.findall(r"[-+]?\d*\.\d+|\d+", val)
                    values_dict[f].append(float(match[0]) if match else None)
                except:
                    values_dict[f].append(None)

        for i, field in enumerate(self.selected_fields):
            ax = self.graph_fig.add_subplot(len(self.selected_fields), 1, i+1)
            line, = ax.plot(timestamps, values_dict[field], marker='o', label=field)
            unit = self.unit_map.get(field, "")
            ax.set_title(f"{field} ({unit})" if unit else field)
            ax.set_ylabel("Valor")
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            y_values = [v for v in values_dict[field] if v is not None]
            if y_values:
                ymin = min(y_values)
                ymax = max(y_values)
                if ymin != ymax:
                    ax.set_ylim(ymin - 0.1 * abs(ymin), ymax + 0.1 * abs(ymax))
                else:
                    ax.set_ylim(ymin - 1, ymax + 1)
            ax.legend()
            mplcursors.cursor(line)

        self.graph_fig.tight_layout()
        self.canvas.draw()
        self.root.after(self.update_interval, self.update_graphs)

if __name__ == "__main__":
    root = tk.Tk()
    app = CubeMonitorApp(root)
    root.mainloop()
