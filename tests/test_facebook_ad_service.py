import sys
import types
import unittest


campaign_module = types.ModuleType('facebook_business.adobjects.campaign')


class Campaign:
    class Status:
        paused = 'PAUSED'


campaign_module.Campaign = Campaign

sys.modules['facebook_business'] = types.ModuleType('facebook_business')
sys.modules['facebook_business.adobjects'] = types.ModuleType('facebook_business.adobjects')
sys.modules['facebook_business.adobjects.campaign'] = campaign_module

facebook_business_api_module = types.ModuleType('services.facebook_business_api')


class FacebookBusinessApi:
    pass


facebook_business_api_module.FacebookBusinessApi = FacebookBusinessApi
sys.modules['services.facebook_business_api'] = facebook_business_api_module

from app_errors import AppError
from services.facebook_ad_service import FacebookAdsService


class DummyApi:
    pass


class FakeAdCreativeBuilder:
    def __init__(self):
        self.calls = []

    def buildData(self, field, value):
        self.calls.append((field, value))


class FakeAdSet:
    def __init__(self, ad_set_id='adset_1', should_fail=False):
        self.data = {'id': ad_set_id}
        self.should_fail = should_fail
        self.updated = False

    def setDailyBudget(self, daily_budget):
        self.data['daily_budget'] = float(daily_budget) * 100

    def getData(self):
        return self.data

    def setData(self, data):
        self.data = data

    def update(self, api):
        if self.should_fail:
            raise Exception('AdSet update failed')

        self.updated = True
        return True


class FakeApi:
    def __init__(self):
        self.ad_set = FakeAdSet()
        self.creative_data_requested = False

    def getAdSet(self, ad_set_id):
        return self.ad_set

    def getAdCreativeData(self, ad_creative_id):
        self.creative_data_requested = True
        raise AssertionError('Creative data should not be requested')


class FakeCreativeUpdateApi:
    def __init__(self, fail_attach=False, unavailable_creative=False):
        self.status_updates = []
        self.attached_creatives = []
        self.name_updates = []
        self.created_ads = []
        self.fail_attach = fail_attach
        self.unavailable_creative = unavailable_creative

    def createCreativeAd(self, ad_account_id, ad_creative_builder):
        return {'id': 'creative_new'}

    def updateAdStatus(self, ad_id, status):
        self.status_updates.append((ad_id, status))
        return {'success': True}

    def attachNewCreativeAdToCreativeAd(self, ad_id, creative_id):
        self.attached_creatives.append((ad_id, creative_id))
        if self.unavailable_creative:
            raise AppError(
                "Blad podpinania nowej kreacji do reklamy",
                cause=AppError("Meta odrzucila zapytanie", meta={'subcode': 2446289}),
            )
        if self.fail_attach:
            raise Exception('Attach failed')

        return True

    def updateAdName(self, ad_id, name):
        self.name_updates.append((ad_id, name))
        return {'success': True}

    def createAd(self, ad_account_id, adset_id, name, creative_id, status='PAUSED'):
        ad = {
            'id': 'replacement_ad_1',
            'ad_account_id': ad_account_id,
            'adset_id': adset_id,
            'name': name,
            'creative_id': creative_id,
            'status': status,
        }
        self.created_ads.append(ad)
        return ad


class FakeCampaign:
    def __init__(self, smart_promotion_type=None, campaign_id='campaign_1', name='Campaign one'):
        self.updated = False
        self.data = {
            'id': campaign_id,
            'name': name,
            'smart_promotion_type': smart_promotion_type,
        }

    def getId(self):
        return self.data['id']

    def getSmartPromotionType(self):
        return self.data.get('smart_promotion_type')

    def getStatus(self):
        return self.data.get('status')

    def getName(self):
        return self.data.get('name')

    def isLegacyAdvantagePlusCampaign(self):
        return self.getSmartPromotionType() in {
            'AUTOMATED_SHOPPING_ADS',
            'SMART_APP_PROMOTION',
        }

    def setStopTime(self, stop_time):
        self.data['stop_time'] = stop_time

    def setName(self, name):
        self.data['name'] = name

    def setStatus(self, status):
        self.data['status'] = status

    def getData(self):
        return self.data

    def setData(self, data):
        self.data = data

    def update(self, api):
        self.updated = True
        return True

    def copy(self, api):
        return api.copyCampaign(self.getId())


class FakePartialApi:
    def __init__(self, campaign=None):
        self.ad_sets = {
            'adset_ok': FakeAdSet('adset_ok'),
            'adset_bad': FakeAdSet('adset_bad', should_fail=True),
        }
        self.campaign = campaign or FakeCampaign()
        self.copied_campaign = FakeCampaign(campaign_id='campaign_copy_1', name='Campaign one')
        self.ads_requested = False
        self.requested_statuses = None
        self.requested_campaign_id = None
        self.renamed_campaigns = []

    def getAdsForCampaign(self, campaign_id, statuses=None):
        self.ads_requested = True
        self.requested_statuses = statuses
        self.requested_campaign_id = campaign_id

        ads = [
            {
                'id': 'ad_ok',
                'name': 'Good ad',
                'status': 'ACTIVE',
                'creative': {'id': 'creative_ok'},
                'adset_id': 'adset_ok',
            },
            {
                'id': 'ad_bad',
                'name': 'Bad ad',
                'status': 'PAUSED',
                'creative': {'id': 'creative_bad'},
                'adset_id': 'adset_bad',
            },
            {
                'id': 'ad_archived',
                'name': 'Archived ad',
                'status': 'ARCHIVED',
                'creative': {'id': 'creative_archived'},
                'adset_id': 'adset_archived',
            },
        ]

        if statuses:
            return [ad for ad in ads if ad.get('status') in statuses]

        return ads

    def getAdSet(self, ad_set_id):
        return self.ad_sets[ad_set_id]

    def getCampaignData(self, campaign_id):
        return self.campaign

    def copyCampaign(self, campaign_id):
        return self.copied_campaign

    def renameCampaign(self, campaign_id, name):
        self.renamed_campaigns.append((campaign_id, name))
        return {'success': True}


class FacebookAdsServiceUpdateCreativeAdsTests(unittest.TestCase):
    def setUp(self):
        self.service = FacebookAdsService(DummyApi())

    def test_update_creative_ads_maps_url_address_to_address_url(self):
        builder = FakeAdCreativeBuilder()

        self.service.updateCreativeAds(builder, {'url_address': 'https://example.com'})

        self.assertIn(('address_url', 'https://example.com'), builder.calls)

    def test_update_creative_ads_skips_url_address_when_missing(self):
        builder = FakeAdCreativeBuilder()

        self.service.updateCreativeAds(builder, {})

        self.assertEqual([], builder.calls)

    def test_process_input_data_wraps_snake_case_creative_fields(self):
        data = self.service.processInputData({'single_header_name': 'Title'})

        self.assertEqual(['Title'], data['single_header_name'])

    def test_has_creative_updates_detects_placeholders(self):
        self.assertTrue(self.service.hasCreativeUpdates({'{$headline}': 'Title'}))

    def test_has_creative_updates_ignores_adset_only_fields(self):
        self.assertFalse(self.service.hasCreativeUpdates({'daily_budget': '10'}))

    def test_format_ad_update_error_adds_hint_for_unavailable_reel(self):
        message = self.service.formatAdUpdateError(Exception('error_subcode":2446289'))

        self.assertIn('Prawdopodobna przyczyna', message)

    def test_extract_creative_source_refs_returns_story_and_asset_ids(self):
        refs = self.service.extractCreativeSourceRefs({
            'object_story_spec': {
                'page_id': 'page_1',
                'video_data': {'video_id': 'video_1'},
            },
            'asset_feed_spec': {
                'videos': [{'video_id': 'video_2'}],
                'images': [{'image_hash': 'hash_1'}],
            },
        })

        self.assertIn('page_id=page_1', refs)
        self.assertIn('video_id=video_1', refs)
        self.assertIn('video_id=video_2', refs)
        self.assertIn('image_hash=hash_1', refs)

    def test_format_ad_error_context_includes_creative_source_refs(self):
        context = self.service.formatAdErrorContext('ad_1', 'Test ad', 'creative_1', 'video_id=video_1')

        self.assertIn('video_id=video_1', context)

    def test_update_single_ad_skips_creative_when_only_adset_fields_change(self):
        api = FakeApi()
        service = FacebookAdsService(api)
        ad = {
            'id': 'ad_1',
            'name': 'Test ad',
            'creative': {'id': 'creative_1'},
            'adset_id': 'adset_1',
        }

        service.updateSingleAd('act_1', ad, {'daily_budget': '10'})

        self.assertFalse(api.creative_data_requested)
        self.assertTrue(api.ad_set.updated)
        self.assertEqual(1000, api.ad_set.data['daily_budget'])

    def test_update_single_ad_skips_archived_ads(self):
        api = FakeApi()
        service = FacebookAdsService(api)
        ad = {
            'id': 'ad_1',
            'name': 'Archived ad',
            'status': 'ARCHIVED',
            'creative': {'id': 'creative_1'},
            'adset_id': 'adset_1',
        }

        service.updateSingleAd('act_1', ad, {'daily_budget': '10'})

        self.assertFalse(api.creative_data_requested)
        self.assertFalse(api.ad_set.updated)

    def test_update_single_ad_skips_old_creative_ads(self):
        api = FakeApi()
        service = FacebookAdsService(api)
        ad = {
            'id': 'ad_1',
            'name': 'Test ad - old creative',
            'status': 'PAUSED',
            'creative': {'id': 'creative_1'},
            'adset_id': 'adset_1',
        }

        service.updateSingleAd('act_1', ad, {'daily_budget': '10'})

        self.assertFalse(api.creative_data_requested)
        self.assertFalse(api.ad_set.updated)

    def test_create_and_attach_pauses_active_ad_before_creative_swap(self):
        api = FakeCreativeUpdateApi()
        service = FacebookAdsService(api)

        result = service.createAndAttachNewCreativeAd(
            'act_1',
            FakeAdCreativeBuilder(),
            {'id': 'ad_1', 'status': 'ACTIVE'},
        )

        self.assertTrue(result)
        self.assertEqual([('ad_1', 'PAUSED'), ('ad_1', 'ACTIVE')], api.status_updates)
        self.assertEqual([('ad_1', 'creative_new')], api.attached_creatives)

    def test_create_and_attach_restores_active_ad_when_attach_fails(self):
        api = FakeCreativeUpdateApi(fail_attach=True)
        service = FacebookAdsService(api)

        with self.assertRaises(Exception):
            service.createAndAttachNewCreativeAd(
                'act_1',
                FakeAdCreativeBuilder(),
                {'id': 'ad_1', 'status': 'ACTIVE'},
            )

        self.assertEqual([('ad_1', 'PAUSED'), ('ad_1', 'ACTIVE')], api.status_updates)

    def test_create_and_attach_creates_paused_replacement_for_unavailable_creative(self):
        api = FakeCreativeUpdateApi(unavailable_creative=True)
        service = FacebookAdsService(api)

        result = service.createAndAttachNewCreativeAd(
            'act_1',
            FakeAdCreativeBuilder(),
            {
                'id': 'ad_1',
                'name': 'Problem ad',
                'status': 'ACTIVE',
                'adset_id': 'adset_1',
            },
        )

        self.assertTrue(result)
        self.assertEqual([('ad_1', 'PAUSED'), ('ad_1', 'PAUSED')], api.status_updates)
        self.assertEqual([('ad_1', 'Problem ad - old creative')], api.name_updates)
        self.assertEqual(
            [{
                'id': 'replacement_ad_1',
                'ad_account_id': 'act_1',
                'adset_id': 'adset_1',
                'name': 'Problem ad',
                'creative_id': 'creative_new',
                'status': 'PAUSED',
            }],
            api.created_ads,
        )

    def test_update_continues_after_one_ad_fails_and_reports_partial_update(self):
        api = FakePartialApi()
        service = FacebookAdsService(api)

        with self.assertRaises(Exception) as ctx:
            service.update('act_1', 'campaign_1', {'daily_budget': '10'})

        self.assertTrue(api.ad_sets['adset_ok'].updated)
        self.assertTrue(api.campaign.updated)
        self.assertEqual({'ACTIVE', 'PAUSED'}, api.requested_statuses)
        self.assertIn('czesciowo', str(ctx.exception))
        self.assertIn('ad_bad', str(ctx.exception))

    def test_update_blocks_legacy_advantage_plus_before_loading_ads(self):
        api = FakePartialApi(FakeCampaign('AUTOMATED_SHOPPING_ADS'))
        service = FacebookAdsService(api)

        with self.assertRaises(Exception) as ctx:
            service.update('act_1', 'campaign_1', {'daily_budget': '10'})

        self.assertFalse(api.ads_requested)
        self.assertIn('Advantage+ Shopping/App', str(ctx.exception))

    def test_update_copies_archived_campaign_before_loading_ads(self):
        api = FakePartialApi(FakeCampaign())
        api.campaign.data['status'] = 'ARCHIVED'
        service = FacebookAdsService(api)

        with self.assertRaises(Exception):
            service.update('act_1', 'campaign_1', {'daily_budget': '10'})

        self.assertTrue(api.ads_requested)
        self.assertEqual('campaign_copy_1', api.requested_campaign_id)
        self.assertEqual([('campaign_1', 'Campaign one - archived')], api.renamed_campaigns)
        self.assertTrue(api.copied_campaign.updated)
        self.assertEqual('PAUSED', api.copied_campaign.data['status'])


if __name__ == '__main__':
    unittest.main()
