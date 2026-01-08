import shutil
from pathlib import Path
from typing import Literal

import config
from utils.commands import run_command
from utils.herd import add_ssl, is_herd_open
from utils.os_helper import herd_path
from utils.user_input import get_input, clean_input, get_confirmation, get_input_options
from utils.time_helper import formatted_time

herd_sites_path, _, _ = herd_path()


class WordPress:
    def __init__(self, wpc_li, wp_api, mysql):
        self.wp_cli = wpc_li
        self.wp_api = wp_api
        self.mysql = mysql
    
    def get_admin_credentials(self):
        admin_username = config.admin_username
        admin_password = config.admin_password
        admin_email = config.admin_email
        
        if not self.mysql.check_db_connection():
            print('Cannot connect to the database. Please check your database settings.')
            exit(1)
        
        if not is_herd_open():
            print('The Herd Desktop application is not running. Please start Herd and try again.')
            exit(1)
        
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
            admin_pass_input = get_input(f'Enter the admin password "{admin_password}":', default=admin_password,
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
        
        self.wp_cli.wp_install(site_name, admin_username, admin_password, admin_email)
        if len(selected_themes) == 0:
            selected_themes = [config.default_theme_slug]
            self.install_packages(site_path, selected_themes, item_type="theme")
        
        if len(selected_plugins) > 0:
            self.install_packages(site_path, selected_plugins, item_type="plugin")
        if is_setup_wp_config:
            self.wp_cli.wp_options_set(site_path)
        
        add_ssl(site_path)
    
    def delete_websites(self):
        selected_sites = self.select_websites()
        if not selected_sites:
            exit(0)
        
        print(f'You have selected the following websites for deletion: {", ".join(selected_sites)}')
        if not get_confirmation("Are you sure you want to delete these websites? This action cannot be undone. (y/N): ",
                                default=False):
            print("Deletion cancelled by user.")
            exit(0)
        
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
                print(f'Error deleting website "{site_name}": {e}')
                return
    
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
        
        selected_pkg_urls = self.wp_api.get_download_urls(selected_pkg_slugs)
        
        if item_type == "theme":
            self.wp_cli.install_themes(selected_pkg_urls, path)
        elif item_type == "plugin":
            self.wp_cli.install_plugins(selected_pkg_urls, path)
    
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
            '1. Reset Admin information to default',
            '2. Setup WordPress options',
            '3. Both 1 and 2',
            '4. Exit'
        ]
        print("Select an option to configure WordPress:")
        for option in options:
            print(option)
        choice = get_input('Your choice (1-4): ', required=True)
        if choice == '4':
            exit(0)
        
        if choice not in ['1', '2', '3']:
            print("Invalid choice. Please select a valid option.")
            return self.configure_wp()
        
        selected_website = self.select_websites()
        
        if choice == '1':
            self.reset_admin_info(selected_website)
        elif choice == '2':
            self.setup_wp_options(selected_website)
        elif choice == '3':
            self.reset_admin_info(selected_website)
            self.setup_wp_options(selected_website)
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
            
            print(f'Deleting all transients...')
            self.wp_cli.delete_all_transients(site_path)
            print(f'Clearing cache...')
            self.wp_cli.cache_clear(site_path)
            print(f'Exporting database...')
            self.wp_cli.export_db(site_path)
            
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
            run_command(command, shell=False)
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
            ai1wmu = self.wp_cli.is_plugin_installed(required_plugin, site_path)
            if not ai1wmu:
                print('All-in-One WP Migration Unlimited Extension plugin is not installed.')
                print('Installing All-in-One WP Migration Unlimited Extension plugin...')
                plugin_url = self.wp_api.get_download_url(required_plugin)
                self.wp_cli.install_plugins(['all-in-one-wp-migration', plugin_url], site_path)
            self.wp_cli.activate_plugin(required_plugin, site_path)
            
            print(f'Backing up site "{site}" to ".wpress"...')
            result = self.wp_cli.ai1_backup(site_path)
            wpress_path = ''
            wpress_parent_path = ''
            if 'Backup location' in result:
                wpress_path = result.split('Backup location: ')[1].strip()
                wpress_parent_path = Path(wpress_path).parent
            
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
            run_command(command, shell=False)
            print(f'Backup for site "{site}" created at "{backup_path}"')
            
            self.wp_cli.activate_all_plugins(site_path)
    
    def restore_options(self):
        options = [
            'Restore by full source code and database include',
            'Restore by wp-content only',
            'Restore by plugin All-in-One WP Migration (.wpress file)',
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
    
    def restore_full_source(self):
        print("Restoring full source code...")
    
    def restore_by_wp_content(self):
        print("Restoring wp-content only")
    
    def restore_by_wpress(self):
        print("Restoring with All-in-One WP Migration plugin")
    
    def restore_by_duplicator(self):
        print('Restoring with Duplicator plugin')
