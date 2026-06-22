import os
import sys
import subprocess
import importlib

REQUIRED_PACKAGES = ['gspread', 'oauth2client', 'google-api-python-client']
def ensure_packages(packages):
    for pkg in packages:
        try:
            importlib.import_module(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        else:
            # print('Пакет {} уже установлен.'.format(pkg))
            pass
ensure_packages(REQUIRED_PACKAGES)


import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from collections import OrderedDict
error = {}

try:
    dirName = os.path.dirname(os.path.abspath(__file__))

    # Авторизация с использованием учетных данных Google API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(dirName, 'collisionszh-75467132a233.json'), scope)
    client = gspread.authorize(creds)

    with open(os.path.join(dirName, 'sendDataNameGoogleTable.json'), 'r') as file:
        googleNameTable = json.load(file)['NameTable']


    # Открываем нужную таблицу
    try:
        spreadsheet = client.open(googleNameTable)
    except Exception as e:
        print("Ошибка при обращении к {} ->-> {}".format(googleNameTable, e))
        sys.exit()

    # Получаем все листы в таблице
    sheets = spreadsheet.worksheets()
    sheets_names = [s.title for s in sheets]

    all_data = OrderedDict()

    itogData = OrderedDict()

    sheetData = OrderedDict()
    # Проходим по каждому листу, за исключением тех, у которых название "Координация"
    for sheet in sheets:
        if sheet.title not in ['Текст.ТЗ (Кирпич)', 'Текст.ТЗ (Монолит)','Текст.ТЗ (Панель)' ,'Шаблон', 'Данные', 'Изменения', 'Памятка',
                               'Архив (05.11.25)']:
            sheetData[sheet.title] = sheet.get_all_values()

        # if sheet.title == 'Лист 1':
        #     # Получаем все данные с листа и добавляем в общий список
        #     sheet_data = sheet.get_all_values()


    with open(os.path.join(dirName, 'result.json'), 'w') as file:
        json.dump(sheetData, file)

    print('Данные получены...')
    sys.exit()
except Exception as e:
    print('Error')
    import datetime
    with open(os.path.join(dirName, 'error.json'), 'w') as file:
        json.dump({'error': str(e), 'datetime': str(datetime.datetime.today())}, file)
        print(e)
