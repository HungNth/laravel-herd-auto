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
    - Add WordPress site:
      ```bash
      python main.py -a
      ```

    - Delete WordPress site:
      ```bash
      python main.py -d
      ```
    - For help:
      ```bash
      python main.py -h
      ```