import json
import shutil
import sys
import webbrowser
from pathlib import Path
from typing import Literal

import httpx
from packaging.version import Version

import config
from utils.commands import run_command
from utils.data_file_handle import load_data_file, save_data_file
from utils.get_filename import get_filename_from_response
from utils.herd import add_ssl
from utils.os_helper import herd_path
from utils.time_helper import formatted_time
from utils.user_input import get_input, clean_input, get_confirmation, get_input_options

herd_sites_path, herd_cached_path, _ = herd_path()


class WordPress:
    def __init__(self, wpc_li, wp_api, mysql):
        self.wp_cli = wpc_li
        self.wp_api = wp_api
        self.mysql = mysql
        self.data_file = Path.cwd() / 'data/data.json'
        Path(self.data_file).parent.mkdir(parents=True, exist_ok=True)
    
    def get_admin_credentials(self):
        admin_username = config.admin_username
        admin_password = config.admin_password
        admin_email = config.admin_email
        
        site_name = get_input('Enter the site name: ', required=True)
        site_name = clean_input(site_name)
        
        if self.is_website_exists(site_name):
            print(f'Site "{site_name}" already exists. Please choose a different name.')
            return self.get_admin_credentials()
        if self.mysql.check_database_exists(site_name):
            print(f'Database for site "{site_name}" already exists. Please choose a different name.')
            return self.get_admin_credentials()
        
        is_default = get_confirmation('Do you want to use default admin credentials? (Y/n): ', default=True)
        
        if is_default is False:
            admin_username_input = get_input(f'Enter the admin username "{admin_username}": ', default=admin_username,
                                             required=True)
            admin_pass_input = get_input(f'Enter the admin password "{admin_password}": ', default=admin_password,
                                         required=True)
            admin_email_input = get_input(f'Enter the admin email "{admin_email}": ', default=admin_email,
                                          required=True)
        else:
            admin_username_input = admin_username
            admin_pass_input = admin_password
            admin_email_input = admin_email
        
        return site_name, admin_username_input, admin_pass_input, admin_email_input
    
    def create_website(self):
        site_name, admin_username, admin_password, admin_email = self.get_admin_credentials()
        selected_themes, selected_plugins, is_setup_wp_config = self.get_setup_options()
        
        site_path = herd_sites_path / site_name
        Path(site_path).mkdir(parents=True, exist_ok=True)
        
        file_name = self.download_wp()
        print(f'Extracting WordPress to site path: "{site_path}"')
        command = [
            'tar',
            '-xf',
            herd_cached_path / file_name,
            '-C',
            site_path,
            '--strip-components=1'
        ]
        run_command(command, cwd=herd_sites_path, shell=False)
        
        self.wp_cli.wp_config_create(site_path, site_name)
        self.wp_cli.wp_db_create(site_path)
        self.wp_cli.wp_install(site_name, admin_username, admin_password, admin_email)
        
        if len(selected_themes) == 0:
            selected_themes = [config.default_theme_slug]
            self.install_packages(site_path, selected_themes, item_type="theme")
        
        if len(selected_plugins) > 0:
            self.install_packages(site_path, selected_plugins, item_type="plugin")
        if is_setup_wp_config:
            self.wp_cli.wp_options_set(site_path)
        
        add_ssl(site_path)
        webbrowser.open(f'https://{site_name}.test/wp-admin')
    
    def download_wp(self):
        api = config.wp_version_api
        
        response = httpx.get(api, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        offer = data['offers'][0]
        latest_version = offer['current']  # string
        download_url = offer['packages']['no_content']
        filename = download_url.split('/')[-1]
        download_path = herd_cached_path / filename
        
        data_json = load_data_file(self.data_file)
        saved_version = Version(data_json.get('wordpress', {}).get('version', '0'))
        latest_version_v = Version(latest_version)
        
        need_download = (
                saved_version is None or
                saved_version < latest_version_v or
                not download_path.exists()
        )
        
        if need_download:
            print(f'Downloading WordPress {latest_version}...')
            
            with httpx.stream('GET', download_url, timeout=30) as r:
                r.raise_for_status()
                with open(download_path, 'wb') as f:
                    for chunk in r.iter_bytes():
                        f.write(chunk)
            
            data_json['wordpress'] = {
                "version": latest_version,
                "file_name": filename
            }
            save_data_file(self.data_file, data_json)
        else:
            print(f'WordPress {latest_version} is already downloaded.')
        
        return filename
    
    def download_package(self, slug):
        latest_version = self.wp_api.get_latest_version(slug)
        download_url = self.wp_api.get_download_url(slug)
        
        filename = get_filename_from_response(download_url)
        download_path = herd_cached_path / filename
        
        data_json = load_data_file(self.data_file)
        saved_version = Version(data_json.get(slug, {}).get('version', '0'))
        latest_version_v = Version(latest_version)
        
        need_download = (
                saved_version is None or
                saved_version < latest_version_v or
                not download_path.exists()
        )
        
        if need_download:
            print(f'Downloading {slug} {latest_version}...')
            
            with httpx.stream('GET', download_url, timeout=30) as r:
                r.raise_for_status()
                with open(download_path, 'wb') as f:
                    for chunk in r.iter_bytes():
                        f.write(chunk)
            
            data_json[slug] = {
                "version": latest_version,
                "file_name": filename
            }
            save_data_file(self.data_file, data_json)
        else:
            print(f'{slug} {latest_version} is already downloaded.')
        
        return filename
    
    def download_packages(self, slugs):
        file_names = []
        for slug in slugs:
            file_name = self.download_package(slug)
            file_names.append(file_name)
        
        return file_names
    
    def delete_websites(self):
        selected_sites = self.select_websites()
        if not selected_sites:
            sys.exit(0)
        
        print(f'You have selected the following websites for deletion: {", ".join(selected_sites)}')
        if not get_confirmation("Are you sure you want to delete these websites? This action cannot be undone. (y/N): ",
                                default=False):
            print("Deletion cancelled by user.")
            sys.exit(0)
        
        for site in selected_sites:
            self.delete_website(site)
    
    def delete_website(self, site_name):
        site_path = herd_sites_path / site_name
        
        if site_path.exists():
            try:
                self.mysql.drop_database(site_name)
                shutil.rmtree(site_path)
                print(f'Website "{site_name}" and its database have been deleted successfully.\n')
            except Exception as e:
                print(f'Error deleting website "{site_name}": {e}\n')
                pass
    
    def get_setup_options(self):
        selected_themes = ""
        selected_plugins = []
        
        is_install_theme = get_confirmation(
            'Do you want to install another themes? (Default theme: "Flatsome") (y/N): ',
            default=False)
        if is_install_theme:
            selected_themes = self.wp_api.select_packages("theme")
        
        is_install_plugins = get_confirmation('Do you want to install plugins? (y/N): ', default=False)
        if is_install_plugins:
            selected_plugins = self.wp_api.select_packages("plugin")
        
        is_setup_wp_config = get_confirmation('Do you want to setup WordPress options? (Y/n): ', default=True)
        
        return selected_themes, selected_plugins, is_setup_wp_config
    
    def is_website_exists(self, site_name):
        site_path = herd_sites_path / site_name
        return site_path.exists()
    
    def get_site_list(self):
        site_list = []
        for site in herd_sites_path.iterdir():
            if site.is_dir():
                site_list.append(site.name)
        return site_list
    
    def print_site_list(self):
        site_list = self.get_site_list()
        if not site_list:
            print('No websites found to delete.')
            return
        
        print('Existing websites:')
        for index, site in enumerate(site_list, start=1):
            if site.startswith("."):
                continue
            print(f"{index}. {site}")
    
    def select_websites(self):
        from utils.user_input import clean_selection
        
        site_list = self.get_site_list()
        selected_websites = []
        
        self.print_site_list()
        
        while True:
            try:
                print(
                    "Enter the website numbers you want to select, (e.g., 1 2 3 or 1,2,3). Enter 0 to select all websites.")
                site_index = input("Your selection: ")
                
                cleaned_site_index = clean_selection(site_index)
                cleaned_site_index = [int(x) for x in cleaned_site_index]
                
                if 0 in cleaned_site_index:
                    return site_list
                
                for index in cleaned_site_index:
                    if 1 <= index <= len(site_list):
                        selected_websites.append(site_list[index - 1])
                    else:
                        print(f"Please enter a number from 1 to {len(site_list)}!\n")
                        break
                else:
                    break
            
            except ValueError:
                print("Please enter a number!")
        
        return selected_websites
    
    def install_packages(self, path, selected_pkg_slugs, item_type: Literal["theme", "plugin"]):
        if selected_pkg_slugs is None:
            return
        
        file_names = self.download_packages(selected_pkg_slugs)
        file_paths = [herd_cached_path / file_name for file_name in file_names]
        
        if item_type == "theme":
            self.wp_cli.install_themes(file_paths, path)
        elif item_type == "plugin":
            self.wp_cli.install_plugins(file_paths, path)
    
    def reset_admin_info(self, selected_website):
        for site in selected_website:
            path = herd_sites_path / site
            print(f'Resetting admin information for site: "{site}"')
            self.mysql.change_username(site, config.admin_username)
            self.mysql.change_password(site, config.admin_password)
            self.wp_cli.update_admin_email(path, config.admin_email)
            self.mysql.change_email(site, config.admin_email)
    
    def setup_wp_options(self, selected_website):
        for site in selected_website:
            path = herd_sites_path / site
            print(f'Setting up WordPress options for site: "{site}"')
            self.wp_cli.wp_options_set(path)
    
    def configure_wp(self):
        options = [
            'Create a new website',
            'Delete website(s)',
            'Backup website options',
            'Restore website options'
            'Reset Admin information to default',
            'Setup WordPress options',
            'Both 1 and 2',
            'Install Themes',
            'Install Plugins'
        ]
        print("Select an option to configure WordPress:")
        choice = get_input_options(options)
        
        selected_website = self.select_websites()
        
        if choice == '1':
            self.create_website()
        elif choice == '2':
            self.delete_websites()
        elif choice == '3':
            self.backup_options()
        elif choice == '4':
            self.restore_options()
        elif choice == '5':
            self.reset_admin_info(selected_website)
        elif choice == '6':
            self.setup_wp_options(selected_website)
        elif choice == '7':
            self.reset_admin_info(selected_website)
            self.setup_wp_options(selected_website)
        elif choice == '8':
            for site in selected_website:
                site_path = herd_sites_path / site
                selected_themes = self.wp_api.select_packages("theme")
                self.install_packages(site_path, selected_themes, item_type="theme")
        elif choice == '9':
            for site in selected_website:
                site_path = herd_sites_path / site
                selected_plugins = self.wp_api.select_packages("plugin")
                self.install_packages(site_path, selected_plugins, item_type="plugin")
        return None
    
    def backup_options(self):
        options = [
            'Backup by full source code and database include',
            'Backup by plugin All-in-One WP Migration (.wpress file)',
        ]
        
        choice = get_input_options(options)
        if choice == '1':
            self.backup_full_source()
        elif choice == '2':
            self.backup_by_ai1_plugin()
    
    def backup_full_source(self):
        selected_websites = self.select_websites()
        
        for site in selected_websites:
            site_path = herd_sites_path / site
            backup_path = herd_sites_path / f'{site}_full_backup_{formatted_time()}.zip'
            
            for file in site_path.rglob('*.sql'):
                file.unlink()
            
            ai1wm_backups_path = site_path / 'wp-content' / 'ai1wm-backups'
            if ai1wm_backups_path.exists() and ai1wm_backups_path.is_dir():
                for file in ai1wm_backups_path.rglob('*.wpress'):
                    file.unlink()
            
            print(f'Deleting all transients...')
            self.wp_cli.delete_all_transients(site_path)
            print(f'Clearing cache...')
            self.wp_cli.cache_clear(site_path)
            print(f'Exporting database...')
            self.mysql.export_db(site, export_path=site_path)
            
            command = [
                'tar',
                '-acf',
                backup_path
            ]
            
            excludes_config = config.excludes
            for exclude in excludes_config:
                exclude_build = f'--exclude={exclude}'
                command.append(exclude_build)
            
            command += ['-C', str(herd_sites_path), site]
            
            print(f'Creating backup for site "{site}"...')
            run_command(command, cwd=herd_sites_path, shell=False)
            print(f'Backup for site "{site}" created at "{backup_path}"')
    
    def backup_by_ai1_plugin(self):
        selected_websites = self.select_websites()
        
        for site in selected_websites:
            site_path = herd_sites_path / site
            print(f'Deleting all transients...')
            self.wp_cli.delete_all_transients(site_path)
            print(f'Clearing cache...')
            self.wp_cli.cache_clear(site_path)
            
            print('Deactivating all plugins...')
            self.wp_cli.deactivate_all_plugins(site_path)
            required_plugin = 'all-in-one-wp-migration-unlimited-extension'
            plugin_list = self.wp_cli.plugin_list(site_path, field='name')
            if required_plugin not in plugin_list:
                print('All-in-One WP Migration Unlimited Extension plugin is not installed.')
                print('Installing All-in-One WP Migration Unlimited Extension plugin...')
                plugin_url = self.wp_api.get_download_url(required_plugin)
                self.wp_cli.install_plugins(['all-in-one-wp-migration', plugin_url], site_path)
            self.wp_cli.activate_plugin(required_plugin, site_path)
            
            print(f'Backing up site "{site}" to ".wpress"...')
            result = self.wp_cli.ai1_backup(site_path)
            if 'Backup location' in result:
                wpress_path = result.split('Backup location: ')[1].strip()
                # check wpress_path exists
                if Path(wpress_path).exists():
                    wpress_path = wpress_path
                    wpress_parent_path = Path(wpress_path).parent
                else:
                    print('Error: Backup file not found after AI1 backup command.')
                    sys.exit(1)
            else:
                print('Error: Could not find backup location in AI1 backup command output.')
                sys.exit(1)
            
            backup_path = herd_sites_path / f'{site}_ai1m_backup_{formatted_time()}.zip'
            command = [
                'tar',
                '-acf',
                backup_path,
                '-C',
                wpress_parent_path,
                Path(wpress_path).name
            ]
            
            print(f'Creating backup for site "{site}"...')
            run_command(command, cwd=herd_sites_path, shell=False)
            print(f'Backup for site "{site}" created at "{backup_path}"')
            
            self.wp_cli.activate_all_plugins(site_path)
    
    def restore_options(self):
        options = [
            'Restore by full source code and database include',
            'Restore by wp-content only',
            'Restore by plugin All-in-One WP Migration (.wpress or .zip file)',
            'Restore by plugin Duplicator'
        ]
        
        choice = get_input_options(options)
        
        if choice == '1':
            self.restore_full_source()
        elif choice == '2':
            self.restore_by_wp_content()
        elif choice == '3':
            self.restore_by_wpress()
        elif choice == '4':
            self.restore_by_duplicator()
    
    def restore_full_source(self, site_name=None, backup_file=None):
        site_name = site_name
        backup_file = backup_file
        admin_username_input = config.admin_username
        admin_pass_input = config.admin_password
        admin_email_input = config.admin_email
        
        if site_name is None:
            site_name, admin_username_input, admin_pass_input, admin_email_input = self.get_admin_credentials()
        
        if backup_file is None:
            while True:
                backup_file = get_input('Enter the path to the full backup file (.zip, .tar, .gz): ', required=True)
                backup_file = backup_file.strip('\'"')
                backup_file = Path(backup_file).expanduser().resolve()
                
                accepted_extensions = ['.zip', '.tar', '.gz']
                if not backup_file.exists() or not backup_file.is_file() or backup_file.suffix.lower() not in accepted_extensions:
                    print('Invalid backup file. Please provide a valid .zip, .tar, or .gz file.')
                    continue
                break
        
        site_path = herd_sites_path / site_name
        site_path.mkdir(parents=True, exist_ok=True)
        
        print(f'Extracting backup file to site path: "{site_path}"')
        command = [
            'tar',
            '-xf',
            backup_file,
            '-C',
            site_path
        ]
        run_command(command, cwd=site_path, shell=False)
        
        wp_settings_path = site_path / 'wp-settings.php'
        wp_login_path = site_path / 'wp-login.php'
        if not wp_settings_path.exists() or not wp_login_path.exists():
            for subdir in site_path.iterdir():
                if subdir.is_dir():
                    potential_wp_settings = subdir / 'wp-settings.php'
                    potential_wp_login = subdir / 'wp-login.php'
                    if potential_wp_settings.exists() and potential_wp_login.exists():
                        for item in subdir.iterdir():
                            shutil.move(str(item), str(site_path / item.name))
                        shutil.rmtree(subdir)
                        break
        
        wp_config_path = site_path / 'wp-config.php'
        if wp_config_path.exists():
            wp_config_path.unlink()
        
        self.wp_cli.wp_config_create(site_path, site_name)
        self.wp_cli.wp_db_create(site_path)
        
        sql_files = list(site_path.rglob('*.sql'))
        
        if not sql_files:
            sql_file = None
        else:
            sql_file = max(sql_files, key=lambda f: f.stat().st_mtime)
        
        if sql_file is None:
            print('No SQL file found in the backup. Please provide the path to the SQL file to restore the database.')
            while True:
                sql_file = get_input('Enter the path to the SQL file (.sql): ', required=True)
                if not Path(sql_file).exists():
                    print('The provided SQL file does not exist. Cannot restore database.')
                    continue
                break
        
        print('Importing database...')
        self.mysql.import_db(site_name, sql_file)
        
        self.mysql.update_table_prefix(site_name, wp_config_path)
        self.mysql.change_username(site_name, admin_username_input)
        self.mysql.change_password(site_name, admin_pass_input)
        self.mysql.change_email(site_name, admin_email_input)
        self.wp_cli.update_admin_email(site_path, admin_email_input)
        self.wp_cli.update_site_url(site_path)
        self.wp_cli.delete_all_transients(site_path)
        self.wp_cli.cache_clear(site_path)
        
        add_ssl(site_path)
        webbrowser.open(f'https://{site_name}.test/wp-admin')
    
    def restore_by_wp_content(self, site_name=None, wp_content_path=None, sql_file=None):
        site_name = site_name
        wp_content_path = wp_content_path
        sql_file = sql_file
        admin_username_input = config.admin_username
        admin_pass_input = config.admin_password
        admin_email_input = config.admin_email
        
        if site_name is None:
            site_name, admin_username_input, admin_pass_input, admin_email_input = self.get_admin_credentials()
        
        if wp_content_path is None:
            while True:
                wp_content_path = get_input('Enter the path to the folder "wp-content": ', required=True)
                wp_content_path = wp_content_path.strip('\'"')
                wp_content_path = Path(wp_content_path).expanduser().resolve()
                if 'wp-content' not in str(wp_content_path):
                    print('Invalid backup folder. Please provide the path to the "wp-content" folder.')
                    continue
                
                plugins_path = wp_content_path / 'plugins'
                themes_path = wp_content_path / 'themes'
                if not (plugins_path.exists() and themes_path.exists()):
                    print('Invalid backup file. Please provide a valid .zip, .tar, or .gz file.')
                    continue
                break
        
        if sql_file is None:
            while True:
                sql_file = get_input('Enter the path to the SQL file (.sql): ', required=True)
                sql_file = sql_file.strip('\'"')
                sql_file = Path(sql_file).expanduser().resolve()
                if not sql_file.exists():
                    print('The provided SQL file does not exist. Cannot restore database.')
                    continue
                break
        
        site_path = herd_sites_path / site_name
        wp_config_path = site_path / 'wp-config.php'
        self.wp_cli.wp_install(site_name, admin_username_input, admin_pass_input, admin_email_input)
        
        # Copy wp-content
        dest_wp_content_path = site_path / 'wp-content'
        print('Copying wp-content folder...')
        shutil.copytree(wp_content_path, dest_wp_content_path, dirs_exist_ok=True)
        
        print('Importing database...')
        self.mysql.drop_database(site_name)
        self.wp_cli.wp_db_create(site_path)
        self.mysql.import_db(site_name, sql_file)
        
        self.mysql.update_table_prefix(site_name, wp_config_path)
        self.mysql.change_username(site_name, admin_username_input)
        self.mysql.change_password(site_name, admin_pass_input)
        self.mysql.change_email(site_name, admin_email_input)
        self.wp_cli.update_admin_email(site_path, admin_email_input)
        self.wp_cli.update_site_url(site_path)
        self.wp_cli.delete_all_transients(site_path)
        self.wp_cli.cache_clear(site_path)
        
        add_ssl(site_path)
        webbrowser.open(f'https://{site_name}.test/wp-admin')
    
    def restore_by_wpress(self, site_name=None, wpress_path=None):
        site_name = site_name
        wpress_path = wpress_path
        admin_username_input = config.admin_username
        admin_pass_input = config.admin_password
        admin_email_input = config.admin_email
        
        if site_name is None:
            site_name, admin_username_input, admin_pass_input, admin_email_input = self.get_admin_credentials()
        
        site_path = herd_sites_path / site_name
        ai1wm_backups_path = site_path / 'wp-content' / 'ai1wm-backups'
        wp_config_path = site_path / 'wp-config.php'
        
        if wpress_path is None:
            while True:
                wpress_path = get_input('Enter the path to the .wpress or .zip backup file: ', required=True)
                wpress_path = wpress_path.strip('\'"')
                wpress_path = Path(wpress_path).expanduser().resolve()
                accepted_extensions = ['.wpress', '.zip', '.tar', '.gz']
                if not wpress_path.exists() or not wpress_path.is_file() or wpress_path.suffix.lower() not in accepted_extensions:
                    print('Invalid backup file. Please provide a valid .zip, .tar, or .gz file.')
                    continue
                break
        
        self.wp_cli.wp_install(site_name, admin_username_input, admin_pass_input, admin_email_input)
        
        required_plugin = 'all-in-one-wp-migration-unlimited-extension'
        exclude = ['duplicator-pro', 'updraftplus']
        plugin_list = self.wp_cli.plugin_list(site_path, field='name')
        if required_plugin not in plugin_list:
            print('All-in-One WP Migration Unlimited Extension plugin is not installed.')
            print('Installing All-in-One WP Migration Unlimited Extension plugin...')
            plugin_url = self.wp_api.get_download_url(required_plugin)
            self.wp_cli.install_plugins(['all-in-one-wp-migration', plugin_url], site_path)
        self.wp_cli.activate_plugin(required_plugin, site_path)
        
        if wpress_path.suffix.lower() == '.zip':
            print('Extracting .zip backup file...')
            command = [
                'tar',
                '-xf',
                wpress_path,
                '-C',
                ai1wm_backups_path
            ]
            run_command(command, cwd=site_path, shell=False)
        
        elif wpress_path.suffix.lower() == '.wpress':
            print('Copying .wpress file to ai1wm-backups...')
            ai1wm_backups_path.mkdir(parents=True, exist_ok=True)
            shutil.copy2(wpress_path, ai1wm_backups_path)
        
        wpress_files = list(ai1wm_backups_path.rglob('*.wpress'))
        if len(wpress_files) > 0:
            print('Founded .wpress files:')
            for wpress_file in wpress_files:
                print(f'- {wpress_file}')
        else:
            print('No .wpress files found in the provided backup. Cannot restore.')
            sys.exit(0)
        
        wpress_file = max(wpress_files, key=lambda f: f.stat().st_mtime)
        wpress_file_name = wpress_file.name
        
        print('Restoring from .wpress file...')
        print(f'Site path: {site_path}')
        print(f'Wpress file name: {wpress_file_name}')
        
        self.wp_cli.ai1_restore(site_path, wpress_file_name, auto_confirm=True)
        
        self.mysql.update_table_prefix(site_name, wp_config_path)
        self.mysql.change_username(site_name, admin_username_input)
        self.mysql.change_password(site_name, admin_pass_input)
        self.mysql.change_email(site_name, admin_email_input)
        self.wp_cli.update_admin_email(site_path, admin_email_input)
        self.wp_cli.activate_all_plugins(site_path, exclude=exclude)
        self.wp_cli.update_site_url(site_path)
        self.wp_cli.delete_all_transients(site_path)
        self.wp_cli.cache_clear(site_path)
        
        add_ssl(site_path)
        webbrowser.open(f'https://{site_name}.test/wp-admin')
    
    def restore_by_duplicator(self):
        site_name, admin_username_input, admin_pass_input, admin_email_input = self.get_admin_credentials()
        
        while True:
            package_path = get_input('Enter the path to the Duplicator package (.zip): ', required=True)
            package_path = package_path.strip('\'"')
            package_path = Path(package_path).expanduser().resolve()
            if not package_path.exists() or not package_path.is_file() or package_path.suffix.lower() != '.zip':
                print('Invalid package file. Please provide a valid .zip file.')
                continue
            break
        
        site_path = herd_sites_path / site_name
        site_path.mkdir(parents=True, exist_ok=True)
        
        print(f'Extracting backup file to site path: "{site_path}"')
        command = [
            'tar',
            '-xf',
            package_path,
            '-C',
            site_path
        ]
        run_command(command, cwd=site_path, shell=False)
        
        installer_file = site_path / 'installer.php'
        if not installer_file.exists():
            for subdir in site_path.iterdir():
                if subdir.is_dir():
                    potential_installer = subdir / 'installer.php'
                    if potential_installer.exists():
                        for item in subdir.iterdir():
                            shutil.move(str(item), str(site_path / item.name))
                        shutil.rmtree(subdir)
                        break
        
        print('Creating database...')
        self.mysql.create_database(site_name)
        
        add_ssl(site_path)
        webbrowser.open(f'https://{site_name}.test/installer.php')
        
        print('If you have completed the installation via the web installer.')
        print('Please run the following commands to finalize setup:')
        is_finished = get_confirmation('Have you completed the installation via the web installer? (Y/n): ',
                                       default=True)
        
        if is_finished:
            self.reset_admin_info([site_name])
            self.setup_wp_options([site_name])
