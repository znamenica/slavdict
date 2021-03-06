# -*- coding: utf-8 -*-
import base64
import datetime
import random
import re
import StringIO
import urllib

from coffin.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import InvalidPage
from django.db.models import Q
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template import RequestContext
from django.views.decorators.cache import never_cache

from slavdict import unicode_csv
from slavdict.dictionary import filters
from slavdict.dictionary import models
from slavdict.dictionary import viewmodels
from slavdict.custom_user.models import CustomUser
from slavdict.dictionary.forms import BilletImportForm
from slavdict.dictionary.forms import FilterEntriesForm
from slavdict.dictionary.forms import FilterExamplesForm
from slavdict.dictionary.models import civilrus_convert
from slavdict.dictionary.models import Entry
from slavdict.dictionary.models import Etymology
from slavdict.dictionary.models import Example
from slavdict.dictionary.models import GreekEquivalentForExample
from slavdict.dictionary.models import OrthographicVariant



# Вспомогательная функция
# для сортировки списка словарных статей.
def entry_key(entry):
    return u'%s %s' % ( entry.civil_equivalent.lower(), entry.homonym_order )


@login_required
def direct_to_template(request, template):
    empty_context = {}
    return render_to_response(template, empty_context, RequestContext(request))


@login_required
def all_entries(request, is_paged=False):
    if not request.GET:
        text = u'''
Отображение статей как бы для печати. Для фильтрации статей используйте
параметры адреса данной страницы, например:

    %s?authors=Калужнина&startswith=В

Данный запрос найдет все статьи Калужниной, начинающиеся с буквы «В».


Допустимые параметры
====================

?authors=Петрова,Корнилаева     Статьи соответствующих авторов. Для статей без
                                авторства используйте сочетание "без автора",
                                для авторских статей — фамилию автора.

?startswith=Ав                  Отображать только статьи, начинающиеся
                                на «Ав» без учета регистра символов.

?duplicates                     Отображать только статьи-дубликаты.

?corrupted-greek                Статьи, где есть примеры с испорченными
                                греческими соответствиями.

?goodness                       Отображать только "хорошие" статьи.

?hide-ai                        При отображении статей не показывать рабочие
                                примечания-комментарии.

?show-ai                        При отображении статей обязательно показывать
                                рабочие примечания-комментарии.

?hide-numbers                   Не нумеровать статьи.

?list=1324,3345,22              Отображать только статьи с указанными
                                числовыми идентификаторами.

?status=в работе,поиск греч.    Отображать только статьи с перечиленными
?status=-создана                значениями поля "статус статьи". При постановке
                                перед наименованием статуса знака минус статьи
                                с данным статусом будут исключены из выборки.

?hide-refentries                Не отображать отсылочные статьи.


        ''' % request.path
        response = HttpResponse(text, content_type="text/plain; charset=utf-8")
        return response

    httpGET_AUTHORS = urllib.unquote(request.GET.get('authors', ''))
    httpGET_CORRUPTED_GREEK = 'corrupted-greek' in request.GET
    httpGET_DUPLICATES = 'duplicates' in request.GET
    httpGET_GOODNESS = request.GET.get('goodness')
    httpGET_HIDEAI = 'hide-ai' in request.GET
    httpGET_HIDENUMBERS = 'hide-numbers' in request.GET
    httpGET_LIST = request.GET.get('list')
    httpGET_SHOWAI = 'show-ai' in request.GET
    httpGET_STARTSWITH = request.GET.get('startswith')
    httpGET_STATUS = urllib.unquote(request.GET.get('status', ''))
    httpGET_HIDEREFENTRIES = 'hide-refentries' in request.GET

    COMMA = re.compile(ur'\s*\,\s*')
    SPACE = re.compile(ur'\s+')
    entries = Entry.objects.all()

    if httpGET_AUTHORS:
        httpGET_AUTHORS = [a.strip() for a in COMMA.split(httpGET_AUTHORS)]
        httpGET_AUTHORS = [SPACE.sub(u' ', a) for a in httpGET_AUTHORS]
        httpGET_AUTHORS = [a[:1].upper() + a[1:].lower() for a in httpGET_AUTHORS]
        query = Q(authors__last_name__in=httpGET_AUTHORS)
        if u'Без автора' in httpGET_AUTHORS:
            query = query | Q(authors__isnull=True)
        entries = entries.filter(query)

    if httpGET_STARTSWITH:
        httpGET_STARTSWITH = httpGET_STARTSWITH.strip()
        entries = entries.filter(
                civil_equivalent__istartswith=httpGET_STARTSWITH)

    if httpGET_STATUS:
        httpGET_STATUS = COMMA.split(httpGET_STATUS)
        httpGET_STATUS = [SPACE.sub(u' ', s.strip()) for s in httpGET_STATUS]
        httpGET_STATUS = [s.lower() for s in httpGET_STATUS]
        statuus = []
        exclude_statuus = []
        for status in httpGET_STATUS:
            for value, label in models.STATUS_CHOICES:
                if status[0] == u'-':
                    status = status[1:]
                    lst = exclude_statuus
                else:
                    lst = statuus
                if label.startswith(status):
                    lst.append(value)
        if exclude_statuus:
            entries = entries.exclude(status__in=exclude_statuus)
        if statuus:
            entries = entries.filter(status__in=statuus)

    if httpGET_GOODNESS:
        g = httpGET_GOODNESS
        if len(g) == 1:
            entries = entries.filter(good=g)
        else:
            g = g.split(',')
            entries = entries.filter(good__in=g)

    if httpGET_DUPLICATES:
        entries = entries.filter(duplicate=True)

    if httpGET_LIST:
        try:
            httpGET_LIST = [int(i) for i in httpGET_LIST.split(',')]
        except ValueError:
            pass
        else:
            entries = entries.filter(pk__in=httpGET_LIST)

    if httpGET_CORRUPTED_GREEK:
        greek_etymons = Etymology.objects.filter(
                language=models.LANGUAGE_MAP['greek'],
                corrupted=True)
        greqex = GreekEquivalentForExample.objects.filter(corrupted=True)

        # WARNING: Переменная entries теперь будет содержать обычный список
        # вместо объекта django.db.models.query.QuerySet, так что теперь на
        # entries больше нельзя нанизывать никаких фильтров.
        entries = set([i.host_entry for i in greek_etymons])
        entries.update([i.host_entry for i in greqex])
        entries = list(entries)
        entries.sort(key=lambda entry: entry.civil_equivalent)

    # Формирование заголовка страницы в зависимости от переданных
    # GET-параметров
    if httpGET_DUPLICATES:
        title = u'Статьи-дубликаты'
    else:
        if httpGET_AUTHORS:
            title = u'Статьи авторов %s' % u', '.join(httpGET_AUTHORS)
        else:
            title = u'Все статьи'

    if httpGET_STARTSWITH:
        title += u', начинающиеся на „{0}-“'.format(httpGET_STARTSWITH)

    entries = sorted(entries, key=entry_key)
    if is_paged:
        paginator = Paginator(entries, per_page=12, orphans=2)
        try:
            pagenum = int(request.GET.get('page', 1))
        except ValueError:
            pagenum = 1
        try:
            page = paginator.page(pagenum)
        except (EmptyPage, InvalidPage):
            page = paginator.page(paginator.num_pages)
        entries = page.object_list
    else:
        page = None

    show_additional_info = (httpGET_SHOWAI or
            'ai' in request.COOKIES and not httpGET_HIDENUMBERS)
    if httpGET_HIDEAI:
        show_additional_info = False

    context = {
        'entries': entries,
        'show_numbers': not httpGET_HIDENUMBERS,
        'show_refentries': not httpGET_HIDEREFENTRIES,
        'title': title,
        'show_additional_info': show_additional_info,
        'show_duplicates_warning': False if httpGET_DUPLICATES else True,
        'user': request.user,
        'is_paged': is_paged,
        'page': page,
        'params_without_page': urllib.urlencode(
            dict(
                (k, unicode(v).encode('utf-8'))
                for k, v in request.GET.items()
                if k != 'page'
            )
        ),
        }
    return render_to_response('all_entries.html',
                              context, RequestContext(request))


@login_required
def all_examples(request, is_paged=False, mark_as_audited=False,
                                          mark_as_unaudited=False):
    httpGET_ADDRESS = request.GET.get('address')
    httpGET_ADDRESS_REGEX = request.GET.get('address-regex')
    httpGET_ADDRESS_GREP_V = request.GET.get('address-grep-v')
    httpGET_AUDITED = request.GET.get('audited') or ('audited' in request.GET)
    httpGET_EXCLUDE = request.GET.get('exclude')
    httpGET_HIDEAI = 'hide-ai' in request.GET
    httpGET_HIDENUMBERS = 'hide-numbers' in request.GET
    httpGET_INCLUDE_ONLY = request.GET.get('include-only')
    httpGET_SHOWAI = 'show-ai' in request.GET
    httpGET_STATUS = request.GET.get('status')
    httpGET_SUBSET_OF = request.GET.get('subset-of')

    examples = Example.objects.all().order_by('address_text')

    if httpGET_AUDITED:
        if httpGET_AUDITED == '2':
            # Отобразить и "проверенные", и "непроверенные" примеры.
            pass
        else:
            # Отобразить только "проверенные" примеры.
            examples = examples.filter(audited=True)
    else:
        # Отобразить только "НЕпроверенные" примеры.
        examples = examples.filter(audited=False)

    if httpGET_ADDRESS_REGEX:
        examples = examples.filter(address_text__iregex=httpGET_ADDRESS_REGEX)
    elif httpGET_ADDRESS:
        examples = examples.filter(address_text__istartswith=httpGET_ADDRESS)

    if httpGET_ADDRESS_GREP_V:
        examples = examples.exclude(address_text__iregex=httpGET_ADDRESS_GREP_V)

    if (httpGET_STATUS and httpGET_STATUS in
                       (status for status, name in Example.GREEK_EQ_STATUS)):
        examples = examples.filter(greek_eq_status=httpGET_STATUS)

    if httpGET_EXCLUDE:
        excludes = [int(ID)
                    for ID in [i.strip().split('-')[-1]
                               for i in httpGET_EXCLUDE.split(',')]
                    if ID.isdigit()]
        examples = examples.exclude(pk__in=excludes)

    if httpGET_INCLUDE_ONLY:
        includes = [int(ID)
                    for ID in [i.strip().split('-')[-1]
                               for i in httpGET_INCLUDE_ONLY.split(',')]
                    if ID.isdigit()]
        examples = Example.objects.filter(pk__in=includes)

    is_subset = None
    parts = []
    if httpGET_SUBSET_OF:
        superset = set(int(ID)
                       for ID in [i.strip().split('-')[-1]
                                  for i in httpGET_SUBSET_OF.split(',')]
                       if ID.isdigit())
        subset = set(example.id for example in examples)
        is_subset = subset.issubset(superset)

        unionset = sorted(superset.union(subset))
        superset, subset = sorted(superset), sorted(subset)

        cursor = -1
        kind = None  # 'both' or 'superset' or 'subset'
        for i in unionset:
            if i in superset and i in subset:
                if kind == 'both':
                    parts[cursor][1].append(i)
                else:
                    cursor += 1
                    kind = 'both'
                    parts.append((kind, [i]))
            if i in superset and not i in subset:
                if kind == 'superset':
                    parts[cursor][1].append(i)
                else:
                    cursor += 1
                    kind = 'superset'
                    parts.append((kind, [i]))
            if not i in superset and i in subset:
                if kind == 'subset':
                    parts[cursor][1].append(i)
                else:
                    cursor += 1
                    kind = 'subset'
                    parts.append((kind, [i]))


    # Формирование заголовка страницы в зависимости от переданных GET-параметров
    title = u'Примеры'
    if httpGET_ADDRESS:
        title += u', с адресом на „{0}...“'.format(httpGET_ADDRESS)

    SORT_REGEX = re.compile(ur'[\s\.\,\;\:\-\(\)\!]+', re.UNICODE)
    def key_emitter(x):
        x = x.address_text.strip().lower()
        parts = SORT_REGEX.split(x)
        parts = [ int(part) if part.isdigit() else part
                  for part in parts ]
        return parts

    examples = sorted(examples, key=key_emitter)
    if is_paged:
        paginator = Paginator(entries, per_page=12, orphans=2)
        try:
            pagenum = int(request.GET.get('page', 1))
        except ValueError:
            pagenum = 1
        try:
            page = paginator.page(pagenum)
        except (EmptyPage, InvalidPage):
            page = paginator.page(paginator.num_pages)
        examples = page.object_list
    else:
        page = None

    show_additional_info = (httpGET_SHOWAI or
            'ai' in request.COOKIES and not httpGET_HIDENUMBERS)
    if httpGET_HIDEAI:
        show_additional_info = False

    context = {
        'examples': examples,
        'show_numbers': not httpGET_HIDENUMBERS,
        'title': title,
        'show_additional_info': show_additional_info,
        'is_paged': is_paged,
        'page': page,
        'params_without_page': urllib.urlencode(
            dict(
                (k, unicode(v).encode('utf-8'))
                for k, v in request.GET.items()
                if k != 'page'
            )
        ),
        'is_subset': is_subset,
        'unionset': parts,
        }

    if mark_as_audited or mark_as_unaudited:
        mark = mark_as_audited #  or not mark_as_unaudited
        for example in examples:
            example.audited = mark
            example.save(without_mtime=True)
        url = '/print/examples/'
        if context['params_without_page']:
            url += '?' + context['params_without_page']
        return redirect(url)

    return render_to_response('all_examples.html',
                              context, RequestContext(request))


@login_required
def single_entry(request, entry_id, extra_context=None,
                 template='single_entry.html'):
    if not extra_context:
        extra_context = {}
    entry = get_object_or_404(Entry, id=entry_id)
    user = request.user

    if request.path.endswith('intermed/'):
        user_groups = [t[0] for t in user.groups.values_list('name')]
        if (not entry.authors.exists() or user.is_superuser
        or 'editors' in user_groups or 'admins' in user_groups
        or user in entry.authors.all()):
            pass
        else:
            return redirect(entry.get_absolute_url())

    context = {
        'entry': entry,
        'title': u'Статья «%s»' % entry.civil_equivalent,
        'show_additional_info': 'ai' in request.COOKIES,
        'user': user,
    }
    context.update(extra_context)
    return render_to_response(template, context, RequestContext(request))


@login_required
def switch_additional_info(request):
    referer = request.META.get('HTTP_REFERER', '/')
    response = redirect(referer)
    if 'ai' in request.COOKIES:
        response.delete_cookie('ai')
    else:
        date_expired = datetime.datetime.now() + datetime.timedelta(days=90)
        response.set_cookie('ai', max_age=7776000, expires=date_expired)
    return response


@login_required
def import_csv_billet(request):

    if request.method == 'POST':
        form = BilletImportForm(request.POST, request.FILES)
        if form.is_valid():

            csvfile = request.FILES['csvfile']
            csv_reader = unicode_csv.UnicodeReader(csvfile,
                    dialect=unicode_csv.calc, encoding='utf-8')

            output = StringIO.StringIO()
            csv_writer = unicode_csv.UnicodeWriter(output,
                    dialect=unicode_csv.calc, encoding='utf-8')

            # Первую строку, -- в ней обязаны быть заголовки, --
            # упреждающе записываем в возможный файл возврата конфликтующих
            # csv-записей.
            csv_writer.writerow(csv_reader.next())

            # Список списков, каждый из которых содержит один элемент.
            idems = OrthographicVariant.objects.all().values_list('idem')

            # Переходим от списка списков к списку самих элементов
            # (орфографических вариантов).
            idems = [x[0] for x in idems]

            # Оформляем орф.варианты в виде множества, а не списка
            idems = set(idems)

            authors = CustomUser.objects.all()

            orthvar_collisions = False
            csv_authors = {u'': None}

            # Регулярное выражение для отыскания любой черты (прямой, косой,
            # обратной косой), обрамленной любым количеством пробельного
            # материала.
            bar = re.compile(r"\s*[/\|\\]\s*", re.MULTILINE + re.UNICODE)

            for row in csv_reader:
                # Столбцы в CSV-файле
                (orthvars_info, civil_equivalent, word_forms_list,
                        antconc_query, author_in_csv, additional_info,
                        homonym_order, homonym_gloss, duplicate) = row

                # Обработка поля с орфографическими вариантами.
                # Орфографические варианты разделяются любой чертой (прямой,
                # косой или обратной косой).  Звездочка означает, что
                # орфогр.вариант был реконструирован. Вопросительный знак --
                # сомнения в правильности реконструкции. Черты и знаки могут
                # отделяться друг от друга и от орф.вариантов любым количеством
                # пробельного материала.
                _list = bar.split(orthvars_info)
                orthvars_list = [
                        (
                            i.strip(" \r\n\t*?"),
                            "*" in i,
                            "?" in i
                        )
                        for i in _list
                ]
                orthvars_set = set([i[0] for i in orthvars_list])

                # GET-параметр "force":
                #
                # =add    -- добавить лексему, даже если похожие лексемы
                #            уже есть.
                #
                # =update -- если похожая лексема всего одна, то дополнить
                #            информацию по ней из CSV-файла.
                #
                force = request.GET.get('force', False)
                intersection = idems.intersection(orthvars_set)

                if not force and intersection:
                    orthvar_collisions = True
                    csv_writer.writerow(row)
                else:
                    author_in_csv = author_in_csv.lower()
                    if author_in_csv in csv_authors:
                        author = csv_authors[author_in_csv]
                    else:
                        for au in authors:
                            if au.last_name and author_in_csv.startswith(
                                                    au.last_name.lower()):
                                author = au
                                csv_authors[author_in_csv] = au
                                break
                        else:
                            raise NameError(u"""Автор, указанный в CSV-файле,
                            не найден среди участников работы над словарём.""")

                    # Если поле с гражданским эквивалентом пусто, то берем
                    # конвертацию в гражданку заглавного слова. Если же это
                    # поле заполнено, то берём его без изменений.
                    # С практической точки зрения это значит, что в CSV-файле
                    # можно не указывать гражданку для слов без титл, они
                    # автоматом должны хорошо преобразовываться. А для слов
                    # с титлами или буквотитлами гражданку лучше указывать,
                    # чтобы впоследствии не надо было её уточнять из форм
                    # вроде "бл*годетель".
                    if not civil_equivalent.strip():
                        civil_equivalent = civilrus_convert(orthvars_list[0][0])

                    from_csv = {
                        'word_forms_list': word_forms_list,
                        'civil_equivalent': civil_equivalent,
                        'antconc_query': antconc_query,
                        'additional_info': additional_info,
                        'homonym_order': (int(float(homonym_order))
                                          if homonym_order else None),
                        'homonym_gloss': homonym_gloss or u'',
                        'duplicate': bool(duplicate),
                    }
                    raise NameError(u'''В переменной from_csv необходимо
                                        учесть новое поле authors.''')

                    entry = Entry()
                    if not intersection or (force == 'add'):
                        entry.__dict__.update(from_csv)
                        entry.__dict__.update({
                            'reconstructed_headword': orthvars_list[0][1],
                            'questionable_headword': orthvars_list[0][2],
                            })

                        entry.save()

                        for i in orthvars_list:
                            orthvar = i[0]
                            ov = OrthographicVariant.objects.create(
                                                entry=entry, idem=orthvar)
                            ov.save()
                            idems.add(orthvar)
                    elif intersection and (force=='update'):
                        raise NameError(u"""Поддержка GET-параметра 'force'
                                со значением 'update' ещё не реализована.""")
                        # Вытягиваем из базы все словарные статьи, у которых
                        # встречаются хотя бы один из орф.вариантов Если их
                        # больше одной, выплёвываем строку таблицы в csv-файл.
                        # Если нет, то заменяем запрос для АнтКонка, дополняем
                        # доп.инфо через "||". Для каждого орф.варианта если
                        # он уже существует обновляем флаги реконструкции
                        # и надежности. Если нет, добавляем его полностью.
                    else:
                        raise NameError(u"""Поддержка GET-параметра 'force'
                          со значением '{0}' не реализована.""".format(force))

            if 'force' not in request.GET and orthvar_collisions:
                response = HttpResponse(output.getvalue(), content_type="text/csv")
                response['Content-Disposition'] = ('attachment; '
                        'filename={:%Y.%m.%d--%H.%M.%S}--not.imported.csv'
                        .format(datetime.datetime.now()))
            else:
                response = HttpResponseRedirect('/')

            output.close()
            csvfile.close()
            return response
    else:
        form = BilletImportForm()

    get_parameters = '?' + urllib.urlencode(request.GET)
    return render_to_response('csv_import.html', {'form': form,
                  'get_parameters': get_parameters})


@login_required
def entry_list(request):
    if 'find' in request.COOKIES:
        request.COOKIES['find'] = base64 \
            .standard_b64decode(request.COOKIES['find']) \
            .decode('utf8')

    if request.method == 'POST' and len(request.POST) > 1:
        # Сам по себе объект QueryDict, на который указывает request.POST,
        # является неизменяемым. Метод ``copy()`` делает его полную уже
        # доступную для изменения копию.
        data = request.POST.copy()
        if request.POST['hdrSearch']:
            data['find'] = request.POST['hdrSearch']
    else:
        data = dict(FilterEntriesForm.default_data)
        data.update(request.COOKIES)
        if (request.method == 'POST' and len(request.POST) == 1
        and 'hdrSearch' in request.POST):
            data['find'] = request.POST['hdrSearch']

    form = FilterEntriesForm(data)
    assert form.is_valid(), u'Форма заполнена неправильно'
    entries = filters.get_entries(form.cleaned_data)

    paginator = Paginator(entries, per_page=12, orphans=2)
    if request.method == 'POST':
        pagenum = 1
    else:
        try:
            pagenum = int(request.GET.get('page', 1))
        except ValueError:
            pagenum = 1
    try:
        page = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    context = {
        'viewmodel': {
            'authors': viewmodels.jsonAuthors,
            'canonical_name': viewmodels.jsonCanonicalName,
            'gender': viewmodels.jsonGenders,
            'onym': viewmodels.jsonOnyms,
            'pos': viewmodels.jsonPos,
            'possessive': viewmodels.jsonPossessive,
            'statuses': viewmodels.jsonStatuses,
            'sortdir': viewmodels.jsonSortdir,
            'sortbase': viewmodels.jsonSortbase,
            'tantum': viewmodels.jsonTantum,
            },
        'entries': page.object_list,
        'number_of_entries': paginator.count,
        'form': form,
        'page': page,
        'user': request.user,
        }
    response = render_to_response('entry_list.html', context,
                                  RequestContext(request))
    if request.method == 'POST':
        form.cleaned_data['find'] = base64 \
            .standard_b64encode(form.cleaned_data['find'].encode('utf8'))
        for param, value in form.cleaned_data.items():
            response.set_cookie(param, value, path=request.path)
    return response


@login_required
def hellinist_workbench(request):
    if 'hwPrfx' in request.COOKIES:
        request.COOKIES['hwPrfx'] = base64 \
            .standard_b64decode(request.COOKIES['hwPrfx']) \
            .decode('utf8')

    if 'hwAddress' in request.COOKIES:
        request.COOKIES['hwAddress'] = base64 \
            .standard_b64decode(request.COOKIES['hwAddress']) \
            .decode('utf8')

    if request.method == 'POST':
        data = request.POST
    else:
        data = FilterExamplesForm.default_data
        data.update(request.COOKIES)

    form = FilterExamplesForm(data)
    assert form.is_valid(), u'Форма FilterExamplesForm заполнена неправильно'
    examples = filters.get_examples(form.cleaned_data)

    paginator = Paginator(examples, per_page=4, orphans=2)
    if request.method == 'POST':
        pagenum = 1
    else:
        try:
            pagenum = int(request.GET.get('page', 1))
        except ValueError:
            pagenum = 1
    try:
        page = paginator.page(pagenum)
    except (EmptyPage, InvalidPage):
        page = paginator.page(paginator.num_pages)

    vM_examples = [
    {
        'id': e.id,
        'triplet': e.context_ucs,
        'antconc': e.context.strip() or e.example,
        'example': e.example,
        'address': e.address_text,
        'status': e.greek_eq_status,
        'comment': e.additional_info,
        'greqs': [
            {
                'unitext': greq.unitext,
                'initial_form': greq.initial_form,
                'id': greq.id,
                'additional_info': greq.additional_info
            }
            for greq in e.greek_equivs]
    }
    for e in page.object_list]

    context = {
        'examples': page.object_list,
        'form': form,
        'jsonExamples': viewmodels._json(vM_examples),
        'number_of_examples': paginator.count,
        'indicators': {
            'urgent': Example.objects.filter(greek_eq_status=u'U').count(),
            'meaning': Example.objects.filter(greek_eq_status=u'M').count(),
            },
        'page': page,
        'statusList': models.Example.GREEK_EQ_STATUS,
        'title': u'Греческий кабинет',
        'viewmodel': {
            'authors': viewmodels.jsonAuthors,
            'statuses': viewmodels.jsonGreqStatuses,
            'sortdir': viewmodels.jsonSortdir,
            'sortbase': viewmodels.jsonGreqSortbase,
            },
        }
    response = render_to_response('hellinist_workbench.html', context,
                                  RequestContext(request))
    if request.method == 'POST':
        form.cleaned_data['hwPrfx'] = base64 \
            .standard_b64encode(form.cleaned_data['hwPrfx'].encode('utf8'))
        form.cleaned_data['hwAddress'] = base64 \
            .standard_b64encode(form.cleaned_data['hwAddress'].encode('utf8'))
        for param, value in form.cleaned_data.items():
            response.set_cookie(param, value, path=request.path)
    return response


@login_required
def antconc2ucs8_converter(request):
    random.seed()
    examples = (
        u"Дрꙋ'гъ дрꙋ'га тѧготы^ носи'те, и та'кѡ испо'лните зако'нъ хрСто'въ.",

        u"Ѿ дне'й же іѡа'нна крСти'телѧ досе'лѣ, црСтвіе нбСное нꙋ'дитсѧ, "
        u"и нꙋ'ждницы восхища'ютъ є`",

        u"Пре'жде же всѣ'хъ дрꙋ'гъ ко дрꙋ'гꙋ любо'вь прилѣ'жнꙋ имѣ'йте: "
        u"зане` любо'вь покрыва'етъ мно'жество грѣхѡ'въ. "
        u"Страннолю'бцы дрꙋ'гъ ко дрꙋ'гꙋ, безЪ ропта'ній.",

        u"Наказꙋ'ѧ наказа' мѧ гдСь, сме'рти же не предаде' мѧ",

        u"Вни'дите ѹ'зкими враты`, ꙗ'кѡ простра'ннаѧ врата`, и широ'кій "
        u"пꙋ'ть вводѧ'й въ па'гꙋбꙋ, и мно'зи сꙋ'ть входѧ'щіи и'мъ. Что` "
        u"ѹ'зкаѧ врата`, и тѣ'сный пꙋ'ть вводѧ'й въ живо'тъ, и ма'лѡ и'хъ "
        u"є'сть, и`же ѡбрѣта'ютъ єго`",

        u"Бꙋ'дите ѹ'бѡ вы` соверше'ни, ꙗ'коже ѻц~ъ ва'шъ нбСный "
        u"соверше'нъ є'сть.",

        u"Возведо'хъ ѻ'чи мои` въ го'ры, ѿню'дꙋже пріи'детъ по'мощь моѧ`",
    )
    context = { 'convertee': random.choice(examples) }
    return render_to_response('converter.html', context,
                              RequestContext(request))


@login_required
@never_cache
def edit_entry(request, id):
    choices = {
        'author': viewmodels.editAuthors,
        'entry_status': viewmodels.editStatuses,
        'gender': viewmodels.editGenders,
        'onym': viewmodels.editOnyms,
        'part_of_speech': viewmodels._choices(
                            models.PART_OF_SPEECH_CHOICES),
        'participle_type': viewmodels.editParticiples,
        'substantivus_type': viewmodels.editSubstantivusTypes,
        'tantum': viewmodels.editTantum,
    }
    labels = {
        'author': dict(viewmodels.AUTHOR_CHOICES),  # sic! viewmodels
        'entry_status': dict(models.STATUS_CHOICES),
        'gender': dict(models.GENDER_CHOICES),
        'onym': dict(models.ONYM_CHOICES),
        'part_of_speech': dict(models.PART_OF_SPEECH_CHOICES),
        'participle_type': dict(models.PARTICIPLE_CHOICES),
        'substantivus_type': dict(models.SUBSTANTIVUS_TYPE_CHOICES),
        'tantum': dict(models.TANTUM_CHOICES)
    }
    slugs = {
        'onym': models.ONYM_MAP,
        'part_of_speech': models.PART_OF_SPEECH_MAP,
    }
    context = {
        'entry': viewmodels.entry_json(id),
        'choices': viewmodels._json(choices),
        'labels': viewmodels._json(labels),
        'slugs': viewmodels._json(slugs),
        'entryURL': Entry.objects.get(pk=id).get_absolute_url(),
        'PARTS_OF_SPEECH': models.PART_OF_SPEECH_CHOICES,
        'GENDERS': models.GENDER_CHOICES,
        'STATUSES': models.STATUS_CHOICES,
        'GREEK_EQ_STATUSES': models.Example.GREEK_EQ_STATUS,
        'SUBSTANTIVUS_TYPES': models.SUBSTANTIVUS_TYPE_CHOICES,
        'MAX_LENGTHS': models.MAX_LENGTHS,
    }
    return render_to_response('single_entry_edit.html', context,
                              RequestContext(request))

@login_required
def dump(request):
    import os
    pid = os.fork()
    if not pid:
        # NOTE: Избавляемся от процессов-зомби, создавая дочерний процесс
        # дочернего процесса. См. http://stackoverflow.com/a/16809886
        # Использовать сигналы ``signal.signal(signal.SIGCHLD,
        # signal.SIG_IGN)`` не получается, поскольку данная функция сама будет
        # выполняться джангой не в родительском процессе.
        pid = os.fork()
        if not pid:
            os.execvp('python', ('python', 'url_mail_dumper.py'))
            raise NameError(u'В параллельном процессе отсылки дампа базы '
                            u'возникла непредвиденная ошибка.')
        else:
            os._exit(0)
    else:
        os.wait()
    return  HttpResponseRedirect('/')
