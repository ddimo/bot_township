# coding=utf-8

FULL_LOG_FROM_LEVEL = 0 # с какого уровня записать полный лог, если 0 - то используется следующая переменная
FULL_LOG_FOR_LEVEL = 30 # для какого конкретно уровня записать полный лог

MAX_WAIT_FOR_UPGRADE = 100    # сколько шагов максимум ждем прежде чем купим апгрейд даже если копим на здание

RESULT_FILES_SAVED = False
f = open ("result.html","w")
fshort = open ("short_result.html","w")
favrg = open ("avrg_result.html","w")