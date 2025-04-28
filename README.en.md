<div align="center">
  <img src="image/ARC-X-Logo.png" alt="ARC-X Gaming Compressor Logo" width="300">
  <p><em>Logo is a temporary placeholder</em></p>
</div>

# ARC-X Gaming Compressor

A powerful tool for scanning, compressing, and extracting game files with multithreading support.

## Description

The ARC-X Gaming Compressor is an advanced tool that can efficiently compress and manage game files. It categorizes files by type (textures, audio, 3D models, scripts) and uses the Zstandard compression algorithm for optimal compression rates. The new multithreading support enables significantly faster processing of large game directories.

### Comparison with Conventional Compression Tools

At first glance, ARC-X may resemble general compression tools like 7-Zip or WinRAR, but it has been specifically designed for the requirements of modern games and offers several decisive advantages:

- **Game-specific file detection**: Automatically recognizes and categorizes different game file types for optimal compression
- **Intelligent compression strategies**: Applies different compression settings based on file type
- **Optimized for large game directories**: Specially developed to handle the extensive data volumes of modern games
- **Multithreaded architecture**: Utilizes the full power of modern multi-core processors for faster compression
- **Game developer-friendly**: Provides detailed analyses and logs that are valuable for game developers and publishers

ARC-X was built from the ground up for the gaming industry and focuses on the specific challenges of compressing game files, rather than being a universal solution for all types of data.

## Features

- **Directory scanner**: Recursively scans directories and categorizes files
- **Smart compression**: Applies different compression levels based on file type
- **Multithreaded processing**: Utilizes all available CPU cores for faster compression
- **Detailed statistics**: Provides information on file sizes, compression ratios, and processing time
- **Extractor**: Unpacks .arcx archives and restores the original structure
- **Detailed logging**: Creates comprehensive logs about file size and compression rate
- **Error logging**: Stores detailed information about failed files

## New Features

- **Multithreaded compression**: Up to 10x faster processing through parallel compression
- **Improved error handling**: Robust processing even with problems in individual files
- **Real-time progress display**: Shows percentage, remaining time, and error count
- **Detailed error logs**: Separate log file for failed files
- **Optimized memory usage**: Efficient processing even with very large game directories

> **Note**: Some of the advanced features are still under development and will be available in future updates. The core functionality of multithreaded compression and improved error handling is already fully implemented.

## Compression Examples

| File Type | Typical Compression Ratio | Space Savings |
|-----------|---------------------------|---------------|
| Textures  | 20-40%                    | 60-80%        |
| Audio     | 10-30%                    | 70-90%        |
| 3D Models | 40-60%                    | 40-60%        |
| Scripts   | 70-90%                    | 10-30%        |

### Real-world Example: Modern RPG (120 GB)

- **Original size**: 120 GB
- **Compressed size**: 89.7 GB
- **Space savings**: 30.3 GB (30.3% less storage space)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/ARC-X.git
   cd ARC-X
   ```

2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Compressing Game Files

```
python src/compressor.py --input "C:/Games/MyGame" --output "compressed/mygame.arcx" --threads 8
```

Scans the specified game directory, categorizes files, and compresses them using 8 threads.

### Extracting Compressed Files

```
python src/extractor.py --input "compressed/mygame.arcx" --output "C:/Games/MyGame_Extracted"
```

Extracts an .arcx archive from the `compressed/` folder to the specified output directory.

## Project Structure

```
├── src/
│   ├── compressor.py  # Main module for scanning and compressing
│   ├── extractor.py   # Module for extracting .arcx archives
│   ├── utils.py       # Helper functions for file detection and processing
├── compressed/        # Output directory for compressed archives
├── requirements.txt   # Dependencies
└── README.md          # Documentation
```

> **Development Note**: The current version of ARC-X is implemented as a test version in only three main files. In future versions, the code structure will be improved and modularized to ensure better maintainability and extensibility. The simple structure of the current version allows for quick testing and iteration of core functionalities.

## Dependencies

- Python 3.6+
- zstandard>=0.15.0
- pillow>=11.2.0
- pydub>=0.25.1

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## Acknowledgments

- The Zstandard compression library
- All contributors who have helped with testing and development