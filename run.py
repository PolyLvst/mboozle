from rclone_uploader import RcloneUploader
from extractor import MoodleExtractor
from crawler import MboozleCrawler
import yaml
import os

class Mboozle:
    def __init__(self, config_path:str='config.yaml'):
        self.config_path = config_path
        self.config = {}
        self.__load_config(config_path=config_path)
    
    def __load_config(self, config_path:str):
        if not os.path.exists(config_path):
            print(f'Config file {config_path} not found. Using default settings.')
            return
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            if config:
                self.config.update(config)
    
    def run(self):
        # CONFIGURATION: Whether to enable rclone uploader after extraction and crawling
        enable_rclone_uploader = self.config.get('enable_rclone_uploader', False)

        extractor_instance = MoodleExtractor(config_path=self.config_path)
        extractor_instance.extract_all()

        crawler_instance = MboozleCrawler(config_path=self.config_path)
        crawler_instance.crawl()

        if enable_rclone_uploader:
            rclone_uploader_instance = RcloneUploader()
            rclone_uploader_instance.load_config(config_path=self.config_path)
            rclone_uploader_instance.start()
        
        print("[#] Mboozle process completed. [#]")

if __name__ == "__main__":
    mboozle = Mboozle(config_path='config.yaml')
    mboozle.run()
