from facebook_business.adobjects.campaign import Campaign

from app_errors import AppError
from models.ad_creative_builder import AdCreativeBuilder
from services.facebook_business_api import FacebookBusinessApi
from text_modifier import TextModifier


class FacebookAdsService:
    CREATIVE_UPDATE_FIELDS = {
        'single_header_name',
        'single_header_description',
        'single_basic_description',
        'carousel_header',
        'carousel_header_description',
        'basic_description',
        'short_description',
        'url_address',
        'singleHeaderName',
        'singleHeaderDescription',
        'singleBasicDescription',
        'carouselHeaderName',
        'carouselHeaderDescription',
        'basicDescription',
        'shortDescription',
    }

    def __init__(self, api: FacebookBusinessApi):
        self.__api = api
        self.__textModifier = TextModifier()

    def update(self, adAccountId: str, campaignId: str, data: dict) -> None:
        try:
            data = self.processInputData(data)
            campaign = self.__api.getCampaignData(campaignId)
            self.ensureCampaignCanBeUpdated(campaign)
            ads = self.__api.getAdsForCampaign(campaignId)
            adUpdateErrors = []

            for ad in ads:
                try:
                    self.updateSingleAd(adAccountId, ad, data)
                except Exception as e:
                    adUpdateErrors.append(str(e))

            if ads and len(adUpdateErrors) == len(ads):
                raise AppError(
                    "Nie udalo sie zaktualizowac zadnej reklamy w kampanii",
                    detail="\n---\n".join(adUpdateErrors),
                    context={
                        "campaign_id": campaignId,
                        "liczba reklam z bledem": len(adUpdateErrors),
                    },
                    hint=(
                        "sprawdz pierwszy blad z listy ponizej. Zwykle wskazuje konkretny AdSet, "
                        "reklame albo kreacje, ktora blokuje cala aktualizacje."
                    ),
                )

            self.updateCampaign(campaign, data)

            if adUpdateErrors:
                raise AppError(
                    "Kampania zostala zaktualizowana czesciowo",
                    detail="\n---\n".join(adUpdateErrors),
                    context={
                        "campaign_id": campaignId,
                        "liczba nieudanych reklam": len(adUpdateErrors),
                    },
                    hint=(
                        "kampania zostala ruszona, ale czesc reklam ma osobny problem. "
                        "Sprawdz ID reklam/kreacji wymienione w bledach."
                    ),
                )

        except Exception as e:
            raise AppError(
                "Blad aktualizacji kampanii z Excela",
                context={"campaign_id": campaignId, "ad_account_id": adAccountId},
                cause=e,
            )

    def processInputData(self, data: dict) -> dict:
        fields = [
            'carousel_header_description', 'carousel_header', 'basic_description',
            'short_description', 'single_header_name', 'single_header_description',
            'single_basic_description', 'carouselHeaderDescription', 'carouselHeaderName',
            'basicDescription', 'shortDescription', 'singleHeaderName',
            'singleHeaderDescription', 'singleBasicDescription'
        ]
        for field in fields:
            if field in data and not isinstance(data[field], list):
                data[field] = [data[field]]
        return data

    def updateSingleAd(self, adAccountId: str, ad: dict, data: dict) -> None:
        adId = ad.get('id')
        adName = ad.get('name')
        adCreativeId = ad.get('creative', {}).get('id')
        adSetId = ad.get('adset_id')
        creativeSourceRefs = None
        stage = "start aktualizacji reklamy"

        try:
            if self.hasCreativeUpdates(data):
                stage = "sprawdzenie ID kreacji"
                if not adCreativeId:
                    raise AppError("Brak ID kreacji przy reklamie")

                stage = "pobieranie danych starej kreacji"
                adCreativeData = self.__api.getAdCreativeData(adCreativeId)
                creativeSourceRefs = self.extractCreativeSourceRefs(adCreativeData)
                adCreativeBuilder = AdCreativeBuilder()
                adCreativeBuilder.copyAdCreativeData(adCreativeData)

                stage = "podmiana tekstow/URL w nowej kreacji"
                self.updateCreativeAds(adCreativeBuilder, data)

                modifiedData = self.__textModifier.modifyDictionaryByKey(data, adCreativeBuilder.getData())
                adCreativeBuilder.setData(modifiedData)

                stage = "tworzenie i podpinanie nowej kreacji"
                creativeUpdatedResult = self.createAndAttachNewCreativeAd(adAccountId, adCreativeBuilder, adId)

                if not creativeUpdatedResult:
                    raise AppError("Meta API nie potwierdzilo aktualizacji reklamy")

            stage = "aktualizacja AdSet"
            self.updateAdSet(adSetId, data)

        except Exception as e:
            context = self.formatAdErrorContext(adId, adName, adCreativeId, creativeSourceRefs)
            raise AppError(
                "Blad aktualizacji reklamy",
                detail=self.formatAdUpdateError(e),
                context={"etap": stage, "ad": context, "adset_id": adSetId},
                cause=e,
            )

    def hasCreativeUpdates(self, data: dict) -> bool:
        return any(key in self.CREATIVE_UPDATE_FIELDS or self.isPlaceholderKey(key) for key in data)

    def ensureCampaignCanBeUpdated(self, campaign) -> None:
        if campaign.isLegacyAdvantagePlusCampaign():
            raise AppError(
                "Kampania jest starym typem Advantage+ Shopping/App "
                f"({campaign.getSmartPromotionType()}). Meta blokuje aktualizacje "
                "takich kampanii przez Marketing API v25. Zmigruj kampanie w Ads Managerze "
                "do nowego Advantage+ setup i uruchom aktualizacje ponownie."
            )

    def isPlaceholderKey(self, key) -> bool:
        return isinstance(key, str) and key.startswith('{$') and key.endswith('}')

    def formatAdErrorContext(self, adId, adName, adCreativeId, creativeSourceRefs=None) -> str:
        details = []
        if adId:
            details.append(f"Ad {adId}")
        if adName:
            details.append(f"nazwa '{adName}'")
        if adCreativeId:
            details.append(f"Creative {adCreativeId}")
        if creativeSourceRefs:
            details.append(f"zrodlo {creativeSourceRefs}")

        if not details:
            return "Ad"

        return " / ".join(details)

    def extractCreativeSourceRefs(self, adCreativeData: dict) -> str:
        interestingKeys = {
            'object_story_id',
            'effective_object_story_id',
            'instagram_actor_id',
            'instagram_user_id',
            'page_id',
            'post_id',
            'video_id',
            'photo_id',
            'image_hash',
        }
        refs = []

        def collect(value):
            if isinstance(value, dict):
                for key, nestedValue in value.items():
                    if key in interestingKeys and nestedValue:
                        refs.append(f"{key}={nestedValue}")
                    collect(nestedValue)
            elif isinstance(value, list):
                for item in value:
                    collect(item)

        collect(adCreativeData.get('object_story_spec', {}))
        collect(adCreativeData.get('asset_feed_spec', {}))

        uniqueRefs = list(dict.fromkeys(refs))
        return ", ".join(uniqueRefs[:12])

    def formatAdUpdateError(self, error) -> str:
        message = str(error)
        lower_message = message.lower()
        is_unavailable_media_error = (
            '2446289' in message
            or 'rolka' in lower_message
            or 'reel' in lower_message
            or ('material' in lower_message and 'niekompletn' in lower_message)
            or ('materia' in lower_message and 'niekompletn' in lower_message)
        )

        if not is_unavailable_media_error:
            return message

        return (
            f"{message} | Prawdopodobna przyczyna: kreacja wskazuje na rolke/post, "
            "ktory zostal usuniety albo nie jest dostepny dla tego konta. "
            "Sprawdz wskazane ID Ad/Creative w Menedzerze reklam."
        )

    def updateCreativeAds(self, adCreativeBuilder: AdCreativeBuilder, data: dict) -> None:
        buildDataMappings = {
            'single_header_name': 'single_header_names',
            'single_header_description': 'single_header_descriptions',
            'single_basic_description': 'single_basic_descriptions',
            'carousel_header': 'carousel_header_names',
            'carousel_header_description': 'carousel_header_descriptions',
            'basic_description': 'basic_descriptions',
            'short_description': 'short_descriptions',
            'url_address': 'address_url',
            'singleHeaderName': 'single_header_names',
            'singleHeaderDescription': 'single_header_descriptions',
            'singleBasicDescription': 'single_basic_descriptions',
            'carouselHeaderName': 'carousel_header_names',
            'carouselHeaderDescription': 'carousel_header_descriptions',
            'basicDescription': 'basic_descriptions',
            'shortDescription': 'short_descriptions',
        }
        for key, value in buildDataMappings.items():
            if key in data:
                adCreativeBuilder.buildData(value, data[key])

    def createAndAttachNewCreativeAd(self, adAccountId: str, adCreativeBuilder: AdCreativeBuilder, adId: str) -> bool:
        adCreative = self.__api.createCreativeAd(adAccountId, adCreativeBuilder)

        return self.__api.attachNewCreativeAdToCreativeAd(adId, adCreative['id'])

    def updateAdSet(self, adSetId: str, data: dict) -> None:
        changedFields = []

        try:
            adSet = self.__api.getAdSet(adSetId)

            if 'latitude' in data:
                adSet.setLatitude(data['latitude'])
                changedFields.append('latitude')
            if 'longitude' in data:
                adSet.setLongitude(data['longitude'])
                changedFields.append('longitude')
            if 'radius' in data:
                adSet.setRadius(data['radius'])
                changedFields.append('radius')
            if 'daily_budget' in data:
                adSet.setDailyBudget(data['daily_budget'])
                changedFields.append('daily_budget')
            if 'end_time' in data:
                adSet.setEndTime(data['end_time'])
                changedFields.append('end_time')

            modifiedData = self.__textModifier.modifyDictionaryByKey(data, adSet.getData())
            adSet.setData(modifiedData)

            adSetUpdated = adSet.update(self.__api)

            if not adSetUpdated:
                raise AppError("Meta API nie potwierdzilo aktualizacji AdSet")

        except Exception as e:
            raise AppError(
                "Blad aktualizacji AdSet",
                context={
                    "adset_id": adSetId,
                    "zmieniane pola": ", ".join(changedFields) if changedFields else "brak pol AdSet w Excelu",
                },
                cause=e,
            )

    def updateCampaign(self, campaign, data: dict) -> None:
        try:
            changedFields = []

            if 'end_time' in data:
                campaign.setStopTime(data['end_time'])
                changedFields.append('end_time')
            if 'campaign_name' in data:
                campaign.setName(data['campaign_name'])
                changedFields.append('campaign_name')

            campaign.setStatus(Campaign.Status.paused)
            changedFields.append('status=PAUSED')

            modifiedData = self.__textModifier.modifyDictionaryByKey(data, campaign.getData())
            campaign.setData(modifiedData)

            campaign.update(self.__api)

        except Exception as e:
            raise AppError(
                "Blad aktualizacji Campaign",
                context={
                    "campaign_id": campaign.getId(),
                    "zmieniane pola": ", ".join(changedFields),
                },
                cause=e,
            )
