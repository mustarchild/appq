from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen


# ================= DASHBOARD SCREEN =================
class DashboardScreen(Screen):

    def build_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # ---------- Top Bar ----------
        top_layout = BoxLayout(size_hint_y=None, height=75, spacing=10)

        menu_button = Button(
            text="Set Parameters",
            size_hint=(None, None),
            size=(200, 75),
            font_size=20
        )
        menu_button.bind(on_press=self.goto_params)

        title = Label(
            text="16S BMS DASHBOARD",
            font_size=34,
            bold=True
        )

        top_layout.add_widget(menu_button)
        top_layout.add_widget(title)
        main_layout.add_widget(top_layout)

        # ---------- Pack Parameters ----------
        def create_param(label_text):
            layout = BoxLayout(size_hint_y=None, height=55, spacing=10)
            label = Label(text=label_text, font_size=18, bold=True)
            value = TextInput(
                readonly=True,
                font_size=26,
                text="0.0"
            )
            layout.add_widget(label)
            layout.add_widget(value)
            main_layout.add_widget(layout)
            return value

        self.pack_voltage = create_param("Pack Voltage (V)")
        self.pack_current = create_param("Pack Current (A)")
        self.pack_temp = create_param("Temperature (°C)")
        self.pack_soc = create_param("State of Charge (%)")

        # ---------- SOC Progress ----------
        self.soc_bar = ProgressBar(max=100, size_hint_y=None, height=25)
        self.soc_bar.value = 0
        main_layout.add_widget(self.soc_bar)

        # ---------- Cell Voltages ----------
        cell_title = Label(
            text="Cell Voltages (16S)",
            font_size=26,
            bold=True,
            size_hint_y=None,
            height=40
        )
        main_layout.add_widget(cell_title)

        grid = GridLayout(cols=2, spacing=10, size_hint_y=None)
        grid.bind(minimum_height=grid.setter('height'))
        self.cell_inputs = []

        for i in range(1, 17):
            cell_box = BoxLayout(size_hint_y=None, height=50, spacing=5)
            label = Label(text=f"Cell {i}", font_size=16, bold=True)
            value = TextInput(
                readonly=True,
                font_size=22,
                text="0.000"
            )
            cell_box.add_widget(label)
            cell_box.add_widget(value)
            grid.add_widget(cell_box)
            self.cell_inputs.append(value)

        main_layout.add_widget(grid)
        self.add_widget(main_layout)

        # Update loop (real data can be placed here later)
        Clock.schedule_interval(self.update_values, 1)

    def goto_params(self, instance):
        self.manager.current = "params"

    def update_values(self, dt):
        # PLACEHOLDER VALUES (replace with real BMS data)
        pack_voltage = 0.0
        pack_current = 0.0
        pack_temp = 0.0
        soc = 0.0
        cell_voltages = [0.0] * 16

        self.pack_voltage.text = str(pack_voltage)
        self.pack_current.text = str(pack_current)
        self.pack_temp.text = str(pack_temp)
        self.pack_soc.text = str(soc)
        self.soc_bar.value = soc

        for i, cell in enumerate(self.cell_inputs):
            cell.text = str(cell_voltages[i])


# ================= PARAMETERS SCREEN =================
class ParamsScreen(Screen):

    def build_ui(self):
        root = BoxLayout(
            orientation='vertical',
            padding=[20, 20, 20, 20],
            spacing=15
        )

        title = Label(
            text="BMS Protection Parameters",
            font_size=30,
            bold=True,
            size_hint_y=None,
            height=50
        )
        root.add_widget(title)

        self.uv = self.param_row(root, "Under Voltage (V)", 2.8)
        self.ov = self.param_row(root, "Over Voltage (V)", 4.2)
        self.uc = self.param_row(root, "Under Current (A)", -50)
        self.oc = self.param_row(root, "Over Current (A)", 100)

        back_btn = Button(
            text="Back to Dashboard",
            size_hint_y=None,
            height=65,
            font_size=22
        )
        back_btn.bind(on_press=self.goto_dashboard)
        root.add_widget(back_btn)

        root.add_widget(Label(size_hint_y=1))
        self.add_widget(root)

    def param_row(self, parent, name, default):
        box = BoxLayout(size_hint_y=None, height=60, spacing=10)
        label = Label(text=name, font_size=18)
        ti = TextInput(
            text=str(default),
            multiline=False,
            font_size=24
        )
        box.add_widget(label)
        box.add_widget(ti)
        parent.add_widget(box)
        return ti

    def goto_dashboard(self, instance):
        self.manager.current = "dashboard"


# ================= APP =================
class BMSApp(App):

    def build(self):
        sm = ScreenManager()

        dashboard = DashboardScreen(name="dashboard")
        dashboard.build_ui()

        params = ParamsScreen(name="params")
        params.build_ui()

        sm.add_widget(dashboard)
        sm.add_widget(params)

        return sm


if __name__ == "__main__":
    BMSApp().run()
