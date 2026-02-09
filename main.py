from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

import threading
from jnius import autoclass

PythonActivity = autoclass("org.kivy.android.PythonActivity")
BluetoothAdapter = autoclass("android.bluetooth.BluetoothAdapter")
UUID = autoclass("java.util.UUID")

ActivityCompat = autoclass("androidx.core.app.ActivityCompat")

SPP_UUID = "00001101-0000-1000-8000-00805F9B34FB"


class BluetoothSendApp(App):
    def build(self):
        self.layout = BoxLayout(orientation="vertical", padding=20, spacing=10)

        self.status = Label(text="Ready")
        self.btn = Button(text="Send HI to Paired Device")
        self.btn.bind(on_press=self.send_hi)

        self.layout.add_widget(self.status)
        self.layout.add_widget(self.btn)

        return self.layout

    def request_permissions(self):
        activity = PythonActivity.mActivity
        permissions = [
            "android.permission.BLUETOOTH_CONNECT",
            "android.permission.BLUETOOTH_SCAN",
            "android.permission.ACCESS_FINE_LOCATION"
        ]
        ActivityCompat.requestPermissions(activity, permissions, 0)

    def send_hi(self, instance):
        self.request_permissions()
        self.status.text = "Checking paired devices..."

        threading.Thread(target=self.send_thread, daemon=True).start()

    def send_thread(self):
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
                Clock.schedule_once(lambda dt: self.set_status("No paired device found"))
                return

            device = paired[0]   # first paired device
            name = device.getName()
            addr = device.getAddress()

            Clock.schedule_once(lambda dt: self.set_status(f"Connecting to {name}..."))

            uuid = UUID.fromString(SPP_UUID)
            socket = device.createRfcommSocketToServiceRecord(uuid)

            adapter.cancelDiscovery()
            socket.connect()

            msg = "hi\n"
            socket.getOutputStream().write(msg.encode())
            socket.getOutputStream().flush()

            socket.close()

            Clock.schedule_once(lambda dt: self.set_status(f"Sent HI to {name} ({addr})"))

        except Exception as e:
            Clock.schedule_once(lambda dt: self.set_status("Failed (pair device first)"))

    def set_status(self, text):
        self.status.text = text


if __name__ == "__main__":
    BluetoothSendApp().run()
