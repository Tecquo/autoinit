init python early: # TODO добавить синтаксический сахар, а то я ёбнусь это разбирать через несколько месяцев.
    import time, builtins

    class autoInitialization_autoinit:
        """
        Класс для автоматической инициализации файлов мода.
        Инициализирует аудио и изображения (включая спрайты).

        Параметры класса:

            :param modID: str
                название корневой папки Вашего мода
            :param modPostfix: str, optional, :default value: ""
                опциональный параметр для добавления постфикса к названиям объявлённых ресурсов.
            :param write_into_file: boolean, optional, :default value: False
                если равно True, вместо инициализации записывает ресурсы мода в отдельный файл. Для дальнейшей инициализации ресурсов мода из файла необходимо перезагрузить БЛ.
                если равно False, ресурсы мода инициализируются в момент загрузки БЛ.
        """

        def __init__(self, modID, modPostfix="", write_into_file=False):
            """
            Параметры класса:

                :param modID: str
                    название корневой папки Вашего мода
                :param modPostfix: str, optional, :default value: ""
                    опциональный параметр для добавления постфикса к названиям объявлённых ресурсов.
                :param write_into_file: boolean, optional, :default value: False
                    если равно True, вместо инициализации записывает ресурсы мода в отдельный файл. Для дальнейшей инициализации ресурсов мода из файла необходимо перезагрузить БЛ.
                    если равно False, ресурсы мода инициализируются в момент загрузки БЛ.
            """
            self.modID = modID
            self.modPostfix = ("_" + modPostfix if modPostfix else "")
            self.modFiles = []
            self.write_into_file = write_into_file
            self.modPaths = self.process_mod_paths()
            self.modPath = self.process_mod_path()
            self.modImagesPath = self.process_images_path()
            #self.modDist = self.process_distances()

            with builtins.open(self.modID + "Logger.txt", "w+") as logger:
                logger.write(self.modID.upper() + " " + "AUTOINITIALIZATION" + "\n")

            if not(self.__class__.__name__.endswith(self.modID) or self.__class__.__name__.startswith(self.modID)):
                renpy.error("Название класса автоматической инициализации файлов должно быть уникальным и содержать название корневой папки мода")

            self.initialize()

        def _join_path(self, *args):
            return "/".join(args)

        def _walk(self, dir):
            for dirpath, dirnames, filenames in os.walk(dir):
                yield dirpath.replace(os.sep, "/"), dirnames, filenames

        def _relpath(self, path, start=None):
            return os.path.relpath(path, start).replace(os.sep, "/")
        
        def logger_write(self, txt):
            with builtins.open(self.modID + "Logger.txt", "a+") as logger:
                logger.write(txt + "\n")

        def timer(func):
            def wrapper(self, *args, **kwargs):
                #self.logger_write("\n{} начал работу\n".format(func.__name__)) #TODO реализовать в JSON формате
                start = time.time()
                result = func(self, *args, **kwargs)
                end = time.time()
                self.logger_write("{} took {}s".format(func.__name__, round(end - start, 4)))
                #print("{0} took {1:.2f} seconds".format(func.__name__, end - start))
                return result
            return wrapper

        def count_file(self, type, file_name, file):
            """
            Добавляет название файла, сам файл и его тип в лист modFiles.

            :param type: str
                тип файла
            :param file_name: srt
                имя файла
            :param file: str
                путь до файла
            """
            self.modFiles.append([type, file_name, file])

        def process_mod_paths(self):
            """
            Находит все пути с названием папки мода, на замену renpy.list_files() для оптимизации

            :return: str
            """
            mod_paths = []
            for i in renpy.list_files():
                if self.modID + "/" in i or "/".join(["mods", self.modID + "/"]) in i:
                    mod_paths.append(i)
            if len(mod_paths) == 0:
                renpy.error("AUTOINIT: Проверьте наличие мода в папке game (вне вложенных папок)")
            return mod_paths

        def process_mod_path(self):
            """
            Находит путь до папки мода.

            :return: str
            """

            return "/".join(self.modPaths[0].split("/")[:self.modPaths[0].split("/").index(self.modID)+1])

            #renpy.error("/".join(self.modPaths[0].split("/")[:self.modPaths[0].split("/").index(self.modID)+1]))

            # for dir, fn in renpy.loader.listdirfiles(False):
            #     if self.modID in fn:
            #         return self._join_path(dir, self.modID)
            #     else:
            #         for root, dirs, files in self._walk(dir):
            #             if self.modID in dirs:
            #                 return self._join_path(root, self.modID)

        def process_images_path(self):
            """
            Находит путь до папки изображений мода.

            :return: str
            """
            return self._join_path(self.modPath, 'images')

        def process_distances(self):
            """
            Находит путь до папки sprites, строит названия дистанций по именам внутри (для normal дистанции имя будет "", как в самом БЛ), ищет изображение в каждой из папок с дистанциями, получает размер изображения и добавляет в словарь

            :return: dict

            Пример возврата функции:
            {
                "far": {"far", (675, 1080)},
                "normal": {"", (900, 1080)},
                "close": {"close", (1125, 1080)},
            }
            """
            folder_names = {}
            path = os.path.join(self.modImagesPath, "sprites")
            for name in os.listdir(path):
                full_path = self._join_path(path, name)
                if os.path.isdir(full_path):
                    for root, dirs, files in self._walk(full_path):
                        for file in files:
                            relative_path = self._relpath(self._join_path(root, file), renpy.loader.listdirfiles(False)[0][0])
                            image_size = renpy.image_size(relative_path)
                            folder_names[name] = (name if name != "normal" else "", image_size)
                            break
                        else:
                            continue
                        break
            return folder_names
        
        @timer
        def process_audio(self): # TODO реализовать вложенную систему для названий треков
            """
            Обрабатывает аудио. Поддерживает расширения (".wav", ".mp2", ".mp3", ".ogg", ".opus")

            Имя аудио для вызова будет в формате:
            [имя][_постфикс]

            Пример:
            newmusic
            """
            audio_extensions = {".wav", ".mp2", ".mp3", ".ogg", ".opus"}
            for file_path in self.modPaths:
                if file_path.endswith(tuple(audio_extensions)):
                    file_name = file_path[file_path.rfind("/")+1:file_path.find(".")]
                    self.count_file("sound", file_name, file_path)

        @timer
        def process_images(self): # TODO 
            for file_path in self.modPaths:
                if file_path.endswith((".png", ".jpg", ".webp")):
                    if self.modImagesPath + "/" + "sprites" in file_path:
                        pass
                    else:
                        if self.modImagesPath + "/bg/" in file_path or self.modImagesPath + "/cg/" in file_path:
                            file_name = " ".join(file_path[file_path.find(self.modImagesPath)+len(self.modImagesPath)+1:file_path.find(".")].split("/"))
                            self.count_file("image", file_name, file_path)
                        else:
                            file_name = "_".join(file_path[file_path.find(self.modImagesPath)+len(self.modImagesPath)+1:file_path.find(".")].split("/"))
                            self.count_file("image", file_name, file_path)
        @timer
        def process_sprites_general(self):
            sizes = []
            body_list = []
            emo_lists = {}
            clothes_lists = {}
            accs_lists = {}

            # body
            for file_path in self.modPaths:
                if "body." in file_path and self.modImagesPath + "/" + "sprites" in file_path:
                    file_path_split = file_path.split("/")
                    body_list.append(file_path_split)
                    file_composite = "Composite({}, (0, 0), \"{}\")".format(renpy.image_size(file_path), file_path)
                    file_name = " ".join([file_path_split[-3] + self.modPostfix, (file_path_split[-4] if file_path_split[-4] != "normal" else "")])
                    self.count_file("sprite", file_name, file_composite)

            # emo
            for body in body_list:
                emo_list = []
                emo_path = list(body)[:-1] + ["emo"]
                for file_path in self.modPaths:
                    if "/".join(emo_path) in file_path:
                        emo_list.append(file_path)
                emo_lists["/".join(body)] = emo_list
            for body_path in emo_lists:
                for emo in emo_lists[body_path]:
                    emo_path_split = emo.split("/")
                    file_composite = "Composite({}, (0, 0), \"{}\", (0, 0), \"{}\")".format(renpy.image_size(body_path), body_path, emo)
                    file_name = " ".join([emo_path_split[-4] + self.modPostfix, emo_path_split[-1].split(".")[0].split("_")[-1], (emo_path_split[-5] if emo_path_split[-5] != "normal" else "")])
                    self.count_file("sprite", file_name, file_composite)

            # cloth
            for body in body_list:
                clothes_list = []
                cloth_path = list(body)[:-1] + ["clothes"]
                for file_path in self.modPaths:
                    if "/".join(cloth_path) in file_path:
                        clothes_list.append(file_path)
                clothes_lists["/".join(body)] = clothes_list
            for body_path in clothes_lists:
                for cloth in clothes_lists[body_path]:
                    cloth_path_split = cloth.split("/")
                    file_composite = "Composite({}, (0, 0), \"{}\", (0, 0), \"{}\")".format(renpy.image_size(body_path), body_path, cloth)
                    file_name = " ".join([cloth_path_split[-4] + self.modPostfix, cloth_path_split[-1].split(".")[0].split("_")[-1], (cloth_path_split[-5] if cloth_path_split[-5] != "normal" else "")])
                    self.count_file("sprite", file_name, file_composite)

            # acc
            for body in body_list:
                accs_list = []
                acc_path = list(body)[:-1] + ["acc"]
                for file_path in self.modPaths:
                    if "/".join(acc_path) in file_path:
                        accs_list.append(file_path)
                accs_lists["/".join(body)] = accs_list
            for body_path in accs_lists:
                for acc in accs_lists[body_path]:
                    acc_path_split = acc.split("/")
                    file_composite = "Composite({}, (0, 0), \"{}\", (0, 0), \"{}\")".format(renpy.image_size(body_path), body_path, acc)
                    file_name = " ".join([acc_path_split[-4] + self.modPostfix, acc_path_split[-1].split(".")[0].split("_")[-1], (acc_path_split[-5] if acc_path_split[-5] != "normal" else "")])
                    self.count_file("sprite", file_name, file_composite)

            # комбинаторика из emo, cloth, acc
            for body_path in emo_lists:
                for emo in emo_lists[body_path]:
                    emo_path_split = emo.split("/")
                    for cloth in clothes_lists[body_path]:
                        cloth_path_split = cloth.split("/")
                        file_composite = "Composite({}, (0, 0), \"{}\", (0, 0), \"{}\", (0, 0), \"{}\")".format(renpy.image_size(body_path), body_path, emo, cloth)
                        file_name = " ".join([cloth_path_split[-4] + self.modPostfix, emo_path_split[-1].split(".")[0].split("_")[-1], cloth_path_split[-1].split(".")[0].split("_")[-1], (cloth_path_split[-5] if cloth_path_split[-5] != "normal" else "")]) #TODO прибавлять "body" перед эмоцией, эсли припрёт
                        self.count_file("sprite", file_name, file_composite)
                        for acc in accs_lists[body_path]:
                            acc_path_split = acc.split("/")

                            file_composite = "Composite({}, (0, 0), \"{}\", (0, 0), \"{}\", (0, 0), \"{}\")".format(renpy.image_size(body_path), body_path, emo, acc)
                            file_name = " ".join([acc_path_split[-4] + self.modPostfix, emo_path_split[-1].split(".")[0].split("_")[-1], acc_path_split[-1].split(".")[0].split("_")[-1], (acc_path_split[-5] if acc_path_split[-5] != "normal" else "")]) #TODO прибавлять "body" перед эмоцией, эсли припрёт
                            self.count_file("sprite", file_name, file_composite)

                            file_composite = "Composite({}, (0, 0), \"{}\", (0, 0), \"{}\", (0, 0), \"{}\")".format(renpy.image_size(body_path), body_path, cloth, acc)
                            file_name = " ".join([acc_path_split[-4] + self.modPostfix, cloth_path_split[-1].split(".")[0].split("_")[-1], acc_path_split[-1].split(".")[0].split("_")[-1], (acc_path_split[-5] if acc_path_split[-5] != "normal" else "")]) #TODO прибавлять "body" перед эмоцией, эсли припрёт
                            self.count_file("sprite", file_name, file_composite)

                            file_composite = "Composite({}, (0, 0), \"{}\", (0, 0), \"{}\", (0, 0), \"{}\", (0, 0), \"{}\")".format(renpy.image_size(body_path), body_path, emo, cloth, acc)
                            file_name = " ".join([acc_path_split[-4] + self.modPostfix, emo_path_split[-1].split(".")[0].split("_")[-1], cloth_path_split[-1].split(".")[0].split("_")[-1], acc_path_split[-1].split(".")[0].split("_")[-1], (acc_path_split[-5] if acc_path_split[-5] != "normal" else "")]) #TODO прибавлять "body" перед эмоцией, эсли припрёт
                            self.count_file("sprite", file_name, file_composite)
        @timer
        def process_files(self):
            """
            Обрабатывает файлы мода.

            Если write_into_file равно True, вместо инициализации записывает ресурсы мода в отдельный файл. Для дальнейшей инициализации ресурсов мода из файла необходимо перезагрузить БЛ.
            """
            if self.write_into_file:
                with builtins.open("game/" + self.modPath + "/autoinit_assets.txt", "w+") as log_file:
                    log_file.write("init python:\n    ")
                    for type, file_name, file in self.modFiles:
                        if type == "sound":
                            log_file.write("%s = \"%s\"\n    " % (file_name.strip() + self.modPostfix, file))
                        elif type == "image":
                            log_file.write("renpy.image(\"%s\", \"%s\")\n    " % (file_name.strip() + self.modPostfix, file))
                        if type == "sprite":
                            log_file.write("renpy.image(\"%s\", %s)\n    " % (file_name.strip(), file))
            else:
                for type, file_name, file in self.modFiles:
                    if type == "sound":
                        globals()[file_name.strip() + self.modPostfix] = file
                    elif type == "image":
                        renpy.image(file_name.strip() + self.modPostfix, file)
                    if type == "sprite":
                        renpy.image(file_name.strip(), eval(file))
        @timer
        def initialize(self):
            """
            Инициализация ресурсов мода
            """
            self.process_audio()
            self.process_images()
            self.process_sprites_general()
            self.process_files()

