from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

import threading

from jnius import autoclass
from android.permissions import request_permissions, Permission

# ================= BLUETOOTH =================
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
UUID = autoclass('java.util.UUID')


class BluetoothClient:
    def __init__(self):
        self.adapter = BluetoothAdapter.getDefaultAdapter()
        self.socket = None
        self.stream = None
        self.connected = False

    def request_permissions(self):
        request_permissions([
            Permission.BLUETOOTH,
            Permission.BLUETOOTH_ADMIN,
            Permission.BLUETOOTH_CONNECT
        ])

    def connect(self, device_name):
        devices = self.adapter.getBondedDevices().toArray()
        for d in devices:
            if d.getName() == device_name:
                uuid = UUID.fromString(
                    "00001101-0000-1000-8000-00805F9B34FB"
                )
                self.socket = d.createRfcommSocketToServiceRecord(uuid)
                self.socket.connect()
                self.stream = self.socket.getInputStream()
                self.connected = True
                return True
        return False

    def read_line(self):
        if not self.connected:
            return None

        data = bytearray()
        while True:
            c = self.stream.read()
            if c == 10:  # \n
                break
            data.append(c)

        return data.decode().strip()


# ================= DASHBOARD SCREEN =================
class DashboardScreen(Screen):

    def build_ui(self):
        main = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # ---------- Top Bar ----------
        top = BoxLayout(size_hint_y=None, height=75, spacing=10)

        btn_params = Button(text="Set Parameters", size=(200, 75),
                            size_hint=(None, None), font_size=20)
        btn_params.bind(on_press=lambda x: self.manager.switch_to(
            self.manager.get_screen("params")))

        title = Label(text="16S BMS DASHBOARD", font_size=34, bold=True)

        top.add_widget(btn_params)
        top.add_widget(title)
        main.add_widget(top)

        # ---------- Bluetooth ----------
        bt_bar = BoxLayout(size_hint_y=None, height=60, spacing=10)
        self.bt_status = Label(text="Bluetooth: Disconnected", font_size=18)

        bt_btn = Button(text="Connect BMS", font_size=20)
        bt_btn.bind(on_press=self.connect_bt)

        bt_bar.add_widget(self.bt_status)
        bt_bar.add_widget(bt_btn)
        main.add_widget(bt_bar)

        # ---------- Pack Params ----------
        def param(label):
            row = BoxLayout(size_hint_y=None, height=55)
            l = Label(text=label, font_size=18, bold=True)
            t = TextInput(readonly=True, font_size=26, text="0.0")
            row.add_widget(l)
            row.add_widget(t)
            main.add_widget(row)
            return t

        self.pack_voltage = param("Pack Voltage (V)")
        self.pack_current = param("Pack Current (A)")
        self.pack_temp = param("Temperature (°C)")
        self.pack_soc = param("State of Charge (%)")

        self.soc_bar = ProgressBar(max=100, height=25, size_hint_y=None)
        main.add_widget(self.soc_bar)

        # ---------- Cells ----------
        main.add_widget(Label(text="Cell Voltages (16S)",
                              font_size=26, bold=True,
                              size_hint_y=None, height=40))

        grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        self.cell_inputs = []

        for i in range(16):
            box = BoxLayout(size_hint_y=None, height=50)
            box.add_widget(Label(text=f"Cell {i+1}", font_size=16))
            ti = TextInput(readonly=True, font_size=22, text="0.000")
            self.cell_inputs.append(ti)
            box.add_widget(ti)
            grid.add_widget(box)

        main.add_widget(grid)
        self.add_widget(main)

    # ---------- Bluetooth ----------
    def connect_bt(self, instance):
        self.bt = BluetoothClient()
        self.bt.request_permissions()

        try:
            if self.bt.connect("HC-05"):  # CHANGE NAME
                self.bt_status.text = "Bluetooth: Connected"
                threading.Thread(target=self.read_bt, daemon=True).start()
            else:
                self.bt_status.text = "Device not found"
        except Exception:
            self.bt_status.text = "Connection failed"

    def read_bt(self):
        while True:
            line = self.bt.read_line()
            if line:
                Clock.schedule_once(lambda dt: self.parse_data(line))

    def parse_data(self, data):
        try:
            parts = dict(item.split("=") for item in data.split(","))

            self.pack_voltage.text = parts.get("PV", "0")
            self.pack_current.text = parts.get("PC", "0")
            self.pack_temp.text = parts.get("T", "0")
            self.pack_soc.text = parts.get("SOC", "0")
            self.soc_bar.value = float(parts.get("SOC", 0))

            for i in range(16):
                self.cell_inputs[i].text = parts.get(f"C{i+1}", "0.000")

        except Exception:
            pass


# ================= PARAMETERS SCREEN =================
class ParamsScreen(Screen):

    def build_ui(self):
        root = BoxLayout(orientation='vertical', padding=20, spacing=15)
        root.add_widget(Label(text="BMS Protection Parameters",
                              font_size=30, bold=True,
                              size_hint_y=None, height=50))

        self.param(root, "Under Voltage (V)", 2.8)
        self.param(root, "Over Voltage (V)", 4.2)
        self.param(root, "Under Current (A)", -50)
        self.param(root, "Over Current (A)", 100)

        back = Button(text="Back to Dashboard", height=65,
                      size_hint_y=None, font_size=22)
        back.bind(on_press=lambda x: self.manager.switch_to(
            self.manager.get_screen("dashboard")))

        root.add_widget(back)
        self.add_widget(root)

    def param(self, parent, name, default):
        box = BoxLayout(size_hint_y=None, height=60)
        box.add_widget(Label(text=name, font_size=18))
        box.add_widget(TextInput(text=str(default), font_size=24))
        parent.add_widget(box)


# ================= APP =================
class BMSApp(App):
    def build(self):
        sm = ScreenManager()

        dash = DashboardScreen(name="dashboard")
        dash.build_ui()

        params = ParamsScreen(name="params")
        params.build_ui()

        sm.add_widget(dash)
        sm.add_widget(params)
        return sm


if __name__ == "__main__":
    BMSApp().run()
