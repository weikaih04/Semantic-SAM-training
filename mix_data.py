import os
import shutil
import argparse


def mix_datasets(folder1, folder2, output_folder, num_from_folder1, num_from_folder2):
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Get ordered pairs from a folder
    def get_pairs(folder):
        images = sorted([f for f in os.listdir(folder) if f.endswith(('.jpg', '.png'))])
        jsons = sorted([f for f in os.listdir(folder) if f.endswith('.json')])
        
        # Create lookup dictionaries for matching
        image_dict = {os.path.splitext(f.replace('_relight', ''))[0]: f for f in images}
        json_dict = {os.path.splitext(f)[0]: f for f in jsons}

        # Find matching pairs while preserving original filenames
        pairs = [(image_dict[key], json_dict[key]) for key in json_dict if key in image_dict]
        return pairs

    # Get all matching pairs from both folders
    all_pairs1 = get_pairs(folder1)
    all_pairs2 = get_pairs(folder2)
    
    print(f"Folder1 contains {len(all_pairs1)} image-JSON pairs.")
    print(f"Folder2 contains {len(all_pairs2)} image-JSON pairs.")

    # Select the desired number of pairs from each folder
    pairs1 = all_pairs1[:num_from_folder1]
    pairs2 = all_pairs2[:num_from_folder2]
    selected_pairs = pairs1 + pairs2
    print(f"Total pairs selected for the output folder: {len(selected_pairs)}.")

    # Copy selected pairs to the output folder with sequential naming
    for idx, (img_file, json_file) in enumerate(selected_pairs):
        src_folder = folder1 if img_file in dict(pairs1) else folder2
        _, ext = os.path.splitext(img_file)  # Preserve original extension
        shutil.copy(os.path.join(src_folder, img_file), os.path.join(output_folder, f"{idx}{ext}"))
        shutil.copy(os.path.join(src_folder, json_file), os.path.join(output_folder, f"{idx}.json"))

    # After copying, count the files in the output folder
    output_files = os.listdir(output_folder)
    image_count = len([f for f in output_files if f.endswith(('.jpg', '.png'))])
    json_count = len([f for f in output_files if f.endswith('.json')])
    print(f"Output folder now contains {image_count} image files and {json_count} JSON files.")
    print(f"Dataset mixed successfully in {output_folder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mix datasets from two folders into one while maintaining original order.")
    parser.add_argument("--folder1", type=str, required=True, help="Path to the first dataset folder")
    parser.add_argument("--folder2", type=str, required=True, help="Path to the second dataset folder")
    parser.add_argument("--num_from_folder1", type=int, required=True, help="Number of image-JSON pairs to take from the first folder")
    parser.add_argument("--num_from_folder2", type=int, required=True, help="Number of image-JSON pairs to take from the second folder")
    parser.add_argument("--output_folder", type=str, required=True, help="Path to the output dataset folder")

    args = parser.parse_args()
    
    mix_datasets(args.folder1, args.folder2, args.output_folder, args.num_from_folder1, args.num_from_folder2)