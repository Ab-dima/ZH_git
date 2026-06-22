#-*- coding: utf-8 -*-

a = 123
import getpass
import json
from datetime import datetime

def track_run(title, base_dir):
    try:
        month = {
            1: "январь", 2: "февраль", 3: "март", 4: "апрель",
            5: "май", 6: "июнь", 7: "июль", 8: "август",
            9: "сентябрь", 10: "октябрь", 11: "ноябрь", 12: "декабрь"}[datetime.now().month].capitalize()
        userName = getpass.getuser()

        for spl in base_dir.split("\\"):
            if '.tab' in spl:
                tabPanel = spl.replace('.tab', '')

        title_ = '{}-{}'.format(tabPanel, title.replace('\n', ' '))

        if title_ and userName and tabPanel:
            try:
                with open(r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\Плагины\Железно\CollectingStatistics_DmitryA\dataStatistic.json', 'r') as file:
                    data = json.load(file)
                if month in data:
                    if userName in data[month]:
                        if title_ in data[month][userName]:
                            data[month][userName][title_] += 1
                        else:
                            data[month][userName][title_] = 1
                    else:
                        data[month][userName] = {title_ : 1}
                else:
                    data[month] = {userName : {title_ : 1}}
                with open(r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\Плагины\Железно\CollectingStatistics_DmitryA\dataStatistic.json', 'w') as file:
                    json.dump(data, file)
            except Exception as e:
                with open(r'P:\10_Документы\Bim\Библиотека ресурсов\Revit\Плагины\Железно\CollectingStatistics_DmitryA\dataStatistic.json', 'w') as file:
                    json.dump({month: {userName: {title_ : 1}}}, file)
    except Exception as e:
        print('run_stats: {}'.format(e))

