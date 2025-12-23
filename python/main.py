import sys
import signal
import time
import numpy as np
from npy_append_array import NpyAppendArray
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

LOG_FILE = "log.npy"  # LOG file name
# =========================================


# -------------- LOGGING --------------
log_buffer = np.empty((0, 2), dtype=np.float64)

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
    global latest_value, running, log_buffer
    while running:
        while ser.in_waiting:
            line = ser.readline()
            try:
                val = float(line.decode(errors="ignore").strip())
                with lock:
                    latest_value = val  # always keep newest
                    new_sample = np.array(
                        [[time.time(), adc_to_voltage(val)]], dtype=np.float64
                    )
                    log_buffer = np.vstack((log_buffer, new_sample))
            except ValueError:
                continue
            except Exception:
                print_exc()


# ---------- main ----------
def main():
    global running, log_buffer

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
        global log_buffer
        nonlocal filtered
        to_dump = []
        with lock:
            to_dump = list(log_buffer)
            val = latest_value
        if to_dump:
            with NpyAppendArray(LOG_FILE) as npaa:
                npaa.append(log_buffer)
                log_buffer = np.empty((0, 2), dtype=np.float64)
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

        app.quit()

    signal.signal(signal.SIGINT, lambda *_: cleanup())
    app.aboutToQuit.connect(cleanup)

    win.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
