import unittest

from models.ad_creative_builder import AdCreativeBuilder


class AdCreativeBuilderAddressUrlTests(unittest.TestCase):
    def test_build_data_sets_link_data_link_for_address_url(self):
        builder = AdCreativeBuilder()

        builder.buildData('address_url', 'https://example.com')

        self.assertEqual(
            'https://example.com',
            builder.getData()['object_story_spec']['link_data']['link']
        )

    def test_build_data_preserves_existing_link_data_when_setting_address_url(self):
        builder = AdCreativeBuilder()
        builder.setData({
            'object_story_spec': {
                'link_data': {
                    'message': 'Existing message'
                }
            }
        })

        builder.buildData('address_url', 'https://example.com')

        self.assertEqual(
            {
                'message': 'Existing message',
                'link': 'https://example.com'
            },
            builder.getData()['object_story_spec']['link_data']
        )

    def test_get_data_forces_recommendations_and_enhancements_off(self):
        builder = AdCreativeBuilder()
        builder.setData({
            'degrees_of_freedom_spec': {
                'creative_features_spec': {
                    'standard_enhancements': {'enroll_status': 'OPT_IN'},
                    'video_auto_crop': {'enroll_status': 'OPT_IN'},
                }
            },
            'contextual_multi_ads': {'enroll_status': 'OPT_IN'},
            'product_suggestion_settings': {'enabled': True},
            'recommender_settings': {'preferred_events': ['PURCHASE']},
        })

        data = builder.getData()
        creativeFeatures = data['degrees_of_freedom_spec']['creative_features_spec']

        self.assertEqual('OPT_OUT', creativeFeatures['standard_enhancements']['enroll_status'])
        self.assertEqual('OPT_OUT', creativeFeatures['advantage_plus_creative']['enroll_status'])
        self.assertEqual('OPT_OUT', creativeFeatures['video_auto_crop']['enroll_status'])
        self.assertEqual('OPT_OUT', creativeFeatures['multi_photo_to_video']['enroll_status'])
        self.assertEqual({'enroll_status': 'OPT_OUT'}, data['contextual_multi_ads'])
        self.assertEqual({'enabled': False}, data['product_suggestion_settings'])
        self.assertNotIn('recommender_settings', data)

    def test_copy_ad_creative_data_does_not_remove_standard_enhancements_opt_out(self):
        builder = AdCreativeBuilder()

        builder.copyAdCreativeData({
            'id': 'creative_1',
            'degrees_of_freedom_spec': {
                'creative_features_spec': {
                    'standard_enhancements': {'enroll_status': 'OPT_OUT'},
                }
            },
        })

        data = builder.getData()

        self.assertNotIn('id', data)
        self.assertEqual(
            'OPT_OUT',
            data['degrees_of_freedom_spec']['creative_features_spec']['standard_enhancements']['enroll_status']
        )


if __name__ == '__main__':
    unittest.main()
