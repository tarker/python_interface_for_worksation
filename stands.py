stands = {
    #                                Пример описания стенда:
    #
    # 'W10641': {                                 -идентификатор машины
    #
    #                                    Обязательные параметры:
    #
    #     'path': r"C:\AT\W10641\W10641.vmx",     - путь к .vmx
    #     'path': r"C:\AT\W10641\W10641.vmx",     - путь к .vmx
    #     'name': "W10641",                       - имя машины, отображается в логах
    #                                              не должен содержать символы  / \ : * ? <> |
    #     'user': "tester",                       - юзер под которым логинимся
    #     'pass': "0",                            - его пароль
    #
    #                                    Необязательные параметры:
    #
    #     'delay': 120                            - максимальное время на выполнения операций с vm
    #     'parent': r"D:\Windows7 x32 RUS.vmx",   - если этот параметр есть , стенд будет создаваться путем
    #                                             клонирования с машины указаной в его значении
    #     'snapshot': "clean",                    - если создается клонироанием то клонируется с этого снапшота, иначе
    #                                             просто переводим машину из 'path' в этот снпашот
    #     'fullname': "Windows 10 x64 clean OS",  - полное имя стенда, отображается в логах
    #     'state': 0,                             - состояние машины на момент старта теста (1 -выкл, 0 - вкл)
    #     'guest_dir': 'C:\\Users\\tester',       - путь куда льем тесты и свежие сборки и другие нужные файлы,
    #                                             на этот путь будет заменяться' .\ ' в командах тестов и путях отчета
    #     'host_dir': "d:\\toGuest\\",            - путь откуда льем тесты и свежие сборки и другие нужные файлы
    # },
    #
    #                                     Примечания:
    #
    #     -Структура файла представляет из себя литерал словаря. При необходимости вы можете видоизменить структуру файла,
    #     приведя её в удобный для вас вид. Имя первичного словаря ДОЛЖНО быть 'stands'. Ключи могут быть любыми, но
    #     использоваться будут только те, что описаны выше.
    #     - Внимательно заполняйте строковые литералы! Спецсимволы должны экранироваться, либо перед литералом должен
    #     стоять символ 'r'.
    #     Примеры как можно:
    #         "C:\\Windows\\system32"
    #         r"C:\Windows\system32"
    #         "My name is \"Ivan\""
    #         'My name is "Ivan"'

    # чистые стенды для тестов инсталяции
    'w7_32_clean_os': {
        'path': r"C:\AT\W732_1\W732_1.vmx",
        'name': "Win 7 32 clean_os",
        'user': "tester",
        'pass': "0",
        'snapshot': "clean_os",
        'fullname': "Windows 7 x32 clean OS",
        'host_dir': "D:\\projects\\toGuest",
        'guest_dir': "C:\\users\\tester\\win7_32"
        },

    'w7_64_clean_os': {
        'user': "tester",
        'pass': "0",
        'path': r"C:\AT\W764_1\W764_1.vmx",
        'name': "Win 7 64 clean_os",
        'snapshot': "clean_os",
        'fullname': "Windows 7 x64 clean OS",
        'host_dir': "D:\\projects\\toGuest",
        'guest_dir': "C:\\users\\tester\\win7_64"
        },

    'w8_86_clean_os': {
        'user': "tester",
        'pass': "0",
        'snapshot': "clean_os",
        'path': r"C:\AT\W886_1\W886_1.vmx",
        'name': "Win 8 86 clean_os",
        'fullname': "Windows 8 x86 RUS",
        'host_dir': "D:\\projects\\toGuest",
        'guest_dir': "C:\\users\\tester\\win8_86"
        },

    'w8.1_64_clean_os': {
        'user': "tester_pc",
        'pass': "0",
        'path': r"C:\AT\W8.164_1\W8.164_1.vmx",
        'name': "Win 8.1 64",
        'snapshot': "clean_os",
        'fullname': "Windows 8.1 x64 RUS",
        'host_dir': "d:\\projects\\toGuest",
        'guest_dir': "C:\\users\\tester_pc\\w8_1_64"
        },

    'w2012r2_clean_os': {
        'user': "Администратор",
        'pass': "0",
        'path': r"C:\AT\W2012R2_1\W2012R2_1.vmx",
        'name': "Win 2012 R2",
        'snapshot': "clean_os",
        'fullname': "Windows Server 2012 R2 clean_os",
        'host_dir': "d:\\projects\\toGuest",
        'guest_dir': "C:\\Users\\Администратор\\w2012r2"
        },

    'w10_64_clean_os': {
        'user': "tester",
        'pass': "0",
        'path': r"C:\AT\W10641\W10641.vmx",
        'name': "Win 10 64",
        'snapshot': "clean_os",
        'fullname': "Windows 10 x 64",
        'host_dir': "d:\\projects\\toGuest",
        'guest_dir': "C:\\users\\tester\\Win_10_64"
    },
    'w7_32_ready_os': {
        'path': r"C:\AT\W732_1\W732_1.vmx",
        'name': "Win 7 32",
        'user': "tester",
        'pass': "0",
        'snapshot': "ready_os",
        'fullname': "Windows 7 x32",
        'guest_dir': "C:\\users\\tester\\win7_32"
        },

    'w7_64_ready_os': {
        'user': "tester",
        'pass': "0",
        'path': r"C:\AT\W764_1\W764_1.vmx",
        'name': "Win 7 64 ",
        'snapshot': "ready_os",
        'fullname': "Windows 7 x64",
        'guest_dir': "C:\\users\\tester\\win7_64"
        },

    'w8_86_ready_os': {
        'user': "tester",
        'pass': "0",
        'snapshot': "ready_os",
        'path': r"C:\AT\W886_1\W886_1.vmx",
        'name': "Win 8 86",
        'fullname': "Windows 8 x86 RUS",
        'guest_dir': "C:\\users\\tester\\win8_86"
        },

    'w8.1_64_ready_os': {
        'user': "tester_pc",
        'pass': "0",
        'path': r"C:\AT\W8.164_1\W8.164_1.vmx",
        'name': "Win 8.1 64",
        'snapshot': "ready_os",
        'fullname': "Windows 8.1 x64 RUS",
        'guest_dir': "C:\\users\\tester_pc\\w8_1_64"
        },

    'w2012r2_ready_os': {
        'user': "Администратор",
        'pass': "0",
        'path': r"C:\AT\W2012R2_1\W2012R2_1.vmx",
        'name': "Win 2012 R2",
        'snapshot': "ready_os",
        'fullname': "Windows Server 2012 R2",
        'guest_dir': "C:\\Users\\Администратор\\w2012r2"
        },

    'w10_64_ready_os': {
        'user': "tester",
        'pass': "0",
        'path': r"C:\AT\W10641\W10641.vmx",
        'name': "Win 10 64",
        'snapshot': "ready_os",
        'fullname': "Windows 10 x 64",
        'guest_dir': "C:\\users\\tester\\Win_10_64"
    },

    #nix clean
    'Deb9_3_64': {
        'path': r"C:\AT\Deb9_3_64\Deb9_3_64.vmx",
        'name': "Debian 9.3 x64 ",
        'user': "tester",
        'pass': "11111111",
        'snapshot': "clean_os",
        'fullname': "Debian 9.3 x64 ",
        'host_dir': "D:\\projects\\toNIXGuest",
        'guest_dir': "/home/tester"
    },
}



groups = {
    # 'W10641': ['stand1','stand2'],            - список стендов : [список стендов]
    

    'clean_os': ['w10_64_clean_os',  'w7_64_clean_os', 'w8.1_64_clean_os', 'w8_86_clean_os', 'w7_32_clean_os', 'w2012r2_clean_os'],
    'update': ['w7_32_update', 'w7_64_update', 'w8_86_update', 'w8.1_64_update', 'w2012r2_update', 'w10_64_update'],
    'ready_os': ['w7_32_ready_os', 'w7_64_ready_os', 'w8_86_ready_os', 'w8.1_64_ready_os', 'w2012r2_ready_os', 'w10_64_ready_os'],
    'demo_group': ['w7_32_clean_os', 'w10_64_clean_os']

}


# print(stands.keys())
