import subprocess

import config
from utils.os_helper import is_windows, is_mac


class MySQL:
    def __init__(self):
        self.db_user = config.db_username
        self.db_password = config.db_password
        self.db_host = config.db_host if is_windows() else '127.0.0.1'
        self.db_port = config.db_port
        self.db_socket = config.db_socket if is_mac() else ''
    
    def clean_db_name(self, db_name):
        return db_name.replace('-', '_').replace(' ', '_').lower()
    
    def run(self, command, output=True, print_output=True):
        mysql_command = f'mysql -u {self.db_user} -P {self.db_port} {self.db_socket} {command}'
        
        result = subprocess.run(mysql_command, shell=True, capture_output=True, text=True)
        
        if result.stderr:
            print(result.stderr)
        if print_output:
            print(result.stdout.strip())
        if output:
            return result.stdout.strip()
        return None
    
    def check_database_exists(self, db_name):
        
        db_name = self.clean_db_name(db_name)
        
        try:
            result = self.run(f'-e "SHOW DATABASES LIKE \'{db_name}\';"', print_output=False)
            return db_name in result
        except Exception as e:
            print(f'Error: {e}')
            return False
    
    def create_database(self, db_name):
        db_name = self.clean_db_name(db_name)
        
        if self.check_database_exists(db_name):
            print(f'Database "{db_name}" already exists.\n')
            return
        
        try:
            self.run(
                f'-e "CREATE DATABASE IF NOT EXISTS {db_name}; GRANT ALL PRIVILEGES ON {db_name}.* TO root@localhost WITH GRANT OPTION; FLUSH PRIVILEGES;"')
            print(f'Created database: "{db_name}"\n')
        except Exception as e:
            print(f'Error: "{db_name}": {e}')
            return
    
    def drop_database(self, db_name):
        db_name = self.clean_db_name(db_name)
        
        if not self.check_database_exists(db_name):
            print(f'Database "{db_name}" does not exist.')
            return
        else:
            self.run(f'-e "DROP DATABASE {db_name};"')
    
    def get_table_prefix(self, db_name):
        db_name = self.clean_db_name(db_name)
        
        if not self.check_database_exists(db_name):
            print(f'Database "{db_name}" does not exist.')
            return None
        
        result = self.run(f'-e "USE {db_name}; SHOW TABLES LIKE \'%_options\';"', print_output=False)
        if result:
            table_name = result.splitlines()[1]
            prefix = table_name.replace('options', '')
            return prefix
        return None
    
    def get_admin_id(self, db_name):
        db_name = self.clean_db_name(db_name)
        
        if not self.check_database_exists(db_name):
            print(f'Database "{db_name}" does not exist.')
            return None
        
        prefix = self.get_table_prefix(db_name)
        if not prefix:
            print(f'Could not determine table prefix for database "{db_name}".')
            return None
        
        result = self.run(
            f'-e "USE {db_name}; SELECT ID FROM {prefix}users;"',
            print_output=False)
        
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
            self.run(
                f'-e "USE {db_name}; UPDATE {prefix}users SET user_login = \'{new_username}\' WHERE ID = {user_id};"')
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
            self.run(
                f'-e "USE {db_name}; UPDATE {prefix}users SET user_pass = MD5(\'{new_password}\') WHERE ID = {user_id};"')
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
            self.run(
                f'-e "USE {db_name}; UPDATE {prefix}users SET user_email = \'{new_email}\' WHERE ID = {user_id};"')
            print(f'Changed user email to "{new_email}" in database "{db_name}".')
        except Exception as e:
            print(f'Error changing email in database "{db_name}": {e}')
            return
