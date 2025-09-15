from PyQt5.QtWidgets import (QDialog, QLineEdit, QPushButton, QApplication, 
                             QLabel, QVBoxLayout, QCheckBox, QWidget, QButtonGroup, QRadioButton, QHBoxLayout, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class InputWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Animation Settings")
        self.resize(800, 600)
        self.setup_ui()
        self.setup_style()
        
        # Initialize attributes with default values
        self.animation_duration = None
        self.delay = None
        self.randomness = None
        self.loop_curtain_effect = None
        self.loop_curtain_new_image = None
        self.delay_behaviour = None
        self.random_delay_range = None
        self.curtain_direction = None

    def setup_ui(self):
        layout = QVBoxLayout(self)
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(0, 1)  # Label column
        grid_layout.setColumnStretch(1, 2)  # Input column
        grid_layout.setVerticalSpacing(20)  # Add vertical spacing between rows

        # Create input fields and labels
        self.duration_input = QLineEdit()
        self.delay_input = QLineEdit("0")
        self.randomness_input = QLineEdit("0")
        self.random_delay_range_input = QLineEdit("0")
        self.loop_checkbox = QCheckBox("Enable")
        self.new_image_checkbox = QCheckBox("Enable")
        self.new_image_checkbox.setChecked(True)

        # Add widgets to grid layout with alternating row colors
        labels = [
            "Animation Duration (1-100)",
            "Delay (0-100)",
            "Randomness (0-100)",
            "Random Delay Range (0-100)",
            "Loop curtain effect",
            "Loop curtain on new image",
            "Delay Behaviour",
            "Curtain Direction"
        ]

        inputs = [
            self.duration_input,
            self.delay_input,
            self.randomness_input,
            self.random_delay_range_input,
            self.loop_checkbox,
            self.new_image_checkbox,
            None,  # Placeholder for delay behaviour radio buttons
            None   # Placeholder for curtain direction radio buttons
        ]

        for i, (label, input_widget) in enumerate(zip(labels, inputs)):
            row_widget = QWidget()
            row_widget.setObjectName("evenRow" if i % 2 == 0 else "oddRow")
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(10, 10, 10, 10)  # Add padding
            
            label_widget = QLabel(label)
            label_widget.setObjectName("boldRedLabel")
            row_layout.addWidget(label_widget)
            
            if input_widget:
                row_layout.addWidget(input_widget)
            elif i == 6:  # Delay Behaviour radio buttons
                delay_behaviour_layout = QHBoxLayout()
                self.delay_behaviour_group = QButtonGroup(self)
                default_behaviour = "Hold last position"  # Changed default to Hold last position
                for behaviour in ["Black", "Transparent", "Hold last position"]:
                    radio = QRadioButton(behaviour)
                    delay_behaviour_layout.addWidget(radio)
                    self.delay_behaviour_group.addButton(radio)
                    if behaviour == default_behaviour:
                        radio.setChecked(True)  # Set "Hold last position" radio button as default selected
                row_layout.addLayout(delay_behaviour_layout)
            elif i == 7:  # Curtain Direction radio buttons
                curtain_direction_layout = QHBoxLayout()
                self.curtain_direction_group = QButtonGroup(self)
                default_direction = "Left to Right"  # Set default curtain direction
                for direction in ["Left to Right", "Top to Bottom", "Bottom to Top", "Random Mix"]:
                    radio = QRadioButton(direction)
                    curtain_direction_layout.addWidget(radio)
                    self.curtain_direction_group.addButton(radio)
                    if direction == default_direction:
                        radio.setChecked(True)  # Set "Left to Right" radio button as default selected
                row_layout.addLayout(curtain_direction_layout)
            
            grid_layout.addWidget(row_widget, i, 0, 1, 2)

        self.submit_button = QPushButton("Submit")
        self.submit_button.clicked.connect(self.submit)
        self.submit_button.setFixedHeight(60)  # Set a fixed height for the submit button

        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setObjectName("errorLabel")

        layout.addLayout(grid_layout)
        layout.addSpacing(20)  # Add space before the submit button
        layout.addWidget(self.submit_button)
        layout.addWidget(self.error_label)

    def setup_style(self):
        font = QFont()
        font.setPointSize(14)
        self.setFont(font)

        self.setStyleSheet("""
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 14pt;
            }
            QLineEdit, QCheckBox, QRadioButton {
                background-color: #3b3b3b;
                border: 1px solid #555555;
                padding: 10px;
                border-radius: 5px;
                min-height: 30px;
            }
            QPushButton {
                background-color: #0d47a1;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-size: 16pt;
            }
            QPushButton:hover {
                background-color: #1565c0;
            }
            QLabel#errorLabel {
                color: #ff5252;
                font-weight: bold;
                font-size: 16pt;
                background-color: #461818;
                padding: 10px;
                border-radius: 5px;
            }
            QLabel#boldRedLabel {
                color: #ff5252;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 25px;
                height: 25px;
                background-color: #3b3b3b;
                border: 2px solid #555555;
                border-radius: 5px;
            }
            QCheckBox::indicator:checked {
                background-color: #0d47a1;
                border: 2px solid #0d47a1;
            }
            QRadioButton::indicator {
                width: 25px;
                height: 25px;
                background-color: #3b3b3b;
                border: 2px solid #555555;
                border-radius: 12px;
            }
            QRadioButton::indicator:checked {
                background-color: #0d47a1;
                border: 2px solid #0d47a1;
            }
            QWidget#evenRow {
                background-color: #2b2b2b;
            }
            QWidget#oddRow {
                background-color: #363636;
            }
        """)

        self.setStyleSheet(self.styleSheet() + """
            QLineEdit, QCheckBox {
                min-width: 200px;
            }
            QWidget#evenRow, QWidget#oddRow {
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
    def submit(self):
        try:
            duration = int(self.duration_input.text())
            delay = float(self.delay_input.text())
            randomness = int(self.randomness_input.text())
            random_delay_range = int(self.random_delay_range_input.text())
            
            if (1 <= duration <= 100 and 0 <= delay <= 100 and 
                0 <= randomness <= 100 and 0 <= random_delay_range <= 100):
                self.animation_duration = duration
                self.delay = delay
                self.randomness = randomness
                self.loop_curtain_effect = self.loop_checkbox.isChecked()
                self.loop_curtain_new_image = self.new_image_checkbox.isChecked()
                self.delay_behaviour = self.delay_behaviour_group.checkedButton().text() if self.delay_behaviour_group.checkedButton() else None
                self.curtain_direction = self.curtain_direction_group.checkedButton().text() if self.curtain_direction_group.checkedButton() else None
                self.random_delay_range = random_delay_range
                self.accept()
            else:
                self.error_label.setText("Please enter valid numbers within the specified ranges.")
        except ValueError:
            self.error_label.setText("Please enter valid numbers for all numeric fields.")

def main():
    app = QApplication([])
    
    input_window = InputWindow()
    result = input_window.exec_()
    
    if result == QDialog.Accepted:
        return (input_window.animation_duration, input_window.delay, input_window.randomness,
                input_window.loop_curtain_effect, input_window.loop_curtain_new_image, 
                input_window.delay_behaviour, input_window.random_delay_range, input_window.curtain_direction)
    else:
        print("User closed the window without submitting.")
        return None

if __name__ == '__main__':
    result = main()
    if result:
        (animation_duration, delay, randomness, loop_curtain_effect, 
         loop_curtain_new_image, delay_behaviour, random_delay_range, curtain_direction) = result
        print(f"Animation duration: {animation_duration}")
        print(f"Delay: {delay}")
        print(f"Randomness: {randomness}")
        print(f"Loop curtain effect: {loop_curtain_effect}")
        print(f"Loop curtain on new image: {loop_curtain_new_image}")
        print(f"Delay Behaviour: {delay_behaviour}")
        print(f"Random Delay Range: {random_delay_range}")
        print(f"Curtain Direction: {curtain_direction}")
    else:
        print("No data received from the input window.")