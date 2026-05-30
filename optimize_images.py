import os
import argparse
from PIL import Image

def optimize_image(file_path, output_path, max_dim=1600):
    try:
        im = Image.open(file_path)
        orig_size = im.size
        orig_bytes = os.path.getsize(file_path)
        
        # Determine format
        original_format = im.format if im.format else os.path.splitext(file_path)[1][1:].upper()
        if original_format == 'JPG':
            original_format = 'JPEG'
        
        # Resize if dimensions exceed max_dim
        w, h = im.size
        if w > max_dim or h > max_dim:
            if w > h:
                new_w = max_dim
                new_h = int(h * (max_dim / w))
            else:
                new_h = max_dim
                new_w = int(w * (max_dim / h))
            im = im.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        # Convert RGBA to RGB (with white background for transparency)
        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
            background = Image.new("RGB", im.size, (255, 255, 255))
            # If it has alpha channel, use it as mask, otherwise just convert
            if 'alpha' in im.getbands():
                background.paste(im, mask=im.split()[im.getbands().index('alpha')])
            else:
                background.paste(im)
            im = background
        else:
            im = im.convert("RGB")
            
        # Save optimized image
        if original_format == 'PNG':
            im.save(output_path, "PNG", optimize=True)
        else:
            # For JPEG, we use quality 85 which is a good balance for academic plots
            im.save(output_path, "JPEG", optimize=True, quality=85)
            
        new_bytes = os.path.getsize(output_path)
        print(f"Optimized {os.path.basename(file_path)}:")
        print(f"  Resolution: {orig_size} -> {im.size}")
        print(f"  Size: {orig_bytes/1024:.1f} KB -> {new_bytes/1024:.1f} KB (saved {(orig_bytes-new_bytes)/1024:.1f} KB)")
        
        return True
    except Exception as e:
        print(f"Error optimizing {os.path.basename(file_path)}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Smart Image Optimizer for Academic Papers (PNG/JPEG)")
    parser.add_argument("-i", "--input", required=True, help="Input directory containing images to optimize")
    parser.add_argument("-o", "--output", help="Output directory (if omitted, overwrites original files)")
    parser.add_argument("--max-dim", type=int, default=1600, help="Maximum allowed width or height in pixels (default: 1600)")
    parser.add_argument("--max-size-kb", type=int, default=200, help="Only optimize images larger than this size in KB (default: 200)")
    
    args = parser.parse_args()
    
    input_dir = args.input
    output_dir = args.output if args.output else input_dir
    
    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return
        
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
        
    valid_extensions = ('.png', '.jpg', '.jpeg')
    optimized_count = 0
    skipped_count = 0
    
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(valid_extensions):
            file_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            try:
                # Check dimensions and size before optimizing
                im = Image.open(file_path)
                w, h = im.size
                im.close() # Always close the file handle after reading metadata
                
                file_size_kb = os.path.getsize(file_path) / 1024.0
                
                if w > args.max_dim or h > args.max_dim or file_size_kb > args.max_size_kb:
                    success = optimize_image(file_path, output_path, args.max_dim)
                    if success:
                        optimized_count += 1
                else:
                    # If it's already optimized and output dir is different, we just copy it
                    if file_path != output_path:
                        import shutil
                        shutil.copy2(file_path, output_path)
                    skipped_count += 1
                    
            except Exception as e:
                print(f"Could not process {filename}: {e}")
                
    print("\n--- Summary ---")
    print(f"Optimized: {optimized_count} images")
    print(f"Skipped (already optimized): {skipped_count} images")

if __name__ == "__main__":
    main()
