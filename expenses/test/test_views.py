from django.test import RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User, AnonymousUser
from expenses.views import expense_edit
from mixer.backend.django import mixer
from django.test import TestCase
import pytest


@pytest.mark.django_db
class TestViews(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestViews, cls).setUpClass()
        mixer.blend('expenses.Expense')
        cls.mfactory =  RequestFactory()


    def test_expenses_authenticated(self):
        path =  reverse('expense-edit', kwargs={'id': 1})
        request =  self.mfactory.get(path)
        request.user =  mixer.blend(User)

        response =  expense_edit(request, id=1)
        assert response.status_code ==  200


    def test_expenses_unauthenticated(self):
        path =  reverse('expense-edit', kwargs={'id': 1})
        request =  self.mfactory.get(path)
        request.user =  AnonymousUser()

        response =  expense_edit(request, id=1)
        assert 'authentication/login' in response.url