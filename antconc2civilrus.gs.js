var scriptAssets;

/**
 * Скрипт Google Docs
 * для конвертации из Антконк в гражданку.
 */
function makeCivil() {
  var sheet = SpreadsheetApp.getActiveSheet(),
      r = sheet.getDataRange().getNumRows(),
      srcCol = sheet.getRange('C2:C' + r),
      dstCol = sheet.getRange('A2:A' + r),
      srcValues = srcCol.getValues(),
      validAntconcValues = [],
      dstValues = [],
      validAntconcVal,
      val,
      invalidAntconc = false;

  for (var i = 0, j = (r - 1); i < j; i++) {
      val = srcValues[i][0];
      validAntconcVal = scriptAssets.toValidAntconc(val);
      validAntconcValues.push([validAntconcVal]);
      if (val != validAntconcVal) invalidAntconc = true;
      val = scriptAssets.antconc2civilrus(validAntconcVal);
      dstValues.push([val]);
  }
  dstCol.setValues(dstValues);
  if (invalidAntconc) srcCol.setValues(validAntconcValues);
};

/**
 * Adds a custom menu to the active spreadsheet, containing a single menu item
 * for invoking the readRows() function specified above.
 * The onOpen() function, when defined, is automatically invoked whenever the
 * spreadsheet is opened.
 * For more information on using the Spreadsheet API, see
 * https://developers.google.com/apps-script/service_spreadsheet
 */
function onOpen() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet();
  var entries = [{
    name : "Создать гражданский вариант заглавных слов",
    functionName : "makeCivil"
  }];
  sheet.addMenu("Скрипты", entries);
};

var scriptAssets = {
convert: function(word, conversion) {
    var conversion_len = conversion.length,
	pattern, replacement;
  
    for (var i = 0; i < conversion_len; i++) {
	pattern     = conversion[i][0];
	replacement = conversion[i][1];
	word        = word.replace(pattern, replacement);
    }
    return word;
},

toValidAntconc: function(word){
  var conversion = [
        [/s/g, '\u0455'], // s  -->  ѕ
        [/i/g, '\u0456'], // i  -->  і
        [/w/g, '\u0461'], // ѡ  -->  о
        [/v/g, '\u0475'], // ѵ  -->  и
    ];
    return this.convert(word, conversion);
},

antconc2civilrus: function(word){
    var conversion = [
        // Все буквы -- строчные.
        [/'/g,              ''],        // '  -->
        [/`/g,              ''],        // `  -->
        [/\^/g,            ''],        // \^  -->
        [/\u0430\u0433\u0433[\u0435\u0454]\u043b/g, '\u0430\u043d\u0433\u0435\u043b'],                    // а[']ггел  -->  ангел
        [/\u0430\u043f\u0421\u043b/g,           '\u0430\u043f\u043e\u0441\u0442\u043e\u043b'],              // апСл  -->  апостол
        [/\u0431\u0433~/g,                      '\u0431\u043e\u0433'],                                      // бг~  -->  бог
        [/\u0431\u0436~/g,                      '\u0431\u043e\u0436'],                                      // бж~  -->  бож
        [/\u0431\u0436\u0421\u0442\u0432/g,     '\u0431\u043e\u0436\u0435\u0441\u0442\u0432'],              // бжСтв  -->  божеств
        [/\u0431\u0437~/g,                      '\u0431\u043e\u0437'],                                      // бз~  -->  боз
        [/\u0431\u043b~\u0433/g,                '\u0431\u043b\u0430\u0433'],                                // бл~г  -->  благ
        [/\u0431\u043b~\u0436/g,                '\u0431\u043b\u0430\u0436'],                                // бл~ж  -->  блаж
        [/\u0431\u043b\u0413\u0432/g,           '\u0431\u043b\u0430\u0433\u043e\u0432'],                    // блГв  -->  благов
        [/\u0431\u043b\u0433\u0414\u0442/g,     '\u0431\u043b\u0430\u0433\u043e\u0434\u0430\u0442'],        // блгДт  -->  благодат
        [/\u0431\u043b\u0433\u0421\u0432/g,     '\u0431\u043b\u0430\u0433\u043e\u0441\u043b\u043e\u0432'],  // блгСв  -->  благослов
        [/\u0431\u043b\u0433\u0421/g,           '\u0431\u043b\u0430\u0433\u043e\u0441'],                    // блгС  -->  благос
        [/\u0431\u0446\u0414/g,                 '\u0431\u043e\u0433\u043e\u0440\u043e\u0434\u0438\u0446'],  // бцД  -->  богородиц
        [/\u0432\u043b\u0414\u043a/g,           '\u0432\u043b\u0430\u0434\u044b\u043a'],                    // влДк  -->  владык
        [/\u0432\u043b\u0414\u0446/g,           '\u0432\u043b\u0430\u0434\u044b\u0446'],                    // влДц  -->  владыц
        [/\u0432\u043b\u0414\u0447\u0446/g,     '\u0432\u043b\u0430\u0434\u044b\u0447\u0438\u0446'],        // влДчц  -->  владычиц
        [/\u0432\u043b\u0414\u0447/g,           '\u0432\u043b\u0430\u0434\u044b\u0447'],                    // влДч  -->  владыч
        [/\u0475\u0413\u043b/g,                 '\u0432\u0430\u043d\u0433\u0435\u043b'],                    // ѵГл  -->  вангел
        [/\u0475\u0413/g,                       '\u0432\u0430\u043d\u0433'],                                // ѵГ  -->  ванг
        [/\u0433\u0433~\u043b/g,                '\u043d\u0433\u0435\u043b'],                                // гг~л  -->  нгел
        [/\u0433\u043b~/g,                      '\u0433\u043b\u0430\u0433\u043e\u043b'],                    // гл~  -->  глагол
        [/\u0433\u043b\u0412/g,                 '\u0433\u043b\u0430\u0432'],                                // глВ  -->  глав
        [/\u0433\u0434\u0421\u043d\u044c/g,     '\u0433\u043e\u0441\u043f\u043e\u0434\u0435\u043d\u044c'],  // гдСнь  -->  господень
        [/\u0433\u0434\u0421\u0432/g,           '\u0433\u043e\u0441\u043f\u043e\u0434\u0435\u0432'],        // гдСв  -->  господев
        [/\u0433\u0434\u0421/g,                 '\u0433\u043e\u0441\u043f\u043e\u0434'],                    // гдС  -->  господ
        [/\u0433\u043f\u0421\u0436/g,           '\u0433\u043e\u0441\u043f\u043e\u0436'],                    // гпСж  -->  госпож
        [/\u0434\u0432~\u0434/g,                '\u0434\u0430\u0432\u0438\u0434'],                          // дв~д  -->  давид
        [/\u0434\u0432~/g,                      '\u0434\u0435\u0432'],                                      // дв~  -->  дев
        [/\u0434\u0432\u0421\u0442\u0432/g,     '\u0434\u0435\u0432\u0441\u0442\u0432'],                    // двСтв  -->  девств
        [/\u0434\u0441~/g,                      '\u0434\u0443\u0441'],                                      // дс~  -->  дус
        [/\u0434\u0445~/g,                      '\u0434\u0443\u0445'],                                      // дх~  -->  дух
        [/\u0434\u0448~/g,                      '\u0434\u0443\u0448'],                                      // дш~  -->  душ
        [/\u0438~\u0441/g,                      '\u0438\u0441\u0443\u0441'],                                // и~с  -->  исус
        [/\u0456\u0438~\u043b/g,                '\u0438\u0437\u0440\u0430\u0438\u043b'],                    // іи~л  -->  израил
        [/\u043a\u0440~\u0441/g,                '\u043a\u0440\u0435\u0441'],                                // кр~с  -->  крес
        [/\u043a\u0440\u0421\u0442/g,           '\u043a\u0440\u0435\u0441\u0442'],                          // крСт  -->  крест
        [/\u043c\u0414\u0440/g,                 '\u043c\u0443\u0434\u0440'],                                // мДр  -->  мудр
        [/\u043c\u043b~\u0442\u0432/g,          '\u043c\u043e\u043b\u0438\u0442\u0432'],                    // мл~тв  -->  молитв
        [/\u043c\u043b\u0414\u043d\u0446\u044a/g,   '\u043c\u043b\u0430\u0434\u0435\u043d\u0435\u0446'],    // млДнцъ  -->  младенец
        [/\u043c\u043b\u0414\u043d/g,           '\u043c\u043b\u0430\u0434\u0435\u043d'],                    // млДн  -->  младен
        [/\u043c\u043b\u0421\u0440\u0434/g,     '\u043c\u0438\u043b\u043e\u0441\u0435\u0440\u0434'],        // млСрд  -->  милосерд
        [/\u043c\u043b\u0421\u0442/g,           '\u043c\u0438\u043b\u043e\u0441\u0442'],                    // млСт  -->  милост
        [/\u043c\u043b\u0421/g,                 '\u043c\u0438\u043b\u043e\u0441'],                          // млС  -->  милос
        [/\u043c\u0442~\u0440/g,                '\u043c\u0430\u0442\u0435\u0440'],                          // мт~р  -->  матер
        [/\u043c\u0442~/g,                      '\u043c\u0430\u0442'],                                      // мт~  -->  мат
        [/\u043c\u0440~\u0456/g,                '\u043c\u0430\u0440\u0438'],                                // мр~і  -->  мари
        [/\u043c\u0420\u043a/g,                 '\u043c\u044f\u0440\u0435\u043a'],                          // мРк  -->  мярек
        [/\u043c\u0447~\u043d\u043a/g,          '\u043c\u0443\u0447\u0435\u043d\u0438\u043a'],              // мч~нк  -->  мученик
        [/\u043c\u0447~\u043d\u0446/g,          '\u043c\u0443\u0447\u0435\u043d\u0438\u0446'],              // мч~нц  -->  мучениц
        [/\u043c\u0447~\u043d\u0447/g,          '\u043c\u0443\u0447\u0435\u043d\u0438\u0447'],              // мч~нч  -->  мученич
        [/\u043c\u0447~\u043d/g,                '\u043c\u0443\u0447\u0435\u043d'],                          // мч~н  -->  мучен
        [/\u043c\u0446\u0421/g,                 '\u043c\u0435\u0441\u044f\u0446'],                          // мцС  -->  месяц
        [/\u043d\u0431~\u0441/g,                '\u043d\u0435\u0431\u0435\u0441'],                          // нб~с  -->  небес
        [/\u043d\u0431C/g,                      '\u043d\u0435\u0431\u0435\u0441'],                          // нбC  -->  небес
        [/\u043d\u0431~/g,                      '\u043d\u0435\u0431'],                                      // нб~  -->  неб
        [/\u043d\u043b\u0414/g,                 '\u043d\u0435\u0434\u0435\u043b'],                          // нлД  -->  недел
        [/\u043d\u043d~/g,                      '\u043d\u044b\u043d'],                                      // нн~  -->  нын
        [/\u047b'\u0447~\u044c/g,               '\u043e\u0442\u0435\u0447\u044c'],                          // ѻ'ч~ь  -->  отечь
        [/\u047b'\u0447~\u0454\u0441/g,         '\u043e\u0442\u0435\u0447\u0435\u0441'],                    // ѻ'ч~єс  -->  отечес
        [/\u047b'\u0447~\u0435\u0441/g,         '\u043e\u0442\u0435\u0447\u0435\u0441'],                    // ѻ'ч~ес  -->  отечес
        [/\u047b'\u0447~/g,                     '\u043e\u0442\u0447'],                                      // ѻ'ч~  -->  отч
        [/\u047b\u0446~\u044a/g,                '\u043e\u0442\u0435\u0446'],                                // ѻц~ъ  -->  отец
        [/\u047b\u0446~/g,                      '\u043e\u0442\u0446'],                                      // ѻц~  -->  отц
        [/\u043f\u0440\u0432\u0414\u043d\u044a/g,   '\u043f\u0440\u0430\u0432\u0435\u0434\u0435\u043d'],    // првДнъ  -->  праведен
        [/\u043f\u0440\u0432\u0414\u043d/g,     '\u043f\u0440\u0430\u0432\u0435\u0434\u043d'],              // првДн  -->  праведн
        [/\u043f\u0440\u0414\u0442\u0447/g,     '\u043f\u0440\u0435\u0434\u0442\u0435\u0447'],              // прДтч  -->  предтеч
        [/\u043f\u0440\u0414\u0442/g,           '\u043f\u0440\u0435\u0434\u0442'],                          // прДт  -->  предт
        [/\u043f\u0440\u043f\u0414\u0431/g,     '\u043f\u0440\u0435\u043f\u043e\u0434\u043e\u0431'],        // прпДб  -->  преподоб
        [/\u043f\u0440\u041e\u0440/g,           '\u043f\u0440\u043e\u0440'],                                // прОр  -->  прор
        [/\u043f\u0440\u0421\u043d/g,           '\u043f\u0440\u0438\u0441\u043d'],                          // прСн  -->  присн
        [/\u043f\u0440\u0421\u0442/g,           '\u043f\u0440\u0435\u0441\u0442'],                          // прСт  -->  прест
        [/\u043f\u0440\u0447\u0421\u0442/g,     '\u043f\u0440\u0435\u0447\u0438\u0441\u0442'],              // прчСт  -->  пречист
        [/\u043f\u0421\u043a\u043f/g,           '\u043f\u0438\u0441\u043a\u043e\u043f'],                    // пСкп  -->  пископ
        [/\u043f\u0421\u043a/g,                 '\u043f\u0438\u0441\u043a'],                                // пСк  -->  писк
        [/\u0440\u0436\u0421\u0442\u0432/g,     '\u0440\u043e\u0436\u0434\u0435\u0441\u0442\u0432'],        // ржСтв  -->  рождеств
        [/\u0440\u0421\u043b/g,                 '\u0440\u0443\u0441\u0430\u043b'],                          // рСл  -->  русал
        [/\u0441\u043b~\u043d\u0446/g,          '\u0441\u043e\u043b\u043d\u0446'],                          // сл~нц  -->  солнц
        [/\u0441\u043d~/g,                      '\u0441\u044b\u043d'],                                      // сн~  -->  сын
        [/\u0441\u043f~\u0441/g,                '\u0441\u043f\u0430\u0441'],                                // сп~с  -->  спас
        [/\u0441\u043f\u0421\u043d/g,           '\u0441\u043f\u0430\u0441\u0435\u043d'],                    // спСн  -->  спасен
        [/\u0441\u0440\u0414\u0446/g,           '\u0441\u0435\u0440\u0434\u0446'],                          // срДц  -->  сердц
        [/\u0441\u0440\u0414\u0447/g,           '\u0441\u0435\u0440\u0434\u0435\u0447'],                    // срДч  -->  сердеч
        [/\u0441\u0442~/g,                      '\u0441\u0432\u044f\u0442'],                                // ст~  -->  свят
        [/\u0441\u0442\u0440\u0421\u0442/g,     '\u0441\u0442\u0440\u0430\u0441\u0442'],                    // стрСт  -->  страст
        [/\u0441\u0425/g,                       '\u0441\u0442\u0438\u0445'],                                // сХ  -->  стих
        [/\u0441\u0442\u0425\u0440/g,           '\u0441\u0442\u0438\u0445\u0438\u0440'],                    // стХр  -->  стихир
        [/\u0441\u0449~/g,                      '\u0441\u0432\u044f\u0449'],                                // сщ~  -->  свящ
        [/\u0442\u0440\u041e\u0446/g,           '\u0442\u0440\u043e\u0438\u0446'],                          // трОц  -->  троиц
        [/\u0442\u0440\u041e\u0447/g,           '\u0442\u0440\u043e\u0438\u0447'],                          // трОч  -->  троич
        [/\u0442\u0440\u0421\u0442/g,           '\u0442\u0440\u0438\u0441\u0432\u044f\u0442'],              // трСт  -->  трисвят
        [/\u0445\u0440\u0421\u0442/g,           '\u0445\u0440\u0438\u0441\u0442'],                          // хрСт  -->  христ
        [/\u0446\u0440~\u043a/g,                '\u0446\u0435\u0440\u043a'],            // цр~к  -->  церк
        [/\u0446\u0440~/g,                      '\u0446\u0430\u0440'],                  // цр~  -->  цар
        [/\u0446\u0440\u0421/g,                 '\u0446\u0430\u0440\u0441'],            // црС  -->  царс
        [/\u0447\u043b~\u0432/g,                '\u0447\u0435\u043b\u043e\u0432'],      // чл~в  -->  челов
        [/\u0447~\u043d\u043a/g,                '\u0447\u0435\u043d\u0438\u043a'],      // ч~нк  -->  ченик
        [/\u0447~\u043d\u0446/g,                '\u0447\u0435\u043d\u0438\u0446'],      // ч~нц  -->  чениц
        [/\u0447~\u0442\u043b/g,                '\u0447\u0438\u0442\u0435\u043b'],      // ч~тл  -->  чител
        [/\u0447\u043d~\u043a/g,                '\u0447\u0435\u043d\u0438\u043a'],      // чн~к  -->  ченик
        [/\u0447\u043d~\u0446/g,                '\u0447\u0435\u043d\u0438\u0446'],      // чн~ц  -->  чениц
        [/\u0447\u043d~/g,                      '\u0447\u0435\u043d'],                  // чн~  -->  чен
        [/\u0447\u0421\u0442\u043d/g,           '\u0447\u0435\u0441\u0442\u043d'],      // чСтн  -->  честн
        [/\u0447\u0442\u0421\u043d/g,           '\u0447\u0435\u0441\u0442\u043d'],      // чтСн  -->  честн
        [/\u0447\u0421\u0442/g,                 '\u0447\u0438\u0441\u0442'],            // чСт  -->  чист
        [/\u0447\u0442\u0421/g,                 '\u0447\u0438\u0441\u0442'],            // чтС  -->  чист
        [/\u0447\u0442~\u043b/g,                '\u0447\u0438\u0442\u0435\u043b'],      // чт~л  -->  чител
        [/\u0454/g,         '\u0435'], // є  -->  е
        [/\u0455/g,         '\u0437'], // ѕ  -->  з
        [/\u0456/g,         '\u0438'], // і  -->  и
        [/\ua64b/g,         '\u0443'], // ꙋ  -->  у
        [/\u0479/g,         '\u0443'], // ѹ  -->  у
        [/\u0461/g,         '\u043e'], // ѡ  -->  о
        [/\u0463/g,         '\u0435'], // ѣ  -->  е
        [/\ua657/g,         '\u044f'], // ꙗ  -->  я
        [/\u0467/g,         '\u044f'],          // ѧ  -->  я
        [/\u046f/g,         '\u043a\u0441'],    // ѯ  -->  кс
        [/\u0471/g,         '\u043f\u0441'],    // ѱ  -->  пс
        [/\u0473/g,         '\u0444'],          // ѳ  -->  ф
        [/\u0430\u0475/g,   '\u0430\u0432'],    // аѵ  -->  ав
        [/\u0435\u0475/g,   '\u0435\u0432'],    // еѵ  -->  ев
        [/\u0454\u0475/g,   '\u0435\u0432'],    // єѵ  -->  ев
        [/\u0475/g,         '\u0438'],          // ѵ  -->  и
        [/\u047b/g,         '\u043e'],          // ѻ  -->  о
        [/\u047d/g,         '\u043e'],          // ѽ  -->  о
        [/\u047f/g,         '\u043e\u0442'],    // ѿ  -->  от
        [/~/g,              '*'],       // ~  -->  *
        [/\u042a/g,         '\u044a'],  // Ъ  -->  ъ
        [/\u0412/g,         '*'],       // В  -->  *
        [/\u0413/g,         '*'],       // Г  -->  *
        [/\u0414/g,         '*'],       // Д  -->  *
        [/\u0416/g,         '*'],       // Ж  -->  *
        [/\u0417/g,         '*'],       // З  -->  *
        [/\u041d/g,         '*'],       // Н  -->  *
        [/\u041e/g,         '*'],       // О  -->  *
        [/\u0420/g,         '*'],       // Р  -->  *
        [/\u0421/g,         '*'],       // С  -->  *
        [/\u0425/g,         '\u0445'],  // Х  -->  х
        [/\u0427/g,         '*'],       // Ч  -->  *
        [/\u044a$/g,        ''],        // ъ$  -->
        [/\u044a\s/g,       ' '],       // ъ\s -->
        [/\u044a\u0430/g,   '\u0430'],  // ъа  -->  а
        [/\u044a\u043e/g,   '\u043e'],  // ъо  -->  о
        [/\u044a\u0443/g,   '\u0443'],  // ъу  -->  у
        [/\u044a\u044b/g,   '\u044b'],  // ъы  -->  ы
        [/\u044a\u0438/g,   '\u044b'],  // ъи  -->  ы
    ];
  return this.convert(word, conversion);
}
};
