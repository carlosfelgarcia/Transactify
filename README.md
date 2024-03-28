# Transactify

Transactify is a brother tool of Money Mind app -- Visit [www.carlosgarciadev.com](http://www.carlosgarciadev.com) for more information

This tool that allows you to transform QFX files and Excel files from Questrade into JSON files, which the Money Mind app will use to ingest the information.

## Features

- Convert QFX files to JSON format
- Convert Questrade Excel files to JSON format

## Installation

1. You can either clone the repository or download the ZIP file from the releases page:

   - To download the ZIP file, go to the releases page and download the latest release on zip file.

   - To clone the repository, use the following command:

   ```shell
   git clone https://github.com/your-username/Transactify.git
   ```

2. Create a virtual environment and activate it:

   ```shell
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required dependencies:

   ```shell
   pip install -r requirements.txt
   ```

Now you have successfully installed the required dependencies for Transactify.

## Usage

To use Transactify, follow these steps:

1. Navigate to the directory where `main.py` is located:

   ```shell
   cd path/to/Transactify
   ```

2. Run the `main.py` script with the following command:

   ```shell
   ./main.py
   ```

   By default, the script will look for files to convert in your `Downloads` folder. If your files are located in a different folder, you can specify the path using the `--files-path` option:

   ```shell
   ./main.py --files-path /path/to/your/files
   ```

3. The converted JSON files will be created in the same directory as the original files.

### Example

Suppose you have a QFX file and a Questrade Excel file in your `Downloads` folder. After running the script, you will find the corresponding JSON files in the same folder:

- `your_file.qfx` will be converted to `your_file.json`
- `your_questrade_file.xlsx` will be converted to `your_questrade_file.json`

## Contributing

If you would like to contribute to the development of Transactify, please feel free to submit a pull request or open an issue on the GitHub repository.

## License

Transactify is released under the MIT License. See the LICENSE file for more details.
