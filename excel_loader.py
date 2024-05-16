import pandas as pd


class ExcelLoader:

    def load(self, filePath):
        try:
            return pd.read_excel(filePath)
        except Exception as e:
            raise Exception("Wystąpił błąd podczas wczytywania pliku Excel:", e)
