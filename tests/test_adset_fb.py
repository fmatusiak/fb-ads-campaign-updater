import unittest

from models.adset_fb import AdSetFb


class AdSetFbCompatibilityTests(unittest.TestCase):
    def test_set_daily_budget_stores_integer_minor_units(self):
        ad_set = AdSetFb({'id': 'adset_1'})

        ad_set.setDailyBudget('10.55')

        self.assertEqual(1055, ad_set.getData()['daily_budget'])

    def test_get_data_removes_unsupported_facebook_video_feeds_placement(self):
        ad_set = AdSetFb({
            'id': 'adset_1',
            'targeting': {
                'facebook_positions': ['feed', 'video_feeds', 'marketplace'],
            },
        })

        targeting = ad_set.getData()['targeting']

        self.assertEqual(['feed', 'marketplace'], targeting['facebook_positions'])


if __name__ == '__main__':
    unittest.main()
