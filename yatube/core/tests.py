from django.test import TestCase


class ViewTestClass(TestCase):
    def test_error_404_page(self):
        response = self.client.get('core/404.html')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, 'core/404.html')
