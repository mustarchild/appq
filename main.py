from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

import threading

try:
    import bluetooth
except:
    bluetooth = None


class BluetoothApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        self.status = Label(text="Bluetooth Ready")
        self.scan_btn = Button(text="Scan Bluetooth")
        self.scan_btn.bind(on_press=self.start_scan)

        self.layout.add_widget(self.status)
        self.layout.add_widget(self.scan_btn)

        return self.layout

    def start_scan(self, instance):
        self.status.text = "Scanning..."
        threading.Thread(target=self.scan_devices, daemon=True).start()

    def scan_devices(self):
        if bluetooth is None:
            Clock.schedule_once(
                lambda dt: self.set_status("Bluetooth module not found"),
                0
            )
            return

        try:
            devices = bluetooth.discover_devices(duration=6, lookup_names=True)
            if not devices:
                Clock.schedule_once(
                    lambda dt: self.set_status("No devices found"),
                    0
                )
                return

            addr, name = devices[0]
            Clock.schedule_once(
                lambda dt: self.set_status(f"Found {name}, connecting..."),
                0
            )

            sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            sock.connect((addr, 1))
            sock.close()

            Clock.schedule_once(
                lambda dt: self.set_status(f"Connected to {name}"),
                0
            )

        except Exception as e:
            Clock.schedule_once(
                lambda dt: self.set_status("Bluetooth error"),
                0
            )

    def set_status(self, text):
        self.status.text = text


if __name__ == "__main__":
    BluetoothApp().run()
