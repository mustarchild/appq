from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock

import threading
from jnius import autoclass, PythonJavaClass, java_method

BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
UUID = autoclass('java.util.UUID')

IntentFilter = autoclass('android.content.IntentFilter')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
ContextCompat = autoclass('androidx.core.content.ContextCompat')
ActivityCompat = autoclass('androidx.core.app.ActivityCompat')
PackageManager = autoclass('android.content.pm.PackageManager')


SPP_UUID = "00001101-0000-1000-8000-00805F9B34FB"


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


class BluetoothSendApp(App):
    def build(self):
        self.receiver = None
        self.devices = []

        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)

        self.status = Label(text="Ready")
        self.scan_btn = Button(text="Scan Devices")
        self.send_btn = Button(text="Send HI")
        self.send_btn.disabled = True

        self.scan_btn.bind(on_press=self.start_scan)
        self.send_btn.bind(on_press=self.send_hi)

        self.layout.add_widget(self.status)
        self.layout.add_widget(self.scan_btn)
        self.layout.add_widget(self.send_btn)

        return self.layout

    def request_permissions(self):
        activity = PythonActivity.mActivity
        permissions = [
            "android.permission.BLUETOOTH_SCAN",
            "android.permission.BLUETOOTH_CONNECT",
            "android.permission.ACCESS_FINE_LOCATION"
        ]
        ActivityCompat.requestPermissions(activity, permissions, 0)

    def has_permission(self, permission):
        activity = PythonActivity.mActivity
        return ContextCompat.checkSelfPermission(activity, permission) == PackageManager.PERMISSION_GRANTED

    def start_scan(self, instance):
        adapter = BluetoothAdapter.getDefaultAdapter()

        if adapter is None:
            self.set_status("Bluetooth not supported")
            return

        if not adapter.isEnabled():
            self.set_status("Turn Bluetooth ON")
            return

        if not self.has_permission("android.permission.BLUETOOTH_SCAN"):
            self.set_status("Grant permission and tap scan again")
            self.request_permissions()
            return

        self.devices.clear()
        self.send_btn.disabled = True

        try:
            self.set_status("Scanning...")

            activity = PythonActivity.mActivity
            self.receiver = BluetoothReceiver(self)

            flt = IntentFilter()
            flt.addAction(BluetoothAdapter.ACTION_FOUND)
            flt.addAction(BluetoothAdapter.ACTION_DISCOVERY_FINISHED)

            activity.registerReceiver(self.receiver, flt)

            adapter.startDiscovery()

        except Exception as e:
            self.set_status("Scan error")

    def add_device(self, name, addr):
        self.devices.append((name, addr))
        self.layout.add_widget(Label(text=f"{name or 'Unknown'}\n{addr}"))

        # Enable send button once we found at least 1 device
        self.send_btn.disabled = False

    def send_hi(self, instance):
        if not self.devices:
            self.set_status("No device found")
            return

        if not self.has_permission("android.permission.BLUETOOTH_CONNECT"):
            self.set_status("Grant connect permission")
            self.request_permissions()
            return

        # Send to first found device
        name, addr = self.devices[0]
        self.set_status(f"Connecting to {name}...")

        threading.Thread(target=self.connect_and_send, args=(addr, name), daemon=True).start()

    def connect_and_send(self, addr, name):
        try:
            adapter = BluetoothAdapter.getDefaultAdapter()
            adapter.cancelDiscovery()

            device = adapter.getRemoteDevice(addr)

            uuid = UUID.fromString(SPP_UUID)

            socket = device.createRfcommSocketToServiceRecord(uuid)
            socket.connect()

            msg = "hi\n"
            socket.getOutputStream().write(msg.encode())
            socket.getOutputStream().flush()

            socket.close()

            Clock.schedule_once(lambda dt: self.set_status(f"Sent HI to {name}"))

        except Exception as e:
            Clock.schedule_once(lambda dt: self.set_status("Send failed"))

    def set_status(self, text):
        self.status.text = text

    def on_stop(self):
        try:
            if self.receiver:
                PythonActivity.mActivity.unregisterReceiver(self.receiver)
        except:
            pass


if __name__ == "__main__":
    BluetoothSendApp().run()
