class AdCreativeBuilder:
    def __init__(self):
        self.__data = {}

    def copyAdCreativeData(self, adCreativeData):
        if 'id' in adCreativeData:
            adCreativeData.pop('id')

        self.__data = adCreativeData

    def buildData(self, field, value):
        if field == 'header_names':
            if 'object_story_spec' not in self.__data:
                self.__data['object_story_spec'] = {'link_data': {'child_attachments': []}}

            childAttachments = self.__data['object_story_spec']['link_data']['child_attachments']

            for i, name in enumerate(value):
                if i < len(childAttachments):
                    if name:
                        childAttachments[i]['name'] = name

        if field == 'header_descriptions':
            if 'object_story_spec' not in self.__data:
                self.__data['object_story_spec'] = {'link_data': {'child_attachments': []}}

            childAttachments = self.__data['object_story_spec']['link_data']['child_attachments']

            for i, description in enumerate(value):
                if i < len(childAttachments):
                    if description:
                        childAttachments[i]['description'] = description

        elif field == 'descriptions':
            if 'asset_feed_spec' not in self.__data:
                self.__data['asset_feed_spec'] = {}
            if 'bodies' not in self.__data['asset_feed_spec']:
                self.__data['asset_feed_spec']['bodies'] = []

            bodies = self.__data['asset_feed_spec']['bodies']

            for i, text in enumerate(value):
                if i < len(bodies):
                    if text:
                        bodies[i]['text'] = text

        elif field == 'address_url':
            if 'object_story_spec' not in self.__data:
                self.__data['object_story_spec'] = {'link_data': {}}

            self.__data['object_story_spec']['link_data']['link'] = value

        elif field == 'header_urls':
            if 'object_story_spec' not in self.__data:
                self.__data['object_story_spec'] = {'link_data': {'child_attachments': []}}

            childAttachments = self.__data['object_story_spec']['link_data']['child_attachments']

            for i, link in enumerate(value):
                if i < len(childAttachments):
                    if link:
                        childAttachments[i]['link'] = link

        elif field == 'short_description':
            if 'asset_feed_spec' not in self.__data:
                self.__data['asset_feed_spec'] = {}

            descriptions = self.__data['asset_feed_spec']['descriptions']

            for i, description in enumerate(value):
                if i < len(descriptions):
                    if description:
                        descriptions[i]['text'] = description
        else:
            raise ValueError("Nieobsługiwane pole do aktualizacji")

    def getData(self):
        return self.__data
