from date_parser import DateParser
from app_errors import AppError


class CampaignFb:
    def __init__(self, data):
        self.__data = data

    def setName(self, name):
        self.__data['name'] = name

    def setStatus(self, status):
        self.__data['status'] = status

    def setStartTime(self, startTime):
        self.__data['start_time'] = DateParser.parseToDateTime(startTime)

    def setStopTime(self, stopTime):
        self.__data['stop_time'] = DateParser.parseToDateTime(stopTime)

    def getId(self):
        return self.__data.get('id')

    def getName(self):
        return self.__data.get('name')

    def getStatus(self):
        return self.__data.get('status')

    def getSmartPromotionType(self):
        return self.__data.get('smart_promotion_type')

    def isLegacyAdvantagePlusCampaign(self):
        return self.getSmartPromotionType() in {
            'AUTOMATED_SHOPPING_ADS',
            'SMART_APP_PROMOTION',
        }

    def getStartTime(self):
        return self.__data.get('start_time')

    def getStopTime(self):
        return self.__data.get('stop_time')

    def getData(self):
        return self.__data

    def setData(self, data):
        self.__data = data

    def update(self, api):
        try:
            jsonResponse = api.updateCampaign(self)

            if "success" in jsonResponse and jsonResponse["success"]:
                return True
            else:
                raise AppError("Meta API nie potwierdzilo aktualizacji kampanii")
        except Exception as e:
            raise AppError(
                "Aktualizacja kampanii nie powiodla sie",
                context={"campaign_id": self.getId()},
                cause=e,
            )

    def copy(self, api):
        try:
            return api.copyCampaign(self.getId())
        except Exception as e:
            raise AppError(
                "Klonowanie kampanii nie powiodlo sie",
                context={"campaign_id": self.getId()},
                cause=e,
            )
