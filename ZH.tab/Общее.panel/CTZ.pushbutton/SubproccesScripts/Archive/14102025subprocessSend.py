import os
import pprint
import sys

import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import re
from typing import Optional
import subprocess
from datetime import datetime
import getpass

dt = datetime.now()
nowTime = f'{dt.strftime("%d/%m/%Y\n%H.%M.%S")}\n{getpass.getuser()}'

from collections import OrderedDict
error = {}

dirName = os.path.dirname(os.path.abspath(__file__))
external_PY_script_path_getData = dirName + r'\subprocessFile.py'



def a1_col_to_index(col_a1: str) -> int:
    """ 'A'->1, 'Z'->26, 'AA'->27 ... """
    col_a1 = col_a1.strip().upper()
    if not re.fullmatch(r"[A-Z]+", col_a1):
        raise ValueError(f"Неверный A1 столбец: {col_a1}")
    n = 0
    for ch in col_a1:
        n = n * 26 + (ord(ch) - ord('A') + 1)
    return n


def merge_blocks_in_range_with_limit_py(
        client,  # gspread client (не используется, но пусть будет для совместимости)
        spreadsheet,  # gspread Spreadsheet
        sheet_name: str,
        start_col_a1: str,
        end_col_a1: str,
        limit_col_a1: str,
        start_row: Optional[int] = None,
        end_row: Optional[int] = None,
        max_retries: int = 3):
    """
    Оптимизированная версия: 2 чтения максимум (прямоугольник + лимит, если вне прямоугольника) и 1 batchUpdate.
    """
    if not sheet_name:
        raise ValueError("Укажите имя листа.")
    if not start_col_a1 or not end_col_a1:
        raise ValueError("Укажите начальный и конечный столбцы, напр. 'P' и 'BZ'.")
    if not limit_col_a1:
        raise ValueError("Укажите столбец-ограничитель, напр. 'L'.")

    ws = spreadsheet.worksheet(sheet_name)

    col_start = a1_col_to_index(start_col_a1)
    col_end = a1_col_to_index(end_col_a1)
    if col_end < col_start:
        raise ValueError("Конечный столбец левее начального.")
    lim_col = a1_col_to_index(limit_col_a1)

    s = start_row or 1
    e = end_row or ws.row_count
    if e < s:
        return
    num_rows = e - s + 1
    num_cols = col_end - col_start + 1

    # --- helper with light retries for value reads
    def safe_get(a1_range: str):
        delay = 1.0
        for attempt in range(max_retries):
            try:
                return ws.get(a1_range, value_render_option="UNFORMATTED_VALUE", major_dimension="ROWS")
            except Exception as ex:
                # 429/backoff
                if "Quota exceeded" in str(ex) or "429" in str(ex):
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
                    delay *= 2
                else:
                    raise

    # 1) читаем сразу весь прямоугольник данных, который будем мерджить
    rect_a1 = f"{start_col_a1}{s}:{end_col_a1}{e}"
    rect_values = safe_get(rect_a1)  # список строк, каждая строка — список ячеек по столбцам
    # нормализуем размеры
    if len(rect_values) < num_rows:
        rect_values += [[] for _ in range(num_rows - len(rect_values))]
    for r in range(len(rect_values)):
        row = rect_values[r]
        if len(row) < num_cols:
            row += [""] * (num_cols - len(row))
        rect_values[r] = [(str(c).strip() if c is not None else "") for c in row]

    # 2) читаем лимит-столбец. Если лимит внутри прямоугольника — берём из него.
    if col_start <= lim_col <= col_end:
        # индекс внутри прямоугольника
        lim_idx = lim_col - col_start  # 0-based внутри прямоугольника
        lim_vals = [row[lim_idx] if lim_idx < len(row) else "" for row in rect_values]
    else:
        lim_a1 = f"{limit_col_a1}{s}:{limit_col_a1}{e}"
        lim_raw = safe_get(lim_a1)
        lim_vals = [(r[0] if r else "") for r in lim_raw]
        if len(lim_vals) < num_rows:
            lim_vals += [""] * (num_rows - len(lim_vals))

    def is_empty(v):
        return v == "" or v is None

    requests = []

    # 3) сначала снимем мерджи на всём прямоугольнике одним запросом в каждом столбце (или можно одним — но безопаснее по столбцам)
    # (одним запросом на весь прямоугольник unmergeCells тоже корректно)
    requests.append({
        "unmergeCells": {
            "range": {
                "sheetId": ws.id,
                "startRowIndex": s - 1,
                "endRowIndex": e,
                "startColumnIndex": col_start - 1,
                "endColumnIndex": col_end
            }
        }
    })

    # 4) обрабатываем каждый столбец из уже загруженного массива (без доп. чтений)
    for c in range(num_cols):  # 0..num_cols-1
        col_index_1based = col_start + c
        vals = [rect_values[r][c] for r in range(num_rows)]

        i = 0
        while i < num_rows:
            if is_empty(vals[i]):
                i += 1
                continue

            j = i + 1
            while j < num_rows:
                if not is_empty(vals[j]):
                    break
                if is_empty(lim_vals[j]):
                    break
                j += 1

            natural_len = max(1, j - i)

            k_str = str(lim_vals[i]) if lim_vals[i] is not None else ""
            try:
                k_val = float(k_str.replace(",", "."))
            except Exception:
                k_val = None
            if not (k_val and k_val > 0):
                k = None
            else:
                k = int(k_val)

            length = min(natural_len, k) if k else natural_len

            if length > 1:
                requests.append({
                    "mergeCells": {
                        "range": {
                            "sheetId": ws.id,
                            "startRowIndex": (s - 1) + i,
                            "endRowIndex": (s - 1) + i + length,
                            "startColumnIndex": col_index_1based - 1,
                            "endColumnIndex": col_index_1based
                        },
                        "mergeType": "MERGE_ALL"
                    }
                })
            i += length

    # 5) один batchUpdate
    if requests:
        spreadsheet.batch_update({"requests": requests})





def num_to_label(n: int) -> str:
    """
    Преобразует 0-индексированное число в буквенную метку (A, B, ..., Z, AA, AB, ...)
    0 -> A, 1 -> B, ..., 25 -> Z, 26 -> AA, ...
    """
    if n < 0:
        raise ValueError("n должно быть неотрицательным")
    n += 1  # смещаем к excel-представлению (1->A)
    letters = []
    while n > 0:
        n, r = divmod(n - 1, 26)  # "-1" делает систему без нулевого разряда
        letters.append(chr(ord('A') + r))
    return ''.join(reversed(letters))

try:
    with open(os.path.join(dirName, 'sendDataNameGoogleTable.json'), 'r') as file:
        data = json.load(file)
        googleNameTable = data['NameTable']
        googleNameSheet = data['NameSheet']

    # Авторизация с использованием учетных данных Google API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive", 'https://www.googleapis.com/auth/script.projects']
    creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(dirName, 'collisionszh-75467132a233.json'), scope)
    service = build("script", "v1", credentials=creds, cache_discovery=False)
    client = gspread.authorize(creds)

    # Открываем нужную таблицу
    spreadsheet = client.open(googleNameTable)

    # Получаем все листы в таблице
    sheets = spreadsheet.worksheets()
    sheets_names = [s.title for s in sheets]

    with open(os.path.join(dirName, r'resultToSend.json'), 'r') as file:
        resultChecks = json.load(file)

    for sheet in sheets:
        batch_data = []
        if sheet.title == googleNameSheet:
            sheet_data = sheet.get_all_values()
            counter = 0

            indexInsertArchive = None
            for i, data in enumerate(sheet_data):
                googleCodeCheck = data[2]
                googleNameCheck = data[3]
                checkNameResult = '{}||{}'.format(googleCodeCheck, googleNameCheck)
                columnStatus = 7

                counter += 1
                if counter < 3:
                    continue
                if checkNameResult != '' and checkNameResult in resultChecks.keys():

                    for k in range(16, 60):
                        if len(data[k]) == 0 and indexInsertArchive is None:
                            indexInsertArchive = k
                            break
                        else:
                            continue

                    status = data[columnStatus]
                    itogBoolStatus = resultChecks[checkNameResult]['itogBoolValue']
                    passed_count_elems = int(resultChecks[checkNameResult]['passed_count_currentFile']) + int(resultChecks[checkNameResult]['passed_count_linkFile'])
                    isPassedCheck = resultChecks[checkNameResult]['isPassedCheck']

                    strToSend = ''
                    if isPassedCheck == 'True':
                        strToSend = 'Не проверяется'
                    elif status == 'TRUE' and itogBoolStatus == 'True':
                        strToSend = 'Замоделировано\n({})'.format(passed_count_elems)
                    elif status == 'FALSE' and itogBoolStatus == 'True':
                        strToSend = 'Не должно присутствовать\n({})'.format(passed_count_elems)
                    elif status in ['TRUE'] and itogBoolStatus == 'False':
                        strToSend = 'Не замоделировано'
                    elif status in ['FALSE'] and itogBoolStatus == 'False':
                        strToSend = 'Не присутствует'
                    batch_data.append({
                        'range': f'K{i + 1}:K{i + 1}',
                        'values': [[strToSend]]})
                    batch_data.append({'range': f'{num_to_label(indexInsertArchive)}{i + 1}:{num_to_label(indexInsertArchive)}{i + 1}',
                                       'values': [[strToSend]]})

            if isinstance(indexInsertArchive, int):
                batch_data.append({'range': f'{num_to_label(indexInsertArchive)}{2}:{num_to_label(indexInsertArchive)}{2}',
                                   'values': [[nowTime]]})

            if batch_data:
                sheet.batch_update(batch_data)

            try:
                merge_blocks_in_range_with_limit_py(
                    client=client,
                    spreadsheet=spreadsheet,
                    sheet_name=sheet.title,  # из твоего JSON
                    start_col_a1=num_to_label(indexInsertArchive),
                    end_col_a1=num_to_label(indexInsertArchive),
                    limit_col_a1="M",
                    start_row=1,
                    end_row=None  # или число
                )
                # print("Python-merge: готово.")
            except Exception as ex:
                print("Python-merge: ошибка:", ex)

        else:
            continue




    print('Результаты отправлены...')
    sys.exit()

except Exception as e:
    print(e)
    print('Error')
    import datetime
    with open(os.path.join(dirName, 'error.json'), 'w') as file:
        json.dump({'error': str(e), 'datetime': str(datetime.datetime.today())}, file)
    print(e)
