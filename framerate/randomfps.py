import os
import random, time

# TODO: Make it more modular, so make it so that maybe a window opens where you can select a directory and maybe an option to override or add new framerates

def process_videos(input_dirs, output_dir):
    # d = 0
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize an empty list to store frame rates
    frame_rates = []

    # Iterate over input directories
    for input_dir in input_dirs:
        # Iterate over files in the input directory
        for root, _, files in os.walk(input_dir):
            for file in files:
                if file.endswith('.mp4'):
                    input_file = os.path.join(root, file)
                    output_file = os.path.join(output_dir, file)
                    # Generate a random frame rate between 10 and 30 frames per second
                    fps_values = [.1, .2, .25, .33, .5, .67, .83, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 6, 7, 8, 9]
                    target_frame_rate = random.choice(fps_values)
                    # Execute FFmpeg command to change frame rate
                    os.system(f'ffmpeg -i "{input_file}" -r {target_frame_rate} -c:a copy "{output_file}"')
                    # Log the randomly generated frame rate
                    frame_rates.append(target_frame_rate)

                    # Convert output file to 30 fps
                    output_high_fps_file = os.path.join(output_dir, f"{target_frame_rate}_fps_{file}")
                    os.system(f'ffmpeg -i "{output_file}" -r 30 "{output_high_fps_file}"')

                    os.remove(output_file)

                    print("\n\n",target_frame_rate,"\n\n")
                    time.sleep(3)
        #             d += 1
        #             if d > 5:
        #                 break
        #     if d > 5:
        #         break
        # if d > 5:
        #     break

    # Initialize an empty dictionary to store the count of each frame rate
    frame_rate_counts = {}

    # Count the occurrences of each frame rate in the frame_rates list
    for frame_rate in frame_rates:
        if frame_rate in frame_rate_counts:
            frame_rate_counts[frame_rate] += 1
        else:
            frame_rate_counts[frame_rate] = 1

    # Display the count of each frame rate
    for frame_rate, count in frame_rate_counts.items():
        print(f"Frame rate {frame_rate}: {count} times")


# Specify input and output directories
input_directory = ['D:\\Test\\1_1folders']
output_directory = 'D:\\Test\\1_1folders\\fpsOutput'

# Call the function to process videos
process_videos(input_directory, output_directory)


