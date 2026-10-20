import html
import json
import urllib.request
import urllib.error
import re
import streamlit as st
import pandas as pd
TRANSLATIONS = {'🏠 Overview': ('🏠 Главная', '🏠 Басты бет'), '🔎 Analyzer': ('🔎 Анализатор', '🔎 Талдағыш'), '📚 Safety Academy': ('📚 Академия безопасности', '📚 Қауіпсіздік академиясы'), '🧪 Test Lab': ('🧪 Тестирование', '🧪 Сынақтар'), '💡 About QALQAN': ('💡 О проекте', '💡 Жоба туралы'), 'Your digital safety companion': ('Твой помощник по цифровой безопасности', 'Цифрлық қауіпсіздік көмекшісі'), 'Think twice.': ('Думай дважды.', 'Екі рет ойлан.'), 'Click wisely.': ('Нажимай осознанно.', 'Саналы түрде бас.'), 'QALQAN checks messages for common warning signs,': ('QALQAN проверяет сообщения на признаки угроз,', 'QALQAN хабарламалардағы қауіп белгілерін тексереді,'), 'explains what looks suspicious, and helps you decide': ('объясняет подозрительные моменты и помогает понять,', 'күдікті белгілерді түсіндіреді және'), 'what to verify before taking action.': ('что проверить перед действием.', 'әрекет алдында нені тексеру керегін көрсетеді.'), 'Check a message': ('Проверить сообщение', 'Хабарламаны тексеру'), 'Open analyzer': ('Открыть анализатор', 'Талдағышты ашу'), 'Learn the patterns': ('Изучи схемы обмана', 'Алаяқтық тәсілдерін үйрен'), 'Open Safety Academy': ('Открыть Академию безопасности', 'Қауіпсіздік академиясын ашу'), 'Your workspace': ('Твоя статистика', 'Сенің статистикаң'), 'Messages analyzed': ('Проверено сообщений', 'Тексерілген хабарламалар'), 'Flagged messages': ('Подозрительных сообщений', 'Күдікті хабарламалар'), 'Built-in test examples': ('Тестовых примеров', 'Сынақ мысалдары'), 'Recent analyses': ('Последние проверки', 'Соңғы тексерулер'), 'Message scanner': ('Сканер сообщений', 'Хабарлама сканері'), "Let's inspect that message.": ('Проверим сообщение.', 'Хабарламаны тексерейік.'), 'Try an example': ('Выбрать пример', 'Мысалды таңдау'), 'Choose an example...': ('Выберите пример...', 'Мысалды таңдаңыз...'), 'Message to analyze': ('Текст сообщения', 'Хабарлама мәтіні'), 'Paste the message here...': ('Вставь сообщение сюда...', 'Хабарламаны осында енгіз...'), '🔍 Analyze message': ('🔍 Проверить сообщение', '🔍 Хабарламаны тексеру'), 'Analysis results': ('Результаты анализа', 'Талдау нәтижелері'), 'Suspicion score': ('Оценка риска', 'Қауіп деңгейі'), 'What did QALQAN notice?': ('Что заметил QALQAN?', 'QALQAN нені байқады?'), 'Message with detected phrases': ('Сообщение с выделенными признаками', 'Белгіленген белгілері бар хабарлама'), 'What should you do?': ('Что делать?', 'Не істеу керек?'), 'Suspicious': ('Подозрительно', 'Күдікті'), 'Needs attention': ('Требует внимания', 'Назар аудару керек'), 'Low detected risk': ('Низкий риск', 'Төмен қауіп'), 'Matched:': ('Найдено:', 'Табылды:'), 'points': ('баллов', 'ұпай'), 'Spot the red flags.': ('Замечай признаки опасности.', 'Қауіп белгілерін байқа.'), 'Urgency and pressure': ('Срочность и давление', 'Асықтыру және қысым'), 'Unexpected prizes': ('Неожиданные призы', 'Күтпеген сыйлықтар'), 'Private information': ('Личные данные', 'Жеке деректер'), 'Suspicious payments': ('Подозрительные платежи', 'Күдікті төлемдер'), 'Unexpected links': ('Неожиданные ссылки', 'Күтпеген сілтемелер'), 'Impersonation and threats': ('Подмена личности и угрозы', 'Жалған тұлға және қорқыту'), 'Example:': ('Пример:', 'Мысал:'), 'Evaluation workspace': ('Лаборатория тестирования', 'Сынақ зертханасы'), 'Test the detector.': ('Проверь детектор.', 'Детекторды тексер.'), 'How the evaluation works': ('Как проходит тестирование', 'Сынақ қалай өтеді'), '🧪 Run all 12 tests': ('🧪 Запустить 12 тестов', '🧪 12 сынақты іске қосу'), 'Performance overview': ('Результаты тестов', 'Сынақ нәтижелері'), 'Accuracy': ('Точность', 'Дәлдік'), 'Precision': ('Точность обнаружения', 'Анықтау дәлдігі'), 'Recall': ('Полнота', 'Толықтық'), 'Specificity': ('Специфичность', 'Ерекшелік'), 'Confusion matrix': ('Матрица ошибок', 'Қателер матрицасы'), 'Individual test results': ('Результаты каждого теста', 'Әр сынақтың нәтижелері'), 'View the full test messages': ('Посмотреть тексты тестов', 'Сынақ мәтіндерін көру'), 'What to improve next': ('Что улучшить дальше', 'Әрі қарай нені жақсарту керек'), 'About the project': ('О проекте', 'Жоба туралы'), 'QALQAN protects through awareness.': ('QALQAN защищает знаниями.', 'QALQAN білім арқылы қорғайды.'), 'The idea': ('Идея', 'Идея'), 'What the prototype can do': ('Возможности проекта', 'Жоба мүмкіндіктері'), 'Current limitations': ('Ограничения', 'Шектеулер'), 'Message safety, made understandable.': ('Понятная безопасность сообщений.', 'Хабарлама қауіпсіздігі түсінікті тілде.'), 'NAVIGATION': ('НАВИГАЦИЯ', 'НАВИГАЦИЯ'), 'Sections': ('Разделы', 'Бөлімдер'), 'Navigate between sections': ('Переключение разделов', 'Бөлімдер арасында ауысу')}

TRANSLATIONS.update({'Paste a message and inspect the warning signs. QALQAN explains the reasons behind its score.': ('Вставь сообщение и проверь признаки угроз. QALQAN объяснит, почему выставлена такая оценка.', 'Хабарламаны енгізіп, қауіп белгілерін тексер. QALQAN бағасының себебін түсіндіреді.'), 'Explore common scam techniques and simple ways to protect your accounts and personal information.': ('Узнай о схемах мошенников и способах защиты аккаунтов и личных данных.', 'Алаяқтық әдістері мен аккаунтты және жеке деректерді қорғау жолдарын үйрен.'), 'Paste a message and inspect the warning signs.': ('Вставь сообщение и проверь признаки угроз.', 'Хабарламаны енгізіп, қауіп белгілерін тексер.'), 'QALQAN explains the reasons behind its score.': ('QALQAN объяснит причину оценки.', 'QALQAN бағасының себебін түсіндіреді.'), 'Explore common scam techniques and simple ways': ('Изучи схемы мошенничества и способы', 'Алаяқтық тәсілдері мен'), 'to protect your accounts and personal information.': ('защиты аккаунтов и личных данных.', 'аккаунт пен жеке деректерді қорғау жолдарын үйрен.'), 'Creative Lab edition': ('Версия Creative Lab', 'Creative Lab нұсқасы'), 'A student prototype for safer digital communication.': ('Учебный проект по цифровой безопасности.', 'Цифрлық қауіпсіздікке арналған оқу жобасы.'), 'Your recent analyses will appear here after you check a message.': ('Здесь появятся результаты последних проверок.', 'Соңғы тексеру нәтижелері осында көрсетіледі.'), 'Paste any message to scan. The examples are only for testing.': ('Вставь сообщение для проверки. Примеры только для тестирования.', 'Тексеру үшін хабарламаны енгіз. Мысалдар тек сынақ үшін.'), 'Paste a message first, then run the analysis.': ('Сначала вставь сообщение.', 'Алдымен хабарламаны енгіз.'), 'Analyzing with QALQAN rules...': ('Проверяем сообщение...', 'Хабарлама тексерілуде...'), 'Offline risk assessment (no AI or API key needed)': ('Проверка по правилам без ИИ и API-ключа', 'ЖИ мен API кілтінсіз ережелер бойынша тексеру'), 'Rule-based analysis': ('Анализ по правилам', 'Ережелер бойынша талдау'), 'No known warning phrases were detected.': ('Известные тревожные признаки не найдены.', 'Белгілі қауіп белгілері табылмады.'), 'Scams often rely on pressure, curiosity, fear, or tempting rewards.': ('Мошенники используют давление, страх и обещания наград.', 'Алаяқтар қысым, қорқыныш және сыйлық уәдесін қолданады.'), 'Knowing the patterns helps you pause and verify.': ('Знание схем помогает остановиться и проверить информацию.', 'Бұл тәсілдерді білу ақпаратты тексеруге көмектеседі.'), 'Run the test set to calculate the evaluation metrics.': ('Запусти тесты для расчёта показателей.', 'Көрсеткіштерді есептеу үшін сынақтарды іске қос.'), 'Correct predictions overall': ('Доля правильных ответов', 'Дұрыс жауаптар үлесі'), 'Flagged messages that are truly suspicious': ('Доля настоящих угроз среди найденных', 'Белгіленгендердің ішіндегі шынайы қауіп үлесі'), 'Suspicious examples detected': ('Найденные опасные примеры', 'Анықталған қауіпті мысалдар'), 'Ordinary examples correctly cleared': ('Правильно распознанные обычные сообщения', 'Дұрыс танылған қалыпты хабарламалар'), 'Actually suspicious': ('Действительно опасно', 'Шын мәнінде қауіпті'), 'Actually ordinary': ('Действительно безопасно', 'Шын мәнінде қауіпсіз'), 'Predicted suspicious': ('Прогноз: опасно', 'Болжам: қауіпті'), 'Predicted ordinary': ('Прогноз: безопасно', 'Болжам: қауіпсіз'), 'True positives': ('Верно обнаруженные угрозы', 'Дұрыс анықталған қауіптер'), 'True negatives': ('Верно распознанные обычные', 'Дұрыс танылған қалыпты'), 'False positives': ('Ложные тревоги', 'Жалған дабылдар'), 'False negatives': ('Пропущенные угрозы', 'Өткізіп алған қауіптер'), 'What do these results mean?': ('Что означают результаты?', 'Нәтижелер нені білдіреді?')})

def tr(value):
    if not isinstance(value, str):
        return value
    lang = st.session_state.get('lang', 'EN')
    if lang == 'EN':
        return value
    for en, options in sorted(TRANSLATIONS.items(), key=lambda kv: -len(kv[0])):
        value = value.replace(en, options[0 if lang == 'RU' else 1])
    return value
st.set_page_config(page_title='QALQAN | Message Safety', page_icon='🛡️', layout='wide', initial_sidebar_state='expanded')
st.set_option('client.toolbarMode', 'minimal')
BLUE = '#79C9B0'
PEACH = '#D9A36E'
LAVENDER = '#9BBBD0'
MINT = '#79C9B0'
DARK = '#E6EDF4'
MUTED = '#9BAFC0'
RULES = [{'name': 'Urgency and pressure', 'weight': 2, 'terms': ['act now', 'immediately', 'urgent', 'urgently', 'within 24 hours', 'right now', 'limited time', 'last chance', 'срочно', 'немедленно', 'прямо сейчас', 'в течение 24 часов', 'последний шанс', 'в течение 15 минут', 'в течение 30 минут', 'тез арада', 'шұғыл', 'дереу'], 'explanation': 'The message pressures you to act quickly.'}, {'name': 'Prize or unexpected reward', 'weight': 2, 'terms': ['you won', 'you have won', 'winner', 'congratulations', 'claim your prize', 'free iphone', 'cash prize', 'free money', 'you are selected', 'won a prize', 'вы выиграли', 'ты выиграл', 'ваш приз', 'получите подарок', 'бесплатные деньги', 'ұтып алдыңыз', 'сіз жеңдіңіз'], 'explanation': 'Unexpected prizes and rewards can be used as bait.'}, {'name': 'Sensitive information request', 'weight': 3, 'terms': ['send your password', 'enter your password', 'share your password', 'your verification code', 'send the code', 'enter the code', 'bank card details', 'card number', 'cvv', 'pin code', 'social security number', 'введите пароль', 'отправьте пароль', 'назовите код', 'код подтверждения', 'данные карты', 'личные данные', 'номер карты', 'пин-код', 'пароль от аккаунта', 'құпиясөз', 'растау кодын', 'карта деректері'], 'explanation': 'The message asks for private account or payment information.'}, {'name': 'Suspicious payment or transfer', 'weight': 3, 'terms': ['pay a fee', 'pay to receive', 'transfer money', 'send money', 'processing fee', 'pay delivery', 'payment required', 'make a deposit', 'gift card payment', 'переведите деньги', 'отправьте деньги', 'оплатите комиссию', 'оплатите доставку', 'требуется оплата', 'сделайте перевод', 'оплатите штраф', 'штраф в размере', 'ақша аударыңыз', 'төлем жасаңыз'], 'explanation': 'A payment or transfer is requested in a potentially suspicious context.'}, {'name': 'Links and destinations', 'weight': 1, 'terms': ['click this link', 'click the link', 'open this link', 'verify your account here', 'follow this link', 'перейдите по ссылке', 'нажмите на ссылку', 'откройте ссылку', 'ссылка для входа', 'сілтемеге өтіңіз'], 'explanation': 'The message directs you to a link or online destination.'}, {'name': 'Impersonation or threats', 'weight': 2, 'terms': ['your account is blocked', 'account will be blocked', 'account suspended', 'your account will be deleted', 'lose access', 'legal action', 'police will', 'we will close your account', 'bank security department', 'your bank account', 'final warning', 'ваш аккаунт заблокирован', 'аккаунт будет заблокирован', 'ваш счёт заблокирован', 'потеряете доступ', 'последнее предупреждение', 'служба безопасности банка', 'служба безопасности вашего банка', 'подозрительную активность', 'предотвращения блокировки', 'полиция', 'аккаунт удалят', 'аккаунтыңыз бұғатталды', 'соңғы ескерту'], 'explanation': 'The sender may be impersonating an authority or using threats.'}]
SAMPLES = {'Suspicious prize message': 'Congratulations! You won a free iPhone. Claim your prize immediately. Send your password to receive it.', 'Suspicious parcel message': 'Your parcel is waiting. Pay a delivery fee immediately and click this link to receive your package.', 'Suspicious password request': 'Your account will be blocked. Enter your password and send your verification code immediately.', 'Suspicious bank message': 'Your bank account is blocked. Click this link and enter your password or you will lose access to your money.', 'Ordinary school message': 'Hi everyone, remember to bring your notebooks tomorrow. Our lesson starts at 9.', 'Ordinary friendly message': 'Hey! Do you want to play a game after school? I will be online at six.', 'Kazakh example': 'Сәлем! Ертең сабақ сағат тоғызда басталады. Дәптеріңді алып кел.'}

def normalize(text):
    return re.sub('\\s+', ' ', text.lower().replace('ё', 'е')).strip()

def analyze_message(message):
    """Transparent, offline scam-risk rules. No API, no keys, no network calls."""
    normalized = normalize(message)
    findings = []
    categories = [('Urgency and pressure', 2, 'The sender pressures you to act quickly.', ['\\bсрочн\\w*\\b', '\\bнемедленн\\w*\\b', '\\bнезамедлительн\\w*\\b', '\\bпрямо сейчас\\b', '\\bв течение\\s+\\d+\\s*(?:минут|час\\w*)\\b', '\\b(?:за|через)\\s+\\d+\\s*(?:минут|час\\w*)\\b', '\\b(?:осталось|дается|даётся)\\s+\\d+\\s*(?:минут|час\\w*)\\b', '\\bпоследн\\w+\\s+(?:шанс|предупрежден\\w*)\\b', '\\b(?:urgent|immediately|act now|right now|last chance)\\b', '\\b(?:within|in)\\s+\\d+\\s*(?:minutes?|hours?)\\b', '\\b(?:шұғыл|дереу|тез арада)\\b']), ('Threats and intimidation', 3, 'Threats of punishment, blocking, or prosecution are used to pressure you.', ['\\b(?:заблокир\\w*|блокировк\\w*|замороз\\w*|арест\\w*|отключ\\w*)\\b', '\\b(?:уголовн\\w+\\s+дел\\w*|возбужден\\w+\\s+дел\\w*|судебн\\w+\\s+разбирательств\\w*)\\b', '\\b(?:правоохранительн\\w+\\s+орган\\w*|передан\\w+\\s+в\\s+полици\\w*|передан\\w+\\s+в\\s+суд)\\b', '\\b(?:штраф\\w*|наказан\\w*|ответственност\\w*|задержан\\w*)\\b', '\\b(?:account (?:will be )?(?:blocked|locked|suspended)|legal action|arrest|prosecution)\\b', '\\b(?:бұғаттал\\w*|айыппұл|полицияға)\\b']), ('Money or payment demand', 3, 'The message asks for a transfer, payment, or fee.', ['\\b(?:переведите|перевести|переводите|отправьте|скиньте|внесите|оплатите|заплатите)\\b.{0,50}\\b(?:деньги|сумм\\w*|тенге|тг|₸|рубл\\w*|штраф\\w*|комисси\\w*|сбор\\w*|сч[её]т|реквизит\\w*)\\b', '\\b(?:оплатите|переведите|заплатите|внесите)\\s+\\d[\\d\\s]*(?:₸|тг|тенге|руб|₽|\\$)\\b', '\\b(?:для получения|чтобы получить)\\b.{0,65}\\b(?:оплат\\w*|перевед\\w*|заплат\\w*)\\b', '\\b(?:предоплат\\w*|комисси\\w+\\s+за\\s+(?:вывод|получение)|перевод\\s+на\\s+(?:карту|сч[её]т))\\b', '\\b(?:transfer|send|pay)\\b.{0,40}\\b(?:money|fee|deposit|fine|payment)\\b', '\\b(?:ақша аудар\\w*|төлем жаса\\w*|айыппұл төле\\w*)\\b']), ('Password, code or personal data', 4, 'The message requests sensitive account, identity, or bank information.', ['\\b(?:парол\\w*|пин[- ]?код\\w*|cvv|cvc|код\\s+(?:из\\s+смс|подтверждения|доступа)|одноразов\\w+\\s+код\\w*)\\b', '\\b(?:номер\\s+карт\\w*|данн\\w+\\s+(?:карт\\w*|паспорт\\w*|удостоверени\\w*)|личн\\w+\\s+данн\\w*)\\b', '\\b(?:подтверд\\w*|сообщ\\w*|назов\\w*|введ\\w*|отправ\\w*)\\b.{0,45}\\b(?:личност\\w*|данн\\w*|код\\w*|парол\\w*|карт\\w*)\\b', '\\b(?:password|passcode|verification code|otp|cvv|card details|personal data|pin code)\\b', '\\b(?:құпиясөз|растау кодын|карта деректері)\\b']), ('Impersonation of an organization', 2, 'The sender claims authority from a bank, agency, or support team.', ['\\b(?:служб\\w+\\s+безопасност\\w*|сотрудник\\w+\\s+(?:банк\\w*|полици\\w*|служб\\w*))\\b', '\\b(?:центральн\\w+\\s+банк\\w*|национальн\\w+\\s+банк\\w*|налогов\\w+\\s+(?:служб\\w*|орган\\w*))\\b', '\\b(?:от\\s+имени\\s+(?:банк\\w*|полици\\w*|госорган\\w*)|официальн\\w+\\s+уведомлен\\w*)\\b', '\\b(?:bank security|security department|government agency|official notice)\\b']), ('Links or external actions', 1, 'A link or external destination needs independent verification.', ['https?://[^\\s<>]+', 'www\\.[^\\s<>]+', '\\b(?:перейдите|переходите|нажмите|откройте|кликните)\\b.{0,30}\\b(?:ссылк\\w*|сайт\\w*|адрес\\w*)\\b', '\\b(?:click|follow|open)\\b.{0,20}\\b(?:link|url|website)\\b', '\\bсілтемеге\\s+өтіңіз\\b']), ('Secrecy or isolation', 2, 'The sender discourages you from verifying the message with others.', ['\\b(?:никому\\s+не\\s+(?:говорите|рассказывайте|сообщайте)|не\\s+сообщайте\\s+(?:об\\s+этом|третьим\\s+лицам))\\b', '\\b(?:держите\\s+в\\s+секрете|это\\s+конфиденциально|не\\s+обращайтесь\\s+в\\s+банк)\\b', "\\b(?:do not tell anyone|keep this secret|don't contact the bank)\\b"]), ('Unexpected prize or easy profit', 2, 'Unexpected prizes or easy profits can be used as bait.', ['\\b(?:вы\\s+выиграли|поздравляем.{0,25}выигр\\w*|заберите\\s+(?:приз|подарок)|вам\\s+полагается\\s+(?:приз|выплата))\\b', '\\b(?:гарантированн\\w+\\s+(?:доход|заработок)|быстр\\w+\\s+заработок|легк\\w+\\s+деньги)\\b', '\\b(?:you (?:have )?won|claim your prize|guaranteed profit|free money)\\b', '\\b(?:ұтып алдыңыз|сіз жеңдіңіз)\\b']), ('Suspicious installation or remote access', 4, 'Requests to install software or give remote access can be dangerous.', ['\\b(?:установите|скачайте|загрузите)\\b.{0,45}\\b(?:приложени\\w*|программ\\w*|apk|файл\\w*)\\b', '\\b(?:удаленн\\w+\\s+доступ|доступ\\s+к\\s+экран\\w*|демонстраци\\w+\\s+экран\\w*)\\b', '\\b(?:install this app|download the apk|remote access|share your screen)\\b'])]
    for name, weight, explanation, patterns in categories:
        matches = []
        for pattern in patterns:
            for match in re.finditer(pattern, normalized, flags=re.IGNORECASE):
                fragment = message[match.start():match.end()].strip()
                if fragment and fragment.casefold() not in [m.casefold() for m in matches]:
                    matches.append(fragment)
                if len(matches) >= 5:
                    break
            if len(matches) >= 5:
                break
        if matches:
            findings.append({'name': name, 'weight': weight, 'matches': matches, 'explanation': explanation})
    names = {item['name'] for item in findings}
    educational = bool(re.search('(?:никогда\\s+не\\s+(?:сообщайте|передавайте|вводите|переходите)|не\\s+(?:сообщайте|передавайте)\\s+(?:парол|код)|(?:мошенник|фишинг|скам|осторожно|как распознать|признаки мошенничества)|(?:never share|do not share|beware of scams))', normalized))
    direct_request = bool(re.search('(?:\\b(?:срочно\\s+)?(?:назовите|сообщите|введите|подтвердите|переведите|оплатите|заплатите|скиньте|отправьте|установите|скачайте)\\b|\\b(?:send|enter|verify|transfer|pay|install)\\b)', normalized))
    weights = {'Urgency and pressure': 1, 'Threats and intimidation': 2, 'Money or payment demand': 2, 'Password, code or personal data': 2, 'Impersonation of an organization': 1, 'Links or external actions': 1, 'Secrecy or isolation': 1, 'Unexpected prize or easy profit': 2, 'Suspicious installation or remote access': 3}
    score = sum((weights[name] for name in names))
    if 'Threats and intimidation' in names and 'Money or payment demand' in names:
        score += 2
    if 'Password, code or personal data' in names and direct_request:
        score += 2
    if 'Urgency and pressure' in names and ('Money or payment demand' in names or 'Password, code or personal data' in names):
        score += 1
    if 'Impersonation of an organization' in names and direct_request:
        score += 1
    if 'Secrecy or isolation' in names and 'Money or payment demand' in names:
        score += 1
    serious = {'Threats and intimidation', 'Money or payment demand', 'Password, code or personal data', 'Suspicious installation or remote access'}
    serious_count = len(names & serious)
    if serious_count == 0:
        score = min(score, 4)
    elif serious_count == 1:
        score = min(score, 6)
    elif serious_count == 2:
        score = min(score, 8)
    if educational and (not direct_request):
        score = min(score, 2)
    elif educational and 'никогда не' in normalized:
        score = min(score, 3)
    score = max(0, min(int(score), 10))
    if score >= 7:
        risk = 'Suspicious'
        recommendation = 'High risk: do not pay, open links, share codes, or install files. Contact the organization using its official app or website.'
    elif score >= 3:
        risk = 'Needs attention'
        recommendation = 'Check the sender independently. Avoid unexpected links, payments, passwords and verification codes.'
    else:
        risk = 'Low detected risk'
        recommendation = 'Few warning signs were found. This does not prove the message is safe. Verify unexpected requests independently.'
    return {'score': score, 'risk': risk, 'findings': findings, 'recommendation': recommendation}

def risk_color(score):
    if score >= 4:
        return '#C74454'
    if score > 0:
        return '#B47720'
    return '#27845D'

def render_highlights(message, findings):
    terms = sorted({term for finding in findings for term in finding['matches']}, key=len, reverse=True)
    safe_message = html.escape(message)
    for term in terms:
        escaped_term = html.escape(term)
        pattern = re.compile(re.escape(escaped_term), re.IGNORECASE)
        safe_message = pattern.sub(lambda match: '<mark style="background:#FF8F70;padding:2px 4px;border-radius:4px;">' + match.group(0) + '</mark>', safe_message)
    return safe_message
TEST_MESSAGES = [{'message': 'Your account is blocked. Enter your password immediately.', 'label': True, 'category': 'Account threat'}, {'message': 'Congratulations! You won a prize. Claim your prize now.', 'label': True, 'category': 'Prize bait'}, {'message': 'Pay a fee to receive your parcel. Click this link.', 'label': True, 'category': 'Parcel fee'}, {'message': 'Send your verification code and bank card details.', 'label': True, 'category': 'Private information'}, {'message': 'Your bank account will be blocked. Transfer money now.', 'label': True, 'category': 'Bank impersonation'}, {'message': 'Last chance! Pay a processing fee to claim free money.', 'label': True, 'category': 'Urgency and payment'}, {'message': 'Hi! Do you want to play a game after school?', 'label': False, 'category': 'Friendly message'}, {'message': 'Please bring your notebook to class tomorrow.', 'label': False, 'category': 'School reminder'}, {'message': 'Our lesson starts at nine. See you tomorrow!', 'label': False, 'category': 'School schedule'}, {'message': 'I will send you the drawing when I finish it.', 'label': False, 'category': 'Ordinary conversation'}, {'message': 'Сәлем! Ертең сабақ сағат тоғызда басталады.', 'label': False, 'category': 'Kazakh school message'}, {'message': 'What game are you playing today?', 'label': False, 'category': 'Gaming conversation'}]

def evaluate_test_set():
    rows = []
    for item in TEST_MESSAGES:
        result = analyze_message(item['message'])
        predicted = result['score'] >= 4
        actual = item['label']
        if predicted and actual:
            outcome = 'True positive'
        elif predicted and (not actual):
            outcome = 'False positive'
        elif not predicted and actual:
            outcome = 'False negative'
        else:
            outcome = 'True negative'
        rows.append({'Category': item['category'], 'Message': item['message'], 'Expected': 'Suspicious' if actual else 'Ordinary', 'Predicted': 'Suspicious' if predicted else 'Ordinary', 'Score': result['score'], 'Outcome': outcome, 'Correct': predicted == actual})
    return pd.DataFrame(rows)
if 'page' not in st.session_state:
    st.session_state.page = '🏠 Overview'
if 'history' not in st.session_state:
    st.session_state.history = []
if 'message_input' not in st.session_state:
    st.session_state.message_input = ''
if 'lab_results' not in st.session_state:
    st.session_state.lab_results = None

def go_to(page):
    st.session_state.page = page
    st.session_state.nav_choice = page

def nav_changed():
    st.session_state.page = st.session_state.nav_choice

def load_sample():
    selected = st.session_state.get('sample_choice', '')
    if selected in SAMPLES:
        st.session_state.message_input = SAMPLES[selected]

def save_analysis(message, result):
    st.session_state.history.insert(0, {'message': message, 'score': result['score'], 'risk': result['risk']})
    st.session_state.history = st.session_state.history[:10]
st.markdown(tr('\n    <style>\n    @import url(\'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap\');\n\n    html, body, [class*="css"] {\n        font-family: \'DM Sans\', sans-serif;\n    }\n\n    .stApp {\n        background: #0A111C;\n        color: #E6EDF4;\n    }\n\n    h1, h2, h3 {\n        font-family: \'Manrope\', sans-serif !important;\n        color: #E6EDF4;\n    }\n\n    .block-container {\n        padding-top: 5.5rem;\n        padding-bottom: 3rem;\n        max-width: 1200px;\n    }\n\n    section[data-testid="stSidebar"] {\n        background: #142333 !important;\n        border-right: 1px solid #24364A;\n    }\n\n    /* Force sidebar text to stay dark */\n    section[data-testid="stSidebar"],\n    section[data-testid="stSidebar"] * {\n        color: #E6EDF4;\n    }\n\n    section[data-testid="stSidebar"] h1 {\n        color: #79C9B0 !important;\n    }\n\n    section[data-testid="stSidebar"] [data-testid="stRadio"] label {\n        color: #E6EDF4 !important;\n        background: transparent;\n        border-radius: 10px;\n        padding: 9px 10px;\n        transition: background 0.15s ease;\n    }\n\n    section[data-testid="stSidebar"] [data-testid="stRadio"] label p,\n    section[data-testid="stSidebar"] [data-testid="stRadio"] label span {\n        color: #E6EDF4 !important;\n        font-weight: 600 !important;\n    }\n\n    section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {\n        background: #1A3442 !important;\n    }\n\n    /* Selected navigation item */\n    section[data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {\n        background: #79C9B0 !important;\n        border-radius: 10px;\n    }\n\n    section[data-testid="stSidebar"] [data-testid="stRadio"] input {\n        accent-color: #79C9B0 !important;\n    }\n\n    section[data-testid="stSidebar"] [data-testid="stRadio"] [role="radiogroup"] {\n        gap: 8px;\n    }\n\n    .hero {\n        background: linear-gradient(125deg, #101D2C 0%, #142538 55%, #18343B 100%);\n        padding: 32px;\n        border-radius: 24px;\n        border: 1px solid #26394A;\n        margin-bottom: 22px;\n    }\n\n    .eyebrow {\n        text-transform: uppercase;\n        letter-spacing: 2px;\n        font-size: 12px;\n        font-weight: 800;\n        color: #79C9B0;\n    }\n\n    .hero-title {\n        font-family: \'Manrope\', sans-serif;\n        font-size: 38px;\n        line-height: 1.15;\n        font-weight: 800;\n        margin: 10px 0;\n        color: #E6EDF4;\n    }\n\n    .hero-copy {\n        color: #B2C7BA;\n        font-size: 16px;\n        max-width: 720px;\n    }\n\n    .soft-card {\n        background: white;\n        border: 1px solid #26394A;\n        border-radius: 18px;\n        padding: 20px;\n        margin-bottom: 12px;\n    }\n\n    .soft-card h3 {\n        margin-top: 0;\n    }\n\n    .metric-card {\n        background: white;\n        border: 1px solid #26394A;\n        border-radius: 18px;\n        padding: 20px;\n        min-height: 115px;\n    }\n\n    .metric-label {\n        color: #9BAFC0;\n        font-size: 13px;\n        font-weight: 600;\n    }\n\n    .metric-value {\n        color: #E6EDF4;\n        font-family: \'Manrope\', sans-serif;\n        font-size: 29px;\n        font-weight: 800;\n        margin-top: 5px;\n    }\n\n    .tag {\n        display: inline-block;\n        background: #142333;\n        color: #B0DED0;\n        border-radius: 20px;\n        padding: 5px 10px;\n        font-size: 12px;\n        font-weight: 700;\n    }\n\n    .stButton > button {\n        background: #79C9B0;\n        color: white !important;\n        border: none;\n        border-radius: 12px;\n        padding: 0.65rem 1rem;\n        font-weight: 700;\n        min-height: 42px;\n    }\n\n    .stButton > button:hover {\n        background: #67BBA0;\n        color: white !important;\n        border: none;\n    }\n\n    .stTextArea textarea {\n        border-radius: 14px;\n        border-color: #30495A;\n        background: #101D2A;\n    }\n\n    div[data-baseweb="select"] > div {\n        border-radius: 12px;\n    }\n\n    hr {\n        border-color: #26394A;\n    }\n\n    /* Hide Streamlit\'s built-in menu, toolbar, footer, and GitHub links. */\n    #MainMenu,\n    footer,\n    [data-testid="stToolbar"],\n    [data-testid="stStatusWidget"],\n    .viewerBadge_container__1QSob,\n    a[href*="github.com"],\n    a[aria-label*="GitHub"],\n    a[title*="GitHub"] {\n        display: none !important;\n        visibility: hidden !important;\n    }\n\n    /* QALQAN entrance: staggered drop, white first, then the real theme colors. */\n    @keyframes qalqan-drop-color {\n        0% { opacity: 0; transform: translateY(-14px); }\n        100% { opacity: 1; transform: translateY(0); }\n    }\n\n    @keyframes qalqan-sidebar-in {\n        0% { opacity: 0; transform: translateY(-28px); }\n        100% { opacity: 1; transform: translateY(0); }\n    }\n\n    /* Force the new midnight theme across Streamlit\'s main canvas and sidebar. */\n    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {\n        background: #0A111C !important;\n        color: #E6EDF4 !important;\n    }\n    [data-testid="stSidebar"] {\n        background: #0D1723 !important;\n        border-right: 1px solid #26394A !important;\n        animation: qalqan-sidebar-in 650ms cubic-bezier(.2,.8,.2,1) both;\n    }\n    [data-testid="stSidebar"] * { color: #D8E3ED; }\n    .block-container { color: #E6EDF4; }\n    .block-container [data-testid="stElementContainer"] {\n        animation: qalqan-drop-color 650ms cubic-bezier(.2,.8,.2,1) both;\n    }\n    .block-container [data-testid="stElementContainer"]:nth-of-type(2) { animation-delay: 100ms; }\n    .block-container [data-testid="stElementContainer"]:nth-of-type(3) { animation-delay: 200ms; }\n    .block-container [data-testid="stElementContainer"]:nth-of-type(4) { animation-delay: 300ms; }\n    .block-container [data-testid="stElementContainer"]:nth-of-type(5) { animation-delay: 400ms; }\n    .block-container [data-testid="stElementContainer"]:nth-of-type(6) { animation-delay: 500ms; }\n    .block-container [data-testid="stElementContainer"]:nth-of-type(7) { animation-delay: 600ms; }\n    .block-container [data-testid="stElementContainer"]:nth-of-type(8) { animation-delay: 700ms; }\n    .hero { animation: qalqan-drop-color 750ms cubic-bezier(.2,.8,.2,1) both; }\n    .soft-card, .metric-card {\n        background: #101D2A !important;\n        border: 1px solid #26394A !important;\n        color: #E6EDF4 !important;\n        transition: transform 220ms ease, box-shadow 220ms ease, border-color 220ms ease;\n    }\n    .soft-card:hover, .metric-card:hover {\n        transform: translateY(-2px);\n        box-shadow: 0 6px 18px rgba(0,0,0,.16);\n        border-color: #79C9B0 !important;\n    }\n    .hero {\n        background: linear-gradient(125deg, #101D2A 0%, #142B3A 55%, #1A3038 100%) !important;\n        border: 1px solid #30495A !important;\n    }\n    .hero-title, .metric-value { color: #E6EDF4 !important; }\n    .eyebrow, .tag { color: #B0DED0 !important; }\n    .tag { background: #142333 !important; }\n    .stButton > button {\n        background: #79C9B0 !important;\n        color: #09151D !important;\n        border: 1px solid #79C9B0 !important;\n        border-radius: 12px;\n        font-weight: 800;\n        transition: transform 200ms ease, box-shadow 200ms ease, background-color 200ms ease;\n    }\n    .stButton > button:hover {\n        background: #B0DED0 !important;\n        color: #09151D !important;\n        transform: translateY(-2px);\n        box-shadow: 0 5px 14px rgba(121,201,176,.12);\n    }\n    /* Keep every interactive state in the same restrained blue-green palette. */\n    .stButton > button:focus,\n    .stButton > button:focus-visible,\n    .stButton > button:active,\n    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked),\n    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {\n        outline: none !important;\n        box-shadow: 0 0 0 1px #79C9B0 !important;\n        border-color: #79C9B0 !important;\n        background-color: #18303A !important;\n        color: #E6EDF4 !important;\n    }\n    .stButton > button:focus p,\n    .stButton > button:active p { color: #E6EDF4 !important; }\n    input, textarea, [data-baseweb="select"] * { accent-color: #79C9B0 !important; }\n\n    .stTextArea textarea, .stTextInput input {\n        background: #0D1925 !important;\n        color: #E6EDF4 !important;\n        border-color: #30495A !important;\n        border-radius: 14px;\n    }\n    div[data-baseweb="select"] > div {\n        background: #0D1925 !important;\n        border-color: #30495A !important;\n        border-radius: 12px;\n    }\n    hr { border-color: #26394A !important; }\n    p, label, h1, h2, h3, h4, li { color: #D8E3ED; }\n    a { color: #B0DED0 !important; }\n    .footer { color: #9BAFC0; font-size: 12px; padding: 28px 0 0; }\n\n    /* Respect visitors who prefer reduced motion. */\n    @media (prefers-reduced-motion: reduce) {\n        *, *::before, *::after {\n            animation-duration: 0.01ms !important;\n            animation-iteration-count: 1 !important;\n            scroll-behavior: auto !important;\n            transition-duration: 0.01ms !important;\n        }\n    }\n    </style>\n    '), unsafe_allow_html=True)
if 'lang' not in st.session_state:
    st.session_state.lang = 'EN'
_spacer, _lang_bar = st.columns([7, 2])
with _lang_bar:
    _ru, _kz, _en = st.columns(3, gap='small')
    for _column, _language in [(_ru, 'RU'), (_kz, 'KZ'), (_en, 'EN')]:
        with _column:
            st.button(tr(_language), key='language_' + _language, type='primary' if st.session_state.lang == _language else 'secondary', on_click=lambda code=_language: st.session_state.update(lang=code), use_container_width=True)
PAGES = ['🏠 Overview', '🔎 Analyzer', '📚 Safety Academy', '🧪 Test Lab', '💡 About QALQAN']
with st.sidebar:
    st.markdown(tr('# 🛡️ QALQAN'))
    st.caption(tr('Message safety, made understandable.'))
    st.markdown(tr('---'))
    st.markdown(tr('**NAVIGATION**'))
    for item in PAGES:
        st.button(tr(item), key='side_' + item, on_click=go_to, args=(item,), use_container_width=True)
    st.markdown(tr('---'))
    st.markdown(tr('**Creative Lab edition**'))
    st.caption(tr('A student prototype for safer digital communication.'))
st.caption(tr('🛡️ QALQAN  ·  Navigate between sections'))
if 'nav_choice' not in st.session_state or st.session_state.nav_choice not in PAGES:
    st.session_state.nav_choice = st.session_state.page
st.radio('Sections', PAGES, key='nav_choice', on_change=nav_changed, horizontal=True, label_visibility='collapsed', format_func=tr)
page = st.session_state.page
if page == '🏠 Overview':
    st.markdown(tr('\n        <div class="hero">\n            <div class="eyebrow">Your digital safety companion</div>\n            <div class="hero-title">Think twice.<br>Click wisely.</div>\n            <div class="hero-copy">\n                QALQAN checks messages for common warning signs,\n                explains what looks suspicious, and helps you decide\n                what to verify before taking action.\n            </div>\n        </div>\n        '), unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(tr('\n            <div class="soft-card">\n                <span class="tag">01 / ANALYZE</span>\n                <h3>🔎 Check a message</h3>\n                Paste a message and inspect the warning signs.\n                QALQAN explains the reasons behind its score.\n            </div>\n            '), unsafe_allow_html=True)
        st.button(tr('Open analyzer'), key='overview_analyzer', use_container_width=True, on_click=go_to, args=('🔎 Analyzer',))
    with col2:
        st.markdown(tr('\n            <div class="soft-card">\n                <span class="tag">02 / LEARN</span>\n                <h3>📚 Learn the patterns</h3>\n                Explore common scam techniques and simple ways\n                to protect your accounts and personal information.\n            </div>\n            '), unsafe_allow_html=True)
        st.button(tr('Open Safety Academy'), key='overview_academy', use_container_width=True, on_click=go_to, args=('📚 Safety Academy',))
    st.markdown(tr('### Your workspace'))
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(tr(f'\n            <div class="metric-card">\n                <div class="metric-label">Messages analyzed</div>\n                <div class="metric-value">{len(st.session_state.history)}</div>\n            </div>\n            '), unsafe_allow_html=True)
    with c2:
        flagged = sum((1 for item in st.session_state.history if item['score'] >= 4))
        st.markdown(tr(f'\n            <div class="metric-card">\n                <div class="metric-label">Flagged messages</div>\n                <div class="metric-value">{flagged}</div>\n            </div>\n            '), unsafe_allow_html=True)
    with c3:
        st.markdown(tr('\n            <div class="metric-card">\n                <div class="metric-label">Built-in test examples</div>\n                <div class="metric-value">12</div>\n            </div>\n            '), unsafe_allow_html=True)
    st.markdown(tr('### Recent analyses'))
    if not st.session_state.history:
        st.info(tr('Your recent analyses will appear here after you check a message.'))
    else:
        for item in st.session_state.history[:5]:
            with st.container(border=True):
                st.markdown(tr(f"**{html.escape(item['message'][:140])}**"))
                st.caption(tr(f"Score: {item['score']}/10 · {item['risk']}"))
elif page == '🔎 Analyzer':
    st.markdown(tr('\n        <div class="hero">\n            <div class="eyebrow">Message scanner</div>\n            <div class="hero-title">Let\'s inspect that message.</div>\n            <div class="hero-copy">\n                Paste any message to scan. The examples are only for testing.\n            </div>\n        </div>\n        '), unsafe_allow_html=True)
    st.selectbox(tr('Try an example'), ['Choose an example...'] + list(SAMPLES.keys()), key='sample_choice', on_change=load_sample, format_func=tr)
    message = st.text_area(tr('Message to analyze'), key='message_input', height=180, placeholder='Paste the message here...')
    if st.button(tr('🔍 Analyze message'), key='analyze_button', use_container_width=True):
        if not message.strip():
            st.warning(tr('Paste a message first, then run the analysis.'))
        else:
            with st.spinner(tr('Analyzing with QALQAN rules...')):
                result = analyze_message(message)
                analysis_mode = 'Offline risk assessment (no AI or API key needed)'
            st.session_state.analysis_mode = analysis_mode
            save_analysis(message, result)
            st.session_state.last_result = result
            st.session_state.last_message = message
    if 'last_result' in st.session_state:
        result = st.session_state.last_result
        analyzed_message = st.session_state.last_message
        score = result['score']
        color = risk_color(score)
        st.markdown(tr('---'))
        st.markdown(tr('### Analysis results'))
        st.caption(tr(st.session_state.get('analysis_mode', 'Rule-based analysis')))
        left, right = st.columns([1, 2])
        with left:
            st.markdown(tr(f"""\n                <div class="metric-card">\n                    <div class="metric-label">Suspicion score</div>\n                    <div class="metric-value" style="color:{color}">\n                        {score}<span style="font-size:17px">/10</span>\n                    </div>\n                    <p style="color:{color};font-weight:700">{result['risk']}</p>\n                </div>\n                """), unsafe_allow_html=True)
            st.progress(score / 10)
        with right:
            st.markdown(tr('#### What did QALQAN notice?'))
            if result.get('ai_reasons'):
                for reason in result['ai_reasons']:
                    st.markdown(tr('• ' + html.escape(reason)))
                st.caption(tr('Highlighted phrases below come from rule-based detection.'))
            elif result['findings']:
                for finding in result['findings']:
                    st.markdown(tr(f"""\n                        <div class="soft-card">\n                            <b>{html.escape(finding['name'])}</b>\n                            <span class="tag">+{finding['weight']} points</span>\n                            <p>{html.escape(finding['explanation'])}</p>\n                            <small>Matched: {html.escape(', '.join(finding['matches']))}</small>\n                        </div>\n                        """), unsafe_allow_html=True)
            else:
                st.success(tr('No known warning phrases were detected.'))
        st.markdown(tr('#### Message with detected phrases'))
        st.markdown(tr(f"""\n            <div class="soft-card" style="overflow-wrap:anywhere">\n                {render_highlights(analyzed_message, result['findings'])}\n            </div>\n            """), unsafe_allow_html=True)
        st.markdown(tr('#### What should you do?'))
        st.info(tr(result['recommendation']))
        st.caption(tr('AI-assisted when available, otherwise rule-based. The score is a heuristic, not proof that a message is safe or fraudulent. Do not paste private data.'))
elif page == '📚 Safety Academy':
    st.markdown(tr('\n        <div class="hero">\n            <div class="eyebrow">Safety Academy</div>\n            <div class="hero-title">Spot the red flags.</div>\n            <div class="hero-copy">\n                Scams often rely on pressure, curiosity, fear, or tempting rewards.\n                Knowing the patterns helps you pause and verify.\n            </div>\n        </div>\n        '), unsafe_allow_html=True)
    lessons = [('⏰ Urgency and pressure', '“Act now or your account will be closed!”', 'Pause. Verify a warning through an official channel instead of rushing.', PEACH), ('🎁 Unexpected prizes', '“Congratulations! You won a phone!”', 'Be careful with prizes you never entered to win. Never reveal a password to claim a reward.', LAVENDER), ('🔐 Private information', '“Send us your password and verification code.”', 'Do not share passwords or one-time codes in response to a message.', MINT), ('💳 Suspicious payments', '“Transfer money to unlock your package.”', 'Check unexpected payment requests independently.', PEACH), ('🔗 Unexpected links', '“Click here to verify your account.”', 'Visit the official website yourself instead of trusting an unexpected link.', LAVENDER), ('🎭 Impersonation and threats', '“We are your bank. Your account will be blocked.”', 'Contact the organization using a verified channel.', MINT)]
    for title, example, advice, color in lessons:
        st.markdown(tr(f'\n            <div class="soft-card" style="border-left:5px solid {color}">\n                <h3>{title}</h3>\n                <p><b>Example:</b> {html.escape(example)}</p>\n                <p>{html.escape(advice)}</p>\n            </div>\n            '), unsafe_allow_html=True)
    st.warning(tr('A message can be dangerous even without these phrases. Always consider the context and verify the sender.'))
elif page == '🧪 Test Lab':
    st.markdown(tr('\n        <div class="hero">\n            <div class="eyebrow">Evaluation workspace</div>\n            <div class="hero-title">Test the detector.</div>\n            <div class="hero-copy">\n                Run a fixed set of labeled examples and compare QALQAN\'s\n                predictions with the expected labels.\n            </div>\n        </div>\n        '), unsafe_allow_html=True)
    st.markdown(tr('### How the evaluation works'))
    st.markdown(tr('\n        - **Suspicious** is predicted when the score is **4/10 or higher**.\n        - Every example has an expected label assigned in advance.\n        - The results show where the detector succeeds and where it makes mistakes.\n        '))
    if st.button(tr('🧪 Run all 12 tests'), key='run_lab', use_container_width=True):
        st.session_state.lab_results = evaluate_test_set()
    if st.session_state.lab_results is None:
        st.info(tr('Run the test set to calculate the evaluation metrics.'))
    else:
        df = st.session_state.lab_results
        tp = int((df['Outcome'] == 'True positive').sum())
        tn = int((df['Outcome'] == 'True negative').sum())
        fp = int((df['Outcome'] == 'False positive').sum())
        fn = int((df['Outcome'] == 'False negative').sum())
        total = len(df)
        accuracy = (tp + tn) / total if total else 0
        precision = tp / (tp + fp) if tp + fp else 0
        recall = tp / (tp + fn) if tp + fn else 0
        specificity = tn / (tn + fp) if tn + fp else 0
        st.markdown(tr('---'))
        st.markdown(tr('### Performance overview'))
        columns = st.columns(4)
        metrics = [('Accuracy', accuracy, 'Correct predictions overall'), ('Precision', precision, 'Flagged messages that are truly suspicious'), ('Recall', recall, 'Suspicious examples detected'), ('Specificity', specificity, 'Ordinary examples correctly cleared')]
        for col, (label, value, description) in zip(columns, metrics):
            with col:
                st.markdown(tr(f'\n                    <div class="metric-card">\n                        <div class="metric-label">{label}</div>\n                        <div class="metric-value">{value:.0%}</div>\n                        <div style="font-size:12px;color:#9BAFC0">{description}</div>\n                    </div>\n                    '), unsafe_allow_html=True)
        st.caption(tr(f'Evaluated {total} labeled examples. These results describe this small built-in test set only.'))
        st.markdown(tr('### Confusion matrix'))
        matrix = pd.DataFrame([[tp, fn], [fp, tn]], index=['Actually suspicious', 'Actually ordinary'], columns=['Predicted suspicious', 'Predicted ordinary'])
        st.dataframe(matrix, use_container_width=True)
        a, b, c, d = st.columns(4)
        a.metric('True positives', tp)
        b.metric('True negatives', tn)
        c.metric('False positives', fp)
        d.metric('False negatives', fn)
        with st.expander(tr('What do these results mean?')):
            st.markdown(tr('\n                - **True positive:** a suspicious message was correctly flagged.\n                - **True negative:** an ordinary message was correctly classified.\n                - **False positive:** an ordinary message was incorrectly flagged.\n                - **False negative:** a suspicious message was missed.\n\n                A useful detector should catch suspicious messages while avoiding\n                too many false alarms.\n                '))
        st.markdown(tr('### Individual test results'))
        st.dataframe(df[['Category', 'Expected', 'Predicted', 'Score', 'Outcome']], use_container_width=True, hide_index=True)
        with st.expander(tr('View the full test messages')):
            st.dataframe(df[['Category', 'Message', 'Expected', 'Predicted', 'Score']], use_container_width=True, hide_index=True)
        st.markdown(tr('### What to improve next'))
        if fp > 0:
            st.warning(tr(f'QALQAN raised {fp} false alarm(s). Review these ordinary messages and adjust overly broad rules.'))
        else:
            st.success(tr('No false alarms in this small test set.'))
        if fn > 0:
            st.warning(tr(f'QALQAN missed {fn} suspicious message(s). Review their wording and add useful variations to the rules.'))
        else:
            st.success(tr('All suspicious examples in this test set were detected.'))
        st.caption(tr('This test set is small and hand-written. For stronger evaluation, test more realistic messages that were not used while designing the rules.'))
elif page == '💡 About QALQAN':
    st.markdown(tr('\n        <div class="hero">\n            <div class="eyebrow">About the project</div>\n            <div class="hero-title">QALQAN protects through awareness.</div>\n            <div class="hero-copy">\n                A student-built prototype that helps people recognize\n                suspicious messages and understand common online safety risks.\n            </div>\n        </div>\n        '), unsafe_allow_html=True)
    st.markdown(tr('### The idea'))
    st.markdown(tr('\n        Online scams often use familiar patterns: urgent demands, unexpected\n        prizes, suspicious payment requests, and attempts to collect private data.\n\n        QALQAN checks message text against warning phrases, calculates a\n        suspicion score, and explains which patterns were found.\n        '))
    st.markdown(tr('### What the prototype can do'))
    st.markdown(tr('\n        - Analyze pasted text using transparent offline safety rules, without external AI.\n        - Explain detected warning signs.\n        - Offer basic safety recommendations.\n        - Run a labeled test set and display evaluation metrics.\n        '))
    st.markdown(tr('### Current limitations'))
    st.markdown(tr('\n        - Offline analysis does not require an API key or internet connection.\n        - It may miss unfamiliar wording, slang, or new scam techniques.\n        - It may flag harmless messages containing suspicious phrases.\n        - Its score is a heuristic, not a verified probability of fraud.\n        - The built-in test set is small and cannot represent every real-world message.\n        '))
    st.info(tr('QALQAN is a learning and awareness tool. When a message asks for money, passwords, or verification codes, verify it through an independent official channel.'))
st.markdown(tr('\n    <div class="footer">\n        QALQAN · Creative Lab · Think twice. Click wisely.\n    </div>\n    '), unsafe_allow_html=True)
