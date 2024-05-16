import json


class Config:
    def __init__(self, filePath):
        self.filePath = filePath
        self.configData = self.loadConfig()

    def loadConfig(self):
        try:
            with open(self.filePath, 'r') as file:
                return json.load(file)

        except FileNotFoundError:
            raise FileNotFoundError(f"Plik konfiguracyjny {self.filePath} nie został znaleziony")
        except json.JSONDecodeError:
            raise json.JSONDecodeError(
                f"Błąd dekodowania pliku konfiguracyjnego {self.filePath}. Sprawdź czy jest to poprawny plik JSON")
        except Exception as e:
            raise Exception(f"Wystąpił nieoczekiwany błąd podczas wczytywania pliku konfiguracyjnego", e)

    def get(self, key):
        try:
            return self.configData[key]
        except KeyError:
            raise KeyError(f"Brak klucza '{key}' w pliku konfiguracyjnym")

    def getAppId(self):
        return self.get('app-id')

    def getAppSecret(self):
        return self.get('app-secret')

    def getAccessToken(self):
        return self.get('access-token')

    def getAccountId(self):
        return self.get('account-id')
