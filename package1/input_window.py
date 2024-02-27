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
        self.lineEdit = QLineEdit()
        self.form_layout.addRow("Animation Duration (1-100)", self.lineEdit)

        self.checkBox = QCheckBox()
        self.form_layout.addRow("Loop curtain effect?", self.checkBox)

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
        self.layout.addWidget(self.error_label) # adds error label to the layout

        self.setLayout(self.layout)

        self.animation_duration = None
        self.loop_curtain_effect = None

    def submit(self):
        try:
            value = int(self.lineEdit.text())
            if 1 <= value <= 100:
                self.animation_duration = value
                # Get the state of the checkbox
                self.loop_curtain_effect = self.checkBox.isChecked()
                self.close()
            else:
                self.error_label.setText("Please enter a number between 1 and 100.")
        except ValueError:
            self.error_label.setText("Please enter a valid number.")

def main():
    app = QApplication([])

    input_window = InputWindow()
    input_window.exec_()

    animation_duration = input_window.animation_duration
    loop_curtain_effect = input_window.loop_curtain_effect
    print(f"Animation duration: {animation_duration}")
    print(f"Loop curtain effect: {loop_curtain_effect}")

    return animation_duration, loop_curtain_effect

if __name__ == '__main__':
    main()