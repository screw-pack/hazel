from django.test import TestCase
from django.urls import reverse
from django.template.defaultfilters import date as _date
from django.core.management import call_command
from unittest.mock import patch
from registration.models import User, Family, Child
from .models import Period, Slot, Booking
from datetime import date, timedelta


class SelectChildPageTestCase(TestCase):

    def setUp(self):
        self.username = 'Fake-User'
        self.email = 'fake.user@foo.bar'
        self.password = 'F4K3u53r'
        self.user = User.objects.create_user(self.username, self.email,
                                             self.password)
        self.birth_date = date.fromisoformat('2012-01-01')

    def test_selectchild_page_returns_200(self):
        family = Family.objects.create(user=self.user)
        Child.objects.create(family=family, birth_date=self.birth_date)
        self.client.login(username=self.username, password=self.password)

        response = self.client.get(reverse('booking:select_child'))
        self.assertEqual(response.status_code, 200)

    def test_selectchild_page_redirect_if_not_logged(self):
        response = self.client.get(reverse('booking:select_child'))
        self.assertEqual(response.status_code, 302)

    def test_selectchild_page_redirect_if_no_family(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(reverse('booking:select_child'))
        self.assertEqual(response.status_code, 302)

    def test_selectchild_page_redirect_if_no_child(self):
        self.client.login(username=self.username, password=self.password)
        Family.objects.create(user=self.user)
        response = self.client.get(reverse('booking:select_child'))
        self.assertEqual(response.status_code, 302)


class CalendarPageTestCase(TestCase):

    def setUp(self):
        self.username = 'Fake-User'
        self.email = 'fake.user@foo.bar'
        self.password = 'F4K3u53r'
        self.user = User.objects.create_user(self.username, self.email,
                                             self.password)
        self.birth_date = date.fromisoformat('2012-01-01')
        self.family = Family.objects.create(user=self.user)
        self.child = Child.objects.create(family=self.family,
                                          birth_date=self.birth_date)
        self.monday = date.today()

        while self.monday.weekday() != 0:
            self.monday += timedelta(days=1)

        self.t1 = self.monday + timedelta(days=1)

        self.period = Period.objects.create(
            name='Fake Period',
            start_date=self.monday,
            end_date=self.monday + timedelta(weeks=1)
        )
        self.period2 = Period.objects.create(
            name='Périscolaire',
            start_date=self.monday,
            end_date=self.monday + timedelta(weeks=2)
        )
        self.client.login(username=self.username, password=self.password)

    def test_calendar_page_returns_200(self):
        response = self.client.get(reverse('booking:calendar',
                                   args=(str(self.child.id))))
        self.assertEqual(response.status_code, 200)

    def test_calendar_page_redirect_if_not_logged(self):
        self.client.logout()
        response = self.client.get(reverse('booking:calendar',
                                   args=(str(self.child.id))))
        self.assertEqual(response.status_code, 302)

    def test_calendar_page_redirect_if_no_family(self):
        Family.objects.all().delete()
        response = self.client.get(reverse('booking:calendar',
                                   args=("1")))
        self.assertEqual(response.status_code, 302)

    def test_calendar_page_returns_404_if_no_child(self):
        response = self.client.get(reverse('booking:calendar',
                                   args=("1")))
        self.assertEqual(response.status_code, 404)

    def test_calendar_page_returns_404_if_not_familys_child(self):
        response = self.client.get(reverse('booking:calendar',
                                   args=("2")))
        self.assertEqual(response.status_code, 404)

    def test_calendar_dict_contains_booking(self):
        slot = Slot.objects.create(day=self.t1)
        booking = Booking.objects.create(slot=slot, child=self.child)
        month = _date(self.t1, 'F Y')
        weekday = _date(self.t1, 'D')
        day = self.t1
        response = self.client.get(reverse('booking:calendar',
                                   args=(str(self.child.id))))
        calendar = response.context['calendars']['Fake Period']
        self.assertEqual(
            calendar[month][weekday][day], booking
        )

    def test_calendar_dict_contains_none(self):
        month = _date(self.t1, 'F Y')
        weekday = _date(self.t1, 'D')
        day = self.t1
        response = self.client.get(reverse('booking:calendar',
                                   args=(str(self.child.id))))
        calendar = response.context['calendars']['Fake Period']
        self.assertEqual(
            calendar[month][weekday][day], None
        )

    def test_calendar_dict_contains_full(self):
        Slot.objects.create(day=self.t1, is_full=True)
        month = _date(self.t1, 'F Y')
        weekday = _date(self.t1, 'D')
        day = self.t1
        response = self.client.get(reverse('booking:calendar',
                                   args=(str(self.child.id))))
        calendar = response.context['calendars']['Fake Period']
        self.assertEqual(
            calendar[month][weekday][day], 'full'
        )


class ModifyViewTestCase(TestCase):

    def setUp(self):
        self.username = 'Fake-User'
        self.email = 'fake.user@foo.bar'
        self.password = 'F4K3u53r'
        self.user = User.objects.create_user(self.username, self.email,
                                             self.password)
        self.family = Family.objects.create(user=self.user)
        self.birth_date = date.fromisoformat('2012-01-01')
        self.child = Child.objects.create(family=self.family,
                                          birth_date=self.birth_date)

    def test_modifyview_cancels_booking_and_clears_slot(self):
        slot = Slot.objects.create(day=date.today())
        Booking.objects.create(slot=slot, child=self.child)
        bookings = Booking.objects.all()
        slots = Slot.objects.all()
        old_bookings = bookings.count()
        old_slots = slots.count()
        self.client.post(reverse('booking:modify'), {
            'child_id': self.child.id,
            'command': 'cancel',
            'day': slot.day.isoformat()
        })
        new_bookings = bookings.count()
        new_slots = slots.count()
        self.assertEqual(new_bookings, old_bookings - 1)
        self.assertEqual(new_slots, old_slots - 1)

    def test_modifyview_adds_booking_and_creates_slot(self):
        bookings = Booking.objects.all()
        slots = Slot.objects.all()
        old_booking = bookings.count()
        old_slots = slots.count()
        self.client.post(reverse('booking:modify'), {
            'child_id': self.child.id,
            'day_option': 'full-day',
            'day': date.today().isoformat()
        })
        new_booking = bookings.count()
        new_slots = slots.count()
        self.assertEqual(new_booking, old_booking + 1)
        self.assertEqual(new_slots, old_slots + 1)


class MockResponse:

    def __init__(self):
        self.status_code = 200

    def json(self):
        return {
            "records": [
                {
                    "datasetid": "fr-en-calendrier-scolaire",
                    "recordid": "23751d4d9f293baf7f432ef67c0ee28e1e216d4e",
                    "fields": {
                        "description": "Vacances de Noël",
                        "end_date": "2022-01-03T00:00:00+01:00",
                        "zones": "Zone A",
                        "annee_scolaire": "2021-2022",
                        "location": "Bordeaux",
                        "start_date": "2021-12-18T00:00:00+01:00",
                        "population": "-"
                    },
                    "record_timestamp": "2021-07-20T16:48:46.289000+02:00"
                }]
        }


class GetHolidaysCommandTestCase(TestCase):

    @patch('requests.get', return_value=MockResponse())
    def test_get_holidays_add_periods(self, mocked):
        old_period = Period.objects.count()
        args = []
        opts = {}
        call_command('get_holidays', *args, **opts)
        new_period = Period.objects.count()
        self.assertEqual(new_period, old_period+2)
