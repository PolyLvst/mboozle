# Mboozle - Moodle Backup Archiver & Extractor

A Python-based tool for extracting, organizing, and archiving Moodle course backups (.mbz files) into a human-readable folder structure with automatic cloud upload support.

## Purpose

Mboozle automates the process of extracting Moodle backup files (.mbz) and restoring the original filenames and folder structures. It organizes files by course name, activity type, and optionally by username, making it easy to browse and access course materials outside of Moodle.

## Features

- **Automatic Extraction** - Extracts .mbz (Moodle backup) files into organized directories
- **File Restoration** - Restores original filenames from Moodle's hashed file storage
- **Smart Organization** - Organizes files by:
  - Course name
  - Component type (course, forum, quiz, etc.)
  - File area (attachments, posts, images, etc.)
  - Username (optional)
- **Cloud Upload** - Automatic upload to remote storage via rclone
- **Flexible Configuration** - YAML-based configuration with multiple options
- **Docker Support** - Containerized deployment with docker-compose
- **Scheduled Execution** - Run on specific days (e.g., weekly on Mondays)

## Requirements

- Python 3.10+
- Docker & Docker Compose (for containerized deployment)
- Rclone (for cloud uploads, installed automatically in Docker)

### Python Dependencies
- PyYAML
- (automatically installed via requirements.txt)

## Installation

1. Clone or download this repository
2. Place your .mbz files in the configured input directory (default: current directory)
3. Configure rclone for your cloud storage (if using upload feature)
4. Edit `config.yaml` to match your preferences

## Configuration

Edit `config.yaml` to customize the behavior:

```yaml
# Input/Output Directories
inputs: "."                    # Where .mbz files are located
outputs: './extracted'         # Where extracted files are stored temporarily
results: './results'           # Where organized files are saved

# Organization Options
include_backup_name: true      # Include backup folder name in results path
organize_by_user: true         # Organize files by username within activities
extract_to_source: false       # Extract directly to source folder (not recommended)

# Rclone Upload Settings
enable_rclone_uploader: false
rclone:
  remote_name: "remote-name"               # Your rclone remote name
  remote_path: "Destination"               # Destination path on remote
  mbz_archive_path: "mbz_archive"          # Subfolder for original .mbz files
  delete_after_upload: false               # Delete local files after upload
```

## Usage

### Run with Docker (Recommended)

```bash
docker compose up --build
```

### Run with Python

```bash
# Extract backups
python extractor.py

# Organize files
python crawler.py

# Upload to cloud (optional)
python rclone_uploader.py

# Or run all steps
python run.py
```

### Scheduled Execution

Use the provided `run.sh` script with cron for scheduled execution:

```bash
# Edit crontab
crontab -e

# Run every Monday at 3 AM Jakarta time
0 3 * * 1 /path/to/mboozle/run.sh
```

The script will automatically skip execution if it's not Monday.

## Output Structure

With default settings, files are organized as:

```
results/
└── Literasi/                          # Course name
    ├── course/
    │   └── overviewfiles/
    │       └── admin/
    │           └── wallpaper.jpg
    ├── format_cards/
    │   └── image/
    │       └── admin/
    │           └── course-image.png
    └── mod_forum/
        ├── attachment/
        │   └── admin/
        │       └── document.pdf
        └── post/
            └── username/
                └── image.png
```

## How It Works

1. **Extraction** (`extractor.py`) - Extracts .mbz (tar.gz) files into the `extracted/` directory
2. **Crawling** (`crawler.py`) - Parses XML metadata and restores original filenames from hashed storage
3. **Uploading** (`rclone_uploader.py`) - Uploads organized files and original .mbz archives to cloud storage

## Rclone Setup

To enable cloud uploads, configure rclone:

```bash
# Configure a new remote
rclone config

# Test your remote
rclone ls yourremote:

# Update config.yaml with your remote name
```

## Uptime Monitoring

The `run.sh` script supports Uptime Kuma push notifications. Set the `KUMA_URL` variable in `run.sh`:

```bash
KUMA_URL="https://your-uptime-kuma.com/api/push/xxxxx"
```

## License

MIT License - Feel free to use and modify as needed.

## Troubleshooting

**Files not extracted?**
- Check that .mbz files are in the correct input directory
- Verify file permissions

**Upload failing?**
- Test rclone configuration: `rclone ls yourremote:`
- Check network connectivity
- Verify remote path exists

**Empty folders left after upload?**
- Ensure `delete_after_upload: true` and the script will clean up empty directories automatically

## Contributing

This is a personal archiving tool, but suggestions and improvements are welcome.
