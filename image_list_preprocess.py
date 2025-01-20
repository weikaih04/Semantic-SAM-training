import torch
import os
import argparse

def preprocess_images(base_path, default_path, output_file):
    """
    Preprocess images in the specified directory, saving metadata about images and annotations.
    
    Args:
        base_path (str): The base path where the images and annotations are located.
        default_path (str): The relative or absolute path to be included in the metadata.
        output_file (str): The output file to save the processed metadata.
    """
    save_path = os.path.join(base_path, output_file)

    # Open file for saving
    with open(save_path, 'wb') as f_save:
        data_list = []
        files = os.listdir(base_path)

        for f in files:
            if f.endswith(".jpg") or f.endswith(".png"):
                image_list.append({
                    "img_name": os.path.join(default_path, f),
                    "ann_name": os.path.join(default_path, f.replace('.jpg', '.json').replace('.png', '.json').replace('_relight', ''))
                })
        
        # Save the data
        torch.save(data_list, f_save)
    print(f"Metadata saved to {save_path}")

if __name__ == "__main__":
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Preprocess images to generate metadata for training.")
    parser.add_argument("--base_path", type=str, required=True, help="Base directory containing images and annotations.")
    parser.add_argument("--default_path", type=str, required=True, help="Path to be used in the metadata for image and annotation names.")
    parser.add_argument("--output_file", type=str, default="image_list.da", help="Name of the output file to save the metadata.")

    # Parse arguments
    args = parser.parse_args()

    # Call the preprocessing function with parsed arguments
    preprocess_images(args.base_path, args.default_path, args.output_file)