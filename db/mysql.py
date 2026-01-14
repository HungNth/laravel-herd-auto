import re
import subprocess
from typing import List

from utils.config_parse import parse_config
from utils.os_helper import is_windows, is_mac
from utils.time_helper import formatted_time

config = parse_config()


class MySQL:
    def __init__(self):
        self.db_user = config.get('db_username')
        self.db_password = config.get('db_password')
        self.db_host = config.get('db_host') if is_windows() else '127.0.0.1'
        self.db_port = config.get('db_port')
        self.db_socket = config.get('db_socket')

    def check_db_connection(self):
        try:
            command = [
                '-e',
                'SELECT 1;'
            ]
            self.run(command, print_output=False)
            return True
        except Exception as e:
            print(f'Error connecting to database: {e}')
            return False

    def clean_db_name(self, db_name):
        return db_name.replace('-', '_').replace(' ', '_').lower()

    def run(self, args, *, print_output=True, shell=False):
        command = None

        if isinstance(args, str):
            args = args.split(' ')
        elif isinstance(args, List):
            command = [
                'mysql',
                f'-u{self.db_user}',
                f'-P{self.db_port}',
            ]
        if is_mac():
            command.append(f'{self.db_socket}')

        command.extend(args)
        result = subprocess.run(
            command,
            shell=shell,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip())

        if print_output and result.stdout:
            print(result.stdout)

        return result.stdout.strip()

    def check_database_exists(self, db_name):
        db_name = self.clean_db_name(db_name)

        try:
            command = [
                '-e',
                f'SHOW DATABASES LIKE \'{db_name}\';',
            ]
            result = self.run(command, print_output=False)
            return db_name in result
        except Exception as e:
            print(f'Error: {e}')
            return False

    def create_database(self, db_name):
        db_name = self.clean_db_name(db_name)

        if self.check_database_exists(db_name):
            print(f'Database "{db_name}" already exists.')
            return

        try:
            command = [
                '-e',
                f'CREATE DATABASE IF NOT EXISTS \'{db_name}\'; GRANT ALL PRIVILEGES ON \'{db_name}\'.* TO root@localhost WITH GRANT OPTION; FLUSH PRIVILEGES;'
            ]
            self.run(command)
            print(f'Created database: {db_name}')
        except Exception as e:
            print(f'Error: "{db_name}": {e}')
            return

    def drop_database(self, db_name):
        db_name = self.clean_db_name(db_name)
        command = [
            '-e',
            f'DROP DATABASE IF EXISTS `{db_name}`;',
        ]
        self.run(command)

    def get_table_prefix(self, db_name):
        db_name = self.clean_db_name(db_name)

        if not self.check_database_exists(db_name):
            print(f'Database "{db_name}" does not exist.')
            return None

        command = [
            '-e',
            f'USE `{db_name}`; SHOW TABLES LIKE \'%_options\';'
        ]
        result = self.run(command, print_output=False)
        if result:
            table_name = result.splitlines()[1]
            prefix = table_name.replace('options', '')
            return prefix
        return None

    def update_table_prefix(self, db_name, wp_config_path):
        db_name = self.clean_db_name(db_name)

        prefix = self.get_table_prefix(db_name)
        if prefix != 'wp_':
            try:
                with open(wp_config_path, 'r', encoding='utf-8') as f:
                    config_content = f.read()

                if "$table_prefix" in config_content:
                    updated_content = re.sub(
                        r"\$table_prefix\s*=\s*'[^']*';",
                        f"$table_prefix = '{prefix}';",
                        config_content
                    )
                else:
                    updated_content = config_content + f"\n$table_prefix = '{prefix}';\n"

                with open(wp_config_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                print(f'Updated table prefix on :wp-config.php" to "{prefix}"')
            except IOError as e:
                raise ValueError(f'I/O error: {e}')
            except Exception as e:
                raise ValueError(f'Unexpected error: {e}')

    def get_admin_id(self, db_name):
        db_name = self.clean_db_name(db_name)

        if not self.check_database_exists(db_name):
            print(f'Database "{db_name}" does not exist.')
            return None

        prefix = self.get_table_prefix(db_name)
        if not prefix:
            print(f'Could not determine table prefix for database "{db_name}".')
            return None

        command = [
            '-e',
            f'USE `{db_name}`; SELECT ID FROM {prefix}users;'
        ]
        result = self.run(command, print_output=False)
        if result:
            user_id = result.splitlines()[1]
            return user_id
        return None

    def change_username(self, db_name, new_username):
        db_name = self.clean_db_name(db_name)

        if not self.check_database_exists(db_name):
            print(f'Database "{db_name}" does not exist.')
            return

        user_id = self.get_admin_id(db_name)
        if not user_id:
            print(f'User not found in database "{db_name}".')
            return

        prefix = self.get_table_prefix(db_name)
        if not prefix:
            print(f'Could not determine table prefix for database "{db_name}".')
            return

        try:
            command = [
                '-e',
                f'USE `{db_name}`; UPDATE {prefix}users SET user_login = \'{new_username}\' WHERE ID = {user_id};'
            ]
            self.run(command)
            print(f'Changed username to "{new_username}" in database "{db_name}".')
        except Exception as e:
            print(f'Error changing username in database "{db_name}": {e}')
            return

    def change_password(self, db_name, new_password):
        db_name = self.clean_db_name(db_name)

        if not self.check_database_exists(db_name):
            print(f'Database "{db_name}" does not exist.')
            return

        user_id = self.get_admin_id(db_name)
        if not user_id:
            print(f'User not found in database "{db_name}".')
            return

        prefix = self.get_table_prefix(db_name)
        if not prefix:
            print(f'Could not determine table prefix for database "{db_name}".')
            return

        try:
            command = [
                '-e',
                f'USE `{db_name}`; UPDATE {prefix}users SET user_pass = MD5(\'{new_password}\') WHERE ID = {user_id};'
            ]
            self.run(command)
            print(f'Changed password in database "{db_name}".')
        except Exception as e:
            print(f'Error changing password in database "{db_name}": {e}')
            return

    def change_email(self, db_name, new_email):
        db_name = self.clean_db_name(db_name)

        if not self.check_database_exists(db_name):
            print(f'Database "{db_name}" does not exist.')
            return

        user_id = self.get_admin_id(db_name)
        if not user_id:
            print(f'User not found in database "{db_name}".')
            return

        prefix = self.get_table_prefix(db_name)
        if not prefix:
            print(f'Could not determine table prefix for database "{db_name}".')
            return

        try:
            command = [
                '-e',
                f'USE `{db_name}`; UPDATE {prefix}users SET user_email = \'{new_email}\' WHERE ID = {user_id};'
            ]
            self.run(command)
            print(f'Changed user email to "{new_email}" in database "{db_name}".')
        except Exception as e:
            print(f'Error changing email in database "{db_name}": {e}')
            return

    def export_db(self, db_name, export_path):
        db_name = self.clean_db_name(db_name)
        output = f'{export_path}/{db_name}_{formatted_time()}.sql'

        command = [
            'mysqldump',
            f'-u{self.db_user}',
            f'--password={self.db_password}',
            '--single-transaction',
            '--quick',
            '--skip-lock-tables',
            db_name
        ]
        with open(output, 'w', encoding='utf-8') as f:
            subprocess.run(command, cwd=export_path, stdout=f, check=True)

    def import_db(self, db_name, sql_file):
        db_name = self.clean_db_name(db_name)

        cmd = [
            'mysql',
            f'-u{self.db_user}',
            f'--password={self.db_password}',
            db_name
        ]
        with open(sql_file, 'r', encoding='utf-8') as f:
            subprocess.run(cmd, stdin=f, check=True)

# mysql = MySQL()
# connection = mysql.check_database_exists('wp01')
# print(connection)
