from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QPushButton, QApplication, QLabel, QVBoxLayout, QCheckBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class InputWindow(QDialog):
    def __init__(self):




        
        super().__init__()

        # Set the window size
        self.resize(800, 500)  # Adjust the size as needed

        self.layout = QVBoxLayout()

        self.form_layout = QFormLayout()
        self.lineEdit_duration = QLineEdit()
        self.form_layout.addRow("Animation Duration (1-100)", self.lineEdit_duration)

        self.lineEdit_delay = QLineEdit()
        self.form_layout.addRow("Delay (0-100)", self.lineEdit_delay)

        self.lineEdit_randomness = QLineEdit()
        self.form_layout.addRow("Randomness (0-100)", self.lineEdit_randomness)

        self.checkBox = QCheckBox()
        self.form_layout.addRow("Loop curtain effect?", self.checkBox)

        # Add another checkbox for "Loop curtain on new image"
        self.checkBox_new_image = QCheckBox()
        self.checkBox_new_image.setChecked(True)  # Make the checkbox checked by default
        self.form_layout.addRow("Loop curtain on new image?", self.checkBox_new_image)

        self.checkBox_delay = QCheckBox()
        self.form_layout.addRow("Random delay within x?", self.checkBox_delay)

        self.button = QPushButton("Submit")
        self.button.clicked.connect(self.submit)
        self.form_layout.addRow(self.button)

        # Add the form layout to the main layout
        self.layout.addLayout(self.form_layout)

        # Create a QLabel for error messages and add it to the main layout
        self.error_label = QLabel()
        self.error_label.setAlignment(Qt.AlignCenter)
        font = QFont("Arial", 14)  # Change "Arial" to your desired font and 14 to your desired size
        font.setBold(True)  # Make the font bold
        self.error_label.setStyleSheet("color: red") #change text colour to red
        self.error_label.setFont(font) # Applies the font changes to the error_label
        self.error_label.setWordWrap(True)  # Enable word wrapping
        self.layout.addWidget(self.error_label) # adds error label to the layout

        self.setLayout(self.layout)

        self.animation_duration = None
        self.delay = None
        self.randomness = None
        self.loop_curtain_effect = None
        self.loop_curtain_new_image = None  # Add a new instance variable for the new checkbox
        self.rand_delay = None

    def submit(self):
        try:
            duration_value = int(self.lineEdit_duration.text())
            delay_value = int(self.lineEdit_delay.text())
            randomness_value = int(self.lineEdit_randomness.text())
            if 1 <= duration_value <= 100 and 0 <= delay_value <= 100 and 0 <= randomness_value <= duration_value:
                self.animation_duration = duration_value
                self.delay = delay_value
                self.randomness = randomness_value
                # Get the state of the checkboxes
                self.loop_curtain_effect = self.checkBox.isChecked()
                self.loop_curtain_new_image = self.checkBox_new_image.isChecked()  # Get the state of the new checkbox
                self.rand_delay = self.checkBox_delay.isChecked()
                self.close()
            else:
                self.error_label.setText("Please enter valid numbers. Randomness can't be larger than Animation Duration.")
        except ValueError:
            self.error_label.setText("Please enter valid numbers.")

def main():
    app = QApplication([])

    input_window = InputWindow()
    input_window.exec_()

    animation_duration = input_window.animation_duration
    delay = input_window.delay
    randomness = input_window.randomness
    loop_curtain_effect = input_window.loop_curtain_effect
    loop_curtain_new_image = input_window.loop_curtain_new_image  # Get the state of the new checkbox
    rand_delay = input_window.rand_delay
    print(f"Animation duration: {animation_duration}")
    print(f"Delay: {delay}")
    print(f"Randomness: {randomness}")
    print(f"Loop curtain effect: {loop_curtain_effect}")
    print(f"Loop curtain on new image: {loop_curtain_new_image}")  # Print the state of the new checkbox
    print(f"Generate random delay based off user value: {rand_delay}")

    return animation_duration, delay, randomness, loop_curtain_effect, loop_curtain_new_image, rand_delay  # Return the state of the new checkbox

if __name__ == '__main__':
    main()
