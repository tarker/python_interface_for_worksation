import time


class Log:
    def __init__(self, log_file=None, log_level=2, verbose=False, msg_types=None, log_levels=None):
        self.log_file = log_file
        self.log_level = log_level
        self.verbose = verbose
        if msg_types is None:
            self.msg_types = {0: "ERROR",
                              1: "ALERT",
                              2: "DEBUG"}
        else:
            self.msg_types = msg_types
        if log_levels is None:
            self.log_levels = {-1: {},
                               0: {0},
                               1: {0, 1},
                               2: set(self.msg_types.keys())}
        else:
            self.log_levels = log_levels

    def write(self, msg, msg_type=2):
        path = self.log_file
        if msg_type in self.log_levels[self.log_level]:
            string = "[{}] {}: {}".format(time.strftime("%H:%M:%S"), self.msg_types[msg_type], msg)
        else:
            return 0
        if self.verbose:
            print(string)
        if path is None:
            return 0
        else:
            try:
                with open(path, 'a') as file:
                    file.write(string + '\n')
            except FileNotFoundError:
                return "Не возможно создать файл по этому пути {}".format(path)
            except PermissionError:
                return "Не достаточно прав для записи в {}".format(path)
            except Exception:
                return "Неопознаная ошибка записи в файл {}".format(path)
        return 0

