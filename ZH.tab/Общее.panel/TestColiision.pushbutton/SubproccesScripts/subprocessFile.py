import os
import pprint
import sys

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

    # Открываем нужную таблицу
    spreadsheet = client.open("Коллизии ZH")

    # Получаем все листы в таблице
    sheets = spreadsheet.worksheets()
    sheets_names = [s.title for s in sheets]

    all_data = OrderedDict()

    # Проходим по каждому листу, за исключением тех, у которых название "Координация"
    for sheet in sheets:
        if sheet.title == 'Координация':
            continue
        else:
            all_data[sheet.title] = []
            # Получаем все данные с листа и добавляем в общий список
            sheet_data = sheet.get_all_values()

            result_to_json = OrderedDict()

            for data in sheet_data[1:]:
                data_conflicts = []
                if len(data[0].split('_'))>1:
                    name_proverka = data[0]
                    result_to_json[name_proverka] = []
                elif 'конфликт' in data[0].lower():
                    result_to_json[name_proverka].append(data)
                else:
                    continue

            all_data[sheet.title].append(result_to_json)

    with open(os.path.join(dirName, 'result.json'), 'w') as file:
        json.dump(all_data, file)

    for d in all_data.keys():
        print(d)
        for dd in all_data[d]:
            for ddd in dd.keys():
                print(ddd)
                for bbb in dd[ddd]:
                    print(bbb)

    sys.exit()

except Exception as e:
    print('Error')
    import datetime
    with open(os.path.join(dirName, 'error.json'), 'w') as file:
        json.dump({'error': str(e), 'datetime': str(datetime.datetime.today())}, file)
        print(e)
