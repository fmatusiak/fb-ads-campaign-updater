import requests
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.business import Business
from facebook_business.api import FacebookAdsApi

from config import Config
from models.ad_creative_builder import AdCreativeBuilder
from models.adset_fb import AdSetFb
from models.campaign_fb import CampaignFb


class FacebookBusinessApi:
    def __init__(self, config: Config):
        self.config = config
        self.__initFacebookApi()

    def __initFacebookApi(self):
        try:
            FacebookAdsApi.init(
                self.config.getAppId(),
                self.config.getAppSecret(),
                self.config.getAccessToken()
            )
        except Exception as e:
            raise Exception("Wystąpił błąd podczas inicjalizacji Facebook API:", e)

    def getMyAccount(self):
        try:
            myAccount = AdAccount.get_my_account()

            return myAccount
        except Exception as e:
            raise Exception("Wystąpił błąd podczas pobierania kont reklamowych:", e)

    def getCampaigns(self, accountId, statuses=None):
        try:
            adAccount = AdAccount(accountId)
            campaigns = adAccount.get_campaigns(fields=['id', 'name', 'status'])

            if statuses:
                return [campaign for campaign in campaigns if campaign['status'] in statuses]
            else:
                return campaigns
        except Exception as e:
            raise Exception("Wystąpił błąd podczas pobierania kampanii reklamowych:", e)

    def getCampaignData(self, campaignId):
        try:
            url = f"https://graph.facebook.com/v19.0/{campaignId}?fields=id,name,status,daily_budget,start_time,stop_time"

            headers = {
                "Authorization": f"Bearer {self.config.getAccessToken()}"
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            return CampaignFb(data)
        except Exception as e:
            raise Exception("Wystąpił błąd z pobraniem kampanii", e)

    def updateCampaign(self, campaignFb: CampaignFb):
        try:
            url = f"https://graph.facebook.com/v19.0/{campaignFb.getId()}"

            headers = {
                "Authorization": f"Bearer {self.config.getAccessToken()}",
                "Content-Type": "application/json"
            }

            campaignData = campaignFb.getCampaignData()

            response = requests.post(url, headers=headers, json=campaignData)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            raise Exception("Wystąpił błąd z aktualizacją kampanii", e)

    def copyCampaign(self, campaignId):
        try:
            url = f"https://graph.facebook.com/v19.0/{campaignId}/copies"

            headers = {
                "Authorization": f"Bearer {self.config.getAccessToken()}",
                "Content-Type": "application/json"
            }

            response = requests.post(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            if 'copied_campaign_id' in data:
                copiedCampaignId = data['copied_campaign_id']

                return self.getCampaignData(copiedCampaignId)
            else:
                raise Exception("Nie udało się skopiować kampanii")

        except Exception as e:
            raise Exception("Wystapił błąd z kopiowaniem kampanii", e)

    def getBusinesses(self):
        try:
            url = "https://graph.facebook.com/v19.0/me?fields=businesses"

            headers = {
                "Authorization": f"Bearer {self.config.getAccessToken()}"
            }

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            return response.json()['businesses']['data']
        except Exception as e:
            raise Exception("Wystąpił błąd podczas pobierania biznesów:", e)

    def getAdAccounts(self, businessId):
        try:
            business = Business(fbid=businessId)
            adAccounts = business.get_owned_ad_accounts(fields=['id', 'name'])

            return adAccounts
        except Exception as e:
            raise Exception("Wystąpił błąd podczas pobierania ID konta reklamowego:", e)

    # pobranie reklam z zestawu reklam
    def getAdsForCampaign(self, campaignId, statuses=None):
        try:
            ads = AdSet(campaignId).get_ads(fields=['id', 'name', 'status', 'creative'])

            if statuses:
                return [ad for ad in ads if ad['status'] in statuses]
            else:
                return ads
        except Exception as e:
            raise Exception("Wystąpił błąd podczas pobierania reklam dla danej kampanii:", e)

    def getAd(self, adId):
        try:
            return Ad(adId).api_get(fields={
                Ad.Field.name,
                Ad.Field.targeting,
            })
        except Exception as e:
            raise Exception("Wystąpił błąd podczas Ad sets dla danej kampanii:", e)

    def getAdSet(self, adId):
        try:
            adSet = AdSet(adId)
            adSet.api_get(fields=[
                AdSet.Field.name,
                AdSet.Field.targeting,
                AdSet.Field.adlabels,
                AdSet.Field.daily_budget,
                AdSet.Field.start_time,
                AdSet.Field.end_time,
            ])

            return AdSetFb(adSet.export_all_data())
        except Exception as e:
            raise Exception("Wystąpił błąd podczas pobierania zestawu reklam:", e)

    def createCreativeAd(self, adAccountId, adCreativeBuilder: AdCreativeBuilder):
        try:
            adAccount = AdAccount(adAccountId)

            data = adCreativeBuilder.getData()

            adCreative = adAccount.create_ad_creative(params=data)

            return adCreative
        except Exception as e:
            raise Exception("Wystąpił błąd podczas tworzenia reklamy:", e)

    def attachNewCreativeAdToCreativeAd(self, newCreativeAdId, existsCreativeAdId):
        try:
            url = f"https://graph.facebook.com/v19.0/{newCreativeAdId}"

            data = {
                "creative": {
                    "creative_id": existsCreativeAdId
                }
            }

            response = requests.post(url, json=data)

            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            raise Exception("Wystapił błąd z przypięciem nowej reklamy do aktualnej reklamy")

    def updateAdSet(self, adSetFb: AdSetFb):
        try:
            url = f"https://graph.facebook.com/v19.0/{adSetFb.getId()}"

            headers = {
                "Authorization": f"Bearer {self.config.getAccessToken()}",
                "Content-Type": "application/json"
            }

            adSetData = adSetFb.getData()

            response = requests.post(url, headers=headers, json=adSetData)
            response.raise_for_status()

            return response.json()
        except Exception as e:
            raise Exception("Wystąpił błąd podczas aktualizacji danych zestawu reklam:", e)

    def getAdCreativeData(self, adCreativeId):
        adCreative = AdCreative(adCreativeId)
        adCreative.api_get(fields={
            AdCreative.Field.name,
            AdCreative.Field.object_story_spec,
            AdCreative.Field.asset_feed_spec,
            AdCreative.Field.degrees_of_freedom_spec
        })

        return adCreative.export_all_data()
