from coinmarketcap import Market
from datetime import datetime
import numpy as np
import threading
import _pickle
import time as tm
import sys

time_arr = []


def test1(isThreaded):
    coinmarketcap = Market()
    start_time = tm.time()

    data = coinmarketcap.ticker(limit=10, sort='volume_24h')

    # ПРИХОДИТ ЛИ ОТВЕТ ЗА 500МС
    time = tm.time() - start_time
    if time > 0.5:
        if isThreaded:
            time_arr.append(False)
        else:
            print('Test 1 failed.\nElapsed time: ' + str(time) + '\n')
        return
    time_arr.append(time)

    # АКТУАЛЬНА ЛИ ИНФОРМАЦИЯ ПО КАЖДОЙ ВАЛЮТЕ
    date = datetime.now().date()
    for key in data['data']:
        time = data['data'][key]['last_updated']
        if datetime.fromtimestamp(time).date() < date:
            if isThreaded:
                time_arr.append(False)
            else:
                print('Test 1 failed.\nInformation is not current.\n')
            return

    # НЕ ПРЕВЫШАЕТ ЛИ РАЗМЕР ПАКЕТА 10КБ
    data_str = _pickle.dumps(data)
    if sys.getsizeof(data_str) > 1024 * 10:
        if isThreaded:
            time_arr.append(False)
        else:
            print('Test 1 failed.\nSize of data is over 10kb.\n')
        return

    if not isThreaded:
        print('Test 1 passed.')


def test2(x):
    time_arr.clear()
    # АСИНХРОННЫЙ ЗАПУСК 8 ТЕСТОВ
    for i in range(x):
        t = threading.Thread(target=test1, args=(True,))
        t.start()
    tm.sleep(1)

    if time_arr.count(False) > 0:
        print('Test 2 failed.')
        return

    # ПРОВЕРКА ПЕРЦЕНТИЛЯ И RPS
    p = np.percentile(time_arr, 80)
    rps = x / sum(time_arr)
    if p >= 0.45 or rps <= 5:
        print('Test 2 failed\n80% latency: ' + str(p) + '\nrps: ' + str(rps))
    else:
        print('Test 2 passed.')
        print('80% latency: ' + str(round(p, 3)) + '\nrps: ' + str(round(rps, 2)))


test1(isThreaded=False)
test2(8)
