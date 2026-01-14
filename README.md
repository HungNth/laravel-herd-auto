# Laravel Herd Auto Script

## How to Use

- Clone this repository or download the script.
- Configure the script in `config.py` with your WordPress site details.
- Ensure you have Python installed on your machine.
- Install any required dependencies (if applicable), should use **python environment**.
    ```
    pip install -r requirements.txt
  ```
- Run the script in your terminal:
- Activate your Python environment (if using one):
    - On Windows:
  ```bash
  .venv\Scripts\activate.bat
  ```
    - On MacOS:
  ```bash
  source .venv/bin/activate
  ```
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
the following command:

```commandline
pyinstaller --onefile --icon=data/herd.ico --name hwpy main.py
```

This will create a `dist` folder containing the executable file.

- On Windows, the executable will be located at `dist\hwpy.exe`.
- On MacOS, the executable will be located at `dist/hwpy`.
- Add the executable to your system PATH for easy access from any terminal window.

### Add to PATH

To add the executable to your system PATH:

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
    2. Open your shell profile file in a text editor. This could be `~/.bash_profile`, `~/.zshrc`, or another file
       depending on your shell.
       For example, you can use:
       ```bash
       nano ~/.zshrc
       ```
    3. Add the following line to the file, replacing `laravel-herd-auto/dist` with the actual path to your executable:
       ```bash
       export PATH="laravel-herd-auto/dist:$PATH"
       ```
    4. Save the file and exit the text editor.
    5. Apply the changes by running:
       ```bash
       source ~/.zshrc
       ```
    6. Restart your terminal to ensure the changes take effect.