import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import serial
import serial.tools.list_ports
import threading

BAUD_RATE = 115200

class CubeSatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌐 CubeSat Telemetría - Receptor LoRa")
        self.root.geometry("750x550")

        self.serial_port = None
        self.ser = None
        self.read_thread = None

        # Selector de puerto
        self.port_label = tk.Label(root, text="🔌 Puerto COM:")
        self.port_label.pack(pady=(10, 0))

        self.port_combobox = ttk.Combobox(root, width=40, state="readonly")
        self.port_combobox.pack(pady=5)
        self.refresh_ports()

        self.refresh_button = tk.Button(root, text="🔄 Actualizar puertos", command=self.refresh_ports)
        self.refresh_button.pack(pady=(0, 10))

        self.connect_button = tk.Button(root, text="Conectar", command=self.connect_serial)
        self.connect_button.pack()

        # Área de texto
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Courier", 10))
        self.text_area.pack(expand=True, fill='both', padx=10, pady=10)

        self.status_label = tk.Label(root, text="⏳ Esperando conexión...", fg="blue")
        self.status_label.pack(pady=5)

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combobox['values'] = [port.device for port in ports]
        if ports:
            self.port_combobox.current(0)
        else:
            self.port_combobox.set("No hay puertos disponibles")

    def connect_serial(self):
        selected_port = self.port_combobox.get()
        if not selected_port or "No hay" in selected_port:
            messagebox.showwarning("Advertencia", "Selecciona un puerto COM válido.")
            return

        try:
            self.ser = serial.Serial(selected_port, BAUD_RATE, timeout=1)
            self.status_label.config(text=f"✅ Conectado a {selected_port}", fg="green")
            self.read_thread = threading.Thread(target=self.read_data, daemon=True)
            self.read_thread.start()
            self.connect_button.config(state="disabled")
        except serial.SerialException as e:
            messagebox.showerror("Error", f"No se pudo abrir el puerto {selected_port}.\n\n{e}")
            self.status_label.config(text="❌ Error al conectar", fg="red")

    def read_data(self):
        while True:
            if self.ser and self.ser.in_waiting:
                try:
                    line = self.ser.readline().decode(errors='ignore').strip()
                    if line.startswith("📥 LoRa Message Received:"):
                        continue
                    elif line.startswith("🔹"):
                        self.text_area.insert(tk.END, line + "\n")
                        self.text_area.see(tk.END)
                except Exception as e:
                    print(f"Error de lectura: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CubeSatApp(root)
    root.mainloop()
