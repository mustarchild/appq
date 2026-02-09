from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

from jnius import autoclass
import threading

BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
UUID = autoclass('java.util.UUID')
PythonActivity = autoclass('org.kivy.android.PythonActivity')

# Standard Serial Port Profile UUID (SPP)
SPP_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")


class BluetoothSendApp(App):
    def build(self):
        self.socket = None
        self.outputStream = None

        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=15)

        self.status = Label(text="Ready")
        self.layout.add_widget(self.status)

        self.btn_connect = Button(text="Connect to Paired Device")
        self.btn_connect.bind(on_press=self.connect_device)
        self.layout.add_widget(self.btn_connect)

        self.btn_send = Button(text="Send HI", disabled=True)
        self.btn_send.bind(on_press=self.send_hi)
        self.layout.add_widget(self.btn_send)

        return self.layout

    def connect_device(self, instance):
        self.status.text = "Connecting..."
        threading.Thread(target=self._connect_thread, daemon=True).start()

    def _connect_thread(self):
        try:
            adapter = BluetoothAdapter.getDefaultAdapter()

            if adapter is None:
                Clock.schedule_once(lambda dt: self.set_status("Bluetooth not supported"))
                return

            if not adapter.isEnabled():
                Clock.schedule_once(lambda dt: self.set_status("Turn Bluetooth ON"))
                return

            paired = adapter.getBondedDevices().toArray()

            if len(paired) == 0:
                Clock.schedule_once(lambda dt: self.set_status("No paired devices found"))
                return

            # connect first paired device
            device = paired[0]
            name = device.getName()
            addr = device.getAddress()

            Clock.schedule_once(lambda dt: self.set_status(f"Connecting to {name} ({addr})"))

            self.socket = device.createRfcommSocketToServiceRecord(SPP_UUID)
            adapter.cancelDiscovery()
            self.socket.connect()

            self.outputStream = self.socket.getOutputStream()

            Clock.schedule_once(lambda dt: self.connected(name))

        except Exception as e:
            Clock.schedule_once(lambda dt: self.set_status("Connection Failed"))

    def connected(self, name):
        self.status.text = f"Connected: {name}"
        self.btn_send.disabled = False

    def send_hi(self, instance):
        threading.Thread(target=self._send_thread, daemon=True).start()

    def _send_thread(self):
        try:
            if self.outputStream:
                msg = "hi\n"
                self.outputStream.write(msg.encode("utf-8"))
                Clock.schedule_once(lambda dt: self.set_status("Sent: hi"))
            else:
                Clock.schedule_once(lambda dt: self.set_status("Not connected"))
        except:
            Clock.schedule_once(lambda dt: self.set_status("Send failed"))

    def set_status(self, text):
        self.status.text = text

    def on_stop(self):
        try:
            if self.socket:
                self.socket.close()
        except:
            pass


if __name__ == "__main__":
    BluetoothSendApp().run()
