import pyautogui
from PIL import Image, ImageDraw

def overlay_image():
    # Get screen size
    screen_width, screen_height = pyautogui.size()

    # Create a blank black image
    overlay_image = Image.new('RGB', (screen_width, screen_height), color='black')

    # Save the image
    overlay_image_path = "overlay_image.png"
    overlay_image.save(overlay_image_path)

    # Display the image overlay
    pyautogui.alert(text="Image overlay has been created. Press OK to exit.")

if __name__ == "__main__":
    overlay_image("blank")
