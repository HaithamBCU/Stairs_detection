import pyrealsense2 as rs
import csv
import cv2
import numpy as np
import time

def overlay_depth_on_image(color_image, depth_image_rgb):


    stacked_image = np.hstack((color_image, depth_image_rgb))
    
    return stacked_image

def get_colored_depth(frameset):
    colorizer = rs.colorizer()
    # Create alignment primitive with color as its target stream:
    align = rs.align(rs.stream.color)
    frameset = align.process(frameset)

    # Update color and depth frames:
    aligned_depth_frame = frameset.get_depth_frame()
    colorized_depth = np.asanyarray(colorizer.colorize(aligned_depth_frame).get_data())
    return colorized_depth


def extract_depth_and_color(save_path, num_frames):
    # Create a pipeline
    pipeline = rs.pipeline()
    
    # Create a configuration for the pipeline
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    
    # Start the pipeline
    pipeline.start(config)
    
    frame_count = 0

    # Skip 20 first frames to give the Auto-Exposure time to adjust
    skip_frames = 80
    for i in range(skip_frames):
        frames = pipeline.wait_for_frames()
    
    try:
        # Create CSV file for depth data
        depth_csv_file = open(f"/home/rocker123uk/depth2/depth_data.csv", "w", newline='')
        depth_csv_writer = csv.writer(depth_csv_file)
        
        while frame_count < num_frames:
            # Wait for frames
            frames = pipeline.wait_for_frames()
            
            # Get depth and color frames
            depth_frame = frames.get_depth_frame()
            #time.sleep(1)
            color_frame = frames.get_color_frame()
            #time.sleep(1)
            if not depth_frame or not color_frame:
                continue


            # colorizer = rs.colorizer()
            # colorized_depth = np.array()
            
            # Create alignment primitive with color as its target stream:
            align = rs.align(rs.stream.color)
            frameset = align.process(frames)

            # Update color and depth frames:
            aligned_depth_frame = np.asanyarray(frameset.get_depth_frame().get_data())
            #time.sleep(1)
            # Save depth data to CSV file
            depth_csv_writer.writerows(aligned_depth_frame)
            #time.sleep(1)
            # Convert color frame to a numpy array
            color_image = np.asanyarray(color_frame.get_data())
            #time.sleep(1)

            # creating depth image
            depth_image = get_colored_depth(frameset=frames)

            # Overlay depth data on the color image
            stacked_image = overlay_depth_on_image(color_image=color_image, depth_image_rgb=depth_image)
            #time.sleep(1)

            #show distance at point
            #point = (364, 420) # (x=horizontal,y=vertical)
            #cv2.circle(color_image, point, 4, (0,0,255))
            #distance = aligned_depth_frame[point[1], point[0]]
            #print(distance)

            
            
            # Save RGB image
            cv2.imwrite(f"/home/rocker123uk/depth2/color_image_{frame_count}.jpg", color_image)
            cv2.imwrite(f"/home/rocker123uk/depth2/depth_image_{frame_count}.jpg", depth_image)

             # Save the stacked image
            cv2.imwrite(f"/home/rocker123uk/depth2/stacked_image_{frame_count}.jpg", stacked_image)
            cv2.imshow("colour_image", color_image)
            cv2.imshow("depth_image", depth_image)
            cv2.waitKey(0)
            frame_count += 1
    
    finally:
        # Stop the pipeline
        pipeline.stop()
        
        # Close the CSV file
        depth_csv_file.close()

# Define the save path for depth data and RGB images
save_path = 'output'

# Define the number of frames to capture
num_frames = 1

# Run the function to start capturing depth and color frames and save the data
extract_depth_and_color(save_path, num_frames)

