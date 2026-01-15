# Laravel Herd Auto Script

## How to Use

- Clone this repository or download the script.
- Copy and rename from `config.example.json` to `config.json` and update the configuration values as needed.
- Ensure you have Python installed on your machine.
- Install any required dependencies (if applicable), should use **python environment**.
    ```
    pip install -r requirements.txt
  ```
- Install WP-CLI:
    - On Windows, run script: `install-wp-cli-Windows.bat`
    - On MacOS, open terminal and run script with sudo: `sudo install-wp-cli-MacOS.sh` or use homebrew:
      `brew install wp-cli`

- Activate your Python environment (if using one, recommended for development):
    - On Windows:
  ```bash
  .venv\Scripts\activate.bat
  ```
    - On MacOS:
  ```bash
  source .venv/bin/activate
  ```
- Run the script in your terminal:
    - Add WordPress site:
      ```bash
      python main.py -a
      ```

    - Delete WordPress site:
      ```bash
      python main.py -d
      ```
    - Backup WordPress site:
      ```bash
      python main.py -b
      ```
    - Restore WordPress site:
      ```bash
      python main.py -r
      ```
    - For help:
      ```bash
      python main.py -h
      ```

## Build to Executable

### Building the Executable

To build the script into an executable file, you can use PyInstaller. First, activate your Python environment, then run
the following command in your terminal from the project root directory:

- Run command:
    ```commandline
    pyinstaller --onefile --icon=data/herd.ico --name hwpy main.py
    ```
- Folder structure after build:
  ```
  laravel-herd-auto/
  ├── dist/
  │   ├── hwpy.exe (Windows) or hwpy (MacOS)
  ├── main.py
  ├── data/
  │   └── herd.ico
  └── ...
  ```

This will create a `dist` folder containing the executable file.

- On Windows, the executable will be located at `dist\hwpy.exe`.
- On MacOS, the executable will be located at `dist/hwpy`.

Now you can run the executable directly from the `dist` folder. Or you can add it to your system PATH for easier access.

### Add to PATH

Add the directory containing the executable to your system PATH environment variable, use symbolic links, or move the
executable to a directory already in your PATH.

- On Windows:
    1. Right-click on 'This PC' or 'Computer' on the desktop or in File Explorer.
    2. Select 'Properties'.
    3. Click on 'Advanced system settings'.
    4. Click on the 'Environment Variables' button.
    5. In the 'System variables' section, find and select the 'Path' variable, then click 'Edit'.
    6. Click 'New' and add the path to the directory containing your executable (e.g., `D:\laravel-herd-auto\dist`).
    7. Click 'OK' to close all dialog boxes.
    8. Restart your terminal or command prompt to apply the changes.
- On MacOS:
    1. Open a terminal window.
    2. Create symbolic link to `/opt/homebrew/bin` or `/user/local/bin` or any directory in your PATH:
       ```bash
       ln -s "$(pwd)/dist/hwpy" /opt/homebrew/bin/hwpy
       ls -l /opt/homebrew/bin/hwpy # to verify the link
       ```
    3. Restart your terminal to apply the changes.
    4. To check if it was added successfully, run:
         ```bash
         hwpy -h
         ```
       You should see the help message for the script.