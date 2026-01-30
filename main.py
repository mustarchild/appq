from kivy.app import App
from kivy.uix.label import Label
from jnius import autoclass

class BluetoothApp(App):
    def build(self):
        BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        adapter = BluetoothAdapter.getDefaultAdapter()

        if adapter is None:
            return Label(text="Bluetooth not supported")

        if not adapter.isEnabled():
            return Label(text="Bluetooth is OFF")

        return Label(text="Bluetooth is ON")

if __name__ == "__main__":
    BluetoothApp().run()
