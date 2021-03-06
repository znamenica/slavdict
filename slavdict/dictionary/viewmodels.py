# -*- coding: utf-8 -*-
import json

from django.db.models.fields import CharField

from slavdict.custom_user.models import CustomUser
from slavdict.dictionary import models

def _json(x):
    return json.dumps(x, ensure_ascii=False, separators=(',',':'))

def _tuple(x):
    return tuple((i['id'], i['name']) for i in x)

def _choices(choices):
    return tuple(
        {'id': id, 'name': name}
        for id, name in choices
    )


def entry_json(id):
    entry = models.Entry.objects.get(pk=id)
    return _json(entry.forJSON())

EMPTY_STRING_ID_OBJECT = {'id': '', 'name': u''}
NONE_ID_OBJECT = {'id': None, 'name': u''}

AUTHOR_CHOICES = tuple(
    (user.id, user.__unicode__())
    for user in CustomUser.objects.filter(groups__name=u'authors')
)

authors = (
    {'id': 'all',  'name': u'все авторы'},
    {'id': 'none', 'name': u'статьи без автора'},
    {'id': 'few',  'name': u'статьи с неск. авторами'},
) + tuple(
    {'id': str(u.id), 'name': u.__unicode__()}
    for u in CustomUser.objects.filter(groups__name=u'authors')
)

editAuthors = (NONE_ID_OBJECT,) + _choices(AUTHOR_CHOICES)

canonical_name = (
    {'id': 'all', 'name': u'все имена'},
    {'id': '1',   'name': u'только канонические'},
    {'id': '0',   'name': u'только неканонические'},
)

genders = (
    {'id': 'all',  'name': u'любой'},
    {'id': 'none', 'name': u'где род не указан'},
) + _choices(models.GENDER_CHOICES)

editGenders = (EMPTY_STRING_ID_OBJECT,) + _choices(models.GENDER_CHOICES)

greqSortbase = (
    {'id': 'id',   'name': u'в порядке добавления примеров'},
    {'id': 'addr', 'name': u'по адресу примера'},
)

greqStatuses = ({'id': 'all', 'name': u'— любой —'},) \
        + _choices(models.Example.GREEK_EQ_STATUS)

onyms = (
    {'id': 'all',  'name': u'любой'},
    {'id': 'none', 'name': u'не имя собственное'},
) + _choices(models.ONYM_CHOICES)

editOnyms = (EMPTY_STRING_ID_OBJECT,) + _choices(models.ONYM_CHOICES)

editParticiples = (EMPTY_STRING_ID_OBJECT,) + _choices(models.PARTICIPLE_CHOICES)

pos = (
    {'id': 'all',  'name': u'любая'},
    {'id': 'none', 'name': u'где часть речи не указана'},
) + _choices(models.PART_OF_SPEECH_CHOICES)

possessive = (
    {'id': 'all', 'name': u''},
    {'id': '1',   'name': u'притяжательные'},
    {'id': '0',   'name': u'непритяжательные'},
)

sortdir = (
    {'id': '',  'name': u'по возрастанию'},
    {'id': '-', 'name': u'по убыванию'},
)

sortbase = (
    {'id': 'alph', 'name': u'гражданского написания'},
    {'id': 't',    'name': u'времени изменения'},
)

editSubstantivusTypes = ((EMPTY_STRING_ID_OBJECT,) +
        _choices(models.SUBSTANTIVUS_TYPE_CHOICES))

tantum = (
    {'id': 'all',  'name': u'любое'},
    {'id': 'none', 'name': u'где число не указано'},
) + _choices(models.TANTUM_CHOICES)

editTantum = (EMPTY_STRING_ID_OBJECT,) + _choices(models.TANTUM_CHOICES)

statuses = ({'id': 'all', 'name': u'любой'},) \
        + _choices(models.STATUS_CHOICES)

editStatuses = (EMPTY_STRING_ID_OBJECT,) + _choices(models.STATUS_CHOICES)


jsonAuthors = _json(authors)
jsonCanonicalName = _json(canonical_name)
jsonGenders = _json(genders)
jsonGreqSortbase = _json(greqSortbase)
jsonGreqStatuses = _json(greqStatuses)
jsonOnyms = _json(onyms)
jsonPos = _json(pos)
jsonPossessive = _json(possessive)
jsonSortbase = _json(sortbase)
jsonSortdir = _json(sortdir)
jsonStatuses = _json(statuses)
jsonTantum = _json(tantum)

tupleAuthors = _tuple(authors)
tupleCanonicalName = _tuple(canonical_name)
tupleGenders = _tuple(genders)
tupleGreqSortbase = _tuple(greqSortbase)
tupleGreqStatuses = _tuple(greqStatuses)
tupleOnyms = _tuple(onyms)
tuplePos = _tuple(pos)
tuplePossessive = _tuple(possessive)
tupleSortbase = _tuple(sortbase)
tupleSortdir = _tuple(sortdir)
tupleStatuses = _tuple(statuses)
tupleTantum = _tuple(tantum)
