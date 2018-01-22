r"""vmrun
Утилита vmun.exe (далее просто vmrun) поставляется вместе с ПО виртуализации от VMWare, такими как Workstation PRO, vSphere и т.д.
vmrun позволяет совершать широкий список действий с виртуальными машинами, используя интерфейс командной строки (такие как клонирование, управление питанием, запуск программ в гостевой ОС и т.д.)
Полный список команд, используемых последней версией vmrun можно увидеть в официальной документации﻿
или с помощью встроенной справки утилиты.
vmware.py
Модуль vmware.py содержащий единственный класс (VWmare) представляет из себя примитивный  "интерфейс" для vmrun, облегчающий управление Виртуальными машинами в среде Python

При создании объекта касса VMware коммады
Текущая версия поддерживает:
    OS = Win
    VMware = Workstation
"""
from time import sleep
from subprocess import Popen, PIPE, TimeoutExpired


class VMware:
    """Класс для работы с вирутальными машинами VMware через vmrun.exe.

    Текущая версия поддерживает:
        OS = Win
        VMware = Workstation

    Константы:
        При необходимости могут быть измеdrнен для всего класса после импорта,
        либо явно указываться при инициальизации объекта класса в соответстующих аргументх

        DEFAULT_VMRUN_PATH: значение по умолчанию для атрибута pathToVmrun
        DEFAULT_MAX_WAIT_TIME: значение по умолчанию для атрибута maxWaitTime
        DEFAULT_MAX_CLONE_TIME : значение для атрибутка maxCloneTime
        DEFAULT_MAX_ATTEMPT : количество повторов выполнения команды в случае ошибки 'Unable conect to hsot'
    Атрибуты:
        pathToVmrun: путь  vmrun.exe
        pathToVMX: путь к конфиг файлу машины
        maxWaitTime: сколько даем VMware времени на выполнение операции (сек)
            используется в большинстве методов. Если вызванный методом процесс vmrun.exe не заверщается
            за указанное время, он выбрасывает TimeoutExpired
        maxWaitClone: сколько даем VMware времени на выполнение операции клонирования (сек)
            используется в сlone(...). Вызванный методом процесс vmrun.exe не заверщается
            за указанное время, он выбрасывает TimeoutExpired
        gu: Логин пользователя гостевой ОС. Обязателен для некоторых методов
        gu: Пас пользователя гостевой ОС. Используется только совместно с gu
        hostType: список основных параметров запуска. Зависит от типа VMware.
            временно захардкожено для Workstation
        out: словарь определюяющий путь вывода std потоков методов, использующих Popen

    API:
        Большинство методов возвращают 0 (int) при успешном завершении или сообщение об ошибке (str) при неудачном

        ---Питание---
        сheckStart(self): проверяет состояние машины. Запущена = 0; Остановлена = 1; Не удалось проверить = errMsg
        start(self): запускает машину. Внимание! Если машина уже запущена вернет 0 (так же как и при успешном запуске)
        stop(self): выключает машину

        ---Операции с гостевой ОС---
        run(self, args, maxWaitTime=0, interactive=True, activeWindow=True):
            Запускает в гостевой ОС программу (args[0]) с параметрами (args[1:]).
            Подробнее в описании метода.
        copyTo(self, source, target): копируем в гостевую ос папку или файл source/target - путь источника/назначения
        copyFrom(self,source, target): копируем из гостевой ос

        ---Операции со снапшотами---
        take(self, snapshotName): создать снапшот
        revert(self, snapshotName): откатится к снапшоту
        delete(self, snapshotName): удалить снапшот
        snapshot(self, action, snapshotName): альтернативный вызов методов выше. Подробнее в описании метода
        erase(self): Удаляет машину с диска.
        ---Клонирование---
        clone(self, pathToClone, cloneName=None, snapshot=None, linked=True):
            Клонирует машину в текущем состоянии. Подробнее в описании метода
    """
    DEFAULT_VMRUN_PATH = "C:\\Program Files (x86)\\VMware\\VMware Workstation\\vmrun.exe"
    DEFAULT_MAX_WAIT_TIME = 600
    DEFAULT_CLONE_TIME = 1800
    DEFAULT_MAX_ATTEMPT = 1

    def __init__(self, pathToVMX, gu="", gp="", maxWaitTime=DEFAULT_MAX_WAIT_TIME,
                 maxCloneTime=DEFAULT_CLONE_TIME, maxAttepmt=DEFAULT_MAX_ATTEMPT, pathToVmrun=DEFAULT_VMRUN_PATH):
        """
        Атрибуты смотреть в описании класса.
        """
        self.pathToVmrun = pathToVmrun
        self.pathToVMX = pathToVMX
        self.maxWaitTime = maxWaitTime
        self.maxCloneTime = maxCloneTime
        self.maxAttempt = maxAttepmt
        self.gu = gu
        self.gp = gp
        self.hostType = [self.pathToVmrun, "-T", "ws"]
        self.auth = ["-gu", self.gu, "-gp", self.gp]
        self.out = {"stdin": PIPE, "stdout": PIPE, "stderr": PIPE}

    def checkStart(self):
        """
        Метод для определения состояния VM.
        Возвращает
            выключена: 1 (int)
            включена: 0 (int)
            Fail: Сообщение от vmrun (str)
        """
        process = Popen([self.pathToVmrun, "list"],
                        stdin=PIPE, stdout=PIPE, stderr=PIPE)
        process.wait(self.maxWaitTime)
        # декодим вывод vmrun
        # если получили список запущеных VM ищем в нем нашу
        # иначе отдаем вывод
        vmrunOut = process.communicate()[0].decode('utf-8')
        if process.returncode == 0:
            return 0 if (self.pathToVMX in vmrunOut) else 1
        else:
            return vmrunOut.rstrip('\r \n')

    def start(self):
        """
        Запускает машину.
        Возвращает
            удалось запусить: 0 (int)
            уже была запущена: 0 (int)
            Fail: Сообщение от vmrun (str)
        """
        return self._vmCommand("start")

    def stop(self):
        """
        Останавливает машину.
        Возвращает
            удалось остановить: 0 (int)
            уже остановлена: Сообщение от vmrun (str)
            Fail: Сообщение от vmrun (str)
        """
        return self._vmCommand("stop", params=["soft"])

    def run(self, args, maxWaitTime: int=0, interactive: bool=True, activeWindow: bool=True):
        """
        Запускает программу в гостевой ос.
        Для корректной работы метода должны быть заданы атрибуты self.gu и self.gp
        Аргументы
            args: Полный путь к программе в гостевой ос и аргументы ее запуска.
                Тип аргумента:  список/кортеж строк или одна строка
                Если задается списком, args[0] = Путь к программе, args[1:] аргументы программы
                Если задаяется строкой, args = "Путь_к_программе аргумент1 ... аргументN"
            maxWaitTime: Время, которое ожидаем завершения процесса (int),
                если waitTime = 0 - процесс запускается в фоне
            interactive: запуска графической оболочки вызываемой программы в гостевой ОС (bool)
            activeWindow: при значении True устанавливает фокус на вызванноую программу (bool)
        Возвращает
            успех: 0 (int)
            Fail: Сообщение от vmrun (str)

        Примеры использования.

        Запуск в интерактивном режиме в фоновом процесс:
            MyVM.run("D:\\myProgram.exe")
        Запуск скрипта в консольном режиме c ожидание заверщения минуту:
            MyVM.run("C:\\myscript.bat",60,False,)
        Запуск программы с параметрами в интерактивном режиме c ожиданием завершения час:
            MyVM.run("notepad.exe newfile.txt", 3600)

        """
        # тут заданы опции обработки процесса vmrun-ом по умолчанию
        # если аргументы заданы строками, сплитим их в список
        if type(args) is str:
            args = args.split(" ")
        options = []
        if interactive:
            options.append("-interactive")
        if activeWindow:
            options.append("-activeWindow")
        if not maxWaitTime:
            options.append("-noWait")
        return self._vmCommand("runProgramInGuest", auth=self.auth, params=(options + args), maxWaitTime=maxWaitTime)

    def copyTo(self, source, target):
        """
        Копирует файлы на виртуальную машину с хостовой
        !!! При налиции прав доступа заменяет файлы на гсстевой машине
        Аргументы
            source: Путь к файлу или папке на хосте
            target: Путь к файлу или папке на госте
        Возвращает
            успех: 0 (int)
            Fail: Сообщение от vmrun (str)
        Примеры
        MyVM.copyTo("C:\\ctrlc_dir", "D:\\ctrlv_dir")
        MyVM.copyTo("C:\\Windows\\System32\\mstsc.exe", "D:\\mstsc.exe")

        """
        return self._vmCommand("CopyFileFromHostToGuest", auth=self.auth, params=[source, target])

    def copyFrom(self, source, target):
        """
        Копирует файлы с гостевой машины на хостову.
        !!! При налиции прав доступа заменяет файлы на хостовой
        Остальное идентичено copyTo(...) см выше
        """
        return self._vmCommand("CopyFileFromGuestToHost", auth=self.auth, params=[source, target])

    def snapshot(self, action, snapshotName):
        """
        Управление снашшотами. Вызывает один из методов работы со снапшотами, описанные ниже
        Аргументы
            action: одно из доступных действий (str)
                't' или 'take' - сделать снашот
                'r' или 'revent' - откатиться к снапшоту
                'd' или 'delete' - удалить снапшот
            snapshotNamе: имя снапшота к которому применятеся действие
        Возвращает
            успех: 0 (int)
            недопустимое действие: сообщение (str)
            Fail: Сообщение от vmrun (str)
        """
        actions = {"take": self.take, "t": self.take,
                   "revert": self.revert, "r": self.revert,
                   "delete": self.delete, "d": self.delete}
        if action in actions:
            return actions[action](snapshotName)
        else:
            return " '{}' - неизвестная команда для работы со снапшотом".format(action)

    def take(self, snapshotName):
        """
        Сделать снапшот.
        """
        return self._vmCommand("snapshot", params=[snapshotName])

    def revert(self, snapshotName):
        """
        Откатится к снапшоту.
        """
        return self._vmCommand("revertToSnapshot", params=[snapshotName])

    def delete(self, snapshotName):
        """
        Удалить снапшот
        """
        return self._vmCommand("deleteSnapshot", params=[snapshotName])

    def clone(self, pathToClone, cloneName=None, snapshot=None, linked=True):
        """
        Клонирует текущую VM.
        !!! Использует параметр self.maxCloneTime. Если клонирование не выполнено за это время
            возвращает строку сообщения
        Аргументы
            pathToClone: путь к .vmx клона. Несуществующие папки в пути будут созданы (str)
            cloneName: название создаваемой машины (если не задано будет присвоено автоматическое) (str)
            snapshot: имя снапшота клонируемой машины, из которого будем лепить клон (str)
            linked: делать связный или полный клон. По умолчанию связный (bool)
        Возвращает
            успех: 0 (int)
            Fail: Сообщение от vmrun (str)

        """
        # добавляем обязательные параметры
        params = [pathToClone]
        params.append("linked") if linked else params.append("full")
        # добавляем необязательные параметры, если указаны
        if not (snapshot is None):
            params.append("-snapshot=" + snapshot)
        if not (cloneName is None):
            params.append("-cloneName=" + cloneName)
        return self._vmCommand("clone", params=params, maxWaitTime=self.maxCloneTime)

    # def reg(self):
    #     """
    #     Добавляет машину в список в  GUI Workstation
    #     Возвращает
    #         успех: 0 (int)
    #         Fail: Сообщение от vmrun (str)
    #
    #     """
    #     process = self._vmCommand("register")
    #     return self._exitCode(process)
    #
    # def ureg(self):
    #     """
    #     Убирает машину из списка в GUI Workstation
    #     Возвращает
    #         успех: 0 (int)
    #         Fail: Сообщение от vmrun (str)
    #
    #     """
    #     process = self._vmCommand("unregister")
    #     return self._exitCode(process)

    def erase(self):
        """
        Удаление машины с диска
        Возвращает
            успех: 0 (int)
            Fail: Сообщение от vmrun (str)
        """
        return self._vmCommand("deleteVM")

    def _vmCommand(self, command, auth=[], params=[], maxWaitTime=None):
        if maxWaitTime is None:
            maxWaitTime=self.maxWaitTime

        for attempt in range(0, self.maxAttempt):
            # формирует строку запуска vmrun.exe
            # получаем процесс
            process = Popen([*self.hostType, *auth, command, self.pathToVMX, *params],
                            **self.out)
            # если maxWaittime == 0 даем несколько секунд на запуск процесса в фоне
            # при успешном запуске exit_code будет 0 (используется в self.run, для запуска фоновых процессов)
            maxWaitTime = 10 if maxWaitTime == 0 else maxWaitTime
            # ждем завершения процесса, смотрим код заверщения и сообщение vmrun.exe
            try:
                exit_code = process.wait(maxWaitTime)
                message = process.communicate()[0].decode('utf-8').rstrip('\r \n')
            except TimeoutExpired:
                return "Не хватило {} сек, на выполннение операции с машиной ".format(str(maxWaitTime))
            if exit_code == 0:
                return exit_code
            # в случае ошибки соединения с VMWare повоторяем в цикле
            elif "Unable to connect to host" in message:
                    sleep(10)
                    continue
            # в остальных случаях возвращаем вывод vm.run
            else:
                return message
        return "Не удалось выполнить команду vmrun {} с {} попытки".format(command, self.maxAttempt)


