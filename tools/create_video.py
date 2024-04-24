import cv2
import os
import re

def create_video(image_folder, output_video, fps=2):  # Lower fps for slower video
    images = []
    
    # Load all images (PNG and JPEG) from the folder and sort them based on numerical index
    image_files = [filename for filename in os.listdir(image_folder) if filename.endswith('.png') or filename.endswith('.jpg')]
    sorted_filenames = sorted(image_files, key=lambda x: int(re.search(r'\d+', x).group()))
    print(sorted_filenames)
    for filename in sorted_filenames:
        images.append(cv2.imread(os.path.join(image_folder, filename)))
    
    # Determine video dimensions from the first image
    height, width, _ = images[0].shape
    
    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # You can change the codec here if needed
    out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))
    
    # Write images to video
    for img in images:
        out.write(img)
    
    # Release video writer
    out.release()




# Example usage:
image_folder = "/home/bert/github/5G_CARS_1/Computer_vision/mmdet_outputs/vis"
image_folder = "/home/bert/github/5G_CARS_1/Computer_vision/mmseg_outputs/vis"
image_folder = "/home/bert/github/5G_CARS_1/Computer_vision/yolo_outputs"
output_video = "yolo.mp4"
create_video(image_folder, output_video)

