from datetime import datetime
from pathlib import Path

import config
from utils.user_input import clean_input
from utils.os_helper import is_windows, herd_path, is_mac
from utils.commands import run_command

herd_sites_path, herd_cached_path, herd_bin_path = herd_path()


class WPCLI:
    def __init__(self):
        self.db_user = config.db_username
        self.db_password = config.db_password
        self.db_host = config.db_host if is_windows() else '127.0.0.1'
        self.db_port = config.db_port
        self.db_socket = config.db_socket if is_mac() else ''
        self.wpcli = self.wpcli_path()
        self.wp_options = config.wp_options
    
    def wpcli_path(self):
        wpcli = Path(herd_bin_path / "wp")
        
        result = run_command(f"{wpcli} --version", print_output=False)
        
        if "WP-CLI" not in result:
            print("WP-CLI is not installed or not found in the expected path.")
            print("Installing WP-CLI...")
            self.install_wp_cli()
            return wpcli
        else:
            return wpcli
    
    def install_wp_cli(self):
        if is_windows():
            command = (
                f'cd /d "{herd_bin_path}" && '
                f'curl -L -O "https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar" && '
                f'echo @ECHO OFF > wp.bat && echo php "%~dp0wp-cli.phar" %* >> wp.bat'
            )
            run_command(command)
            print("WP-CLI installed successfully on Windows.")
        elif is_mac():
            command = (
                f'curl -O "https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar" && '
                f'chmod +x wp-cli.phar && '
                fr'mv wp-cli.phar ~/Library/Application\ Support/Herd/bin/wp'
            )
            run_command(command)
            print("WP-CLI installed successfully on MacOs.")
    
    def get_wp_version(self, path):
        command = f'"{self.wpcli}" core version --path="{path}"'
        result = run_command(command)
        return result
    
    def wp_core_download(self, path, skip_content=True):
        command = f'"{self.wpcli}" core download --path="{path}" {"--skip-content" if skip_content else ""}'
        result = run_command(command)
        return result
    
    def wp_config_create(self, path, db_name, db_prefix='wp_'):
        db_name = db_name.replace("-", "_").replace(" ", "_").lower()
        
        command = (
            f'"{self.wpcli}" config create '
            f'--dbname="{db_name}" '
            f'--dbuser="{self.db_user}" '
            f'--dbpass="{self.db_password}" '
            f'--dbhost="{self.db_host}:{self.db_port}" '
            f'{self.db_socket} '
            f'--dbprefix="{db_prefix}" '
            f'--path="{path}"'
        )
        result = run_command(command)
        return result
    
    def wp_db_create(self, path):
        command = (
            f'"{self.wpcli}" db create '
            f'--path="{path}"'
        )
        result = run_command(command)
        return result
    
    def wp_install(self, site_name, admin_username, admin_password, admin_email):
        path = herd_sites_path / clean_input(site_name)
        url = f"{clean_input(site_name)}.test"
        title = site_name
        db_name = clean_input(site_name)
        
        self.wp_core_download(path)
        self.wp_config_create(path, db_name)
        self.wp_db_create(path)
        
        command = (
            f'"{self.wpcli}" core install '
            f'--url="{url}" '
            f'--title="{title}" '
            f'--admin_user="{admin_username}" '
            f'--admin_password="{admin_password}" '
            f'--admin_email="{admin_email}" '
            f'--path="{path}"'
        )
        result = run_command(command)
        return result
    
    def wp_config_set(self, path, key, value):
        command = (
            f'"{self.wpcli}" config set '
            f'"{key}" "{value}" '
            f'--path="{path}"'
        )
        result = run_command(command)
        return result
    
    def wp_options_set(self, path):
        for option in self.wp_options:
            command = (
                f'"{self.wpcli}" {option} '
                f'--path="{path}"'
            )
            run_command(command, output=False)
    
    def get_user_id(self, path):
        command = (
            f'"{self.wpcli}" user list --field=ID '
            f'--path="{path}"'
        )
        result = run_command(command, print_output=False)
        
        return result[0]
    
    def get_db_name(self, path):
        command = (
            f'"{self.wpcli}" config get DB_NAME '
            f'--path="{path}"'
        )
        result = run_command(command, print_output=False)
        
        return result
    
    def get_db_prefix(self, path):
        command = (
            f'"{self.wpcli}" db prefix '
            f'--path="{path}"'
        )
        result = run_command(command, print_output=False)
        
        return result
    
    def export_db(self, path, export_path=None):
        now = datetime.now()
        formatted_datetime = now.strftime("%m-%d-%Y_%Hh%Mm%Ss")
        site_name = Path(path).name
        
        if not export_path:
            export_filename = f"{site_name}_db_backup_{formatted_datetime}.sql"
            export_path = Path(path) / export_filename
        else:
            export_path = Path(export_path).resolve() / ".sql" if Path(export_path).is_dir() else Path(export_path)
        
        command = (
            f'"{self.wpcli}" db export '
            f'"{export_path}" '
            f'--path="{path}"'
        )
        run_command(command)
    
    def import_db(self, path, db_path):
        if not Path(db_path).is_file() and Path(db_path).suffix.lower() != '.sql' and not Path(db_path).exists():
            raise FileNotFoundError(f"The specified database file does not exist or is not a .sql file: {db_path}")
        
        command = (
            f'"{self.wpcli}" db import" '
            f'"{db_path}" '
            f'--path="{path}"'
        )
        run_command(command)
    
    def update_user_email(self, path, new_email):
        user_id = self.get_user_id(path)
        command = (
            f'"{self.wpcli}" user update {user_id} '
            f'--user_email="{new_email}" '
            f'--path="{path}"'
        )
        run_command(command)
    
    def update_admin_email(self, path, new_email):
        command = (
            f'"{self.wpcli}" option update admin_email {new_email} '
            f'--path="{path}"'
        )
        run_command(command)
    
    def update_site_url(self, path):
        site_url = f"https://{Path(path).name}.test"
        
        command1 = (
            f'"{self.wpcli}" option update siteurl "{site_url}" '
            f'--path="{path}"'
        )
        run_command(command1)
        
        command2 = (
            f'"{self.wpcli}" option update home "{site_url}" '
            f'--path="{path}"'
        )
        run_command(command2)
    
    def update_user_password(self, path, new_password):
        user_id = self.get_user_id(path)
        
        command = (
            f'"{self.wpcli}" user update {user_id} '
            f'--user_pass="{new_password}" '
            f'--path="{path}"'
        )
        
        run_command(command)
    
    def install_plugin(self, slug, path, activate=True):
        command = (
            f'"{self.wpcli}" plugin install "{slug}" '
            f'--path="{path}" '
            f'{"--activate" if activate else ""}'
        )
        run_command(command)
    
    def install_plugins(self, plugins, path, activate=False):
        for plugin in plugins:
            self.install_plugin(plugin, path, activate)
        
        self.activate_all_plugins(path)
    
    def activate_all_plugins(self, path):
        command = (
            f'"{self.wpcli}" plugin activate --all '
            f'--path="{path}"'
        )
        run_command(command)
    
    def install_theme(self, slug, path, activate=True):
        command = (
            f'"{self.wpcli}" theme install "{slug}" '
            f'--path="{path}" '
            f'{"--activate" if activate else ""}'
        )
        run_command(command)
    
    def install_themes(self, themes, path):
        for theme in themes:
            self.install_theme(theme, path, )


if __name__ == '__main__':
    wpcli = WPCLI()
    wpcli.install_wp_cli()
