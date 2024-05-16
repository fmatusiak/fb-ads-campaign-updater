from services.facebook_business_api import FacebookBusinessApi


class FacebookAdsService:
    def __init__(self, api: FacebookBusinessApi):
        self.__api = api
