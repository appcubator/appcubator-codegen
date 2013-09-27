from codes.utils import AssignStatement


PROVIDERS = {
        "FACEBOOK": ("FACEBOOK_APP_ID", "FACEBOOK_API_SECRET"),
        "TWITTER": ("TWITTER_CONSUMER_KEY", "TWITTER_CONSUMER_SECRET"),
        "LINKEDIN": ("LINKEDIN_CONSUMER_KEY", "LINKEDIN_CONSUMER_SECRET"),
}


class IncompleteProviderData(Exception):
    pass

class ProviderManager(object):
    def __init__(self, provider_data_dict):
        self.provider_data = provider_data_dict

    def create_settings_chunk(self):
        """
        should return a settings codechunk w all the stuff in it.
        """
        # Iterate over providers, and if key is found, then add all provider data as assign statements
        assign_chunks = []
        for k in PROVIDERS:
            if k not in self.provider_data:
                continue
            for k2 in PROVIDERS[k]:
                if k2 not in PROVIDERS[k]:
                    raise IncompleteProviderData
                ac = AssignStatement(k2, PROVIDERS[k][k2])
                assign_chunks.append(ac)

        # TODO validate in analyzer that the keys are strings in ASCII range
        cast_and_join_chunks = lambda: "\n".join([str(chunk) for chunk in assign_chunks])
        return FnCodeChunk(cast_and_join_chunks)
