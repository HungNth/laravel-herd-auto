import subprocess
from pathlib import Path

import config
from utils.commands import run_command
from utils.os_helper import is_windows, herd_path, is_mac

herd_sites_path, herd_cached_path, herd_bin_path = herd_path()


class WPCLI:
    def __init__(self):
        self.db_user = config.db_username
        self.db_password = config.db_password
        self.db_host = config.db_host if is_windows() else '127.0.0.1'
        self.db_port = config.db_port
        self.wpcli = self.wpcli_path()
        self.wp_options = config.wp_options
    
    def wpcli_path(self):
        wpcli = ""
        
        if is_windows():
            wpcli = herd_bin_path / "wp.bat"
        elif is_mac():
            wpcli = herd_bin_path / "wp"
        
        if not wpcli.exists():
            print("WP-CLI is not installed or not found in the expected path.")
            print("Installing WP-CLI...")
            self.install_wp_cli()
        
        return herd_bin_path / 'wp'
    
    def install_wp_cli(self):
        if is_windows():
            command = (
                f'cd /d "{herd_bin_path}" && '
                f'curl -L -O "https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar" && '
                f'echo @ECHO OFF > wp.bat && echo php "%~dp0wp-cli.phar" %* >> wp.bat'
            )
            run_command(command, cwd=herd_bin_path)
            print("WP-CLI installed successfully on Windows.")
        elif is_mac():
            command = (
                f'curl -O "https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar" && '
                f'chmod +x wp-cli.phar && '
                f'mv wp-cli.phar "{herd_bin_path}/wp"'
            )
            run_command(command, cwd=herd_bin_path)
            print("WP-CLI installed successfully on MacOs.")
    
    def get_wp_version(self, path):
        command = f'"{self.wpcli}" core version'
        result = run_command(command, cwd=path)
        return result
    
    def wp_core_download(self, path, skip_content=True):
        command = f'"{self.wpcli}" core download --path="{path}"'
        if skip_content:
            command += ' --skip-content'
        result = run_command(command, cwd=None)
        return result
    
    def wp_config_create(self, path, db_name, db_prefix='wp_'):
        db_name = db_name.replace("-", "_").replace(" ", "_").lower()
        
        command = (
            f'"{self.wpcli}" config create '
            f'--dbname="{db_name}" '
            f'--dbuser="{self.db_user}" '
            f'--dbpass="{self.db_password}" '
            f'--dbhost="{self.db_host}:{self.db_port}" '
            f'--dbprefix="{db_prefix}"'
        )
        result = run_command(command, cwd=path)
        return result
    
    def wp_db_create(self, path):
        command = (
            f'"{self.wpcli}" db create'
        )
        result = run_command(command, cwd=path)
        return result
    
    def wp_install(self, site_name, admin_username, admin_password, admin_email):
        path = herd_sites_path / site_name
        url = f"https://{site_name}.test"
        title = site_name
        db_name = site_name
        
        self.wp_core_download(path)
        self.wp_config_create(path, db_name)
        self.wp_db_create(path)
        
        command = (
            f'"{self.wpcli}" core install '
            f'--url="{url}" '
            f'--title="{title}" '
            f'--admin_user="{admin_username}" '
            f'--admin_password="{admin_password}" '
            f'--admin_email="{admin_email}"'
        )
        result = run_command(command, cwd=path)
        return result
    
    def wp_config_set(self, path, key, value):
        command = (
            f'"{self.wpcli}" config set '
            f'"{key}" "{value}" '
            f'--path="{path}"'
        )
        result = run_command(command, cwd=path)
        return result
    
    def wp_options_set(self, path):
        for option in self.wp_options:
            command = (
                f'"{self.wpcli}" {option}'
            )
            run_command(command, cwd=path)
        
        subprocess.run(f'wp rewrite structure /%category%/%postname%/', cwd=path, shell=True)
    
    def get_user_id(self, path):
        command = (
            f'"{self.wpcli}" user list --field=ID'
        )
        result = run_command(command, cwd=path, print_output=False)
        return result[0]
    
    def get_db_name(self, path):
        command = (
            f'"{self.wpcli}" config get DB_NAME'
        )
        result = run_command(command, cwd=path, print_output=False)
        return result
    
    def get_db_prefix(self, path):
        command = (
            f'"{self.wpcli}" db prefix'
        )
        result = run_command(command, cwd=path, print_output=False)
        return result
    
    def export_db(self, path):
        command = (
            f'"{self.wpcli}" db export'
        )
        run_command(command, cwd=path)
    
    def import_db(self, path, db_path):
        if not Path(db_path).is_file() and Path(db_path).suffix.lower() != '.sql' and not Path(db_path).exists():
            raise FileNotFoundError(f"The specified database file does not exist or is not a .sql file: {db_path}")
        
        command = (
            f'"{self.wpcli}" db import '
            f'"{db_path}"'
        )
        run_command(command, cwd=path)
    
    def update_user_email(self, path, new_email):
        user_id = self.get_user_id(path)
        
        command = (
            f'"{self.wpcli}" user update {user_id} '
            f'--user_email="{new_email}"'
        )
        run_command(command, cwd=path)
    
    def update_admin_email(self, path, new_email):
        command = (
            f'"{self.wpcli}" option update admin_email {new_email}'
        )
        run_command(command, cwd=path)
    
    def update_site_url(self, path):
        site_url = f'https://{Path(path).name}.test'
        
        command1 = (
            f'"{self.wpcli}" option update siteurl "{site_url}"'
        )
        run_command(command1, cwd=path)
        
        command2 = (
            f'"{self.wpcli}" option update home "{site_url}"'
        )
        run_command(command2, cwd=path)
    
    def update_user_password(self, path, new_password):
        user_id = self.get_user_id(path)
        
        command = (
            f'"{self.wpcli}" user update {user_id} '
            f'--user_pass="{new_password}"'
        )
        run_command(command, cwd=path)
    
    def delete_all_transients(self, path):
        command = (
            f'"{self.wpcli}" transient delete --all'
        )
        run_command(command, cwd=path, print_output=False)
    
    def cache_clear(self, path):
        command1 = (
            f'"{self.wpcli}" cache flush'
        )
        run_command(command1, cwd=path, print_output=False)
        
        command2 = (
            f'"{self.wpcli}" cli cache clear'
        )
        run_command(command2, cwd=path, print_output=False)
    
    def install_plugin(self, slug, path, activate=True):
        command = (
            f'"{self.wpcli}" plugin install "{slug}"'
        )
        if activate:
            command += ' --activate'
        run_command(command, cwd=path)
    
    def install_plugins(self, plugins, path, activate=True):
        for plugin in plugins:
            self.install_plugin(plugin, path, activate=activate)
    
    def activate_plugin(self, slug, path):
        command = (
            f'"{self.wpcli}" plugin activate "{slug}"'
        )
        run_command(command, cwd=path)
    
    def is_plugin_installed(self, slug, path):
        command = (
            f'"{self.wpcli}" plugin is-installed "{slug}"'
        )
        try:
            run_command(command, cwd=path, print_output=False)
            return True
        except RuntimeError:
            return False
    
    def activate_all_plugins(self, path):
        command = (
            f'"{self.wpcli}" plugin activate --all'
        )
        run_command(command, cwd=path)
    
    def deactivate_all_plugins(self, path, exclude=None):
        command = (
            f'"{self.wpcli}" plugin deactivate --all'
        )
        if exclude is None:
            exclude = []
        exclude_args = f'--exclude={",".join(exclude)}'
        
        if exclude is not None:
            command += f' {exclude_args}'
        
        run_command(command, cwd=path)
    
    def install_theme(self, slug, path, activate=True):
        command = (
            f'"{self.wpcli}" theme install "{slug}"'
        )
        
        if activate:
            command += ' --activate'
        
        run_command(command, cwd=path)
    
    def install_themes(self, themes, path):
        for theme in themes:
            self.install_theme(theme, path)
    
    def ai1_backup(self, path):
        command = (
            f'"{self.wpcli}" ai1wm backup'
        )
        result = run_command(command, cwd=path)
        return result
    
    def ai1_restore(self, path, wpress_file, auto_confirm=True):
        command = (
            f'"{self.wpcli}" ai1wm restore "{wpress_file}"'
        )
        
        if auto_confirm:
            command += ' --yes'
        
        result = run_command(command, cwd=path)
        return result

# if __name__ == '__main__':
#     wpcli = WPCLI()
