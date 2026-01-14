import shutil
import subprocess
import os
import yaml

class RcloneUploader:
    config = {}
    sync_folder = "./results/"
    inputs_folder = "./inputs/"
    remote_name = "remote-name"
    remote_path = "Destination"
    mbz_archive_path = "mbz_archive"
    delete_after_upload = False
    extract_folder = "./extracted/"

    @classmethod
    def load_config(cls, config_path: str = 'config.yaml'):
        if not os.path.exists(config_path):
            print(f'Config file {config_path} not found. Please create it before running the uploader.')
            exit()
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            cls.config.update(config)

            cls.sync_folder = cls.config.get('results', cls.sync_folder)
            cls.inputs_folder = cls.config.get('inputs', cls.inputs_folder)
            cls.extract_folder = cls.config.get('outputs', cls.extract_folder)

            rclone_config = cls.config.get('rclone', {})
            cls.remote_name = rclone_config.get('remote_name', cls.remote_name)
            cls.remote_path = rclone_config.get('remote_path', cls.remote_path)
            cls.mbz_archive_path = rclone_config.get('mbz_archive_path', cls.mbz_archive_path)
            cls.delete_after_upload = rclone_config.get('delete_after_upload', cls.delete_after_upload)

    @classmethod
    def get_mbz_files(cls):
        """Get list of .mbz files from inputs folder"""
        if not os.path.exists(cls.inputs_folder):
            print(f"[#] Inputs folder not found: {cls.inputs_folder}")
            return []
        
        mbz_files = [os.path.join(cls.inputs_folder, f) 
                     for f in os.listdir(cls.inputs_folder) 
                     if f.endswith('.mbz')]
        return mbz_files

    @classmethod
    def upload_mbz_files(cls):
        """Upload .mbz files to the archive folder"""
        mbz_files = cls.get_mbz_files()
        
        if not mbz_files:
            print("[#] No .mbz files found to upload")
            return
        
        print(f"[#] Found {len(mbz_files)} .mbz file(s) to upload")
        
        remote_destination = f"{cls.remote_name}:{cls.remote_path}/{cls.mbz_archive_path}"
        
        for mbz_file in mbz_files:
            print(f"[#] Uploading {os.path.basename(mbz_file)} to {remote_destination}")
            cmd = [
                "rclone", "copy",
                mbz_file,
                remote_destination,
                "--progress",
                "--stats=1s",
                "--tpslimit=5",
                "--tpslimit-burst=5",
                "--no-update-modtime"
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            for line in process.stdout:
                print(line, end="")

            process.wait()
            if process.returncode != 0:
                raise RuntimeError(f"Rclone failed with exit code {process.returncode}")
        
        print("[#] All .mbz files uploaded successfully")

    @classmethod
    def delete_extracted_folder(cls):
        """Delete the extracted results folder after upload"""
        if os.path.exists(cls.extract_folder):
            print(f"[#] Deleting extracted results folder: {cls.extract_folder}")
            shutil.rmtree(cls.extract_folder)
        else:
            print(f"[#] Extracted results folder not found: {cls.extract_folder}")

    @classmethod
    def start(cls):
        print("[#] -- Start Rclone Uploader -- [#]")
        rclone_installed = cls.is_rclone_installed()
        print(f"[#] Rclone installed? : {rclone_installed}")
        if not rclone_installed:
            print("[#] Rclone is not installed ...")
            exit()
        
        rclone_operation = "move" if cls.delete_after_upload else "copy"
        print(f"[#] Rclone operation: {rclone_operation} (delete_after_upload: {cls.delete_after_upload})")
        
        remote_destination = f"{cls.remote_name}:{cls.remote_path}"
        cmd = [
            "rclone", rclone_operation,
            cls.sync_folder,
            remote_destination,
            "--progress",
            "--stats=1s",
            "--tpslimit=5",
            "--tpslimit-burst=5",
            "--no-update-modtime"
        ]
        
        # Add flag to delete empty source directories when using move
        if cls.delete_after_upload:
            cmd.append("--delete-empty-src-dirs")
            cls.delete_extracted_folder()

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )

        for line in process.stdout:
            print(line, end="")

        process.wait()
        if process.returncode != 0:
            raise RuntimeError(f"Rclone failed with exit code {process.returncode}")
        
        print("\n[#] Results uploaded successfully")
        print("[#] Now uploading .mbz archive files...\n")
        cls.upload_mbz_files()

    @classmethod
    def is_rclone_installed(cls):
        # Fast check: is it in PATH?
        if shutil.which("rclone") is None:
            return False

        # Extra safety: can we run it?
        try:
            subprocess.run(
                ["rclone", "version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    @classmethod
    def get_sync_folder(cls):
        return cls.sync_folder


if __name__ == "__main__":
    # load config after class definition
    RcloneUploader.load_config(config_path='config.yaml')
    RcloneUploader.start()