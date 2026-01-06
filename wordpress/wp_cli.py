class WPCLI:
    def __init__(self):
        import config
        import utils.os_helper as os_helper
        
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
        import subprocess
        command = f'"{self.wpcli}" core version --path="{path}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    
    def wp_core_download(self, path, version='latest'):
        import subprocess
        command = f'"{self.wpcli}" core download --path="{path}" --version="{version}"'
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    
    def wp_config_create(self, path, db_name, db_prefix='wp_'):
        import subprocess
        command = (
            f'"{self.wpcli}" config create '
            f'--dbname="{db_name}" '
            f'--dbuser="{self.db_user}" '
            f'--dbpass="{self.db_password}" '
            f'--dbhost="{self.db_host}:{self.db_port}" '
            f'--dbprefix="{db_prefix}" '
            f'--path="{path}"'
        )
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    
    def wp_db_create(self, path):
        import subprocess
        command = (
            f'"{self.wpcli}" db create '
            f'--path="{path}"'
        )
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    
    def wp_install(self, site_name, admin_user, admin_password, admin_email):
        import subprocess
        from utils.user_input import clean_input
        
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
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    
    def wp_config_set(self, path, key, value):
        import subprocess
        command = (
            f'"{self.wpcli}" config set '
            f'"{key}" "{value}" '
            f'--path="{path}"'
        )
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    
    def wp_options_set(self, path):
        import subprocess
        
        for option in self.wp_options:
            command = (
                f'"{self.wpcli}" {option} '
                f'--path="{path}"'
            )
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(result.stdout.strip())
            if result.stderr:
                print(result.stderr)


if __name__ == '__main__':
    wpcli = WPCLI()
    wpcli.wp_options_set(r'F:\laravel-herd\sites\astro-estates')
