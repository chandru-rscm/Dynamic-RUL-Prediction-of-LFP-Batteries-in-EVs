import os
import shutil
import zipfile
from PIL import Image

def crop_and_sequence_figures():
    print("=== CROPPING TITLES & SEQUENCING FIGURES 1 TO 9 ===")
    
    src_dir = r"D:\chandru downloads\figures and tables rul"
    
    # Mapping: (output_filename, source_filename_in_src_dir, top_crop_pixels, description)
    # Order matches exactly with Dynamic Remaining Useful Life (RUL) Prediction... (1).docx
    figures_sequence = [
        ("1.png", "02_flow_architecture.png", 0, "Figure 1: Training and validation flow architecture"),
        ("2.png", "04_capacity_fade_curves.png", 140, "Figure 2: Capacity fade curves for the test set battery"),
        ("3.png", "01_feature_importance.png", 140, "Figure 3: LightGBM feature importance ranking"),
        ("4.png", "03_polling_blind_spot.png", 130, "Figure 4: Comparison of diagnostic responsiveness (polling blind spot)"),
        ("5.png", "07_pole_zero_migration_map.png", 110, "Figure 5: Complex s-plane pole-zero migration map"),
        ("6.png", "05_true_vs_predicted_rul.png", 110, "Figure 6: Parity scatter plot across all 24 unseen test batteries"),
        ("7.png", "06_empirical_benchmarking.png", 110, "Figure 7: Empirical benchmark: LightGBM vs Linear Regression..."),
        ("8.png", "07_prediction_errors_histogram.png", 140, "Figure 8: Distribution of prediction errors"),
        ("9.png", "08_confusion_matrix.png", 110, "Figure 9: Prognostic maintenance confusion matrix")
    ]
    
    output_dirs = [
        r"D:\chandru downloads\cropped_figures_sequential",
        r"d:\chandru project\RUL prediction\cropped_figures_sequential"
    ]
    
    for out_dir in output_dirs:
        os.makedirs(out_dir, exist_ok=True)
        print(f"\nProcessing output directory: {out_dir}")
        
        for out_name, src_name, crop_top, desc in figures_sequence:
            src_path = os.path.join(src_dir, src_name)
            out_path = os.path.join(out_dir, out_name)
            
            if not os.path.exists(src_path):
                print(f" ERROR: Missing source file {src_path}")
                continue
                
            img = Image.open(src_path)
            
            # Crop box is (left, upper, right, lower)
            if crop_top > 0:
                cropped_img = img.crop((0, crop_top, img.width, img.height))
                cropped_img.save(out_path)
                print(f" -> Saved {out_name} (cropped top {crop_top}px to remove title) | {desc}")
            else:
                img.save(out_path)
                print(f" -> Saved {out_name} (no title to crop, saved intact) | {desc}")
                
    # Create Zip Archives
    zip_paths = [
        r"D:\chandru downloads\cropped_figures_sequential.zip",
        r"d:\chandru project\RUL prediction\cropped_figures_sequential.zip"
    ]
    
    for zip_path in zip_paths:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for out_name, _, _, desc in figures_sequence:
                file_to_zip = os.path.join(output_dirs[0], out_name)
                if os.path.exists(file_to_zip):
                    zf.write(file_to_zip, out_name)
        print(f"\nSaved Zip Archive to: {zip_path}")
        
    print("\nALL 9 FIGURES SUCCESSFULLY CROPPED AND SEQUENCED!")

if __name__ == "__main__":
    crop_and_sequence_figures()
