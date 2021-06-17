from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser

from datetime import date


class User(AbstractUser):
    pass


class Adult(models.Model):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField(max_length=50, null=True)
    address = models.CharField(max_length=100)
    cell_phone = models.CharField(max_length=10, null=True)
    family_situation = models.CharField(max_length=50, null=True)
    relationship = models.CharField(max_length=50, null=True)
    occupation = models.CharField(max_length=50, null=True)
    job_address = models.CharField(max_length=200, null=True)
    job_phone = models.CharField(max_length=10, null=True)

    def __str__(self):
        return '{} {}'.format(self.firstname, self.lastname)

    @classmethod
    def create_lg(cls, session_dict):
        legal_guardian, created = cls.objects.get_or_create(
            firstname=session_dict['firstname'].title(),
            lastname=session_dict['lastname'].upper(),
            family_situation=session_dict['family_situation'].capitalize(),
            occupation=session_dict['occupation'].capitalize(),
            job_phone=session_dict['job_phone'],
            cell_phone=session_dict['cell_phone'],
            email=session_dict['email'],
            address=session_dict['address'].upper()
        )

        return legal_guardian

    @classmethod
    def create_doc(cls, form):
        doctor, created = cls.objects.get_or_create(
            firstname="Dr",
            lastname=form.cleaned_data.get('lastname').upper(),
            job_phone=form.cleaned_data.get('job_phone'),
            address=form.cleaned_data.get('address').upper()
        )

        return doctor

    @classmethod
    def create_person(cls, form):
        person, created = cls.objects.get_or_create(
            firstname=form.cleaned_data.get('firstname').title(),
            lastname=form.cleaned_data.get('lastname').upper(),
            cell_phone=form.cleaned_data.get('cell_phone'),
            relationship=form.cleaned_data.get('relationship'),
            address="NON REQUIS"
        )

        return person

class Family(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    authorized_person = models.ManyToManyField(
        Adult, related_name='family_friends', blank=True
    )
    doctor = models.ForeignKey(
        Adult, related_name='family_doctor', on_delete=models.SET_NULL, null=True
    )
    plan = models.CharField(max_length=50)
    beneficiary_name = models.CharField(max_length=50, null=True)
    beneficiary_number = models.CharField(max_length=50, null=True)
    insurance_name = models.CharField(max_length=50)
    insurance_number = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Child(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    birth_date = models.CharField(max_length=20)
    grade = models.CharField(max_length=10, blank=True, null=True)
    school = models.CharField(max_length=50, blank=True, null=True)
    info = models.TextField(blank=True, null=True)
    go_alone = models.BooleanField(default=True)
    activity = models.BooleanField(default=True)
    image_rights = models.BooleanField(default=True)
    legal_guardian_1 = models.ForeignKey(
        Adult, related_name='child_lg1',
        on_delete=models.SET_NULL, null=True
    )
    legal_guardian_2 = models.ForeignKey(
        Adult, related_name='child_lg2',
        on_delete=models.SET_NULL, null=True
    )

    def __str__(self):
        return '{} {}'.format(self.firstname, self.lastname)

    @classmethod
    def create_child(cls, family, session_dict):
        child, created = cls.objects.get_or_create(
            family=family,
            firstname=session_dict['firstname'].title(),
            lastname=session_dict['lastname'].upper(),
            birth_date=session_dict['birth_date'],
            grade=session_dict['grade'],
            school=session_dict['school'],
            info=session_dict['info']
        )

        return child

    @classmethod
    def get_age(cls):
        return int(
            (date.today() - date.fromisoformat(cls.birth_date)).days/365.2425
        )
