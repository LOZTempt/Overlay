import tkinter as tk

def kill_switch(event): 
    root.quit()

root = tk.Tk()

# Set the root widget to be fullscreen.
root.attributes('-fullscreen', True)

# Remove window decorations to make it borderless.
root.overrideredirect(True)

label = tk.Label(root, bg="black")  # Create a black Label widget to serve as the overlay.
label.pack(fill=tk.BOTH, expand=True)  # Pack the label to fill the entire window.

label.bind("<Button-2>", kill_switch)

root.mainloop()
