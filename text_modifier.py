import json
import re


class TextModifier:
    def modifyDictionaryByKey(self, data: dict, dictionary: dict) -> dict:
        placeholderPattern = r'\{\$[^\}]+\}'

        try:
            modifiedJsonStr = json.dumps(dictionary)

            for key, value in data.items():
                if re.match(placeholderPattern, key):
                    modifiedJsonStr = modifiedJsonStr.replace(key, str(value))

            return json.loads(modifiedJsonStr)
        except Exception as e:
            return dictionary
