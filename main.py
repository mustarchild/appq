from kivy.app import App
from kivy.uix.label import Label
from jnius import autoclass
import threading

BluetoothAdapter = autoclass("android.bluetooth.BluetoothAdapter")
UUID = autoclass("java.util.UUID")

SPP_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")


class SendHiApp(App):
    def build(self):
        self.lbl = Label(text="Sending hi...")
        threading.Thread(target=self.send_hi, daemon=True).start()
        return self.lbl

    def send_hi(self):
        try:
            adapter = BluetoothAdapter.getDefaultAdapter()

            if adapter is None:
                self.lbl.text = "Bluetooth not supported"
                return

            if not adapter.isEnabled():
                self.lbl.text = "Bluetooth OFF"
                return

            paired = adapter.getBondedDevices().toArray()
            if len(paired) == 0:
                self.lbl.text = "No paired devices"
                return

            device = paired[0]  # first paired device
            socket = device.createRfcommSocketToServiceRecord(SPP_UUID)

            adapter.cancelDiscovery()
            socket.connect()

            out_stream = socket.getOutputStream()
            out_stream.write("hi\n".encode("utf-8"))

            socket.close()
            self.lbl.text = "Sent: hi"

        except Exception as e:
            self.lbl.text = "Send failed"


if __name__ == "__main__":
    SendHiApp().run()
