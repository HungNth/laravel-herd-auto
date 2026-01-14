from typing import Literal
import httpx

from utils.config_parse import parse_config

config = parse_config()


class WPApi:
    def __init__(self):
        self.themes = config.get('themes')
        self.plugins = config.get('plugins')
        self.base_url = config.get('api_base_url')
        self.api_key = config.get('api_key')

    def build_api(self, slug):
        api_endpoint = f"{self.base_url}packages/{slug}/metadata/license/{self.api_key}"
        return api_endpoint

    def get_latest_version(self, slug):
        response = httpx.get(self.build_api(slug), timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            latest_version = data.get('version')
            return latest_version
        return None

    def get_download_url(self, slug):
        response = httpx.get(self.build_api(slug), timeout=10)
        response.raise_for_status()

        if response.status_code == 200:
            data = response.json()
            download_url = data.get('download_url')
            return download_url
        return None

    def get_download_urls(self, slugs: list[str]):
        download_urls = []
        for slug in slugs:
            url = self.get_download_url(slug)
            if url:
                download_urls.append(url)
        return download_urls

    def print_list(self, item_type: Literal["theme", "plugin"]):
        if item_type == "theme":
            items = self.themes
        else:
            items = self.plugins

        for index, item in enumerate(items, start=1):
            print(f"{index}. {item['name']} (slug: {item['slug']})")

    def select_packages(self, item_type: Literal["theme", "plugin"]):
        from utils.user_input import clean_selection, get_confirmation

        if item_type == "theme":
            items = self.themes
        else:
            items = self.plugins

        selected_item_slugs = []
        self.print_list(item_type)

        while True:
            try:
                print(f"Select {item_type}s to install (e.g., 1 2 3 or 1,3,5). Enter 0 for all {item_type}s.")
                selection = input("Your selection: ")
                cleaned_selection = clean_selection(selection)
                cleaned_selection = [int(i) for i in cleaned_selection]

                if 0 in cleaned_selection:
                    if get_confirmation(f"You have selected all {item_type}s. Do you want to continue? (y/N): ",
                                        default=False):
                        for item in items:
                            selected_item_slugs.append(item['slug'])
                        return selected_item_slugs
                    else:
                        continue

                for i in cleaned_selection:
                    if 1 <= i <= len(items):
                        selected_item_slugs.append(items[i - 1]['slug'])
                    else:
                        print(f"Please enter a number from 1 to {len(items)}!")
                        break
                else:
                    break

            except ValueError:
                print("Please enter a number!")

        return selected_item_slugs
