from facebook_business.adobjects.adset import AdSet

from date_parser import DateParser


class AdSetFb:
    def __init__(self, data):
        self.__firstInit = False
        self.__data = data

    def getId(self):
        return self.__data.get('id')

    def setLongitude(self, longitude):
        self.__initGeoLocations()

        targeting = self.__data.get(AdSet.Field.targeting)
        geoLocations = targeting.get('geo_locations', {})

        geoLocations['custom_locations'][0]['longitude'] = longitude

    def setLatitude(self, latitude):
        self.__initGeoLocations()

        targeting = self.__data.get(AdSet.Field.targeting)
        geoLocations = targeting.get('geo_locations', {})

        geoLocations['custom_locations'][0]['latitude'] = latitude

    def setRadius(self, radius):
        self.__initGeoLocations()

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

    def setData(self, data):
        self.__data = data

    def update(self, api):
        try:
            jsonResponse = api.updateAdSet(self)

            if "success" in jsonResponse and jsonResponse["success"]:
                return True
            else:
                raise Exception("Aktualizacja AdSet nie powiodła się.")
        except Exception as e:
            raise Exception("Wystąpił błąd z aktualizacją AdSet", e)

    def __initGeoLocations(self):
        if not self.__firstInit:
            targeting = self.__data.get(AdSet.Field.targeting, {})

            geoLocations = {
                'custom_locations': [{
                    'country': 'PL',
                    'distance_unit': 'kilometer',
                }]
            }

            targeting['geo_locations'] = geoLocations
            self.__data[AdSet.Field.targeting] = targeting

            self.__firstInit = True
