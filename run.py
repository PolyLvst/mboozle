from extractor import MoodleExtractor
from crawler import MboozleCrawler

class Mboozle:
    def __init__(self, config_path:str='config.yaml'):
        self.config_path = config_path
    
    def run(self):
        extractor_instance = MoodleExtractor(config_path=self.config_path)
        extractor_instance.extract_all()

        crawler_instance = MboozleCrawler(config_path=self.config_path)
        crawler_instance.crawl()

if __name__ == "__main__":
    mboozle = Mboozle(config_path='config.yaml')
    mboozle.run()
