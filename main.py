from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

from jnius import autoclass, PythonJavaClass, java_method

# Android classes
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
IntentFilter = autoclass('android.content.IntentFilter')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
ContextCompat = autoclass('androidx.core.content.ContextCompat')
ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
PackageManager = autoclass('android.content.pm.PackageManager')


class BluetoothReceiver(PythonJavaClass):
    __javainterfaces__ = ['android/content/BroadcastReceiver']
    __javacontext__ = 'app'

    def __init__(self, app):
        super().__init__()
        self.app = app

    @java_method('(Landroid/content/Context;Landroid/content/Intent;)V')
    def onReceive(self, context, intent):
        action = intent.getAction()

        if action == BluetoothAdapter.ACTION_FOUND:
            device = intent.getParcelableExtra(BluetoothAdapter.EXTRA_DEVICE)
            name = device.getName()
            addr = device.getAddress()
            Clock.schedule_once(lambda dt: self.app.add_device(name, addr))

        elif action == BluetoothAdapter.ACTION_DISCOVERY_FINISHED:
            Clock.schedule_once(lambda dt: self.app.set_status("Scan finished"))


class BluetoothScanApp(App):
    def build(self):
        self.devices = []
        self.receiver = None

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        self.status = Label(text="Ready")
        self.scan_btn = Button(text="Scan Bluetooth")
        self.scan_btn.bind(on_press=self.start_scan)

        self.layout.add_widget(self.status)
        self.layout.add_widget(self.scan_btn)
        return self.layout

    def request_permissions(self):
        activity = PythonActivity.mActivity
        permissions = [
            "android.permission.BLUETOOTH_SCAN",
            "android.permission.ACCESS_FINE_LOCATION"
        ]
        ActivityCompat.requestPermissions(activity, permissions, 0)

    def has_permission(self, permission):
        activity = PythonActivity.mActivity
        return ContextCompat.checkSelfPermission(
            activity, permission
        ) == PackageManager.PERMISSION_GRANTED

    def start_scan(self, instance):
        adapter = BluetoothAdapter.getDefaultAdapter()

        if adapter is None:
            self.set_status("Bluetooth not supported")
            return

        if not adapter.isEnabled():
            self.set_status("Turn Bluetooth ON")
            return

        if not self.has_permission("android.permission.BLUETOOTH_SCAN"):
            self.set_status("Grant permission and tap again")
            self.request_permissions()
            return

        try:
            self.set_status("Scanning...")
            self.devices.clear()

            activity = PythonActivity.mActivity
            self.receiver = BluetoothReceiver(self)

            filter = IntentFilter()
            filter.addAction(BluetoothAdapter.ACTION_FOUND)
            filter.addAction(BluetoothAdapter.ACTION_DISCOVERY_FINISHED)

            activity.registerReceiver(self.receiver, filter)
            adapter.startDiscovery()

        except Exception as e:
            self.set_status("Scan failed")

    def add_device(self, name, addr):
        text = f"{name or 'Unknown'}\n{addr}"
        self.layout.add_widget(Label(text=text))

    def set_status(self, text):
        self.status.text = text

    def on_stop(self):
        try:
            if self.receiver:
                PythonActivity.mActivity.unregisterReceiver(self.receiver)
        except:
            pass


if __name__ == "__main__":
    BluetoothScanApp().run()
