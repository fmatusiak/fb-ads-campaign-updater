import requests
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.adset import AdSet
from facebook_business.adobjects.business import Business
from facebook_business.api import FacebookAdsApi

from app_errors import AppError, create_http_error
from config import Config
from models.ad_creative_builder import AdCreativeBuilder
from models.adset_fb import AdSetFb
from models.campaign_fb import CampaignFb


class FacebookBusinessApi:
    def __init__(self, config: Config):
        self.config = config
        self.__initFacebookApi()
        self.version = self.config.getVersion()
        self.timeout = 120

    def __initFacebookApi(self):
        try:
            FacebookAdsApi.init(
                self.config.getAppId(),
                self.config.getAppSecret(),
                self.config.getAccessToken(),
                api_version=self.config.getVersion()
            )
        except Exception as e:
            raise AppError("Blad inicjalizacji Facebook API", cause=e)

    def __headers(self, jsonContent=False):
        headers = {
            "Authorization": f"Bearer {self.config.getAccessToken()}"
        }

        if jsonContent:
            headers["Content-Type"] = "application/json"

        return headers

    def __requestJson(self, operation, method, url, **kwargs):
        try:
            response = requests.request(
                method,
                url,
                headers=kwargs.pop("headers", self.__headers()),
                timeout=kwargs.pop("timeout", self.timeout),
                **kwargs
            )
            response.raise_for_status()

            return response.json()
        except requests.HTTPError as exc:
            raise create_http_error(operation, exc.response, url) from exc
        except requests.RequestException as exc:
            raise AppError(
                f"Blad polaczenia z Meta API podczas kroku: {operation}",
                detail=str(exc),
                context={"URL": url},
                cause=exc,
            ) from exc

    def getMyAccount(self):
        try:
            myAccount = AdAccount.get_my_account()

            return myAccount
        except Exception as e:
            raise AppError("Blad pobierania kont reklamowych", cause=e)

    def getRequest(self, url):
        try:
            return self.__requestJson("pobieranie danych z paginacji", "GET", url)
        except Exception as e:
            raise AppError("Blad zapytania HTTP", cause=e)

    def getCampaigns(self, accountId):
        try:
            url = f"https://graph.facebook.com/{self.version}/{accountId}/campaigns?fields=id,name,status"

            return self.__requestJson("pobieranie listy kampanii", "GET", url)
        except Exception as e:
            raise AppError(
                "Blad pobierania kampanii reklamowych",
                context={"account_id": accountId},
                cause=e,
            )

    def getCampaignData(self, campaignId):
        try:
            url = (
                f"https://graph.facebook.com/{self.version}/{campaignId}"
                "?fields=id,name,status,daily_budget,start_time,stop_time,"
                "smart_promotion_type,objective,advantage_state_info"
            )

            data = self.__requestJson("pobieranie danych kampanii", "GET", url)

            return CampaignFb(data)
        except Exception as e:
            raise AppError(
                "Blad pobierania danych kampanii",
                context={"campaign_id": campaignId},
                cause=e,
            )

    def updateCampaign(self, campaignFb: CampaignFb):
        try:
            url = f"https://graph.facebook.com/{self.version}/{campaignFb.getId()}"

            campaignData = campaignFb.getData()

            return self.__requestJson(
                "aktualizacja kampanii",
                "POST",
                url,
                headers=self.__headers(jsonContent=True),
                json=campaignData,
            )
        except Exception as e:
            raise AppError(
                "Blad aktualizacji kampanii",
                context={"campaign_id": campaignFb.getId()},
                cause=e,
            )

    def renameCampaign(self, campaignId, name):
        try:
            url = f"https://graph.facebook.com/{self.version}/{campaignId}"

            return self.__requestJson(
                "oznaczanie zarchiwizowanej kampanii",
                "POST",
                url,
                headers=self.__headers(jsonContent=True),
                json={"name": name},
            )
        except Exception as e:
            raise AppError(
                "Blad oznaczania zarchiwizowanej kampanii",
                context={"campaign_id": campaignId},
                cause=e,
            )

    def copyCampaign(self, campaignId):
        try:
            url = f"https://graph.facebook.com/{self.version}/{campaignId}/copies"

            data = self.__requestJson(
                "kopiowanie kampanii",
                "POST",
                url,
                headers=self.__headers(jsonContent=True),
            )

            if 'copied_campaign_id' in data:
                copiedCampaignId = data['copied_campaign_id']

                return self.getCampaignData(copiedCampaignId)
            else:
                raise AppError("Meta API nie zwrocilo ID skopiowanej kampanii")

        except Exception as e:
            raise AppError(
                "Blad kopiowania kampanii",
                context={"campaign_id": campaignId},
                cause=e,
            )

    def getBusinesses(self):
        try:
            url = f"https://graph.facebook.com/{self.version}/me?fields=businesses"

            data = self.__requestJson("pobieranie firm", "GET", url)

            return data['businesses']['data']
        except Exception as e:
            raise AppError("Blad pobierania firm", cause=e)

    def getAdAccounts(self, businessId):
        try:
            business = Business(fbid=businessId)
            adAccounts = business.get_owned_ad_accounts(fields=['id', 'name'])

            return adAccounts
        except Exception as e:
            raise AppError(
                "Blad pobierania kont reklamowych Ad",
                context={"business_id": businessId},
                cause=e,
            )

    def getAdsForCampaign(self, campaignId, statuses=None):
        try:
            ads = AdSet(campaignId).get_ads(fields={
                Ad.Field.id,
                Ad.Field.name,
                Ad.Field.status,
                Ad.Field.creative,
                Ad.Field.adset_id
            })

            if statuses:
                return [ad for ad in ads if ad.get('status') in statuses]
            else:
                return ads
        except Exception as e:
            raise AppError(
                "Blad pobierania reklam Ads dla kampanii",
                context={"campaign_id": campaignId},
                cause=e,
            )

    def getAd(self, adId):
        try:
            return Ad(adId).api_get(fields={
                Ad.Field.name,
                Ad.Field.targeting,
            })
        except Exception as e:
            raise AppError(
                "Blad pobierania reklamy",
                context={"ad_id": adId},
                cause=e,
            )

    def getAdSet(self, adSetId):
        try:
            adSet = AdSet(adSetId)
            adSet.api_get(fields=[
                AdSet.Field.id,
                AdSet.Field.name,
                AdSet.Field.targeting,
                AdSet.Field.end_time
            ])

            return AdSetFb(adSet.export_all_data())
        except Exception as e:
            raise AppError(
                "Blad pobierania zestawu reklam AdSet",
                context={"adset_id": adSetId},
                cause=e,
            )

    def createCreativeAd(self, adAccountId, adCreativeBuilder: AdCreativeBuilder):
        try:
            adAccount = AdAccount(adAccountId)

            data = adCreativeBuilder.getData()

            adCreative = adAccount.create_ad_creative(params=data)

            return adCreative
        except Exception as e:
            raise AppError(
                "Blad tworzenia reklamy CreativeAd",
                context={"ad_account_id": adAccountId},
                cause=e,
            )

    def attachNewCreativeAdToCreativeAd(self, adId, newCreativeAdId):
        try:
            url = f"https://graph.facebook.com/{self.version}/{adId}?fields=creative"

            data = {
                "creative": {
                    "creative_id": newCreativeAdId
                }
            }

            jsonResponse = self.__requestJson(
                "podpinanie nowej kreacji do reklamy",
                "POST",
                url,
                headers=self.__headers(jsonContent=True),
                json=data,
            )

            if "creative" in jsonResponse and jsonResponse["creative"]:
                return True
            else:
                raise AppError("Meta API nie potwierdzilo podpiecia nowej kreacji")
        except Exception as e:
            raise AppError(
                "Blad podpinania nowej kreacji do reklamy",
                context={"ad_id": adId, "creative_id": newCreativeAdId},
                cause=e,
            )

    def updateAdSet(self, adSetFb: AdSetFb):
        try:
            url = f"https://graph.facebook.com/{self.version}/{adSetFb.getId()}"

            adSetData = adSetFb.getData()

            return self.__requestJson(
                "aktualizacja AdSet",
                "POST",
                url,
                headers=self.__headers(jsonContent=True),
                json=adSetData,
            )
        except Exception as e:
            raise AppError(
                "Blad aktualizacji AdSet",
                context={"adset_id": adSetFb.getId()},
                cause=e,
            )

    def getAdCreativeData(self, adCreativeId):
        try:
            adCreative = AdCreative(adCreativeId)
            adCreative.api_get(fields={
                AdCreative.Field.name,
                AdCreative.Field.object_story_spec,
                AdCreative.Field.asset_feed_spec,
                AdCreative.Field.degrees_of_freedom_spec,
            })

            return adCreative.export_all_data()
        except Exception as e:
            raise AppError(
                "Blad pobierania danych kreatywnej reklamy AdCreative",
                context={"creative_id": adCreativeId},
                cause=e,
            )
