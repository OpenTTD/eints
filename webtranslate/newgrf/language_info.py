# vim: set fileencoding=utf-8
"""
Meta information about languages.

Copied from OpenTTD at 20130203, r24956
"""
class LanguageData:
    """
    @ivar name: Name of the language in English.
    @type name: C{str}

    @ivar ownname: Name of the language in the language itself.
    @type ownname: C{str}

    @ivar isocode: Systematic name of the language.
    @type isocode: C{str}

    @ivar plural: Plural form number.
    @type plural: C{int}

    @ivar textdir: Text direction.
    @ivar digitsep: Digit seperator.
    @type digitsep: C{str}

    @ivar digitsepcur: Digit separator for currency.
    @type digitsepcur: C{str}

    @ivar decimalsep: Separator for decimal numbers.
    @type decimalsep: C{str}

    @ivar winlangid: Language id according to a popular operating system.
    @type winlangid: C{int}

    @ivar grflangid: Language id according to the NewGRF system.
    @type grflangid: C{int}

    @ivar gender: Genders of the language.
    @type gender: C{list} of C{str}

    @ivar case: Cases of the language.
    @type case: C{list} of C{str}
    """
    def __init__(self, name, ownname, isocode, plural, textdir, digitsep,
                 digitsepcur, decimalsep, winlangid, grflangid, gender=None, case=None):
        if gender is None: gender = []
        if case is None: case = []
        if '' not in case: case.append('')
        self.name = name
        self.ownname = ownname
        self.isocode = isocode
        self.plural = plural
        self.textdir = textdir
        self.digitsep = digitsep
        self.digitsepcur = digitsepcur
        self.decimalsep = decimalsep
        self.winlangid = winlangid
        self.grflangid = grflangid
        self.gender = gender
        self.case = case

afrikaans = LanguageData(name = "Afrikaans", ownname = "Afrikaans", isocode = "af_ZA",
                         plural = 0, textdir = "ltr",
                         digitsep = ".", digitsepcur = ".", decimalsep = ",",
                         winlangid = 0x0436, grflangid = 0x1b,
                         gender = ["male"])

arabic_egypt = LanguageData(name="Arabic (Egypt)", ownname="Arabic (Egypt)", isocode="ar_EG",
                            plural=1, textdir="rtl",
                            digitsep="٬", digitsepcur="٬", decimalsep="٫",
                            winlangid=0x0c01, grflangid=0x14)

basque = LanguageData(name="Basque", ownname="Euskara", isocode="eu_ES",
                      plural=0, textdir="ltr",
                      digitsep=".", digitsepcur=".", decimalsep=",",
                      winlangid=0x042d, grflangid=0x21)

belarusian = LanguageData(name="Belarusian", ownname="Беларуская", isocode="be_BY",
                          plural=6, textdir="ltr",
                          digitsep="{NBSP}", digitsepcur="{NBSP}", decimalsep=",",
                          winlangid=0x0423, grflangid=0x10,
                          gender=['m','f','n','p'],
                          case=['m','f','n','p','nom','gen','dat','acc','abl','pre'])

brazilian_portuguese = LanguageData(name="Portuguese (Brazilian)", ownname="Português (BR)",
                                    isocode="pt_BR",
                                    plural=2, textdir="ltr",
                                    digitsep=".", digitsepcur=".", decimalsep=",",
                                    winlangid=0x0416, grflangid=0x37,
                                    gender=['m','f'])

bulgarian = LanguageData(name="Bulgarian", ownname="Български", isocode="bg_BG",
                         plural=0, textdir="ltr",
                         digitsep=".", digitsepcur=".", decimalsep=",",
                         winlangid=0x0402, grflangid=0x18,
                         gender=['m','f','n','p'], case=['m','f','n','p'])

catalan = LanguageData(name="Catalan", ownname="Català", isocode="ca_ES",
                       plural=0, textdir="ltr",
                       digitsep=".", digitsepcur=".", decimalsep=",",
                       winlangid=0x0403, grflangid=0x22,
                       gender=['Masculin','Femenin'])

chuvash = LanguageData(name="Chuvash", ownname="Чӑвашла", isocode="cv_RU",
                       plural=0, textdir="ltr",
                       digitsep="{NBSP}", digitsepcur="{NBSP}", decimalsep=",",
                       winlangid=0x0419, grflangid=0x0B)

croatian = LanguageData(name="Croatian", ownname="Hrvatski", isocode="hr_HR",
                        plural=6, textdir="ltr",
                        digitsep=".", digitsepcur=".", decimalsep=",",
                        winlangid=0x041a, grflangid=0x38,
                        gender=['male','female','middle'],
                        case=['nom','gen','dat','aku','vok','lok','ins'])

czech = LanguageData(name="Czech", ownname="Čeština", isocode="cs_CZ",
                     plural=10, textdir="ltr",
                     digitsep="{NBSP}", digitsepcur="{NBSP}", decimalsep=",",
                     winlangid=0x0405, grflangid=0x15,
                     gender=['m','f','n','map','mnp','fp','np'],
                     case=['nom','gen','dat','acc','voc','loc','ins','big','small'])

danish = LanguageData(name="Danish", ownname="Dansk", isocode="da_DK",
                      plural=0, textdir="ltr",
                      digitsep=".", digitsepcur=".", decimalsep=",",
                      winlangid=0x0406, grflangid=0x2d)

dutch = LanguageData(name="Dutch", ownname="Nederlands", isocode="nl_NL",
                     plural=0, textdir="ltr",
                     digitsep=".", digitsepcur=".", decimalsep=",",
                     winlangid=0x0413, grflangid=0x1f)

english_AU = LanguageData(name="English (AU)", ownname="English (AU)", isocode="en_AU",
                          plural=0, textdir="ltr",
                          digitsep=",", digitsepcur=",", decimalsep=".",
                          winlangid=0x0c09, grflangid=0x3D)

english = LanguageData(name="English (UK)", ownname="English (UK)", isocode="en_GB",
                       plural=0, textdir="ltr",
                       digitsep=",", digitsepcur=",", decimalsep=".",
                       winlangid=0x0809, grflangid=0x01)

english_US = LanguageData(name="English (US)", ownname="English (US)", isocode="en_US",
                          plural=0, textdir="ltr",
                          digitsep=",", digitsepcur=",", decimalsep=".",
                          winlangid=0x0409, grflangid=0x00,)

esperanto = LanguageData(name="Esperanto", ownname="Esperanto", isocode="eo_EO",
                         plural=0, textdir="ltr",
                         digitsep=".", digitsepcur=".", decimalsep=",",
                         winlangid=0x0000, grflangid=0x05,
                         case=['n'])

estonian = LanguageData(name="Estonian", ownname="Eesti keel", isocode="et_EE",
                        plural=0, textdir="ltr",
                        digitsep=".", digitsepcur=".", decimalsep=",",
                        winlangid=0x0425, grflangid=0x34,
                        case=['g','in','sü'])

faroese = LanguageData(name="Faroese", ownname="Føroyskt", isocode="fo_FO",
                       plural=0, textdir="ltr",
                       digitsep=".", digitsepcur=".", decimalsep=",",
                       winlangid=0x0438, grflangid=0x12,
                       gender=['m','f','n'])

finnish = LanguageData(name="Finnish", ownname="Suomi", isocode="fi_FI",
                       plural=0, textdir="ltr",
                       digitsep=".", digitsepcur=".", decimalsep=",",
                       winlangid=0x040b, grflangid=0x35)

french = LanguageData(name="French", ownname="Français", isocode="fr_FR",
                      plural=2, textdir="ltr",
                      digitsep="{NBSP}", digitsepcur="{NBSP}", decimalsep=",",
                      winlangid=0x040c, grflangid=0x03,
                      gender=['m','m2','f'])

frisian = LanguageData(name="Frisian", ownname="Frysk", isocode="fy_NL",
                       plural=0, textdir="ltr",
                       digitsep=".", digitsepcur=".", decimalsep=",",
                       winlangid=0x0462, grflangid=0x32)

galician = LanguageData(name="Galician", ownname="Galego", isocode="gl_ES",
                        plural=0, textdir="ltr",
                        digitsep=".", digitsepcur=".", decimalsep=",",
                        winlangid=0x0456, grflangid=0x31,
                        gender=['m','f','n'])

german = LanguageData(name="German", ownname="Deutsch", isocode="de_DE",
                      plural=0, textdir="ltr",
                      digitsep=".", digitsepcur=".", decimalsep=",",
                      winlangid=0x0407, grflangid=0x02,
                      gender=['m','w','n','p'])

greek = LanguageData(name="Greek", ownname="Ελληνικά", isocode="el_GR",
                     plural=2, textdir="ltr",
                     digitsep=".", digitsepcur=".", decimalsep=",",
                     winlangid=0x0408, grflangid=0x1e,
                     gender=['m','f','n'], case=['subs','date','geniki'])

hebrew = LanguageData(name="Hebrew", ownname="עברית", isocode="he_IL",
                      plural=0, textdir="rtl",
                      digitsep=",", digitsepcur=",", decimalsep=".",
                      winlangid=0x040d, grflangid=0x61,
                      gender=['m','f'], case=['singular','plural','gen'])

hungarian = LanguageData(name="Hungarian", ownname="Magyar", isocode="hu_HU",
                         plural=2, textdir="ltr",
                         digitsep=".", digitsepcur=".", decimalsep=",",
                         winlangid=0x040e, grflangid=0x24,
                         case=['t','ba'])

icelandic = LanguageData(name="Icelandic", ownname="Íslenska", isocode="is_IS",
                         plural=0, textdir="ltr",
                         digitsep=".", digitsepcur=".", decimalsep=",",
                         winlangid=0x040f, grflangid=0x29,
                         gender=['karlkyn','kvenkyn','hvorugkyn'])

ido = LanguageData(name="Ido", ownname="Ido", isocode="io_IO",
                   plural=0, textdir="ltr",
                   digitsep=".", digitsepcur=".", decimalsep=",",
                   winlangid=0x0000, grflangid=0x06)


indonesian = LanguageData(name="Indonesian", ownname="Bahasa Indonesia", isocode="id_ID",
                          plural=1, textdir="ltr",
                          digitsep=".", digitsepcur=".", decimalsep=",",
                          winlangid=0x0421, grflangid=0x5a)

irish = LanguageData(name="Irish", ownname="Gaeilge", isocode="ga_IE",
                     plural=4, textdir="ltr",
                     digitsep=",", digitsepcur=",", decimalsep=".",
                     winlangid=0x083c, grflangid=0x08)

italian = LanguageData(name="Italian", ownname="Italiano", isocode="it_IT",
                       plural=0, textdir="ltr",
                       digitsep=".", digitsepcur=".", decimalsep=",",
                       winlangid=0x0410, grflangid=0x27,
                       gender=['m','ma','f'], case=['ms','mp','fs','fp'])

japanese = LanguageData(name="Japanese", ownname="日本語", isocode="ja_JP",
                        plural=1, textdir="ltr",
                        digitsep=",", digitsepcur=",", decimalsep=".",
                        winlangid=0x0411, grflangid=0x39)

korean = LanguageData(name="Korean", ownname="한국어", isocode="ko_KR",
                      plural=11, textdir="ltr",
                      digitsep=".", digitsepcur=".", decimalsep=",",
                      winlangid=0x0412, grflangid=0x3a,
                      gender=['m','f'])

latvian = LanguageData(name="Latvian", ownname="Latviešu", isocode="lv_LV",
                       plural=3, textdir="ltr",
                       digitsep=".", digitsepcur=".", decimalsep=",",
                       winlangid=0x0426, grflangid=0x2a,
                       gender=['m','f'], case=['kas'])

lithuanian = LanguageData(name="Lithuanian", ownname="Lietuvių", isocode="lt_LT",
                          plural=5, textdir="ltr",
                          digitsep=".", digitsepcur=".", decimalsep=",",
                          winlangid=0x0427, grflangid=0x2b,
                          gender=['vyr','mot'],
                          case=['kas','ko','kam','ka','kuo','kur','kreip'])

luxembourgish = LanguageData(name="Luxembourgish", ownname="Lëtzebuergesch", isocode="lb_LU",
                             plural=0, textdir="ltr",
                             digitsep=".", digitsepcur=".", decimalsep=",",
                             winlangid=0x046e, grflangid=0x23)

macedonian = LanguageData(name="Macedonian", ownname="Македонски", isocode="mk_MK",
                          plural=0, textdir="ltr",
                          digitsep=".", digitsepcur=".", decimalsep=",",
                          winlangid=0x042f, grflangid=0x26)

malay = LanguageData(name="Malay", ownname="Melayu", isocode="ms_MY",
                     plural=0, textdir="ltr",
                     digitsep=",", digitsepcur=",", decimalsep=".",
                     winlangid=0x043a, grflangid=0x3c)

maltese = LanguageData(name="Maltese", ownname="Malti", isocode="mt_MT",
                       plural=12, textdir="ltr",
                       digitsep=",", digitsepcur=",", decimalsep=".",
                       winlangid=0x043a, grflangid=0x09)

marathi = LanguageData(name="Marathi", ownname="मराठी", isocode="mr_IN",
                       plural=0, textdir="ltr",
                       digitsep=",", digitsepcur=",", decimalsep=".",
                       winlangid=0x044e, grflangid=0x11)

norwegian_bokmal = LanguageData(name="Norwegian (Bokmal)", ownname="Norsk (bokmål)",
                                isocode="nb_NO",
                                plural=0, textdir="ltr",
                                digitsep="{NBSP}", digitsepcur="{NBSP}", decimalsep=",",
                                winlangid=0x0414, grflangid=0x2f,
                                gender=['masculine','feminine','neuter'], case=['small'])

norwegian_nynorsk = LanguageData(name="Norwegian (Nynorsk)", ownname="Norsk (nynorsk)",
                                 isocode="nn_NO",
                                 plural=0, textdir="ltr",
                                 digitsep="{NBSP}", digitsepcur="{NBSP}", decimalsep=",",
                                 winlangid=0x0814, grflangid=0x0e,
                                 gender=['masculine','feminine','neuter'],
                                 case=['small'])

persian = LanguageData(name="Persian", ownname="فارسی", isocode="fa_IR",
                       plural=0, textdir="rtl",
                       digitsep="٬", digitsepcur="٬", decimalsep="٫",
                       winlangid=0x0429, grflangid=0x62)

polish = LanguageData(name="Polish", ownname="Polski", isocode="pl_PL",
                      plural=7, textdir="ltr",
                      digitsep=".", digitsepcur=".", decimalsep=",",
                      winlangid=0x0415, grflangid=0x30,
                      gender=['m','f','n'], case=['d c','b','n','m','w'])

portuguese = LanguageData(name="Portuguese", ownname="Português", isocode="pt_PT",
                          plural=0, textdir="ltr",
                          digitsep=".", digitsepcur=".", decimalsep=",",
                          winlangid=0x0816, grflangid=0x36,
                          gender=['n','m','f','mp','fp'])

romanian = LanguageData(name="Romanian", ownname="Românӑ", isocode="ro_RO",
                        plural=0, textdir="ltr",
                        digitsep=".", digitsepcur=".", decimalsep=",",
                        winlangid=0x0418, grflangid=0x28)

russian = LanguageData(name="Russian", ownname="Русский", isocode="ru_RU",
                       plural=6, textdir="ltr",
                       digitsep="{NBSP}", digitsepcur="{NBSP}", decimalsep=",",
                       winlangid=0x0419, grflangid=0x07,
                       gender=['m','f','n','p'],
                       case=['m','f','n','p','nom','gen','dat','acc','abl','pre'])

serbian = LanguageData(name="Serbian", ownname="Srpski", isocode="sr_RS",
                       plural=6, textdir="ltr",
                       digitsep=".", digitsepcur=".", decimalsep=",",
                       winlangid=0x7c1a, grflangid=0x0d,
                       gender=['muški','ženski','srednji'],
                       case=['nom','big','gen','dat','aku','vok','lok','ins'])

simplified_chinese = LanguageData(name="Chinese (Simplified)", ownname="简体中文",
                                  isocode="zh_CN",
                                  plural=1, textdir="ltr",
                                  digitsep=",", digitsepcur=",", decimalsep=".",
                                  winlangid=0x0804, grflangid=0x56)

slovak = LanguageData(name="Slovak", ownname="Slovensky", isocode="sk_SK",
                      plural=10, textdir="ltr",
                      digitsep=".", digitsepcur=".", decimalsep=",",
                      winlangid=0x041b, grflangid=0x16,
                      gender=['m','z','s'], case=['g'])

slovenian = LanguageData(name="Slovenian", ownname="Slovenščina", isocode="sl_SI",
                         plural=8, textdir="ltr",
                         digitsep=".", digitsepcur=".", decimalsep=",",
                         winlangid=0x0424, grflangid=0x2c,
                         case=['r','d','t'])

spanish = LanguageData(name="Spanish", ownname="Español (ES)", isocode="es_ES",
                       plural=0, textdir="ltr",
                       digitsep=".", digitsepcur=".", decimalsep=",",
                       winlangid=0x0c0a, grflangid=0x04,
                       gender=['m','f'])

swedish = LanguageData(name="Swedish", ownname="Svenska", isocode="sv_SE",
                       plural=0, textdir="ltr",
                       digitsep=".", digitsepcur=".", decimalsep=",",
                       winlangid=0x081d, grflangid=0x2e)

tamil = LanguageData(name="Tamil", ownname="தமிழ்", isocode="ta_IN",
                     plural=0, textdir="ltr",
                     digitsep=",", digitsepcur=",", decimalsep=".",
                     winlangid=0x0449, grflangid=0x0A)

thai = LanguageData(name="Thai", ownname="Thai", isocode="th_TH",
                    plural=1, textdir="ltr",
                    digitsep=",", digitsepcur=",", decimalsep=".",
                    winlangid=0x041e, grflangid=0x42)

traditional_chinese = LanguageData(name="Chinese (Traditional)", ownname="繁體中文",
                                   isocode="zh_TW",
                                   plural=1, textdir="ltr",
                                   digitsep=",", digitsepcur=",", decimalsep=".",
                                   winlangid=0x0404, grflangid=0x0c)

turkish = LanguageData(name="Turkish", ownname="Türkçe", isocode="tr_TR",
                       plural=1, textdir="ltr",
                       digitsep=".", digitsepcur=".", decimalsep=",",
                       winlangid=0x041f, grflangid=0x3e,
                       case=['tamlanan'])

ukrainian = LanguageData(name="Ukrainian", ownname="Українська", isocode="uk_UA",
                         plural=6, textdir="ltr",
                         digitsep=".", digitsepcur=".", decimalsep=",",
                         winlangid=0x0422, grflangid=0x33,
                         gender=['m','f','s','mn'], case=['r','d','z'])

vietnamese = LanguageData(name="Vietnamese", ownname="Tiếng Việt", isocode="vi_VN",
                          plural=1, textdir="ltr",
                          digitsep=".", digitsepcur=".", decimalsep=",",
                          winlangid=0x042a, grflangid=0x54)

welsh = LanguageData(name="Welsh", ownname="Cymraeg", isocode="cy_GB",
                     plural=0, textdir="ltr",
                     digitsep=",", digitsepcur=",", decimalsep=".",
                     winlangid=0x0452, grflangid=0x0f)

urdu = LanguageData(name="Urdu", ownname="Urdu", isocode="ur_PK",
                    plural=0, textdir="rtl",
                    digitsep="٬", digitsepcur="٬", decimalsep="٫",
                    winlangid=0x0420, grflangid=0x5c,
                    gender=['m','f'])

all_languages = [afrikaans, arabic_egypt, basque, belarusian,
                 brazilian_portuguese, bulgarian, catalan, chuvash, croatian,
                 czech, danish, dutch, english_AU, english, english_US,
                 esperanto, estonian, faroese, finnish, french, frisian,
                 galician, german, greek, hebrew, hungarian, icelandic, ido,
                 indonesian, irish, italian, japanese, korean, latvian,
                 lithuanian, luxembourgish, macedonian, malay, maltese,
                 marathi, norwegian_bokmal, norwegian_nynorsk, persian,
                 polish, portuguese, romanian, russian, serbian,
                 simplified_chinese, slovak, slovenian, spanish, swedish,
                 tamil, thai, traditional_chinese, turkish, ukrainian,
                 vietnamese, welsh, urdu]

grflangid = dict((x.grflangid, x) for x in all_languages)
assert len(all_languages) == len(grflangid)
