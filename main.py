from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.slider import Slider
import random
import os


class BMSApp(App):
    def build(self):
        # Main layout is BoxLayout to hold title and two sections of grid
        main_layout = BoxLayout(orientation='vertical', padding=5, spacing=10)

        # Create the top layout to include the menu button and title
        top_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=10)

        # Image Path
        image_path = "images/DCS.png"

        # Check if the image exists
        if not os.path.exists(image_path):
            print(f"Image not found at: {image_path}")
            image_path = "images/default_logo.png"  # Provide a default logo if image is missing

        # Add logo image (the logo will be placed at the left)
        logo_image = Image(source=image_path, size_hint=(None, None), size=(75, 75))  # Adjusted size
        top_layout.add_widget(logo_image)

        # Menu button that will open the popup
        menu_button = Button(text='Menu', size_hint=(None, None), size=(100, 75), font_size=25,
                             on_press=self.open_menu)
        top_layout.add_widget(menu_button)

        # Title at the top of the screen (centered)
        title = Label(text='5S1P-BMS', size_hint=(1, 0.1), font_size=40, bold=True)
        top_layout.add_widget(title)

        main_layout.add_widget(top_layout)

        # Add a BoxLayout with a fixed height to add space between the title and voltage section
        main_layout.add_widget(BoxLayout(size_hint_y=None, height=25))  # Adjusted height for gap

        # Create additional sections for voltage, current, and temperature
        self.current_label = Label(text='Voltage (V):', font_size=20, bold=True)
        self.current_value = TextInput(
            text=str(round(random.uniform(57, 60), 2)),  # Initial voltage value between 57 and 60
            multiline=False,
            readonly=True,  # Make the TextInput read-only (no user input)
            font_size=35,
            halign='center',
            font_name='Roboto-Bold',
        )

        self.voltage_label = Label(text='Current (A):', font_size=20, bold=True)
        self.voltage_value = TextInput(
            text=str(round(random.uniform(0.0, 10.0), 2)),
            multiline=False,
            readonly=True,  # Make the TextInput read-only (no user input)
            font_size=35,
            halign='center',
            font_name='Roboto-Bold',
        )

        self.temperature_label = Label(text='Temperature (°C):', font_size=20, bold=True)
        self.temperature_value = TextInput(
            text=str(round(random.uniform(20.0, 40.0), 2)),
            multiline=False,
            readonly=True,  # Make the TextInput read-only (no user input)
            font_size=35,
            halign='center',
            font_name='Roboto-Bold',
        )

        # Add these new labels and TextInputs to the main layout
        current_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=25)
        current_layout.add_widget(self.current_label)
        current_layout.add_widget(self.current_value)
        main_layout.add_widget(current_layout)

        voltage_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=25)
        voltage_layout.add_widget(self.voltage_label)
        voltage_layout.add_widget(self.voltage_value)
        main_layout.add_widget(voltage_layout)

        temperature_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=25)
        temperature_layout.add_widget(self.temperature_label)
        temperature_layout.add_widget(self.temperature_value)
        main_layout.add_widget(temperature_layout)

        # SOC Label and TextInput
        self.soc_label = Label(text='State of Charge (SOC):', font_size=20, bold=True)
        self.soc_value = TextInput(
            text=str(round(random.uniform(0.0, 100.0), 2)) + '%',  # Initial SOC value
            multiline=False,
            readonly=True,  # Make the TextInput read-only (no user input)
            font_size=35,
            halign='center',
            font_name='Roboto-Bold',
        )
        soc_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50, spacing=25)
        soc_layout.add_widget(self.soc_label)
        soc_layout.add_widget(self.soc_value)
        main_layout.add_widget(soc_layout)

        # SOC Progress Bar (representing the charge level)
        self.soc_progress_bar = ProgressBar(
            value=random.uniform(0, 100),  # Initial SOC value
            max=100,
            size_hint=(1, 0.05),
            height=40,  # Reduced height for the progress bar
        )
        main_layout.add_widget(self.soc_progress_bar)

        # Create the two sections (7 cells on each side)
        # Use a horizontal layout to position the two grid sections
        grid_layout = BoxLayout(size_hint=(1, 0.7), spacing=10)

        # Create the left section with 7 numerical displays
        self.left_grid = GridLayout(cols=1, spacing=10, size_hint=(0.4, 1),
                                    padding=5)  # Reduced grid width and padding
        self.left_text_inputs = []
        for i in range(1, 9):  # Starting serial number from 1 for 7 cells
            # Generate random float values between 3.567 and 3.694
            random_value = round(random.uniform(3.567, 3.694), 3)

            # Create a horizontal BoxLayout for serial number and text input side by side
            cell_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=25)

            # Create a label for the serial number
            serial_label = Label(text=f"Cell {i}", font_size=20, size_hint=(0.2, 1), bold=True)
            cell_layout.add_widget(serial_label)

            # For each cell, create a TextInput for numerical value (read-only)
            text_input = TextInput(
                text=str(random_value),
                multiline=False,
                readonly=True,  # Make the TextInput read-only (no user input)
                font_size=35,  # Reduced font size
                halign='center',  # Center-align the text inside the TextInput
                font_name='Roboto-Bold',  # Use a font that supports bold
            )
            self.left_text_inputs.append(text_input)
            cell_layout.add_widget(text_input)

            # Add the cell layout to the left grid
            self.left_grid.add_widget(cell_layout)

        # Create the right section with 7 numerical displays
        self.right_grid = GridLayout(cols=1, spacing=10, size_hint=(0.4, 1),
                                     padding=5)  # Reduced grid width and padding
        self.right_text_inputs = []
        for i in range(9, 17):  # Serial numbers continue from 8 to 14
            # Generate random float values between 3.567 and 3.694
            random_value = round(random.uniform(3.567, 3.694), 3)

            # Create a horizontal BoxLayout for serial number and text input side by side
            cell_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=60, spacing=25)

            # Create a label for the serial number
            serial_label = Label(text=f"Cell {i}", font_size=20, size_hint=(0.2, 1), bold=True)
            cell_layout.add_widget(serial_label)

            # For each cell, create a TextInput for numerical value (read-only)
            text_input = TextInput(
                text=str(random_value),
                multiline=False,
                readonly=True,  # Make the TextInput read-only (no user input)
                font_size=35,  # Reduced font size
                halign='center',  # Center-align the text inside the TextInput
                font_name='Roboto-Bold',  # Use a font that supports bold
            )
            self.right_text_inputs.append(text_input)
            cell_layout.add_widget(text_input)

            # Add the cell layout to the right grid
            self.right_grid.add_widget(cell_layout)

        # Add both grids to the main horizontal box layout
        grid_layout.add_widget(self.left_grid)
        grid_layout.add_widget(self.right_grid)

        # Add the grid_layout to the main layout
        main_layout.add_widget(grid_layout)

        # Schedule the update of random values every 1 second
        Clock.schedule_interval(self.update_values, 1)

        return main_layout

    def update_values(self, dt):
        # Update random values every second
        self.current_value.text = str(round(random.uniform(57, 60), 2))  # Voltage range between 57 and 60
        self.voltage_value.text = str(round(random.uniform(0.0, 10.0), 2))
        self.temperature_value.text = str(round(random.uniform(20.0, 40.0), 2))

        # Update State of Charge (SOC)
        new_soc = round(random.uniform(0.0, 100.0), 2)
        self.soc_value.text = str(new_soc) + '%'
        self.soc_progress_bar.value = new_soc

        # Update cell values every second
        for i, text_input in enumerate(self.left_text_inputs):
            text_input.text = str(round(random.uniform(3.567, 3.694), 3))

        for i, text_input in enumerate(self.right_text_inputs):
            text_input.text = str(round(random.uniform(3.567, 3.694), 3))

    def open_menu(self, instance):
        # Create the menu layout with buttons
        menu_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Button for opening the Dashboard
        dashboard_button = Button(text="Dashboard", size_hint=(1, 0.5), height=25, on_press=self.show_dashboard)
        menu_layout.add_widget(dashboard_button)

        # Button for setting parameters
        set_parameters_button = Button(text="Set Parameters", size_hint=(1, 0.5), height=25,
                                       on_press=self.show_set_parameters)
        menu_layout.add_widget(set_parameters_button)

        # Close Button to close the menu popup
        close_button = Button(text="Close", size_hint=(1, 0.5), height=25, on_press=self.close_menu)
        menu_layout.add_widget(close_button)

        # Create the popup with the menu layout
        self.popup = Popup(title="Menu", content=menu_layout, size_hint=(None, None), size=(500, 750))
        self.popup.open()

    def close_menu(self, instance):
        # Close the popup
        self.popup.dismiss()

    def show_dashboard(self, instance):
        # Handle dashboard button press (you can implement your dashboard logic here)
        print("Dashboard clicked")

    def show_set_parameters(self, instance):
        # Create the layout for setting parameters
        parameter_layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        # Create a horizontal layout for each parameter (label + input field)
        def create_param_layout(label_text, input_field):
            param_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=25, spacing=5)
            label = Label(text=label_text, font_size=15, size_hint=(0.3, 0.5), bold=True)  # Reduced label width
            param_layout.add_widget(label)
            input_field.size_hint_x = 0.5  # Reduced width for input field (adjust as needed)
            param_layout.add_widget(input_field)
            return param_layout

        # Add input fields for setting parameters
        self.cell_no_input = TextInput(text="1", font_size=15, hint_text="Cell No", multiline=False)
        self.nominal_capacity_input = TextInput(text="100.0", font_size=15, hint_text="Nominal Capacity (Ah)",
                                                multiline=False)
        self.over_voltage_input = TextInput(text="4.2", font_size=15, hint_text="Over Voltage (V)", multiline=False)
        self.over_voltage_release_input = TextInput(text="4.0", font_size=15, hint_text="Over Voltage Release (V)",
                                                    multiline=False)
        self.under_voltage_input = TextInput(text="3.0", font_size=15, hint_text="Under Voltage (V)", multiline=False)
        self.under_voltage_release_input = TextInput(text="3.2", font_size=15, hint_text="Under Voltage Release (V)",
                                                     multiline=False)
        self.over_temperature_input = TextInput(text="60.0", font_size=15, hint_text="Over Temperature (°C)",
                                                multiline=False)
        self.over_temperature_release_input = TextInput(text="50.0", font_size=15,
                                                        hint_text="Over Temperature Release (°C)", multiline=False)
        self.under_temperature_input = TextInput(text="0.0", font_size=15, hint_text="Under Temperature (°C)",
                                                 multiline=False)
        self.under_temperature_release_input = TextInput(text="10.0", font_size=15,
                                                         hint_text="Under Temperature Release (°C)", multiline=False)

        parameter_layout.add_widget(create_param_layout("Cell No:", self.cell_no_input))
        parameter_layout.add_widget(create_param_layout("Nominal Capacity (Ah):", self.nominal_capacity_input))
        parameter_layout.add_widget(create_param_layout("Over Voltage (V):", self.over_voltage_input))
        parameter_layout.add_widget(create_param_layout("Over Voltage Release (V):", self.over_voltage_release_input))
        parameter_layout.add_widget(create_param_layout("Under Voltage (V):", self.under_voltage_input))
        parameter_layout.add_widget(create_param_layout("Under Voltage Release (V):", self.under_voltage_release_input))
        parameter_layout.add_widget(create_param_layout("Over Temperature (°C):", self.over_temperature_input))
        parameter_layout.add_widget(
            create_param_layout("Over Temperature Release (°C):", self.over_temperature_release_input))
        parameter_layout.add_widget(create_param_layout("Under Temperature (°C):", self.under_temperature_input))
        parameter_layout.add_widget(
            create_param_layout("Under Temperature Release (°C):", self.under_temperature_release_input))

        # Save and Cancel buttons
        save_button = Button(text="Save", size_hint=(1, 0.2), on_press=self.save_parameters)
        parameter_layout.add_widget(save_button)

        cancel_button = Button(text="Cancel", size_hint=(1, 0.2), on_press=self.close_menu)
        parameter_layout.add_widget(cancel_button)

        # Create the popup for setting parameters
        self.parameter_popup = Popup(title="Set Parameters", content=parameter_layout, size_hint=(None, None),
                                     size=(500, 750))
        self.parameter_popup.open()

    def save_parameters(self, instance):
        # Logic to save the parameters (you can collect the values from the input fields)
        print("Parameters Saved")
        self.parameter_popup.dismiss()


if __name__ == "__main__":
    BMSApp().run()
