# -*- coding: UTF-8 -*-
from django import forms
from django.forms import ModelForm
from django.forms import HiddenInput
from django.forms import TextInput
from django.forms.models import inlineformset_factory
from django.forms.widgets import Widget
from django.forms.widgets import SelectMultiple
from django.utils.safestring import mark_safe

import dictionary.viewmodels

from custom_user.models import CustomUser
from dictionary.models import Entry
from dictionary.models import Meaning
from dictionary.models import Example
from dictionary.models import Etymology
from dictionary.models import MeaningContext
from dictionary.models import GreekEquivalentForMeaning
from dictionary.models import GreekEquivalentForExample
from directory.models import CategoryValue

class EntryForm(ModelForm):
    class Meta:
        model = Entry
        widgets = {
            'civil_equivalent': HiddenInput,
            'hidden': HiddenInput,
            'homonym_order': HiddenInput,
            'homonym_gloss': HiddenInput,
            'word_forms_list': HiddenInput,
            'transitivity': HiddenInput,

            'derivation_entry': HiddenInput,
            'link_to_entry': HiddenInput,
            'link_to_collogroup': HiddenInput,
            'link_to_meaning': HiddenInput,
            'cf_entries': HiddenInput,
            'cf_collogroups': HiddenInput,
            'cf_meanings': HiddenInput,

            'status': HiddenInput,
            'percent_status': HiddenInput,
            'editor': HiddenInput,
            'antconc_query': HiddenInput,
            'grequiv_status': HiddenInput,
        }

class MeaningForm(ModelForm):

    class Meta:
        model = Meaning
        widgets = {
            'entry_container': HiddenInput,
            'collogroup_container': HiddenInput,
            'order': HiddenInput,
            'parent_meaning': HiddenInput,
            'hidden': HiddenInput,

            'link_to_meaning': HiddenInput,
            'link_to_entry': HiddenInput,
            'link_to_collogroup': HiddenInput,
            'cf_entries': HiddenInput,
            'cf_collogroups': HiddenInput,
            'cf_meanings': HiddenInput,
        }

class ExampleForm(ModelForm):
    class Meta:
        model = Example
        widgets = {
            'meaning': HiddenInput,
            'order': HiddenInput,
            'hidden': HiddenInput,
        }

class OrthVarForm(ModelForm):
    class Meta:
        model = Example
        widgets = {
            'entry': HiddenInput,
            'order': HiddenInput,

            'idem': TextInput(attrs={'class':'x5 y1 antconsol'}),
        }

class EtymologyForm(ModelForm):
    class Meta:
        model = Etymology
        widgets = {
            'entry': HiddenInput,
            'collocation': HiddenInput,
            'order': HiddenInput,
            'etymon_to': HiddenInput,
        }

class MnngCntxtForm(ModelForm):
    class Meta:
        model = MeaningContext
        widgets = {
            'meaning': HiddenInput,
            'order': HiddenInput,
        }

class GrEqForMnngForm(ModelForm):
    class Meta:
        model = GreekEquivalentForMeaning
        widgets = {
            'for_meaning': HiddenInput,
        }

class GrEqForExForm(ModelForm):
    class Meta:
        model = GreekEquivalentForExample
        widgets = {
            'for_example': HiddenInput,
            'position': HiddenInput,
        }

class RawValueWidget(Widget):
    def render(self, name, value, attrs=None):
        if value is None:
            value = u''
        return mark_safe(unicode(value))


class BilletImportForm(forms.Form):
    csvfile = forms.FileField()
    def clean(self):
        cleaned_data = self.cleaned_data
        uploaded_file = cleaned_data.get('csvfile')
        if not uploaded_file.name.upper().endswith('.CSV'):
            raise forms.ValidationError(u'Выбранный вами файл «%s», похоже, не является CSV-файлом.' % uploaded_file.name)
        return cleaned_data


class SelectMultipleAutocomplete(SelectMultiple):
    pass



BLANKLABEL = ''

AUTHOR_CHOICES = dictionary.viewmodels.tupleAuthors
POS_CHOICES = dictionary.viewmodels.tuplePos
SORTDIR_CHOICES = dictionary.viewmodels.tupleSortdir
SORTBASE_CHOICES = dictionary.viewmodels.tupleSortbase
STATUS_CHOICES = dictionary.viewmodels.tupleStatuses

def category_values(category):
    return [
        (item.id, item.tag)
        for item
        in CategoryValue.objects.filter(category__slug=category)
    ]

GENDER_CHOICES = (
    ('all',  u'любой'),
    ('none', u'не определен'),
    (BLANKLABEL, category_values('gender')),
)

TANTUM_CHOICES = (
    ('all',  u'любое'),
    ('none', u'не определено'),
    (BLANKLABEL, category_values('tantum')),
)

ONYM_CHOICES = (
    ('all',  u'любой'),
    ('none', u'не определен'),
    (BLANKLABEL, category_values('onym')),
)

CANONNAME_CHOICES = (
    ('all',  u'все имена'),
    (1, u'только канонические'),
    (0, u'только неканонические'),
)

POSSESSIVE_CHOICES = (
    ('all',  u''),
    (1, u'притяжательные'),
    (0, u'непритяжательные'),
)

class FilterEntriesForm(forms.Form):
    sortdir = forms.ChoiceField(choices=SORTDIR_CHOICES, required=False)
    sortbase = forms.ChoiceField(choices=SORTBASE_CHOICES)
    find = forms.CharField(required=False, label=u'Начинается с')
    author = forms.ChoiceField(choices=AUTHOR_CHOICES, label=u'Автор')
    status = forms.ChoiceField(choices=STATUS_CHOICES, label=u'Статус статьи')
    pos = forms.ChoiceField(choices=POS_CHOICES, label=u'Часть речи')
    uninflected = forms.BooleanField(label=u'Только неизменяемые',
            required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, label=u'Род')
    tantum = forms.ChoiceField(choices=TANTUM_CHOICES, label=u'Число')
    onym = forms.ChoiceField(choices=ONYM_CHOICES,
            label=u'Тип имени собственного')
    canonical_name = forms.ChoiceField(choices=CANONNAME_CHOICES,
            label=u'Канонические имена')
    possessive = forms.ChoiceField(choices=POSSESSIVE_CHOICES,
            label=u'Притяжательность')
    etymology = forms.BooleanField(label=u'Статьи с этимологией',
            required=False)
    additional_info = forms.BooleanField(label=u'Статьи с примечаниями',
            required=False)
    homonym = forms.BooleanField(label=u'Статьи-омонимы',
            required=False)
    duplicate = forms.BooleanField(label=u'Статьи-дубликаты',
            required=False)
    default_data = {
        'sortdir':  '-',
        'sortbase': 't',
        'find': u'',
        'author': 'all',
        'status': 'all',
        'pos': 'all',
        'uninflected': False,
        'gender': 'all',
        'tantum': 'all',
        'onym': 'all',
        'canonical_name': 'all',
        'possessive': 'all',
        'etymology': False,
        'additional_info': False,
        'homonym': False,
        'duplicate': False,
    }
