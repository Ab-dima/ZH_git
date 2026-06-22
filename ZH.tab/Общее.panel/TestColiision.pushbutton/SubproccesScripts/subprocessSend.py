import os
import pprint
import sys

import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
import subprocess

from collections import OrderedDict
error = {}

dirName = os.path.dirname(os.path.abspath(__file__))
external_PY_script_path_getData = dirName + r'\subprocessFile.py'

try:
    # Авторизация с использованием учетных данных Google API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(dirName, 'collisionszh-75467132a233.json'), scope)
    client = gspread.authorize(creds)

    # Открываем нужную таблицу
    spreadsheet = client.open("Коллизии ZH")

    # Получаем все листы в таблице
    sheets = spreadsheet.worksheets()
    sheets_names = [s.title for s in sheets]

    with open(os.path.join(dirName, r'sheetNameToSendData.json'), 'r') as file:
        dataConflicts = json.load(file)

    for sheet in sheets:
        batch_data = []
        sheetName = list(dataConflicts.keys())[0]
        if sheet.title == sheetName:
            sheet_data = sheet.get_all_values()
            for conflict in dataConflicts[list(dataConflicts.keys())[0]].values():
                for i, row in enumerate(sheet_data):
                    # Проверяем, есть ли в строке нужные Id1 и Id2
                    if len(row) > 2 and row[1] == conflict[0] and row[2] == conflict[1]:
                        # Если статус совпадает с указанным в конфликте, обновляем его
                        # if row[3] != conflict[2]:
                        #     # batch_data.append({
                        #     #     'range': f'D{i+1}',
                        #     #     'values': [[conflict[2]]]})
                        batch_data.append({
                            'range': f'D{i + 1}:F{i + 1}',
                            'values': [[conflict[2], conflict[3], conflict[4]]]})

            if batch_data:
                sheet.batch_update(batch_data)
        else:
            continue

    subprocess.Popen(['python', external_PY_script_path_getData], stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)

    sys.exit()

except Exception as e:
    print('Error')
    import datetime
    with open(os.path.join(dirName, 'error.json'), 'w') as file:
        json.dump({'error': str(e), 'datetime': str(datetime.datetime.today())}, file)
    print(e)
