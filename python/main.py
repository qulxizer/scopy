import sys
import csv
import signal
import time
from dataclasses import dataclass
from traceback import print_exc
import serial
from threading import Thread, Lock
from collections import deque
from PyQt5 import QtWidgets, QtCore
import pyqtgraph as pg

# ================= CONFIG =================
PORT = "/dev/ttyUSB0"
BAUD = 921600

ADC_BITS = 12
VREF = 3.3

MAX_POINTS = 500
ALPHA = 0.2  # exponential filter
X_WINDOW = 10.0  # seconds
GUI_UPDATE_MS = 16  # ~60 FPS
# =========================================


# -------------- LOGGING --------------
@dataclass
class LogPoint:
    Voltage: float
    Time: float

    def __iter__(self):
        yield self.Time
        yield self.Voltage


log_buffer = deque()
f_csv = open("log.csv", "w", newline="")
writer = csv.writer(f_csv)
writer.writerow(["Time", "Voltage"])

# ---------- shared state ----------
latest_value = 0.0
lock = Lock()
running = True


# ---------- helpers ----------
def adc_to_voltage(adc):
    return abs((adc * VREF / ((1 << ADC_BITS) - 1)) - VREF)


def exp_filter(new, prev):
    return ALPHA * new + (1 - ALPHA) * prev


# ---------- serial reader thread ----------
def serial_reader(ser):
    global latest_value, running
    while running:
        while ser.in_waiting:
            line = ser.readline()
            try:
                val = float(line.decode(errors="ignore").strip())
                with lock:
                    latest_value = val  # always keep newest
                    log_buffer.append(LogPoint(adc_to_voltage(val), time.time()))
            except Exception:
                print_exc()


# ---------- main ----------
def main():
    global running

    ser = serial.Serial(PORT, BAUD, timeout=0.01)

    # start serial thread
    Thread(target=serial_reader, args=(ser,), daemon=True).start()

    app = QtWidgets.QApplication(sys.argv)
    win = pg.GraphicsLayoutWidget(title="High-Speed Scope")
    win.resize(1000, 400)

    plot = win.addPlot()
    plot.enableAutoRange(x=False, y=False)
    plot.setMouseEnabled(x=False, y=False)
    plot.setYRange(0, VREF)
    plot.setLabel("left", "Voltage", units="V")
    plot.setLabel("bottom", "Time", units="s")

    curve = plot.plot(pen="y")

    xdata = deque(maxlen=MAX_POINTS)
    ydata = deque(maxlen=MAX_POINTS)
    filtered = 0.0
    t0 = time.perf_counter()

    def update_plot():
        nonlocal filtered
        to_dump = []
        with lock:
            to_dump = list(log_buffer)
            val = latest_value
        if to_dump:
            writer.writerows(to_dump)
            f_csv.flush()
        voltage = adc_to_voltage(val)
        filtered = exp_filter(voltage, filtered)
        t = time.perf_counter() - t0
        xdata.append(t)
        ydata.append(filtered)
        curve.setData(xdata, ydata)
        plot.setXRange(max(0, t - X_WINDOW), t)

    timer = QtCore.QTimer()
    timer.timeout.connect(update_plot)
    timer.start(GUI_UPDATE_MS)

    # ---------- clean exit ----------
    def cleanup():
        global running
        running = False
        timer.stop()
        if ser.is_open:
            ser.close()

        f_csv.close()
        app.quit()

    signal.signal(signal.SIGINT, lambda *_: cleanup())
    app.aboutToQuit.connect(cleanup)

    win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
