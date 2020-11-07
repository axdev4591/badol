from django.urls import reverse, resolve

class TestUrls:

    def test_detail_url(self):
        path =  reverse('expense-edit', kwargs={'id': 1})
        assert resolve(path).view_name == 'expense-edit'