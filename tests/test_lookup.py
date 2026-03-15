
import sys
import os
import logging

# Add the current directory to sys.path to allow importing from actions
sys.path.append(os.getcwd())

from actions.csv_lookup import find_disease_smart, get_info_from_csv, find_best_match
from actions.config import disease_data

logging.basicConfig(level=logging.INFO)

def test_matching():
    print(f"Loaded CSV rows: {len(disease_data)}")
    
    test_labels = [
        "Peach___Bacterial_spot",
        "Bacterial spot",
        "Tomato Bacterial spot"
    ]
    
    for label in test_labels:
        print(f"\n--- Testing Label: {label} ---")
        parts = label.split("___")
        img_crop = parts[0].replace("_", " ") if len(parts) > 1 else None
        img_label = parts[-1].replace("_", " ")
        full_label = f"{img_crop} {img_label}" if img_crop else img_label
        
        disease, crop = find_disease_smart(full_label, detected_crop=img_crop)
        print(f"Result -> Disease: {disease}, Crop: {crop}")
        
        if disease:
            # Test getting info
            treatment = get_info_from_csv(disease, "treatment", crop=crop)
            print(f"Treatment found: {treatment[:100]}...")
        else:
            print("No disease found.")

if __name__ == "__main__":
    test_matching()
