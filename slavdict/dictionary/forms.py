# -*- coding: UTF-8 -*-
from django import forms

from slavdict.dictionary import viewmodels


class BilletImportForm(forms.Form):
    csvfile = forms.FileField()
    def clean(self):
        cleaned_data = self.cleaned_data
        uploaded_file = cleaned_data.get('csvfile')
        if not uploaded_file.name.upper().endswith('.CSV'):
            raise forms.ValidationError(u'''Выбранный вами файл «%s»,
                                            похоже, не является
                                            CSV-файлом.''' % uploaded_file.name)
        return cleaned_data


AUTHOR_CHOICES = viewmodels.tupleAuthors
CANONNAME_CHOICES = viewmodels.tupleCanonicalName
GENDER_CHOICES = viewmodels.tupleGenders
GREQSORTBASE_CHOICES = viewmodels.tupleGreqSortbase
GREQSTATUS_CHOICES = viewmodels.tupleGreqStatuses
ONYM_CHOICES = viewmodels.tupleOnyms
POS_CHOICES = viewmodels.tuplePos
POSSESSIVE_CHOICES = viewmodels.tuplePossessive
SORTDIR_CHOICES = viewmodels.tupleSortdir
SORTBASE_CHOICES = viewmodels.tupleSortbase
STATUS_CHOICES = viewmodels.tupleStatuses
TANTUM_CHOICES = viewmodels.tupleTantum

class FilterEntriesForm(forms.Form):
    per_se = forms.BooleanField(label=u'Отображать помимо заголовочных '
            u'слов сами статьи', required=False)
    sortdir = forms.ChoiceField(choices=SORTDIR_CHOICES, required=False)
    sortbase = forms.ChoiceField(choices=SORTBASE_CHOICES)
    find = forms.CharField(required=False, label=u'Начинается с')
    author = forms.ChoiceField(choices=AUTHOR_CHOICES, label=u'Автор')
    status = forms.ChoiceField(choices=STATUS_CHOICES, label=u'Статус статьи')
    pos = forms.ChoiceField(choices=POS_CHOICES, label=u'Часть речи')
    uninflected = forms.BooleanField(label=u'Неизменяемые сущ. / прил.',
            required=False)
    gender = forms.ChoiceField(choices=GENDER_CHOICES, label=u'Род')
    tantum = forms.ChoiceField(choices=TANTUM_CHOICES, label=u'Число')
    onym = forms.ChoiceField(choices=ONYM_CHOICES,
            label=u'Тип имени собст.')
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
    variants = forms.BooleanField(label=u'С вар-ми написания',  # C вариантами написания
            required=False)
    collocations = forms.BooleanField(label=u'Со словосочетаниями',
            required=False)
    meaningcontexts = forms.BooleanField(label=u'С контекстами значения',
            required=False)
    default_data = {
        'per_se': False,
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
        'collocations': False,
        'variants': False,
        'meaningcontexts': False,
    }

class FilterExamplesForm(forms.Form):
    hwAddress = forms.CharField(required=False, label=u'Адрес начинается на')
    hwAuthor = forms.ChoiceField(choices=AUTHOR_CHOICES, label=u'Автор статьи')
    hwPrfx = forms.CharField(required=False, label=u'Статья начинается на')
    hwExamplesIds = forms.CharField(required=False, label=u'Идентификаторы иллюстраций')
    hwSortbase = forms.ChoiceField(choices=GREQSORTBASE_CHOICES)
    hwSortdir = forms.ChoiceField(choices=SORTDIR_CHOICES, required=False)
    hwStatus = forms.ChoiceField(choices=GREQSTATUS_CHOICES,
            label=u'Статус греч. парал.')
    default_data = {
        'hwAddress': u'',
        'hwAuthor': 'all',
        'hwPrfx': u'',
        'hwExamplesIds': '',
        'hwSortbase': 'addr',
        'hwSortdir': '',
        'hwStatus': 'all',
    }
