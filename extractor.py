import tarfile
import yaml
import os

class MoodleExtractor:
    def __init__(self, config_path:str='config.yaml'):
        self.config = {}
        self.__load_config(config_path=config_path)
        self.mbz_files = self.get_mbz_files()
    
    def __load_config(self, config_path:str):
        if not os.path.exists(config_path):
            print(f'Config file {config_path} not found. Using default settings.')
            return
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            if config:
                self.config.update(config)
    
    def get_mbz_files(self):
        # CONFIGURATION: Input directory for .mbz files
        mbz_dir = self.config.get('inputs', '.')

        self.mbz_files = [os.path.join(mbz_dir, f) for f in os.listdir(mbz_dir) if f.endswith('.mbz')]
        return self.mbz_files
    
    def extract_all(self):
        # CONFIGURATION: Output directory for extracted files
        output_dir = self.config.get('outputs', './extracted')

        os.makedirs(output_dir, exist_ok=True)

        for mbz_file in self.mbz_files:
            course_name = os.path.splitext(os.path.basename(mbz_file))[0]
            extract_path = os.path.join(output_dir, course_name)
            os.makedirs(extract_path, exist_ok=True)

            # extract the mbz (tar gz)
            with tarfile.open(mbz_file, 'r:gz') as tar:
                tar.extractall(path=extract_path)
            
            print(f'Extracted {mbz_file} to {extract_path}')
    
if __name__ == "__main__":
    extractor = MoodleExtractor(config_path='config.yaml')
    extractor.extract_all()