import unittest
from unittest.mock import Mock

from app_errors import AppError, create_http_error, format_exception_for_display, message_to_html


class AppErrorsTests(unittest.TestCase):
    def test_create_http_error_extracts_meta_fields(self):
        response = Mock()
        response.status_code = 400
        response.text = '{"error": {"message": "Invalid creative", "code": 100}}'
        response.json.return_value = {
            'error': {
                'message': 'Invalid creative',
                'type': 'OAuthException',
                'code': 100,
                'error_subcode': 2446289,
                'fbtrace_id': 'ABC123',
            }
        }

        message = create_http_error('test step', response, 'https://graph.facebook.com/v25.0/x').to_text()

        self.assertIn('test step', message)
        self.assertIn('Invalid creative', message)
        self.assertIn('code: 100', message)
        self.assertIn('subcode: 2446289', message)
        self.assertIn('fbtrace_id: ABC123', message)
        self.assertIn('Co sprawdzic', message)
        self.assertIn('kreacja', message)

    def test_create_http_error_explains_budget_problem(self):
        response = Mock()
        response.status_code = 400
        response.text = ''
        response.json.return_value = {
            'error': {
                'message': 'Invalid daily_budget value',
                'code': 100,
                'fbtrace_id': 'BUDGET1',
            }
        }

        message = create_http_error('aktualizacja AdSet', response, 'url').to_text()

        self.assertIn('problem dotyczy budzetu', message)

    def test_create_http_error_explains_token_problem(self):
        response = Mock()
        response.status_code = 400
        response.text = ''
        response.json.return_value = {
            'error': {
                'message': 'Invalid OAuth access token',
                'code': 190,
                'fbtrace_id': 'TOKEN1',
            }
        }

        message = create_http_error('pobieranie firm', response, 'url').to_text()

        self.assertIn('token dostepu', message)

    def test_format_exception_flattens_nested_exception_args(self):
        error = Exception('outer', AppError('inner', context={'ad_id': 'ad_1'}))

        message = format_exception_for_display(error, 'context')

        self.assertIn('context', message)
        self.assertIn('outer', message)
        self.assertIn('inner', message)
        self.assertIn('ad_id: ad_1', message)

    def test_message_to_html_escapes_and_preserves_newlines(self):
        html = message_to_html('<error>\nline 2')

        self.assertEqual('&lt;error&gt;<br>line 2', html)


if __name__ == '__main__':
    unittest.main()
