import os
import shutil
from PIL import Image
import argparse
import time
Image.MAX_IMAGE_PIXELS = 9999999999999

def write_debug_message(message):
    with open('debug.log', 'a') as f:
        print(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {message}')
        f.write(f'{time.strftime("%Y-%m-%d %H:%M:%S")} - {message}\n')

def calculate_average_color(image_path):
    image = Image.open(image_path)
    image = image.resize((1, 1))
    average_color = image.getpixel((0, 0))
    return average_color

def rgb_to_hue(r, g, b):
    import colorsys
    hue, _, _ = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
    return int(hue * 360)

def group_hue(hue, num_groups=10):
    group_size = 360 // num_groups
    return (hue // group_size) * group_size

def create_hue_folder(grouped_hue, base_output_path):
    write_debug_message(f'Creating folder for hue group {grouped_hue}')
    hue_folder = os.path.join(base_output_path, f'hue_{grouped_hue}-{grouped_hue + 36}')
    if not os.path.exists(hue_folder):
        os.makedirs(hue_folder)
    write_debug_message(f'Folder created: {hue_folder}')
    return hue_folder

def sort_images_by_hue(base_input_path, base_output_path):
    hue_image_map = {}
    
    for root, _, files in os.walk(base_input_path):
        write_debug_message(f'Processing folder: {root}')
        for file in files:
            write_debug_message(f'Found file: {file}')
            if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif')):
                file_path = os.path.join(root, file)
                avg_color = calculate_average_color(file_path)
                try:
                    if len(avg_color) == 4:  # Remove alpha channel
                        avg_color = avg_color[:3]
                    hue = rgb_to_hue(*avg_color)
                    grouped_hue = group_hue(hue)
                    if grouped_hue not in hue_image_map:
                        hue_image_map[grouped_hue] = []
                    hue_image_map[grouped_hue].append(file_path)
                except Exception as e:
                    write_debug_message(f'Error processing file {file_path}: {e}')
    
    for grouped_hue, image_paths in hue_image_map.items():
        hue_folder = create_hue_folder(grouped_hue, base_output_path)
        if len(image_paths) > 50:
            write_debug_message(f'Folder {hue_folder} has more than 50 images, creating subfolders')
            sub_hue_image_map = {}
            for image_path in image_paths:
                avg_color = calculate_average_color(image_path)
                if len(avg_color) > 3:
                    avg_color = avg_color[:3]
                hue = rgb_to_hue(*avg_color)
                sub_grouped_hue = group_hue(hue, num_groups=36)  # 36 subgroups within the main hue group
                sub_hue_folder = os.path.join(hue_folder, f'subhue_{sub_grouped_hue}-{sub_grouped_hue + 10}')
                if not os.path.exists(sub_hue_folder):
                    os.makedirs(sub_hue_folder)
                shutil.copy(image_path, os.path.join(sub_hue_folder, os.path.basename(image_path)))
        else:
            for image_path in image_paths:
                shutil.copy(image_path, os.path.join(hue_folder, os.path.basename(image_path)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sort images by hue')
    parser.add_argument('-i', '--input', help='Input directory', required=True)
    parser.add_argument('-o', '--output', help='Output directory', required=True)
    args = parser.parse_args()
    sort_images_by_hue(base_input_path=args.input, base_output_path=args.output)
