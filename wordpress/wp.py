class WordPress:
    def __init__(self):
        import config
        self.config = config
        self.wp_version_api = self.config.wp_version_api
    
    def wp_latest_version(self):
        import requests
        try:
            response = requests.get(self.wp_version_api)
            if response.status_code == 200:
                data = response.json()
                version = data["offers"][0]["version"]
                return version
            else:
                print(f"Error: Unable to fetch WordPress versions. Status code: {response.status_code}")
                return ""
        except Exception as e:
            print(f"Exception occurred: {e}")
            return ""
    
    def need_update(self):
        pass
    
    def install_wp(self):
        pass
    
    def configure_wp(self):
        pass
