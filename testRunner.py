import time
import os
import json
import configparser
from shutil import copy
from argparse import ArgumentParser
from logger import Log
from vmware import VMware
from glob import glob


def ini_to_dict(path_to_ini):
    ini = configparser.ConfigParser()
    ini.read(path_to_ini, encoding='utf-8')
    section_names = list(ini.sections())
    section_data = []
    for section in ini.sections():
        options = list(ini[section])
        values = list(ini[section].values())
        section_data.append(dict(zip(options, values)))
    dic = dict(zip(section_names, section_data))

    # парсим строки списков стендов/тестов в группах в list
    if 'groups' in dic.keys():
        for group in dic['groups']:
            dic['groups'][group] = [stand.strip(" \"\'[]") for stand in dic['groups'][group].split(",")]

    return dic


def check_stand(stand):

    keys = stand.keys()
    man_keys = ['path', 'name', 'user', 'pass']
    opt_keys = ['fullname', 'OS', 'parent', 'snapshot',
                'host', 'build', 'state', 'delay',
                'guest_dir', 'host_dir', 'linked']

    # проверяемя обязательные параметры
    for key in man_keys:
        if not(key in keys):
            return "обязательный параметр '{}' не задан в настройках стенда".format(key)
        elif not (type(stand[key]) is str):
            return "обязательный параметр '{}' должен быть строкой".format(key)

    # устанавливаем в None незаполненные необязательные параметры
    for key in opt_keys:
        if not(key in keys):
            stand[key] = None

    # задаем дефолты для незаданных опций
    if stand['linked'] is None:
        stand['linked'] = True
    if stand['delay'] is None:
        stand['delay'] = VMware.DEFAULT_MAX_WAIT_TIME
    if not (type(stand['state']) is int):
        stand['state'] = 0

    # режем крайний слеш
    if stand['host_dir']:
        stand['host_dir'] = stand['host_dir'].rstrip("\\")
    if stand['guest_dir']:
        stand['guest_dir'] = stand['guest_dir'].rstrip("\\")
        stand['guest_dir'] = stand['guest_dir'].rstrip("/")

    return 0


def check_test(test):

    keys = test.keys()
    man_keys = ('name',)
    opt_keys = ('fullname', 'report', 'step',
                'delete', 'take', 'delay', 'stand', 'stand_group')

    # проверяемя обязательные параметры
    for key in man_keys:
        if not(key in keys):
            return "обязательный параметр '{}' не задан в описании теста".format(key)

    # устанавливаем в None незаполненные необязательные параметры
    for key in opt_keys:
        if not(key in keys):
            test[key] = None

    # задаем дефолты для незаданных опций
    if test['delay'] is None:
        test['delay'] = VMware.DEFAULT_MAX_WAIT_TIME

    # конвертим опции, заданные строками, в списки
    for key in ('step', 'report', 'stand', 'stand_group'):
        if test[key] is None:
            test[key] = []
        elif type(test[key]) is str:
            test[key] = [s.strip(" \"\'[]") for s in test[key].split(",")]
        elif not (type(test[key]) is list):
            return "параметр '{}' должен быть строкой или списком".format(key)

    return 0


def prepare(stand):
    # проверка параметров стенда
    action = check_stand(stand)
    if action:
        return "Не правильно указаны параметры стенда: '{}'".format(action)

    else:
        log("{1} '{0[name]}' {1}".format(stand, "-" * 20), 1)
        log("Началась подготовка стенда '{0[name]}' ('{0[fullname]}')".format(stand), 1)

    # инициализация стенда
    if stand['parent'] is None:
        vm = VMware(stand['path'], stand['user'], stand['pass'], stand['delay'], maxAttepmt=3)
        if stand['snapshot'] is None:
            action = 0
        else:
            log("Пытаемся откатиться на снапшот '{}' ".format(stand['snapshot']))
            action = vm.revert(stand['snapshot'])
    else:
        log("Пытаемся склонировать стенд")
        parent = VMware(stand['parent'])
        action = parent.clone(stand['path'], stand['name'], stand['snapshot'], stand['linked'])
        vm = VMware(stand['path'], stand['user'], stand['pass'], stand['delay'])
    if action:
        return "не удачно: {}".format(action)
    else:
        log("удачно")

    # включаем / выключаем, если нужно
    state = vm.checkStart()
    if state == stand['state']:
        log("машина в требуемом состоянии")
        action = 0
    elif stand['state'] == 0:
        log("пытаемся запустить машину")
        action = vm.start()
    else:
        log("пыатемся завершить работу")
        action = vm.stop()
        log(stand['state'])
    if action:
        return "не удалость привести машину в требуемое состояние. vmrun.exe:{}".format(action)
    else:
        log("машина приведена в требуемое состояние")

    # выходим, если машина выключена
    if stand['state'] == 1:
        log("подготовка стенда закончена. копирование файлов выполнятся не будет т.к. задано состояние 1(выкл)", 1)
        return vm

    # каждые 10 сек пробуем запустить ping на госте, чтоб проверить логон юзера
    log("Ожидаем логона пользователя")
    timer = 0
    while timer <= stand['delay']:
        win_ping = vm.run("ping.exe localhost")
        nix_ping = vm.run("/bin/ping -c4 localhost")
        time.sleep(10)
        if win_ping == 0 or nix_ping == 0:
            break
        else:
            timer+=30

    if action:
        return "не удалось выполнить вход в систему vmrun.exe:{}".format(action)

    if stand['guest_dir'] is None:
        log("подготовка стенда закончена. копирование файлов выполнятся не будет т.к. не указан 'guest_dir", 1)
        return vm
    elif stand['host_dir'] is None:
        log("подготовка стенда закончена. копирование файлов выполнятся не будет т.к. не указан 'host_dir", 1)
        return vm

    log("Пробуем скопировать необходимые файлы", 1)

    action = vm.copyTo(stand['host_dir'], stand['guest_dir'])
    if action:
        log("Не удалось скопировать необходимые файлы. Выключаем стенд:{}").format(vm.stop())
        return "ошибка копирования vmrun.exe:{}".format(action)
    else:
        log("копирование завершено")

    log("подготовка стенда закончена, файлы скопированы", 1)
    return vm


def completion(vm, test, stand):
    global report
    test_report = {}
    to_path = "{}\\{}_{}\\".format(report, test['name'], stand['name'])
    if not os.path.isdir(to_path):
        os.makedirs(to_path)
    for path in test['report']:
        path = path.replace("[stand_name]", stand['name'])
        if stand['guest_dir']:
            path = path.replace(".\\", stand['guest_dir'] + "\\")
            path = path.replace("./", stand['guest_dir'] + "/")
        action = vm.copyFrom(path, to_path)
        if action:
            log("Не удалость скопировать файл отчета "
                "{} > {}:{}".format(path, to_path, action), 0)
            test_report[path] = "[FAIL]"
        else:
            test_report[path] = "[OK]"

    # попытка выключить стенд
    log("Выключаем стенд '{0[name]}'".format(stand), 1)
    if vm.stop():
        log("Не удалось заверешить работу стенда")

    time.sleep(5)

    if test['delete']:
        action = vm.delete(test['delete'])
        if action:
            test_report["Удаление снапшота '{}' ".format(test['delete'])] = "[FAIL]"
            log("Не удалось удалить снапшот '{}' vmrun.exe:'{}'".format(test['delete'], action, 0))
        else:
            test_report["Удаление снапшота '{}' ".format(test['delete'])] = "[OK]"
            log("Cнапшот '{}' удален".format(test['delete']), 1)

    time.sleep(5)

    if test['take']:
        action = vm.take(test['take'])
        if action:
            test_report["Создание снапшота '{}' ".format(test['take'])] = "[FAIL]"
            log("Не удалось создать снапшот '{}' vmrun.exe:'{}'".format(test['take'], action, 0))
        else:
            test_report["Создание снапшота '{}' ".format(test['take'])] = "[OK]"
            log("Cнапшот '{}' создан".format(test['take']), 1)
    return test_report


def run(test, stand):

    test_report = {'prepare': "Не начата", 'step': {}, 'report': {}, 'result': "Не начат",
                   'test_name': '', 'stand_name': '',
                   'test_fullname': '', 'stand_fullname': '',
                   'start': time.time(), 'stop': time.time()}

    action = check_test(test)

    if action:
        test_report['prepare'] = "Неправильно заданы парамтеры теста: {}'".format(action)
        log("Неправильно заданы парамтеры теста: {}'".format(action), 0)
        return test_report

    test_report['test_name'] = test['name']
    test_report['test__fullname'] = test['fullname']
    log("{1} '{0[name]}' {1}".format(test, "-" * 20), 1)

    vm = prepare(stand)
    if type(vm) is VMware:
        test_report['prepare'] = "Подготовлен [OK]"
    else:
        test_report['prepare'] = str(vm) + " [FAIL]"
        test_report['stop'] = time.time()
        log("тест '{0[name]}' прерван, не удалось подготовить стенд '{1[name]}:{2}'".format(test, stand, str(vm)), 0)
        return test_report

    log("{0} Начался тест: '{1[name]}' на стенде '{2[name]} {0}'".format("-" * 20, test, stand), 1)

    test_report['stand_name'] = stand['name']
    test_report['stand_fullname'] = stand['fullname']
    test_report['result'] = "Запущен [OK]"

    for step in test['step']:
        step = step.replace("[stand_name]", stand['name'])
        if stand['guest_dir']:
            step = step.replace(".\\", stand['guest_dir'] + "\\")
            step = step.replace("./", stand['guest_dir'] + "/")
        log("Попытка выпонения команды '{}' на стенде '{}'".format(step, stand['name']), 1)
        action = vm.run(step, test['delay'])
        if action:
            log("Команда '{}' на стенде '{}' не завершена:{}".format(step, stand['name'], action), 0)
            test_report['step'][step] = action + " [FAIL]"
        else:
            log("Команда '{}' на стенде '{}' выполнена".format(step, stand['name']), 1)
            test_report['step'][step] = "[OK]"

    test_report['report'] = completion(vm, test, stand)
    log("{0} Закончен тест: '{1[name]}' на стенде '{2[name]}' {0}\n".format("-" * 20, test, stand), 1)
    test_report['result'] = "Завершен [OK]"
    test_report['stop'] = time.time()
    return test_report


def fix_len(string: str, length: int):
    if length < 0: length = 0
    if length >= len(string): return string
    div = (length - 5) // 2
    mod = (length - 5) % 2
    result_string = string[:div+mod]
    result_string += "[...]"
    result_string += string[-div:]
    return result_string


# форматированый вывод в txt
def report_write(test_report, report_file):
    steps = test_report['step']
    reports = test_report['report']
    report_file.write("[Стенд] {0[stand_name]} '{0[stand_fullname]}'\n".format(test_report))
    report_file.write("    [Тест] {0[test_name]} '{0[test_fullname]}'\n".format(test_report))
    report_file.write("        [Подготовка]...{:.>100}\n".format(fix_len(test_report['prepare'], 100)))
    report_file.write("        {:.^115}\n".format("[Команды]"))
    for step in steps:
        report_file.write("        {:.<115}\n".format(fix_len(step, 115)))
        report_file.write("        {:.>115}\n".format(fix_len(steps[step], 115)))
    report_file.write("        {:.^115}\n".format("[Файлы отчетов]"))
    for report in reports:
        report_file.write("        {:.<115}\n".format(fix_len(report, 115)))
        report_file.write("        {:.>115}\n".format(fix_len(reports[report], 115)))
    report_file.write("        [Состояние]....{:.>100}\n\n".format(test_report['result']))


# формирование allure отчета о запуске теста на тачке
def allure_report_write(test_report, report_dir, session):
    # дич с конвертацией времени
    test_report['start'] = int(test_report['start']) * 1000
    test_report['stop'] = int(test_report['stop']) * 1000
    start = str(test_report['start'])
    start = start[:10] + start[11:14]
    stop = str(test_report['stop'])
    stop = stop[:10] + stop[11:14]

    # ядро отчета
    report = {
        'name': "{0[test_name]}".format(test_report),
        'status': "passed" if test_report['result'] == "Завершен [OK]" else "failed",
              'statusDetails': {'message': test_report['result'], 'trace': ''},
              'steps': [
                  {'name': "Подготовка стенда",
                   'status': "passed" if test_report['prepare'] == "Подготовлен [OK]" else "failed",
                   'statusDetails': {'message': test_report['prepare'], 'trace': ''}
                   }
              ],
        'start': start,
        'stop': stop,
        'fullName': "{0[test_name]}_({0[test_fullname]}){0[stand_name]}_({0[stand_fullname]})".format(test_report),
        'labels': [
            {'name': "epic", 'value': "VMWare отчет"},
            {'name': "feature", 'value': session},
            {'name': "story", 'value': "{0[stand_name]}".format(test_report)},
            {'name': "framework", 'value': "testRunner"},
            {'name': "package", 'value': "{0[test_name]}_{0[stand_name]}".format(test_report)}
        ]
    }

    # детализация по степам
    for step in test_report['step']:
        step_data = {
            'name': step,
            'status': "passed" if test_report['step'][step] == "[OK]" else "failed",
            'statusDetails': {'message': test_report['step'][step], 'trace': ''},
        }
        report['steps'].append(step_data)
    report_data = str(json.dumps(report))

    with open("{}\\{}{}-result.json".format(report_dir, report['name'], time.strftime("%H%M%S")),
              mode='w', encoding='utf-8') as file:
        file.write(report_data)


if __name__ == '__main__':

    # разбираем параметры строки
    parser = ArgumentParser()
    parser.add_argument('-i', '--ini_path', type=str, default=os.path.normpath(os.path.dirname(__file__)),
                        help="Путь к файлам stands.ini и config.ini")
    parser.add_argument('-t', '--test', nargs='+', default=[],
                        help="Имя теста или нескольких тестов через пробел")
    parser.add_argument('-s', '--stand', nargs='+', default=[],
                        help="Имя стенда или нескольких  стендов через пробел")
    parser.add_argument('-tg', '--test_group', nargs='+', default=[],
                        help="запуск группы (или нескольких групп) тестов")
    parser.add_argument('-sg', '--stand_group', nargs='+', default=[],
                        help="запуск тестов на группе (или нескольких группах) стендов")
    parser.add_argument('-r', '--report', type=str, default=os.getcwd(),
                        help="путь сохраниения логов и отчетов")
    parser.add_argument('-a', '--allure_bin', type=str, default=None,
                        help="--путь папке с allure.bat")
    parser.add_argument('-b', '--build', type=str, default="unknown_build",
                        help="версия дистра")
    parser.add_argument('-c', '--comment', type=str, default="",
                        help="комментарий")
    parser.add_argument('-l', '--log_level', type=int, default=2,
                        help="детализация логов. см logger.py")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="дублировать лог на экран")
    args = parser.parse_args()

    # создаем папку для отчетов
    report = "{}\\{}".format(args.report, args.build)

    for path in (report + "\\allure_input", report + "\\allure_output"):
        if not os.path.isdir(path):
            try:
                os.makedirs(path)
            except PermissionError:
                print("Нет прав записи лога в папку '{}'. Попробуйте задать другую папку."
                      "см атрибуты '-r' (testRunner.py -h)".format(report))
                exit(100)
    log = Log(report + "\\" + "testRunner.log", args.log_level, args.verbose).write


    # проверяем наличие файлов тестов и стендов
    ini = dict(
        stands=args.ini_path.rstrip("\\") + "\\stands.ini",
        tests=args.ini_path.rstrip("\\") + "\\tests.ini"
    )
    if not os.path.isfile(ini['stands']):
        log("Не найден файл stands.ini по пути".format(ini['stands']), 0)
        exit(101)
    if not os.path.isfile(ini['tests']):
        log("Не найден файл tests.ini по пути".format(ini['tests']), 0)
        exit(102)

    # читаем ini
    stands = ini_to_dict(ini['stands'])
    tests = ini_to_dict(ini['tests'])

    # проверяем корректность задания тестов и групп тестов
    test_list = []
    for group in args.test_group:
        if group in tests['groups']:
            args.test += tests['groups'][group]
        else:
            log("В файле тестов не найдена группа {}".format(group), 0)
    for test in args.test:
        if test in tests:
            test_list.append(test)
        else:
            log("В файле тестов не найден тест {}".format(test), 0)

    if "groups" in test_list:
        log("Среди идентификаторов теста указан 'groups'. 'groups' - зарезервированное слово ", 0)
        exit(200)

    # проверяем корректность задания стендов и групп стендов
    stand_list = []
    for group in args.stand_group:
        if group in stands['groups']:
            args.stand += stands['groups'][group]
        else:
            log("В файле стендов не найдена группа {}".format(group), 0)
    for stand in args.stand:
        if stand in stands:
            stand_list.append(stand)
        else:
            log("В файле стендов не найден стенд {}".format(stand), 0)

    # поехали
    log("Запуск тестов: {} на машинах {}".format(test_list, stand_list), 1)
    log("Коментарий: {}".format(args.comment), 1)
    rep_file = "{}\\report_{}.log".format(report, time.strftime("%H%M%S"))
    session = "Запуск на {} в {}".format(args.build, time.ctime())
    with open(rep_file, "a") as report_file:
        report_file.write("Отчет по тестам: {} на машинах {}\n".format(test_list, stand_list))
        report_file.write("Коментарий: {}\n\n".format(args.comment))

    for stand in stand_list:
        for test in test_list:
            # запуск и получение отчета по тесту
            try:
                test_report = run(tests[test], stands[stand])
            except KeyError:
                log("Не правильно указан параметр стенда {} или {}".format(test, stand), 0)
                continue
            with open(rep_file, "a") as report_file:
                report_write(test_report, report_file)
            if args.allure_bin:
                allure_report_write(test_report, report + "\\allure_input", session)

    # собираем отчеты и аттачи для allure
    if args.allure_bin:
        for ext in ("xml", "json", "attach", "txt", "png"):
            search_pattern = "{}\\**\\*.{}".format(report, ext)
            for file in glob(search_pattern, recursive=True):
                if "allure_input\\" in file:
                    continue
                copy(file, report + "\\allure_input")

        # генерим отчет
        log("Генерируем allure-отчет", 1)
        os.system("{0} generate --clean {1}\\allure_input -o {1}\\allure_output".format(args.allure_bin, report))
        log("Генерация  allure-отчета завершена : {0}\\{1}\\index.html".format(report, args.build), 1)


