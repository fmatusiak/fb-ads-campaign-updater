import pandas as pd


class ExcelLoader:

    def load(self, filePath):
        try:
            df = pd.read_excel(filePath, dtype=str, keep_default_na=False)

            rows = []

            for _, row in df.iterrows():
                rowData = {}

                for column, value in row.items():
                    baseKey = column.split('.')[0]

                    if value != "":
                        if baseKey not in rowData:
                            rowData[baseKey] = value
                        else:
                            if not isinstance(rowData[baseKey], list):
                                rowData[baseKey] = [rowData[baseKey]]
                            rowData[baseKey].append(value)

                for key, val in rowData.items():
                    if isinstance(val, list) and len(val) == 1:
                        rowData[key] = val[0]

                rows.append(rowData)

            return rows

        except Exception as e:
            raise Exception("Wystąpił błąd podczas wczytywania pliku Excel:", e)
