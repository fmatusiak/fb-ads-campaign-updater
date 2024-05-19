from models.ad_creative_builder import AdCreativeBuilder
from services.facebook_business_api import FacebookBusinessApi
from text_modifier import TextModifier


class FacebookAdsService:
    def __init__(self, api: FacebookBusinessApi):
        self.__api = api
        self.__textModifier = TextModifier()

    def update(self, adAccountId: str, campaignId: str, data: dict) -> None:
        try:
            data = self.processInputData(data)
            ads = self.__api.getAdsForCampaign(campaignId)

            for ad in ads:
                self.updateSingleAd(adAccountId, ad, data)

            self.updateCampaign(campaignId, data)

        except Exception as e:
            raise Exception(f"Wystapił błąd z aktualizacją Ads : {e}")

    def processInputData(self, data: dict) -> dict:
        fields = [
            'carouselHeaderDescription', 'carouselHeaderName', 'basicDescription',
            'shortDescription', 'singleHeaderName', 'singleHeaderDescription',
            'singleBasicDescription'
        ]
        for field in fields:
            if field in data and not isinstance(data[field], list):
                data[field] = [data[field]]
        return data

    def updateSingleAd(self, adAccountId: str, ad: dict, data: dict) -> None:
        try:
            adCreativeId = ad['creative']['id']
            adId = ad['id']
            adSetId = ad['adset_id']

            adCreativeData = self.__api.getAdCreativeData(adCreativeId)
            adCreativeBuilder = AdCreativeBuilder()
            adCreativeBuilder.copyAdCreativeData(adCreativeData)

            self.updateCreativeAds(adCreativeBuilder, data)

            modifiedData = self.__textModifier.modifyDictionaryByKey(data, adCreativeBuilder.getData())
            adCreativeBuilder.setData(modifiedData)

            creativeUpdatedResult = self.createAndAttachNewCreativeAd(adAccountId, adCreativeBuilder, adId)

            if not creativeUpdatedResult:
                raise Exception('Failed to update creative')

            self.updateAdSet(adSetId, data)

        except Exception as e:
            raise Exception(f"Wystapił błąd z aktualizacją Ad {adId}: {e}")

    def updateCreativeAds(self, adCreativeBuilder: AdCreativeBuilder, data: dict) -> None:
        buildDataMappings = {
            'singleHeaderName': 'singleHeaderNames',
            'singleHeaderDescription': 'singleHeaderDescriptions',
            'singleBasicDescription': 'singleBasicDescriptions',
            'carouselHeader': 'carouselHeaderNames',
            'carouselHeaderDescription': 'carouselHeaderDescriptions',
            # Uncomment the lines below if needed
            # 'basicDescription': 'basicDescriptions',
            # 'shortDescription': 'shortDescriptions'
        }
        for key, value in buildDataMappings.items():
            if key in data:
                adCreativeBuilder.buildData(value, data[key])

    def createAndAttachNewCreativeAd(self, adAccountId: str, adCreativeBuilder: AdCreativeBuilder, adId: str) -> bool:
        adCreative = self.__api.createCreativeAd(adAccountId, adCreativeBuilder)
        return self.__api.attachNewCreativeAdToCreativeAd(adId, adCreative['id'])

    def updateAdSet(self, adSetId: str, data: dict) -> None:
        try:
            adSet = self.__api.getAdSet(adSetId)

            if 'latitude' in data:
                adSet.setLatitude(data['latitude'])
            if 'longitude' in data:
                adSet.setLongitude(data['longitude'])
            if 'radius' in data:
                adSet.setRadius(data['radius'])
            if 'daily_budget' in data:
                adSet.setDailyBudget(data['daily_budget'])
            if 'end_time' in data:
                adSet.setEndTime(data['end_time'])

            modifiedData = self.__textModifier.modifyDictionaryByKey(data, adSet.getData())
            adSet.setData(modifiedData)

            adSetUpdated = adSet.update(self.__api)

            if not adSetUpdated:
                raise Exception('Failed to update ad set')

        except Exception as e:
            raise Exception(f"Wystapił błąd z aktualizacją AdSet {adSetId}: {e}")

    def updateCampaign(self, campaignId: str, data: dict) -> None:
        try:
            campaign = self.__api.getCampaignData(campaignId)

            if 'end_time' in data:
                campaign.setStopTime(data['end_time'])
            if 'campaign_name' in data:
                campaign.setName(data['campaign_name'])

            campaign.setStatus('PAUSED')

            modifiedData = self.__textModifier.modifyDictionaryByKey(data, campaign.getData())
            campaign.setData(modifiedData)

            campaign.update(self.__api)

        except Exception as e:
            raise Exception(f"Wystapił błąd z aktualizacją Campaign {campaignId}: {e}")
