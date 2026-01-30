from kivy.app import App
from kivy.uix.button import Button
from jnius import autoclass

class BluetoothApp(App):
    def build(self):
        btn = Button(text="Turn Bluetooth ON")
        btn.bind(on_press=self.enable_bt)
        return btn

    def enable_bt(self, instance):
        BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        Intent = autoclass('android.content.Intent')

        adapter = BluetoothAdapter.getDefaultAdapter()
        if adapter and not adapter.isEnabled():
            intent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
            self.startActivity(intent)

if __name__ == "__main__":
    BluetoothApp().run()
