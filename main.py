from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

import bluetooth


class BluetoothApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        self.status = Label(text="Bluetooth idle")
        self.scan_btn = Button(text="Scan Devices")
        self.scan_btn.bind(on_press=self.scan_devices)

        self.layout.add_widget(self.status)
        self.layout.add_widget(self.scan_btn)

        return self.layout

    def scan_devices(self, instance):
        self.status.text = "Scanning..."
        devices = bluetooth.discover_devices(duration=8, lookup_names=True)

        if not devices:
            self.status.text = "No devices found"
            return

        addr, name = devices[0]  # connect to first device found
        self.status.text = f"Connecting to {name}"

        try:
            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((addr, 1))
            self.status.text = f"Connected to {name}"
            sock.close()
        except Exception as e:
            self.status.text = f"Connection failed"


if __name__ == "__main__":
    BluetoothApp().run()
