from date_parser import DateParser


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

    def getStartTime(self):
        return self.__data.get('start_time')

    def getStopTime(self):
        return self.__data.get('stop_time')

    def getData(self):
        return self.__data

    def update(self, api):
        try:
            status = api.updateCampaign(self)

            if status.get("success"):
                return True
            else:
                raise Exception("Aktualizacja kampanii nie powiodła się.")
        except Exception as e:
            raise Exception("Wystąpił błąd z aktualizacją kampanii", e)

    def copy(self, api):
        try:
            return api.copyCampaign(self.getId())
        except Exception as e:
            raise Exception("Wystąpił błąd z klonowaniem kampanii", e)
