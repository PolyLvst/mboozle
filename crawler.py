import yaml
import os
import shutil
import xml.etree.ElementTree as ET

class MboozleCrawler:
    def __init__(self, config_path:str='config.yaml'):
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
    
    def crawl(self):
        # CONFIGURATION: Output directory for extracted files, and results directory
        output_dir = self.config.get('outputs', './extracted')

        if not os.path.exists(output_dir):
            print(f'Extracted directory {output_dir} not found. Please run the extractor first.')
            return
        
        # Find all backup folders
        backup_folders = [f for f in os.listdir(output_dir) if os.path.isdir(os.path.join(output_dir, f))]
        if not backup_folders:
            print(f'No backup folders found in {output_dir}')
            return
        
        print(f'Found {len(backup_folders)} backup folder(s) to process\n')
        
        # Process each backup folder
        for idx, backup_folder_name in enumerate(backup_folders, 1):
            print(f'[{idx}/{len(backup_folders)}] Processing backup: {backup_folder_name}')
            backup_folder = os.path.join(output_dir, backup_folder_name)
            self._process_backup(backup_folder, backup_folder_name)
            print()  # Add blank line between backups
        
        print(f'=== All Backups Processed ===')
        print(f'Total backups processed: {len(backup_folders)}')
    
    def _process_backup(self, backup_folder, backup_folder_name):
        """Process a single backup folder"""
        results_dir = self.config.get('results', './results')
        organize_by_user = self.config.get('organize_by_user', False)
        extract_to_source = self.config.get('extract_to_source', False)
        include_backup_name = self.config.get('include_backup_name', True)
        
        # Parse course.xml to get course name
        course_xml_path = os.path.join(backup_folder, 'course', 'course.xml')
        course_name = 'Unknown'
        if os.path.exists(course_xml_path):
            course_tree = ET.parse(course_xml_path)
            course_root = course_tree.getroot()
            fullname_elem = course_root.find('fullname')
            if fullname_elem is not None and fullname_elem.text:
                course_name = fullname_elem.text
        print(f'Course: {course_name}')
        
        # Determine the base results directory
        if extract_to_source:
            # Extract to: extracted_folder/backup-folder-name/CourseName/
            results_dir = os.path.join(backup_folder, course_name)
        else:
            # Extract to: results/[backup-folder-name]/CourseName/
            if include_backup_name:
                results_dir = os.path.join(results_dir, backup_folder_name, course_name)
            else:
                results_dir = os.path.join(results_dir, course_name)
        
        # Parse users.xml to get username mappings
        users_map = {}
        if organize_by_user:
            users_xml_path = os.path.join(backup_folder, 'users.xml')
            if os.path.exists(users_xml_path):
                print(f'Parsing {users_xml_path}...')
                users_tree = ET.parse(users_xml_path)
                users_root = users_tree.getroot()
                for user_elem in users_root.findall('user'):
                    user_id = user_elem.get('id')
                    username = user_elem.find('username').text
                    users_map[user_id] = username
                print(f'Loaded {len(users_map)} users')
            else:
                print(f'Warning: users.xml not found. User organization disabled.')
                organize_by_user = False
        
        # Parse files.xml
        files_xml_path = os.path.join(backup_folder, 'files.xml')
        if not os.path.exists(files_xml_path):
            print(f'files.xml not found in {backup_folder}')
            return
        
        print(f'Parsing {files_xml_path}...')
        tree = ET.parse(files_xml_path)
        root = tree.getroot()
        
        # Create results directory
        os.makedirs(results_dir, exist_ok=True)
        
        # Process each file entry
        files_processed = 0
        files_skipped = 0
        
        for file_elem in root.findall('file'):
            contenthash = file_elem.find('contenthash').text
            filename = file_elem.find('filename').text
            filepath = file_elem.find('filepath').text
            component = file_elem.find('component').text
            filearea = file_elem.find('filearea').text
            filesize = int(file_elem.find('filesize').text)
            userid = file_elem.find('userid').text
            
            # Skip directory entries (filename = '.' or filesize = 0)
            if filename == '.' or filesize == 0:
                files_skipped += 1
                continue
            
            # Find the source file in the files directory
            # The contenthash is stored in subdirectories named by the first 2 characters
            hash_prefix = contenthash[:2]
            source_file = os.path.join(backup_folder, 'files', hash_prefix, contenthash)
            
            if not os.path.exists(source_file):
                print(f'Warning: Source file not found: {source_file}')
                files_skipped += 1
                continue
            
            # Create organized directory structure in results
            # results/component/filearea/[username]/filepath/filename
            dest_dir = os.path.join(results_dir, component, filearea)
            
            # Add username subdirectory if organize_by_user is enabled
            if organize_by_user and userid in users_map:
                username = users_map[userid]
                dest_dir = os.path.join(dest_dir, username)
            
            if filepath and filepath != '/':
                dest_dir = os.path.join(dest_dir, filepath.strip('/'))
            
            os.makedirs(dest_dir, exist_ok=True)
            
            # Copy file with original filename
            dest_file = os.path.join(dest_dir, filename)
            
            # Handle duplicate filenames
            if os.path.exists(dest_file):
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_file):
                    dest_file = os.path.join(dest_dir, f'{base}_{counter}{ext}')
                    counter += 1
            
            shutil.copy2(source_file, dest_file)
            files_processed += 1
            
            if files_processed % 10 == 0:
                print(f'Processed {files_processed} files...')
        
        print(f'Files processed: {files_processed}')
        print(f'Files skipped: {files_skipped}')
        print(f'Results saved to: {results_dir}')


if __name__ == '__main__':
    crawler = MboozleCrawler(config_path='config.yaml')
    crawler.crawl()
        
