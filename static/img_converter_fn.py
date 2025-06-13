from PIL import Image
import os
import pillow_avif
import concurrent.futures
from tqdm import tqdm

class ImgConverter:
    def __init__(self, root_dir):
        self.root_dir = root_dir
        self.supported_formats = ('.jpg', '.jpeg', '.png', 'webp')
        self.quality = 50
        self.speed = 5

    def convert_to_avif(self, input_path):
        try:
            base, _ = os.path.splitext(input_path)
            output_path = base + ".avif"

            #Skip if AVIF already exists.
            if os.path.exists(output_path):
                return False

            with Image.open(input_path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                #Preserve EXIF data
                exif = img.info.get('exif')

                img.save(
                    output_path,
                    format='AVIF',
                    quality=self.quality,
                    speed= self.speed,
                    exif=exif
                )

                os.remove(input_path)
                return True
        except Exception as e:
            print(f"❌ Error converting {input_path}: {e}")


    def process_file(self, file_path):
        if self.convert_to_avif(file_path):
            return file_path
        return None

            
    def find_and_convert(self):
        
        files_to_process = []

        for foldername, _, filenames in os.walk(self.root_dir):
            for filename in filenames:
                if filename.lower().endswith(self.supported_formats):
                    full_path = os.path.join(foldername, filename)
                    files_to_process.append(full_path)

        converted_files = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for file_path in files_to_process:
                futures.append(executor.submit(self.process_file, file_path))

                # Little animation to see the progress
                for future in tqdm(concurrent.futures.as_completed(futures),
                                   total=len(files_to_process),
                                   desc="Converting images"):
                    result = future.result()
                    if result:
                        converted_files.append(result)
        
        return converted_files

    

if __name__ == "__main__":
    converter = ImgConverter(os.getcwd())
    converted = converter.find_and_convert()
    print(f"\n🎉 Converted {len(converted)} images to AVIF")

