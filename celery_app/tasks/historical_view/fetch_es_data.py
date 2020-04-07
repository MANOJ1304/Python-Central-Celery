from cross_shopping_analytics.utility import pull_data, normalization

class ESDataFetch(object):
    
    def __init__(self, config):
        self.config = config
  
    def get_plain_data(self):
        
        config = [
            self.config.get('es').get("index"),
            self.config.get('es').get("username"),
            self.config.get('es').get("password"),
            self.config.get('es').get("search_query"),
            self.config.get('es').get("host"),
            self.config.get('es').get("port"),
        ]


        data = pull_data(*config)
        
        return data 