import shutil

from utils.os_helper import herd_path


class WordPress:
    def __init__(self):
        self.herd_sites_path, _, _ = herd_path()
    
    def create_website(self):
        from utils.user_input import get_admin_credentials
        
        from wordpress.wp_cli import wpcli
        site_name, admin_name_input, admin_pass_input, admin_email_input = get_admin_credentials()
        wpcli.wp_install(site_name, admin_name_input, admin_pass_input, admin_email_input)
    
    def delete_websites(self):
        selected_sites = self.choose_website()
        for site in selected_sites:
            self.delete_website(site)
    
    def delete_website(self, site_name):
        from db.mysql import mysql
        site_path = self.herd_sites_path / site_name
        
        if site_path.exists():
            try:
                shutil.rmtree(site_path)
                mysql.drop_database(site_name)
                print(f'Website "{site_name}" and its database have been deleted successfully.\n')
            except Exception as e:
                print(f'Error deleting website "{site_name}": {e}')
                return
    
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
    
    def is_website_exists(self, site_name):
        site_path = self.herd_sites_path / site_name
        return site_path.exists()
    
    def get_site_list(self):
        site_list = []
        for site in self.herd_sites_path.iterdir():
            if site.is_dir():
                site_list.append(site.name)
        return site_list
    
    def choose_website(self):
        site_list = self.get_site_list()
        selected_websites = []
        
        self.print_site_list()
        
        while True:
            try:
                site_index = input(
                    "Enter the website numbers you want to select\n"
                    "(separated by commas, for example: 1,2,3 or 0 to select all): "
                ).replace(" ", ",").split(",")
                
                site_index = [int(x) for x in site_index]
                
                if 0 in site_index:
                    return site_list
                
                for index in site_index:
                    if 1 <= index <= len(site_list):
                        selected_websites.append(site_list[index - 1])
                    else:
                        print(f"Please enter a number from 1 to {len(site_list)}!")
                        break
                else:
                    break
            
            except ValueError:
                print("Please enter a number!")
        
        return selected_websites


wp = WordPress()
