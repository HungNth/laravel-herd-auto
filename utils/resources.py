class Resources:
    def __init__(self):
        import os_helper
        self.herd_sites_path, self.herd_cached_path, self.herd_bin_path = os_helper.herd_path()
    
    def wp_local_version(self):
        pass
