from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

from jnius import autoclass, PythonJavaClass, java_method


# Android classes
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
Intent = autoclass('android.content.Intent')
IntentFilter = autoclass('android.content.IntentFilter')
PythonActivity = autoclass('org.kivy.android.PythonActivity')


class BluetoothReceiver(PythonJavaClass):
    __javainterfaces__ = ['android/content/BroadcastReceiver']
    __javacontext__ = 'app'

    def __init__(self, app):
        super().__init__()
        self.app = app

    @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
    def onReceive(self, context, intent):
        action = intent.getAction()

        if action == BluetoothAdapter.ACTION_DISCOVERY_FINISHED:
            Clock.schedule_once(lambda dt: self.app.update_status("Scan finished"))

        if action == BluetoothAdapter.ACTION_FOUND:
            device = intent.getParcelableExtra(BluetoothAdapter.EXTRA_DEVICE)
            name = device.getName()
            addr = device.getAddress()

            Clock.schedule_once(
                lambda dt: self.app.add_device(name, addr)
            )


class BluetoothScanApp(App):
    def build(self):
        self.devices = []

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.status = Label(text="Ready")
        self.scan_btn = Button(text="Scan Nearby Bluetooth")
        self.scan_btn.bind(on_press=self.start_scan)

        self.layout.add_widget(self.status)
        self.layout.add_widget(self.scan_btn)

        return self.layout

    def start_scan(self, instance):
        adapter = BluetoothAdapter.getDefaultAdapter()

        if adapter is None:
            self.status.text = "Bluetooth not supported"
            return

        if not adapter.isEnabled():
            self.status.text = "Turn Bluetooth ON"
            return

        self.status.text = "Scanning..."
        self.devices.clear()

        activity = PythonActivity.mActivity
        self.receiver = BluetoothReceiver(self)

        filter = IntentFilter()
        filter.addAction(BluetoothAdapter.ACTION_FOUND)
        filter.addAction(BluetoothAdapter.ACTION_DISCOVERY_FINISHED)

        activity.registerReceiver(self.receiver, filter)
        adapter.startDiscovery()

    def add_device(self, name, addr):
        text = f"{name or 'Unknown'}\n{addr}"
        self.layout.add_widget(Label(text=text))
        self.devices.append((name, addr))

    def update_status(self, text):
        self.status.text = text


if __name__ == "__main__":
    BluetoothScanApp().run()
