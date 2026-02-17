from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

from jnius import autoclass
import threading


BluetoothAdapter = autoclass("android.bluetooth.BluetoothAdapter")
UUID = autoclass("java.util.UUID")


# ================= DASHBOARD SCREEN =================
class DashboardScreen(Screen):

    def build_ui(self):
        main_layout = BoxLayout(
            orientation='vertical',
            padding=15,
            spacing=12
        )

        top_layout = BoxLayout(size_hint_y=None, height=90, spacing=15)

        menu_button = Button(
            text="Set Parameters",
            size_hint=(None, None),
            size=(240, 85),
            font_size=24
        )
        menu_button.bind(on_press=self.goto_params)

        title = Label(
            text="16S BMS DASHBOARD",
            font_size=40,
            bold=True
        )

        top_layout.add_widget(menu_button)
        top_layout.add_widget(title)
        main_layout.add_widget(top_layout)

        def create_param(label_text):
            layout = BoxLayout(size_hint_y=None, height=70, spacing=15)
            label = Label(text=label_text, font_size=22, bold=True)
            value = TextInput(readonly=True, font_size=30, text="0.0")
            layout.add_widget(label)
            layout.add_widget(value)
            main_layout.add_widget(layout)
            return value

        self.pack_voltage = create_param("Pack Voltage (V)")
        self.pack_current = create_param("Pack Current (A)")
        self.pack_temp = create_param("Temperature (°C)")
        self.pack_soc = create_param("State of Charge (%)")

        self.soc_bar = ProgressBar(max=100, size_hint_y=None, height=35)
        self.soc_bar.value = 0
        main_layout.add_widget(self.soc_bar)

        cell_title = Label(
            text="Cell Voltages (16S)",
            font_size=30,
            bold=True,
            size_hint_y=None,
            height=50
        )
        main_layout.add_widget(cell_title)

        grid = GridLayout(cols=2, spacing=12, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        self.cell_inputs = []

        for i in range(1, 17):
            cell_box = BoxLayout(size_hint_y=None, height=65, spacing=10)
            label = Label(text=f"Cell {i}", font_size=20, bold=True)
            value = TextInput(readonly=True, font_size=26, text="0.000")
            cell_box.add_widget(label)
            cell_box.add_widget(value)
            grid.add_widget(cell_box)
            self.cell_inputs.append(value)

        main_layout.add_widget(grid)
        main_layout.add_widget(Label(size_hint_y=1))

        self.add_widget(main_layout)

    def goto_params(self, instance):
        self.manager.current = "params"

    def update_ui(self, data):
        """
        Example expected data format:
        PV:52.3,PC:10.5,T:32,SOC:80,
        C1:3.28,C2:3.29,...,C16:3.27,
        UV:2.80,OV:4.20,UC:-50,OC:100
        """

        try:
            parts = data.split(",")

            values = {}
            for part in parts:
                if ":" in part:
                    key, val = part.split(":")
                    values[key.strip()] = float(val.strip())

            # Dashboard values
            self.pack_voltage.text = str(values.get("PV", 0.0))
            self.pack_current.text = str(values.get("PC", 0.0))
            self.pack_temp.text = str(values.get("T", 0.0))
            self.pack_soc.text = str(values.get("SOC", 0.0))

            soc_val = values.get("SOC", 0.0)
            self.soc_bar.value = soc_val

            for i in range(16):
                self.cell_inputs[i].text = str(values.get(f"C{i+1}", 0.0))

            # 🔥 Update Parameters Screen values also
            params_screen = self.manager.get_screen("params")
            params_screen.update_params(values)

        except Exception as e:
            print("Data parse error:", e)


# ================= PARAMETERS SCREEN =================
class ParamsScreen(Screen):

    def build_ui(self):
        root = BoxLayout(
            orientation='vertical',
            padding=[20, 20, 20, 20],
            spacing=15
        )

        title = Label(
            text="BMS Protection Parameters",
            font_size=30,
            bold=True,
            size_hint_y=None,
            height=50
        )
        root.add_widget(title)

        self.uv = self.param_row(root, "Under Voltage (V)", 2.8)
        self.ov = self.param_row(root, "Over Voltage (V)", 4.2)
        self.uc = self.param_row(root, "Under Current (A)", -50)
        self.oc = self.param_row(root, "Over Current (A)", 100)

        back_btn = Button(
            text="Back to Dashboard",
            size_hint_y=None,
            height=70,
            font_size=24
        )
        back_btn.bind(on_press=self.goto_dashboard)
        root.add_widget(back_btn)

        root.add_widget(Label(size_hint_y=1))
        self.add_widget(root)

    def param_row(self, parent, name, default):
        box = BoxLayout(size_hint_y=None, height=70, spacing=12)
        label = Label(text=name, font_size=22)
        ti = TextInput(text=str(default), multiline=False, font_size=26)
        box.add_widget(label)
        box.add_widget(ti)
        parent.add_widget(box)
        return ti

    def goto_dashboard(self, instance):
        self.manager.current = "dashboard"

    # 🔥 Update protection parameters from Bluetooth
    def update_params(self, values):
        if "UV" in values:
            self.uv.text = str(values["UV"])
        if "OV" in values:
            self.ov.text = str(values["OV"])
        if "UC" in values:
            self.uc.text = str(values["UC"])
        if "OC" in values:
            self.oc.text = str(values["OC"])


# ================= BLUETOOTH CLASS =================
class BluetoothReader:

    def __init__(self, dashboard):
        self.dashboard = dashboard
        self.socket = None
        self.running = False

    def connect(self, mac_address):
        adapter = BluetoothAdapter.getDefaultAdapter()
        device = adapter.getRemoteDevice(mac_address)

        # Standard SPP UUID
        spp_uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")

        self.socket = device.createRfcommSocketToServiceRecord(spp_uuid)
        adapter.cancelDiscovery()
        self.socket.connect()

        self.running = True
        threading.Thread(target=self.read_loop, daemon=True).start()

        print("Bluetooth Connected!")

    def read_loop(self):
        input_stream = self.socket.getInputStream()
        buffer = bytearray(1024)

        while self.running:
            try:
                bytes_read = input_stream.read(buffer)
                if bytes_read > 0:
                    received_data = buffer[:bytes_read].decode("utf-8").strip()
                    print("Received:", received_data)

                    # Update UI in main thread
                    Clock.schedule_once(lambda dt: self.dashboard.update_ui(received_data))

            except Exception as e:
                print("Bluetooth read error:", e)
                self.running = False

    def stop(self):
        self.running = False
        if self.socket:
            self.socket.close()


# ================= APP =================
class BMSApp(App):

    def build(self):
        sm = ScreenManager()

        self.dashboard = DashboardScreen(name="dashboard")
        self.dashboard.build_ui()

        self.params = ParamsScreen(name="params")
        self.params.build_ui()

        sm.add_widget(self.dashboard)
        sm.add_widget(self.params)

        # Start Bluetooth after app loads
        Clock.schedule_once(self.start_bluetooth, 2)

        return sm

    def start_bluetooth(self, dt):
        try:
            mac = "00:11:22:33:44:55"   # 🔥 replace with your BMS Bluetooth MAC address
            self.bt = BluetoothReader(self.dashboard)
            self.bt.connect(mac)

        except Exception as e:
            print("Bluetooth connection error:", e)

    def on_stop(self):
        # Stop Bluetooth when app closes
        if hasattr(self, "bt"):
            self.bt.stop()


if __name__ == "__main__":
    BMSApp().run()
