from facebook_business.adobjects.adset import AdSet

from date_parser import DateParser


class AdSetFb:
    def __init__(self, data):
        self.__data = data

    def getId(self):
        return self.__data.get('id')

    def setLongitude(self, longitude):
        targeting = self.__data.get(AdSet.Field.targeting)
        geoLocations = targeting.get('geo_locations', {})

        geoLocations['custom_locations'][0]['longitude'] = longitude

    def setLatitude(self, latitude):
        targeting = self.__data.get(AdSet.Field.targeting)
        geoLocations = targeting.get('geo_locations', {})

        geoLocations['custom_locations'][0]['latitude'] = latitude

    def setRadius(self, radius):
        targeting = self.__data.get(AdSet.Field.targeting)
        geoLocations = targeting.get('geo_locations', {})

        geoLocations['custom_locations'][0]['radius'] = radius

    def setStartTime(self, startTime):
        self.__data['start_time'] = DateParser.parseToDateTime(startTime)

    def setEndTime(self, endTime):
        self.__data['end_time'] = DateParser.parseToDateTime(endTime)

    def setDailyBudget(self, dailyBudget):
        self.__data['daily_budget'] = float(dailyBudget) * 100

    def getData(self):
        return self.__data

    def update(self, api):
        try:
            status = api.updateAdSet(self)

            if status.get("success"):
                return True
            else:
                raise Exception("Aktualizacja AdSet nie powiodła się.")
        except Exception as e:
            raise Exception("Wystąpił błąd z aktualizacją AdSet", e)

    def __initCustomLocations(self, geoLocations):
        customLocations = geoLocations.get('custom_locations', [])

        if not customLocations:
            geoLocations['custom_locations'] = [{
                'country': 'PL',
                'distance_unit': 'kilometer',
            }]
