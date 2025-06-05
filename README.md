# CUBE-DESKTOP: Desktop App for Real-Time LoRa Telemetry Monitoring

**CUBE-DESKTOP** is a cross-platform desktop application designed for real-time visualization of telemetry data sent from a LoRa transmitter during free-fall experiments, such as in CubeSat or aerial drop simulations. The LoRa transmitter sends environmental data to a ground LoRa receiver connected via USB to a PC or laptop running this application.

Developed using Python and Tkinter, the app provides live plotting, historical logging, and CSV export capabilities for received data, enabling reliable and user-friendly field testing.

---

## 📚 Project Structure

- Transmitter: LoRa-enabled embedded device (e.g., ESP32 + sensors) onboard the Cube.
- Receiver: LoRa module connected to a laptop via USB (serial).
- Desktop App: Python GUI for real-time monitoring, data parsing, and charting.

---

## 🚀 Features

- 📡 Real-time data reception from LoRa receiver via serial (USB).
- 📊 Live plotting of temperature, voltage, altitude, and other telemetry.
- 📝 Automatic data logging with timestamping.
- 💾 Export of received data to CSV files.
- ⏸️ Pause/resume data streaming with UI controls.
- 🔎 Interactive chart tooltips (via mplcursors).
- 🖥️ Clean and responsive UI using Python’s Tkinter and matplotlib.

---

## 🔧 Technologies Used

- **GUI Framework:** Tkinter (Python)
- **Data Plotting:** Matplotlib + Mplcursors
- **Serial Communication:** PySerial
- **Data Handling:** CSV, datetime
- **Packaging:** PyInstaller

---

## 🛠️ Installation Instructions

### Prerequisites
- Python 3.9+
- Required libraries:

```
pip install pyserial matplotlib mplcursors
```

### Running the App
- Clone this repository:
```
git clone https://github.com/storres20/cube-desktop.git
cd cube-desktop
```
- Launch the application:
```
python main.py
```

### Create Executable
Use `PyInstaller` to build a standalone app:
```
pip install pyinstaller
pyinstaller --name "CubeMonitor" --onefile --noconsole main.py
```
➡️ You will find the generated executable file in the dist folder.

---

## ⚡ Quick Start

1. Connect your LoRa receiver to your laptop via USB.
2. Launch CUBE-DESKTOP.
3. Select the correct COM port.
4. Start receiving and visualizing data from the LoRa transmitter.
5. Save or export your logged data for analysis.

---

## 📦 Repository

GitHub Repository:
https://github.com/storres20/cube-desktop <!-- Replace with actual repo URL -->

---

## 🧪 Typical Use Case

- This application is ideal for:
- CubeSat drop simulations from drones (100m altitude).
- Real-time monitoring of telemetry during environmental experiments.
- Educational or research settings involving wireless sensor data collection.

---

## 📜 License

This project is licensed under the [MIT License](https://github.com/storres20/temphu/blob/main/LICENSE.txt).

---

## 🤝 Contributions

Contributions, suggestions, and improvements are welcome!  
Feel free to fork the repositories, open issues, and submit pull requests.

---

## 📬 Contact

If you have any questions, please open an issue in the corresponding GitHub repository.
