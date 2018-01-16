tests = {
    #  'mytest': {                                 -идентификатор теста
    #
    #                                    Обязательные параметры:
    #
    #     'name': "W10641",                       - имя теста. отображается в логах и отчетах
    #
    #                                    Необязательные параметры:
    #
    #     'fullname'                              - подробное имя стенда. используется влогах и отчетах
    #     'delay': 120                            - максимальное время на выполнения КАЖДОГО шага теста
    #                                             если не задан, то используется 'delay' стенда
    #     'step':["ping.exe putin.com",          - спиок строковых команд, которые будут выполняться на стенде
    #               "ping.exe localhost"],        если програме нужны параметры, указываются в строке через пробел
    #     'logs': [".\\silent_install.log"]       - список файлов, которые будем забирать с машины после выполнения
    #                                             всех команд. Содержимое этих файлов будет отображаться в логах,
    #                                             при уровне лога Debug.
    #     'reports': [".\\logs",
    #                 "C:\\temp\\tesxt.rep"]      - список файлов, которые будем забирать с машины после выполнения
    #                                             всех команд.
    #     'delete': "mySnapshot",                 - после завершения всех команд и выключения стенда, будет удален
    #                                             снапшот с указанным именем
    #     'take': "newSnapshot"             - после завершения всех команд и выключения стенда, будет создан
    #                                             снапшот с указанным именем
    # },
    #
    #                                     Примечания:
    #
    #     - В параметрах logs, reports и step ' .\ ' будет заменяться на 'quest_dir' стенда, если он указан
    #
    #     -Структура файла представляет из себя литерал словаря. При необходимости вы можете видоизменить структуру
    #     файла, приведя её в удобный для вас вид. Имя первичного словаря ДОЛЖНО быть 'tests'.
    #     Ключи могут быть любыми, но использоваться будут только те, что описаны выше.
    #
    #      - Внимательно заполняйте строковые литералы! Спецсимволы должны экранироваться, либо перед литералом должен
    #     стоять символ 'r'.
    #     Примеры как можно:
    #         "C:\\Windows\\system32"
    #         r"C:\Windows\system32"
    #         "My name is \"Ivan\""
    #         'My name is "Ivan"'


    'ping': {
        'name': "demo_test",
        'step': ["ping.exe 127.0.0.1"],
    },

    'badping': {
        'name': "demo_test_2",
        'step': ["ping.exe putin.com",
                  "ping.exe localhost"],
    },
    'install': {
        'name': "Тихая установка",
        'fullname': "Тихая установка, лицензия без TLS",
        'step': ["C:\\python\\scripts\\pytest.exe .\\tests\\silent_install.py "
                  "--distr=.\\pki_client_installer.exe --license=.\\lic\\full.itcslic "
                  "--alluredir .\\report"],
        'report': [".\\report"],
        'delete': "ready_os",
        'take': "ready_os"
    },
    'update': {
        'name': "Тихая установка",
        'fullname': "Тихая установка, лицензия без TLS",
        'step': ["C:\\python\\scripts\\pytest.exe .\\tests\\silent_install.py "
                  "--distr=.\\pki_client_installer.exe --license=.\\lic\\full.itcslic "
                  "--alluredir .\\report"],
        'report': [".\\report"],
    },

    'cert_unit': {
        'name': "Запрос на сертификат",
        'delay': 420,
        'fullname': "NUnit test: создание запроса на сертификат",
        'step': ['.\\NUnit\\nunit3-console.exe'
                  ' .\\NUnit\\client.tests.dll --where class=~"CertificateUnitCreateRequest"'
                  ' --work=.\\NUnit'],
        'report': [".\\NUnit\\TestResult.xml", ".\\Documents\\Test1CU.p10",
                    ".\\Documents\\Test2CU.p10", ".\\Documents\\Test3CU.p10",
                    ".\\Documents\\Test4CU.p10"],
    },



    # nix tests



    'simple': {
        'name': "simple_test"
    }
}
groups = {
    # 'group1': ['stand1','stand2'],     идентификатор группы: [список тестов]
    'debug': ['ping', 'badping'],
    'all': tests.keys()
}