from .create_image import create_blank_image 
import tkinter as tk
from PIL import Image, ImageTk

create_blank_image()

def kill_switch(event): # Defines the kill switch event, which will kill the app once called upon
    root.quit()

# Create a new Tk root widget, which is a window with a title bar and other decoration provided by the window manager.
# This must be created before any other widgets.
root = tk.Tk()

# Set the root widget to be fullscreen.
# The '-fullscreen' option is a boolean option, and True sets the widget to be displayed in fullscreen.
root.attributes('-fullscreen', True)

# Open the image file.
# The Image module contains functions to create and manipulate images. Image.open() opens and identifies the given image file.
image = Image.open("package1/overlay_image.png")

# Convert the image object to a PhotoImage object, which can be used to display the image in a Label widget.
# The PhotoImage class is used to display images in labels, buttons, canvases, and text widgets.
photo = ImageTk.PhotoImage(image)

# Create a new Label widget with the root widget as its parent and the PhotoImage object as the image to be displayed.
# A Label widget displays text or images.
label = tk.Label(root, image=photo)

# Add the label to the window.
# The pack() method is one of the three geometry managers in tkinter, it organizes widgets in blocks before placing them in the parent widget.
label.pack()

label.bind("<Button-2>", kill_switch) # Binds the kill switch function to the middle mouse button

# Start the tkinter event loop.
# The mainloop() method is a loop used to catch events. It won't return until the root widget is destroyed.
root.mainloop()