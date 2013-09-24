
PROVIDERS = {
        "FACEBOOK": ("FACEBOOK_APP_ID", "FACEBOOK_API_SECRET"),
        "TWITTER": ("TWITTER_CONSUMER_KEY", "TWITTER_CONSUMER_SECRET"),
        "LINKEDIN": ("LINKEDIN_CONSUMER_KEY", "LINKEDIN_CONSUMER_SECRET"),
}

class ProviderManager(object):
    def __init__(self, provider_data_dict):
        self.provider_data = provider_data_dict

    def create_settings_chunk(self):
        """
        NYI
        should return a settings codechunk w all the stuff in it.
        """
