# coding: utf-8

def tmpl(e, i):
    cslav = u'<span style="font-family: Triodion Ucs;">%s</span>'
    cslav_affix = u'-<span style="font-family: Triodion Ucs;">%s</span>'
    txt = u''
    ov = e.orthographic_variants.all()[0]
    if ov.idem:
                txt = u'<span class="headword">%s</span></td><td>' % cslav % ov.idem_ucs
    else:
        return u''
    if e.homonym_order:
        txt += u' <span class="homonym_order">%s</span>' % e.homonym_order
        if e.homonym_gloss:
            txt += u' <span class="homonym_gloss">[%s]</span>' % e.homonym_gloss

    if e.genitive:
        affix, form = e.genitive_ucs_wax
        if affix:
            x = cslav_affix % form
        else:
            x = cslav % form
        txt += u' <span class="genitive">%s</span>' % x
    if e.nom_sg:
        affix, form = e.nom_sg_ucs_wax
        if affix:
            x = cslav_affix % form
        else:
            x = cslav % form
        txt += u' <span class="nom_sg">%s</span>' % x
    if e.sg1:
        affix, form = e.sg1_ucs_wax
        if affix:
            x = cslav_affix % form
        else:
            x = cslav % form
        txt += u' <span class="sg1">%s</span>' % x
    if e.sg2:
        affix, form = e.sg2_ucs_wax
        if affix:
            x = cslav_affix % form
        else:
            x = cslav % form
        txt += u' <span class="sg2">%s</span>' % x
    if e.short_form:
        affix, form = e.short_form_ucs_wax
        if affix:
            x = cslav_affix % form
        else:
            x = cslav % form
        txt += u' <span class="short_form">%s</span>' % x

    txt += u' %s' % e.get_part_of_speech_display()
    if e.uninflected:
        txt += u' <span class="uninflected">неизм.</span>'
    if e.possessive:
        txt += u' <span class="possessive">притяж.</span>'
    if e.gender:
        txt += u' <span class="gender">%s</span>' % e.get_gender_display()
    if e.tantum:
        txt += u' <span class="tantum">%s</span>' % e.get_tantum_display()
    if e.onym:
        txt += u' <span class="onym">%s</span>' % e.get_onym_display()

    return u'<tr><td>%s</td><td>%s</td><td>%s</td></tr>' % (i, e.id, txt)


from django.db.models import Q
from slavdict.dictionary.models import Entry
l = Entry.objects.filter(
        Q(civil_equivalent__istartswith=u'а') |
        Q(civil_equivalent__istartswith=u'б')
    )
l = list(l)
l.sort(key=lambda e: u''.join(reversed(e.civil_equivalent)))

html_start = u'''<!DOCTYPE html>
<html>
    <head>
        <meta http-equiv="content-type" content="text/html; charset=utf-8">
        <title></title>
        <style>
            table {
                border-collapse: collapse;

            }
            td, td * {
                border: 0px transparent hidden;
                font-size: 12px;
                font-style: italic;
            }
            td {
                padding-right: 1em;
            }
            td:first-child,
            td:nth-child(2) {
                font-style: normal !important;
            }
            td:nth-child(3) {
                text-align: right;
            }
            td [style] {
                font-size: 16px;
                font-style: normal;
            }
            td .homonym_gloss,
            td .homonym_order {
                font-style: normal !important;
            }
            td .headword span {
                font-size: 20px !important;
            }

        </style>
    </head>
    <body>
        <table>
'''
html_end = u'''
        </table>
    </body>
</html>
'''

with open('invers.html', 'w') as f:
    for i, e in enumerate(l):
        x = tmpl(e, i + 1)
        if x:
            f.write(html_start)
            x += u'\n'
            f.write(x)
            f.write(html_end)

with open('invers-revers.html', 'w') as f:
    n = len(l)
    for i, e in enumerate(reversed(l)):
        x = tmpl(e, n - i)
        if x:
            f.write(html_start)
            x += u'\n'
            f.write(x);
            f.write(html_end)

