from datetime import datetime
from pathlib import Path
from utils.user_input import clean_input


class WPCLI:
    def __init__(self):
        import config
        import utils.os_helper as os_helper
        from utils.commands import run_command
        
        self.run_command = run_command
        self.db_user = config.db_username
        self.db_password = config.db_password
        self.db_host = config.db_host if os_helper.is_windows() else '127.0.0.1'
        self.db_port = config.db_port
        self.admin_username = config.admin_username
        self.admin_password = config.admin_password
        self.admin_email = config.admin_email
        self.wpcli = os_helper.wpcli_path()
        self.herd_sites_path, _, _ = os_helper.herd_path()
        self.wp_options = config.wp_options
    
    def wp_version(self, path):
        command = f'"{self.wpcli}" core version --path="{path}"'
        result = self.run_command(command)
        return result
    
    def wp_core_download(self, path):
        command = f'"{self.wpcli}" core download --path="{path}" --skip-content'
        result = self.run_command(command)
        return result
    
    def wp_config_create(self, path, db_name, db_prefix='wp_'):
        command = (
            f'"{self.wpcli}" config create '
            f'--dbname="{db_name}" '
            f'--dbuser="{self.db_user}" '
            f'--dbpass="{self.db_password}" '
            f'--dbhost="{self.db_host}:{self.db_port}" '
            f'--dbprefix="{db_prefix}" '
            f'--path="{path}"'
        )
        result = self.run_command(command)
        return result
    
    def wp_db_create(self, path):
        command = (
            f'"{self.wpcli}" db create '
            f'--path="{path}"'
        )
        result = self.run_command(command)
        return result
    
    def wp_install(self, site_name, admin_user, admin_password, admin_email):
        admin_user = clean_input(admin_user) if clean_input(admin_user) != self.admin_username else self.admin_username
        admin_password = clean_input(admin_password) if clean_input(
            admin_password) != self.admin_password else self.admin_password
        admin_email = clean_input(admin_email) if clean_input(admin_email) != self.admin_email else self.admin_email
        
        path = self.herd_sites_path / clean_input(site_name)
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
            f'--admin_user="{admin_user}" '
            f'--admin_password="{admin_password}" '
            f'--admin_email="{admin_email}" '
            f'--path="{path}"'
        )
        result = self.run_command(command)
        return result
    
    def wp_config_set(self, path, key, value):
        command = (
            f'"{self.wpcli}" config set '
            f'"{key}" "{value}" '
            f'--path="{path}"'
        )
        result = self.run_command(command)
        return result
    
    def wp_options_set(self, path):
        for option in self.wp_options:
            command = (
                f'"{self.wpcli}" {option} '
                f'--path="{path}"'
            )
            self.run_command(command, output=False)
    
    def get_admin_id(self, path):
        command = (
            f'"{self.wpcli}" user list --field=ID '
            f'--path="{path}"'
        )
        result = self.run_command(command, print_output=False)
        
        return result[0]
    
    def get_db_prefix(self, path):
        command = (
            f'"{self.wpcli}" db prefix '
            f'--path="{path}"'
        )
        result = self.run_command(command, print_output=False)
        
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
        self.run_command(command)
    
    def import_db(self, path, db_path):
        if not Path(db_path).is_file() and Path(db_path).suffix.lower() != '.sql' and not Path(db_path).exists():
            raise FileNotFoundError(f"The specified database file does not exist or is not a .sql file: {db_path}")
        
        command = (
            f'"{self.wpcli}" db export" '
            f'"{db_path}" '
            f'--path="{path}"'
        )
        self.run_command(command)


if __name__ == '__main__':
    wpcli = WPCLI()
    wpcli.export_db(r"F:\laravel-herd\sites\astro-estates")
