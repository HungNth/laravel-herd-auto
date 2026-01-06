class MySQL:
    def __init__(self):
        import config
        self.config = config
        self.host = self.config.db_host
        self.user = self.config.db_username
        self.password = self.config.db_password
        self.socket = self.config.db_socket
    
    def get_os(self):
        pass
    
    def connect(self):
        pass
