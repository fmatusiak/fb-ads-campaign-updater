class AdCreativeBuilder:
    def __init__(self):
        self.__data = {}

    def copyAdCreativeData(self, adCreativeData):
        if 'id' in adCreativeData:
            adCreativeData.pop('id')

        dfs = adCreativeData.get('degrees_of_freedom_spec', {})
        dfs.get('creative_features_spec', {}).pop('standard_enhancements', None)

        self.__data = adCreativeData

        # self.add_degrees_of_freedom_spec()

    def add_degrees_of_freedom_spec(self):
        if 'degrees_of_freedom_spec' in self.__data:
            return  # już ustawione, nic nie robimy

        self.__data['degrees_of_freedom_spec'] = {
            "creative_features_spec": {
                # przykładowe, dozwolone przełączniki Advantage+
                "advantage_plus_creative": {"enroll_status": "OPT_IN"},
                "text_optimizations": {"enroll_status": "OPT_IN"},
                "image_brightness_and_contrast": {"enroll_status": "OPT_IN"},
                "video_auto_crop": {"enroll_status": "OPT_IN"}
            }
        }

    def add_ad_format(self):
        if 'ad_format' not in self.__data:
            self.__data['ad_format'] = 'carousel'

    def clean_link_data(self):
        oss = self.__data.get('object_story_spec', {})
        video_data = oss.get('video_data')

        if isinstance(video_data, dict):
            if 'image_url' in video_data and 'image_hash' in video_data:
                del video_data['image_url']

        link_data = self.__data.get('object_story_spec', {}).get('link_data', {})

        if 'picture' in link_data and 'image_hash' in link_data:
            del link_data['picture']

    def buildData(self, field, value):
        def clean_link_data(link_data):
            if 'picture' in link_data and 'image_hash' in link_data:
                del link_data['picture']

        if field == 'single_header_names':
            if 'object_story_spec' not in self.__data:
                self.__data['object_story_spec'] = {}

            if 'link_data' not in self.__data['object_story_spec']:
                self.__data['object_story_spec']['link_data'] = {}

            if len(value) == 1 and 'asset_feed_spec' not in self.__data:
                link_data = self.__data['object_story_spec']['link_data']

                link_data['name'] = value[0] if value[0] else None
            else:
                if 'asset_feed_spec' not in self.__data:
                    self.__data['asset_feed_spec'] = {}

                if 'titles' not in self.__data['asset_feed_spec']:
                    self.__data['asset_feed_spec']['titles'] = []

                titles = self.__data['asset_feed_spec']['titles']

                if len(titles) > len(value):
                    del titles[len(value):]

                for i, name in enumerate(value):
                    if name:
                        if i < len(titles):
                            titles[i]['text'] = name
                        else:
                            titles.append({'text': name})

        elif field == 'single_basic_descriptions':
            if 'object_story_spec' not in self.__data:
                self.__data['object_story_spec'] = {}

            if 'link_data' not in self.__data['object_story_spec']:
                self.__data['object_story_spec']['link_data'] = {}

            if len(value) == 1 and 'asset_feed_spec' not in self.__data:
                link_data = self.__data['object_story_spec']['link_data']

                link_data['message'] = value[0] if value[0] else None
            else:
                if 'asset_feed_spec' not in self.__data:
                    self.__data['asset_feed_spec'] = {}

                if 'bodies' not in self.__data['asset_feed_spec']:
                    self.__data['asset_feed_spec']['bodies'] = []

                bodies = self.__data['asset_feed_spec']['bodies']

                if len(bodies) > len(value):
                    del bodies[len(value):]

                for i, name in enumerate(value):
                    if name:
                        if i < len(bodies):
                            bodies[i]['text'] = name
                        else:
                            bodies.append({'text': name})


        elif field == 'single_header_descriptions':
            if 'object_story_spec' not in self.__data:
                self.__data['object_story_spec'] = {}

            if 'link_data' not in self.__data['object_story_spec']:
                self.__data['object_story_spec']['link_data'] = {}

            if len(value) == 1 and 'asset_feed_spec' not in self.__data:
                link_data = self.__data['object_story_spec']['link_data']

                link_data['description'] = value[0] if value[0] else None
            else:
                if 'asset_feed_spec' not in self.__data:
                    self.__data['asset_feed_spec'] = {}

                if 'descriptions' not in self.__data['asset_feed_spec']:
                    self.__data['asset_feed_spec']['descriptions'] = []

                descriptions = self.__data['asset_feed_spec']['descriptions']

                if len(descriptions) > len(value):
                    del descriptions[len(value):]

                for i, name in enumerate(value):
                    if name:
                        if i < len(descriptions):
                            descriptions[i]['text'] = name
                        else:
                            descriptions.append({'text': name})

        elif field == 'carousel_header_names':
            if 'object_story_spec' not in self.__data:
                self.__data['object_story_spec'] = {}
            if 'link_data' not in self.__data['object_story_spec']:
                self.__data['object_story_spec']['link_data'] = {'child_attachments': []}

            link_data = self.__data['object_story_spec']['link_data']

            if len(link_data['child_attachments']) > len(value):
                del link_data['child_attachments'][len(value):]

            for i, name in enumerate(value):
                if name:
                    if i < len(link_data['child_attachments']):
                        link_data['child_attachments'][i]['name'] = name

        elif field == 'carousel_header_descriptions':
            if 'object_story_spec' not in self.__data:
                self.__data['object_story_spec'] = {'link_data': {'child_attachments': []}}

            childAttachments = self.__data['object_story_spec']['link_data']['child_attachments']

            for i, description in enumerate(value):
                if i < len(childAttachments):
                    if description:
                        childAttachments[i]['description'] = description

        elif field == 'basic_descriptions':
            if 'asset_feed_spec' not in self.__data:
                self.__data['asset_feed_spec'] = {}
            if 'bodies' not in self.__data['asset_feed_spec']:
                self.__data['asset_feed_spec']['bodies'] = []

            bodies = self.__data['asset_feed_spec']['bodies']

            if len(bodies) > len(value):
                del bodies[len(value):]

            for i, text in enumerate(value):
                if text:
                    if i < len(bodies):
                        bodies[i]['text'] = text
                    else:
                        bodies.append({'text': text})

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

        elif field == 'short_descriptions':
            if 'asset_feed_spec' not in self.__data:
                self.__data['asset_feed_spec'] = {}

            if 'descriptions' not in self.__data['asset_feed_spec']:
                self.__data['asset_feed_spec']['descriptions'] = []

            descriptions = self.__data['asset_feed_spec']['descriptions']

            if len(descriptions) > len(value):
                del descriptions[len(value):]

            for i, description in enumerate(value):
                if description:
                    if i < len(descriptions):
                        descriptions[i]['text'] = description
                    else:
                        descriptions.append({'text': description})
        else:
            raise ValueError("Nieobsługiwane pole do aktualizacji")

    def getData(self):
        self.clean_link_data()

        return self.__data

    def setData(self, data):
        self.__data = data
