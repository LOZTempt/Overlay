import pyautogui
import time

target_monitor = 1  # Example: Monitor number 1 (primary monitor is typically 0)
screen_info = pyautogui.getMonitors()[target_monitor]
target_resolution = (screen_info.width, screen_info.height)
target_position = (screen_info.left, screen_info.top)

print(screen_info, target_resolution, target_position)

# Define the region for applying the curtain effect
curtain_region = (0, 0, 3840, 1600)  # Entire primary monitor

# Define the region for monitoring changes
monitor_region = (0, 0, 400, 100)  # Top-left corner

# Define the color of the text you want to detect (in RGB format)
target_color = (0, 0, 255)  # Blue color
tolerance = 30  # Tolerance for color detection (adjust as needed)

# Duration of the curtain effect animation (in seconds)
animation_duration = 9

def capture_screen(region):
    screenshot = pyautogui.screenshot(region=region)  # Capture only the specified region
    return screenshot

def detect_text_change(screen):
    # Check if any pixel in the region is similar to the target color
    for x in range(screen.width):
        for y in range(screen.height):
            pixel_color = screen.getpixel((x, y))
            if color_distance(pixel_color, target_color) <= tolerance:
                return True
    return False

def apply_curtain_effect(screen):
    for i in range(101):
        # Calculate the alpha value for the curtain effect
        alpha = int(255 * (1 - i / 100))
        
        # Create a black image with the same size as the screen
        curtain_image = pyautogui.Image.new('RGBA', screen.size, (0, 0, 0, alpha))
        
        # Paste the curtain image onto the screen
        screen.paste(curtain_image, (0, 0))
        
        # Update the screen
        pyautogui.display(screen)
        
        # Sleep for a short duration to control the animation speed
        time.sleep(animation_duration / 100)

def color_distance(color1, color2):
    # Calculate the Euclidean distance between two colors
    return sum((c1 - c2) ** 2 for c1, c2 in zip(color1, color2)) ** 0.5

while True:
    curtain_screen = capture_screen(curtain_region)
    monitor_screen = capture_screen(monitor_region)
    
    if detect_text_change(monitor_screen):
        apply_curtain_effect(curtain_screen)
    
    time.sleep(15)  # Check for changes every 15 seconds
