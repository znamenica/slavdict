# -*- coding: UTF-8 -*-
from django.db import models

class TermDirectory(models.Model):
    
    name = models.CharField(
        u'название',
        max_length=20,
        )

    abbreviation = models.CharField(
        u'сокращение',
        max_length=8,
        )

    def __unicode__(self):
        return u'%s [%s]' % (self.name, self.abbreviation)

    class Meta:
        abstract = True
        ordering = ('name',)


class PartOfSpeech(TermDirectory):

    class Meta(TermDirectory.Meta):
        verbose_name = u'часть речи'
        verbose_name_plural = u'части речи'


class Gender(TermDirectory):

    class Meta(TermDirectory.Meta):
        verbose_name = u'грамматический род'
        verbose_name_plural = u'значения грамматического рода'


class Tantum(TermDirectory):

    class Meta(TermDirectory.Meta):
        verbose_name = u'tantum'
        verbose_name_plural = u'tantum'


class Onym(TermDirectory):
    
    class Meta(TermDirectory.Meta):
        verbose_name = u'тип имени собственного'
        verbose_name_plural = u'типы имени собственного'


class Transitivity(TermDirectory):

    class Meta(TermDirectory.Meta):
        verbose_name = u'переходность глагола'
        verbose_name_plural = u'переходность глагола'

class SyntArgument(TermDirectory):

    class Meta(TermDirectory.Meta):
        verbose_name = u'синтаксический аргумент'
        verbose_name_plural = u'синтаксические аргументы'


class SubcatFrame(models.Model):

    argument1 = models.ForeignKey(
        SyntArgument,
        verbose_name = u'1-й аргумент',
        related_name = 'argument1_set',
        )

    argument2 = models.ForeignKey(
        SyntArgument,
        verbose_name = u'2-й аргумент',
        related_name = 'argument2_set',
        blank = True,
        null = True,
        )

    argument3 = models.ForeignKey(
        SyntArgument,
        verbose_name = u'3-й аргумент',
        related_name = 'argument3_set',
        blank = True,
        null = True,
        )

    argument4 = models.ForeignKey(
        SyntArgument,
        verbose_name = u'4-й аргумент',
        related_name = 'argument4_set',
        blank = True,
        null = True,
        )

    def __unicode__(self):
        
        rtn = self.argument1.abbreviation
        if self.argument2:
            rtn = u'%s, %s' % (rtn, self.argument2.abbreviation)
        if self.argument3:
            rtn = u'%s, %s' % (rtn, self.argument3.abbreviation)
        if self.argument4:
            rtn = u'%s, %s' % (rtn, self.argument4.abbreviation)
        return rtn

    class Meta:
        verbose_name = u'модель управления'
        verbose_name_plural = u'модели управления'

