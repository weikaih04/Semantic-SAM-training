import os
import shutil
import argparse

def mix_datasets(folder1, folder2, output_folder, num_from_folder1, num_from_folder2):
    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Get ordered pairs from both folders
    def get_pairs(folder):
        images = sorted([f for f in os.listdir(folder) if f.endswith('.jpg')])
        jsons = sorted([f for f in os.listdir(folder) if f.endswith('.json')])
        return list(zip(images, jsons))

    pairs1 = get_pairs(folder1)[:num_from_folder1]
    pairs2 = get_pairs(folder2)[:num_from_folder2]

    # Combine the selected pairs in original order
    selected_pairs = pairs1 + pairs2

    # Copy selected pairs to the output folder with sequential naming
    for idx, (img_file, json_file) in enumerate(selected_pairs):
        src_folder = folder1 if img_file in dict(pairs1) else folder2
        shutil.copy(os.path.join(src_folder, img_file), os.path.join(output_folder, f"{idx}.jpg"))
        shutil.copy(os.path.join(src_folder, json_file), os.path.join(output_folder, f"{idx}.json"))

    print(f"Dataset mixed successfully in {output_folder}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mix datasets from two folders into one while maintaining original order.")
    parser.add_argument("--folder1", type=str, help="Path to the first dataset folder")
    parser.add_argument("--folder2", type=str, help="Path to the second dataset folder")
    parser.add_argument("--num_from_folder1", type=int, help="Number of image-JSON pairs to take from the first folder")
    parser.add_argument("--num_from_folder2", type=int, help="Number of image-JSON pairs to take from the second folder")
    parser.add_argument("--output_folder", type=str, help="Path to the output dataset folder")


    args = parser.parse_args()
    
    mix_datasets(args.folder1, args.folder2, args.output_folder, args.num_from_folder1, args.num_from_folder2)