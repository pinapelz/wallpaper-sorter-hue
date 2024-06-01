import os
from PIL import Image, ImageDraw, ImageFont
import argparse
import random

def get_one_image_from_each_folder(base_path):
    images_info = []
    for root, dirs, files in os.walk(base_path):
        image_files = [file for file in files if file.lower().endswith(('png', 'jpg', 'jpeg', 'bmp', 'gif'))]
        if image_files:
            for file in image_files:
                image_path = os.path.join(root, file)
                img = Image.open(image_path)
                if img.width > 1920 and img.height > 1080:
                    folder_name = os.path.basename(root)
                    images_info.append((image_path, folder_name))
                    break
    return images_info

def resize_images(images_info, target_height):
    resized_images_info = []
    for image_path, folder_name in images_info:
        img = Image.open(image_path)
        aspect_ratio = img.width / img.height
        new_width = int(target_height * aspect_ratio)
        resized_img = img.resize((new_width, target_height))
        resized_images_info.append((resized_img, folder_name))
    return resized_images_info

def create_rainbow_image(images_info, output_image_path, target_height):
    resized_images_info = resize_images(images_info, target_height)
    images = [img for img, _ in resized_images_info]
    widths, heights = zip(*(img.size for img in images))

    total_width = sum(widths)
    max_height = max(heights) + 30  # Adding space for text

    rainbow_image = Image.new('RGB', (total_width, max_height), (255, 255, 255))
    draw = ImageDraw.Draw(rainbow_image)
    
    x_offset = 0
    for img, (image_path, folder_name) in zip(images, images_info):
        rainbow_image.paste(img, (x_offset, 0))
        draw.text((x_offset, max_height - 25), folder_name, fill=(0, 0, 0))
        x_offset += img.width

    rainbow_image.save(output_image_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create a rainbow image from sorted images')
    parser.add_argument('-i', '--input', help='Input directory containing hue folders', required=True)
    parser.add_argument('-o', '--output', help='Output image path', required=True)
    parser.add_argument('-t', '--target_height', type=int, default=200, help='Target height for resized images')
    args = parser.parse_args()

    images_info = get_one_image_from_each_folder(args.input)
    create_rainbow_image(images_info, args.output, args.target_height)
