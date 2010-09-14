# -*- coding: UTF-8 -*-
from hip2unicode.functions import convert
from hip2unicode.functions import compile_conversion
from hip2unicode.conversions import antconc_ucs8

compiled_conversion = compile_conversion(antconc_ucs8.conversion)

def ucs_convert(text):
    return convert(text, compiled_conversion).encode('utf-8')

from django.db import models
from custom_user.models import CustomUser
from slavdict.directory.models import (

    PartOfSpeech,
    Gender,
    Tantum,
    Onym,
    Transitivity,
    SubcatFrame,
    Language,
    EntryStatus,

    )

class AdminInfo:

    add_datetime = models.DateTimeField(
        editable = False,
        auto_now_add = True,
        )

    change_datetime = models.DateTimeField(
        editable = False,
        auto_now = True,
        )

class CivilEquivalent(models.Model):

    text = models.CharField(
        u'гражданское написание',
        max_length = 40,
        unique = True,
        )

    def __unicode__(self):
        return self.text

    class Meta:
        verbose_name = u'эквивалент в гражданском написании'
        verbose_name_plural = u'слова в гражданском написании'


class WordForm(models.Model):

    lexeme = models.ManyToManyField(
        'Entry',
        verbose_name = u'лексема',
        )

    text = models.CharField(
        u'словоформа',
        max_length = 40,
        unique = True,
        )

    def __unicode__(self):
        return self.text


class Entry(models.Model, AdminInfo):

    civil_equivalent = models.ForeignKey(
        CivilEquivalent,
        verbose_name = u'гражданское написание',
        )

    # orthographic_variants
    @property
    def orth_vars(self):
        return self.orthographic_variants.all()

    @property
    def meanings(self):
        return self.meaning_set.all()

    # lexeme (посредник к граматическим формам и свойствам)

    part_of_speech = models.ForeignKey(
        PartOfSpeech,
        verbose_name = u'часть речи',
        )

    uninflected = models.BooleanField(
        u'неизменяемое (для сущ./прил.)',
        )

    word_forms_list = models.TextField(
        u'список словоформ',
        help_text = u'Список словоформ через запятую',
        blank = True,
        )

    # только для существительных
    tantum = models.ForeignKey(
        Tantum,
        blank = True,
        null = True,
        )

    gender = models.ForeignKey(
        Gender,
        verbose_name = u'грам. род',
        blank = True,
        null = True,
        )

    genitive = models.CharField(
        u'окончание Р.п.',
        max_length = 3,
        help_text = u'само окончание без дефиса в начале',
        blank = True,
        )

    @property
    def genitive_ucs(self):
        return ucs_convert(self.genitive)

    # proper_noun

    # только для прилагательных
    short_form = models.CharField(
        # Это поле, по идее, в последствии должно стать FK
        # или даже MtM с приявязкой к WordForm.
        u'краткая форма',
        max_length = 20,
        blank = True,
        )

    @property
    def short_form_ucs(self):
        return ucs_convert(self.short_form)

    possessive = models.BooleanField(
        u'притяжательное прилагательное',
        default = False,
        )

    # только для глаголов
    transitivity = models.ForeignKey(
        Transitivity,
        verbose_name = u'переходность',
        blank = True,
        null = True,
        )

    sg1 = models.CharField(
        u'форма 1sg',
        max_length = 20,
        blank = True,
        )

    @property
    def sg1_ucs(self):
        return ucs_convert(self.sg1)

    sg2 = models.CharField(
        u'форма 2sg',
        max_length = 20,
        blank = True,
        )

    @property
    def sg2_ucs(self):
        return ucs_convert(self.sg2)

    derivation_entry = models.ForeignKey(
        'self',
        verbose_name = u'слово, от которого образовано данное слово',
        related_name = 'derived_entries',
        blank = True,
        null = True,
        )

    derivation_entry_meaning = models.ForeignKey(
        'Meaning',
        verbose_name = u'значение, от которого образовано слово',
        related_name = 'derived_entries',
        blank = True,
        null = True,
        )

    link_to_entry = models.ForeignKey(
        'self',
        verbose_name = u'ссылка на другую лексему',
        help_text = u'''Если вместо значений словарная статья
                        должна содержать только ссылку
                        на другую словарную статью,
                        укажите её в данном поле.''',
        related_name = 'ref_entries'
        )

    link_to_phu = models.ForeignKey(
        'PhraseologicalUnit',
        verbose_name = u'ссылка на фразеологическое сочетание',
        help_text = u'''Если вместо значений словарная статья
                        должна содержать только ссылку
                        на фразеологическое сочетание,
                        укажите его в данном поле.''',
        related_name = 'ref_entries'
        )

    additional_info = models.TextField(
        u'любая дополнительная информация',
        blank = True,
        )

    # административная информация
    status = models.ForeignKey(
        EntryStatus,
        verbose_name = u'статус статьи',
        default = 0,
        )

    percent_status = models.PositiveSmallIntegerField(
        u'статус готовности статьи в процентах',
        default = 0,
        )

    editor = models.ForeignKey(
        CustomUser,
        verbose_name = u'ответственный редактор',
        blank = True,
        null = True,
        )

    antconc_query = models.CharField(
        u'Запрос для программы AntConc',
        max_length = 500,
        )

    def __unicode__(self):
        return self.civil_equivalent.text

    class Meta:
        verbose_name = u'словарная статья'
        verbose_name_plural = u'словарные статьи'
        ordering = ('civil_equivalent__text',)


class OrthographicVariant(models.Model):

    # словарная статья, к которой относиться данный орф. вариант
    entry = models.ForeignKey(
        Entry,
        verbose_name = u'словарная статья',
        related_name = 'orthographic_variants'
        )

    # сам орфографический вариант
    idem = models.CharField(
        u'написание',
        max_length=40,
        )

    @property
    def idem_ucs(self):
        return ucs_convert(self.idem)

    # является ли данное слово реконструкцией (реконструированно, так как не встретилось в корпусе)
    is_reconstructed = models.BooleanField(u'является реконструкцией')

    # в связке с полем реконструкции (is_reconstructed)
    # показывает, утверждена ли реконструкция или нет
    is_approved = models.BooleanField(u'одобренная реконструкция')

    # является ли данный орфографический вариант основным
    is_headword = models.BooleanField(u'основной орфографический вариант')

    # является ли орф. вариант только общей частью словоформ
    # (напр., "вонм-" для "вонми", "вонмем" и т.п.)
    # на конце автоматически добавляется дефис, заносить в базу без дефиса
    is_factored_out = models.BooleanField(u'общая часть нескольких слов или словоформ')

    # частота встречаемости орфографического варианта
    # ? для факторизантов не важна ?
    frequency = models.PositiveIntegerField(
        u'частота',
        blank = True,
        null  = True,
        )

    def __unicode__(self):
        return self.idem

    class Meta:
        verbose_name = u'орфографический вариант'
        verbose_name_plural = u'орфографические варианты'
        ordering = ('-is_headword', 'idem')

class Etymology(models.Model):

    language = models.ForeignKey(
        Language,
        verbose_name = u'язык',
        )

    text = models.CharField(
        u'языковой эквивалент',
        max_length = 40,
        blank = True,
        )

    translit = models.CharField(
        u'траслит.',
        max_length = 40,
        )

    meaning = models.CharField(
        u'перевод',
        max_length = 70,
        )

    def __unicode__(self):
        return self.translit

    class Meta:
        verbose_name = u'этимология слова'
        verbose_name_plural = u'этимология слов'


class ProperNoun(models.Model):

    entry = models.ForeignKey(Entry)

    onym = models.ForeignKey(
        Onym,
        verbose_name = u'тип имени собственного',
        )

    canonical_name = models.BooleanField(
        u'каноническое',
        )

    unclear_ethymology = models.BooleanField(
        u'этимология неясна',
        )

    etymology = models.ManyToManyField(
        Etymology,
        verbose_name = u'этимология',
        blank = True,
        null = True,
        )

    def __unicode__(self):
        return u'<Имя собственное %s>' % self.id

    class Meta:
        verbose_name = u'имя собственное'
        verbose_name_plural = u'имена собственные'


class Meaning(models.Model, AdminInfo):

    entry_container = models.ForeignKey(
        Entry,
        blank = True,
        null = True,
        verbose_name = u'лексема',
        help_text = u'''Лексема, к которой относится значение.
                        Выберите, только если значение
                        не относится к фразеологизму.''',
        )

    phu_container = models.ForeignKey(
        'PhraseologicalUnit',
        blank = True,
        null = True,
        verbose_name = u'фразеологизм',
        help_text = u'''Фразелогическое сочетание,
                        к которому относится значение.
                        Выберите, только если значение
                        не относится к конкретной лексеме.''',
        )

    order = models.IntegerField(
        u'номер',
        )

    hidden = models.BooleanField(
        u'Скрыть значение',
        help_text = u'''Не отображать данное значение
                        при выводе словарной статьи.''',
        default = False,
        )

    link_to_meaning = models.ForeignKey(
        'self',
        verbose_name = u'ссылка на значение',
        help_text = u'''Если значение должно вместо текста
                        содержать только ссылку на другое
                        значение некоторой лексемы или
                        фразеологического сочетания,
                        укажите её в данном поле.''',
        related_name = 'ref_meanings'
        )

    link_to_entry = models.ForeignKey(
        Entry,
        verbose_name = u'ссылка на лексему',
        help_text = u'''Если вместо значения
                        должна быть только ссылка
                        на другую словарную статью,
                        укажите её в данном поле.''',
        related_name = 'ref_meanings'
        )

    link_to_phu = models.ForeignKey(
        'PhraseologicalUnit',
        verbose_name = u'ссылка на фразеологическое сочетание',
        help_text = u'''Если вместо значения должна быть только ссылка
                        на целое фразеологическое сочетание, а не его
                        отдельные значения, укажите его в данном поле.''',
        related_name = 'ref_meanings'
        )

    meaning = models.TextField(
        u'значение',
        blank = True,
        )

    metaphorical = models.BooleanField(
        u'метафорическое',
        )

    # greek_equivalent

    gloss = models.TextField(
        u'толкование',
        help_text = u'''Для неметафорических употреблений/прямых значений
                        здесь указывается энциклопедическая информация.
                        Для метафорических/переносных -- (?) разнообразная
                        дополнительная информация, коментарии к употреблению.''',
        blank = True,
        )

    subcat_frames = models.ManyToManyField(
        SubcatFrame,
        verbose_name = u'модель управления',
        blank = True,
        null = True,
        )

    additional_info = models.TextField(
        u'любая дополнительная информация',
        blank = True,
        )

    @property
    def examples(self):
        return self.example_set.all()

    def __unicode__(self):
        return self.meaning

    class Meta:
        verbose_name = u'значение'
        verbose_name_plural = u'значения'
        ordering = ('entry_container__civil_equivalent__text', 'order')


class Address(models.Model):

    address = models.CharField(
        u'адрес',
        max_length = 15,
        )

    def __unicode__(self):
        return u'(%s)' % self.address

    class Meta:
        verbose_name = u'адрес'
        verbose_name_plural = u'адреса'


class Example(models.Model, AdminInfo):

    example = models.TextField(
        u'пример',
        )

    @property
    def example_ucs(self):
        return ucs_convert(self.example)

    context = models.TextField(
        u'контекст примера',
        help_text = u'более широкий контекст для примера',
        blank = True,
        )

    class SplitContext:
        def __init__(self, left, middle, right, whole):
            self.left = left
            self.example = middle
            self.right = right
            self.whole = whole

        def __unicode__(self):
            return self.whole

    @property
    def context_ucs(self):
        c = self.context
        e = ucs_convert(self.example)
        if c:
            c = ucs_convert(c)
            x, y, z = c.partition(e)
            x = strip(x)
            y = strip(y)
            z = strip(z)
            if y:
                # Разбиение дало положительный результат,
                # в "y" помещён сам пример.
                return SplitContext(x, y, z, c)
        return SplitContext(u'', e, u'', e)

    address = models.ForeignKey(
        Address,
        verbose_name = u'адрес',
        # временно поле сделано необязательным
        blank = True,
        null = True,
        )

    # Временное поле для импорта вордовских статей.
    address_text = models.CharField(
        u'текст адреса',
        max_length = 300,
        help_text = u'''Временное поле для импорта
                        вордовских статей. И заполнения
                        адресов в неунифицированном
                        текстовом виде'''
        )

    hidden = models.BooleanField(
        u'Скрыть пример',
        help_text = u'''Не отображать данный пример
                        при выводе словарной статьи.''',
        default = False,
        )

    translation = models.TextField(
        u'перевод',
        blank = True,
        )

    meaning = models.ForeignKey(Meaning)
    # TODO: это должно быть поле ManyToManyField,
    # а не FK. Соответственно, оно должно
    # иметь название во мн.ч. (meaning*s*)

    # greek_equivalent

    additional_info = models.TextField(
        u'любая дополнительная информация',
        blank = True,
        )

    def __unicode__(self):

        return u'%s %s' % (self.address, self.example)

    class Meta:

        verbose_name = u'пример'
        verbose_name_plural = u'примеры'

class SynonymGroup(models.Model):

    synonyms = models.ManyToManyField(
        Meaning,
        verbose_name = u'синонимы',
        related_name = 'synonym_groups',
        blank = True,
        null = True,
        )

    phu_synonyms = models.ManyToManyField(
        'PhraseologicalUnit',
        verbose_name = u'синонимы-фразеологизмы',
        blank = True,
        null = True,
        )

    base = models.ForeignKey(
        Meaning,
        verbose_name = u'базовый синоним',
        related_name = 'base_synonyms'
        )

    def __unicode__(self):
        return self.base.entry_container.civil_equivalent.text

    class Meta:
        verbose_name = u'группа синонимов'
        verbose_name_plural = u'группы синонимов'

class PhraseologicalUnit(models.Model):

    text = models.CharField(
        u'фразеологическое сочетание',
        max_length = 50,
        )

    @property
    def text_ucs(self):
        return ucs_convert(self.text)

    meaning_constituents = models.ManyToManyField(
        Meaning,
        verbose_name = u'значения',
        help_text = u'''значения (как элементы
                        словарной статьи),
                        при которых необходимо
                        разместить фразеологическую
                        единицу или ссылку
                        на её размещение''',
        blank = True,
        null = True,
        )

    entry_constituents = models.ManyToManyField(
        Entry,
        verbose_name = u'словарные статьи',
        help_text = u'''словарные статьи,
                        при которых необходимо
                        разместить фразеологическую
                        единицу или ссылку
                        на её размещение''',
        blank = True,
        null = True,
        )

    base = models.ForeignKey(
        Entry,
        verbose_name = u'базовая словарная статья',
        related_name = 'based_phus'
        )

    link_to_entry = models.ForeignKey(
        Entry,
        verbose_name = u'ссылка на лексему',
        help_text = u'''Если вместо значений фразеологической
                        единицы должна быть только ссылка
                        на словарную статью, укажите её
                        в данном поле.''',
        related_name = 'ref_phus'
        )

    link_to_phu = models.ForeignKey(
        'self',
        verbose_name = u'ссылка на фразеологическое сочетание',
        help_text = u'''Если вместо значений фразеологической
                        единицы должна быть только ссылка
                        на другое фразеологическое сочетание,
                        укажите её в данном поле.''',
        related_name = 'ref_phus'
        )

    def __unicode__(self):
        return self.text

    class Meta:
        verbose_name = u'фразеологическое сочетание'
        verbose_name_plural = u'фразеологические сочетания'
