init -1498 python: # TODO добавить синтаксический сахар, а то я ёбнусь это разбирать через несколько месяцев.
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
            self.modFilesName = []
            self.write_into_file = write_into_file
            self.modPaths = self.process_mod_paths()
            self.modPath = self.process_mod_path()
            self.modImagesPath = self.process_images_path()

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

        def make_composite_sprite(self, size, file_body, emotion=None, clothes=None, acc=None): # Добавлять 'body', если голое тело
            conditions = [
                ("persistent.sprite_time", "TintMatrix(Color(hls=(0.94, 0.82, 1.0)))", "'sunset'"),
                ("persistent.sprite_time", "TintMatrix(Color(hls=(0.63, 0.78, 0.82)))", "'night'")
            ]
            composite_format = "Composite({0}, (0, 0), \"{1}\""
            if emotion:
                composite_format += ", (0, 0), \"{2}\""
            if clothes:
                composite_format += ", (0, 0), \"{3}\""
            if acc:
                composite_format += ", (0, 0), \"{4}\""
            composite_format += ")"
            condition_switch = "ConditionSwitch(\n"
            for condition, tint, value in conditions:
                condition_switch += "    \"%s==%s\",\n" % (condition, value)
                condition_switch += "    Transform(%s,\n" % composite_format.format(size, file_body, emotion, clothes, acc)
                condition_switch += "        matrixcolor=%s\n" % tint
                condition_switch += "    ),\n"
            condition_switch += "    True,\n"
            condition_switch += "    %s\n" % composite_format.format(size, file_body, emotion, clothes, acc)
            condition_switch += ")"
            return condition_switch

        def logger_write(self, txt):
            with builtins.open(self.modID + "Logger.txt", "a+") as logger:
                logger.write(txt + "\n")

        def timer(func): #TODO реализовать в JSON формате
            def wrapper(self, *args, **kwargs):
                start = time.time()
                result = func(self, *args, **kwargs)
                end = time.time()
                self.logger_write("{} took {}s".format(func.__name__, round(end - start, 4)))
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
            if file_name not in self.modFilesName:
                self.modFilesName.append(file_name)
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

        def process_images_path(self):
            """
            Находит путь до папки изображений мода.

            :return: str
            """
            return self._join_path(self.modPath, 'images')

        def make_composite_sprite(self, size, file_body, emotion=None, clothes=None, acc=None): # Добавлять 'body', если голое тело
            conditions = [
                ("persistent.sprite_time", "TintMatrix(Color(hls=(0.94, 0.82, 1.0)))", "'sunset'"),
                ("persistent.sprite_time", "TintMatrix(Color(hls=(0.63, 0.78, 0.82)))", "'night'")
            ]
            composite_format = "Composite({0}, (0, 0), \"{1}\""
            if emotion:
                composite_format += ", (0, 0), \"{2}\""
            if clothes:
                composite_format += ", (0, 0), \"{3}\""
            if acc:
                composite_format += ", (0, 0), \"{4}\""
            composite_format += ")"
            condition_switch = "ConditionSwitch(\n"
            for condition, tint, value in conditions:
                condition_switch += "    \"%s==%s\",\n" % (condition, value)
                condition_switch += "    Transform(%s,\n" % composite_format.format(size, file_body, emotion, clothes, acc)
                condition_switch += "        matrixcolor=%s\n" % tint
                condition_switch += "    ),\n"
            condition_switch += "    True,\n"
            condition_switch += "    %s\n" % composite_format.format(size, file_body, emotion, clothes, acc)
            condition_switch += ")"
            return condition_switch

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
            body_dict = {}
            sprite_dict = {}
            for file_path in self.modPaths:
                if file_path.endswith((".png", ".jpg", ".webp")):
                    if self.modImagesPath + "/" + "sprites" in file_path:
                        if "body." in file_path:
                            emo_list = []
                            clothes_list = []
                            acc_list = []

                            file_path_split = file_path.split("/")

                            body_path = list(file_path_split)[:-1]
                            emo_path = body_path + ["emo"]
                            clothes_path = body_path + ["clothes"]
                            acc_path = body_path + ["acc"]
                            
                            body_path = "/".join(body_path) + "/"
                            emo_path = "/".join(emo_path) + "/"
                            clothes_path = "/".join(clothes_path) + "/"
                            acc_path = "/".join(acc_path) + "/"

                            for file_subpath in self.modPaths:
                                if emo_path in file_subpath:
                                    emo_list.append(file_subpath)
                                if clothes_path in file_subpath:
                                    clothes_list.append(file_subpath)
                                if acc_path in file_subpath:
                                    acc_list.append(file_subpath)

                            body_dict[file_path] = {"emo": emo_list, "clothes": clothes_list, "acc": acc_list}
                    else:
                        file_name = " ".join(file_path[file_path.find(self.modImagesPath)+len(self.modImagesPath)+1:file_path.find(".")].split("/"))
                        self.count_file("image", file_name, file_path)
            self.body_dict = body_dict
            self.process_sprites()

        @timer
        def process_sprites(self):
            for body_path in self.body_dict:
                body_path_split = body_path.split("/")

                file_composite = self.make_composite_sprite(renpy.image_size(body_path), body_path)
                file_name = " ".join((body_path_split[-3] + self.modPostfix, (body_path_split[-4] if body_path_split[-4] != "normal" else "")))

                self.count_file("sprite", file_name, file_composite)
                
                for emo in self.body_dict[body_path]["emo"]:

                    emo_path_split = emo.split("/")
                    file_composite = self.make_composite_sprite(renpy.image_size(body_path), body_path, emo)
                    file_name = " ".join([emo_path_split[-4] + self.modPostfix, emo_path_split[-1].split(".")[0].split("_")[-1], (emo_path_split[-5] if emo_path_split[-5] != "normal" else "")])

                    self.count_file("sprite", file_name, file_composite)

                    for cloth in self.body_dict[body_path]["clothes"]:
                        cloth_path_split = cloth.split("/")

                        file_composite = self.make_composite_sprite(renpy.image_size(body_path), body_path, clothes=cloth)
                        file_name = " ".join([cloth_path_split[-4] + self.modPostfix, cloth_path_split[-1].split(".")[0].split("_")[-1], (cloth_path_split[-5] if cloth_path_split[-5] != "normal" else "")])
                        self.count_file("sprite", file_name, file_composite)

                        file_composite = self.make_composite_sprite(renpy.image_size(body_path), body_path, emo, cloth)
                        file_name = " ".join([cloth_path_split[-4] + self.modPostfix, emo_path_split[-1].split(".")[0].split("_")[-1], cloth_path_split[-1].split(".")[0].split("_")[-1], (cloth_path_split[-5] if cloth_path_split[-5] != "normal" else "")])

                        self.count_file("sprite", file_name, file_composite)

                        for acc in self.body_dict[body_path]["acc"]:
                            acc_path_split = acc.split("/")

                            file_composite = self.make_composite_sprite(renpy.image_size(body_path), body_path, acc=acc)
                            file_name = " ".join([acc_path_split[-4] + self.modPostfix, acc_path_split[-1].split(".")[0].split("_")[-1], (acc_path_split[-5] if acc_path_split[-5] != "normal" else "")])

                            self.count_file("sprite", file_name, file_composite)


                            file_composite = self.make_composite_sprite(renpy.image_size(body_path), body_path, emo, acc=acc)
                            file_name = " ".join([acc_path_split[-4] + self.modPostfix, emo_path_split[-1].split(".")[0].split("_")[-1], acc_path_split[-1].split(".")[0].split("_")[-1], (acc_path_split[-5] if acc_path_split[-5] != "normal" else "")])

                            self.count_file("sprite", file_name, file_composite)

                            file_composite = self.make_composite_sprite(renpy.image_size(body_path), body_path, clothes=cloth, acc=acc)
                            file_name = " ".join([acc_path_split[-4] + self.modPostfix, cloth_path_split[-1].split(".")[0].split("_")[-1], acc_path_split[-1].split(".")[0].split("_")[-1], (acc_path_split[-5] if acc_path_split[-5] != "normal" else "")])

                            self.count_file("sprite", file_name, file_composite)

                            file_composite = self.make_composite_sprite(renpy.image_size(body_path), body_path, emo, cloth, acc)
                            file_name = " ".join([acc_path_split[-4] + self.modPostfix, emo_path_split[-1].split(".")[0].split("_")[-1], cloth_path_split[-1].split(".")[0].split("_")[-1], acc_path_split[-1].split(".")[0].split("_")[-1], (cloth_path_split[-5] if cloth_path_split[-5] != "normal" else "")])

                            self.count_file("sprite", file_name, file_composite)


        @timer
        def process_files(self):
            """
            Обрабатывает файлы мода.

            Если write_into_file равно True, вместо инициализации записывает ресурсы мода в отдельный файл. Для дальнейшей инициализации ресурсов мода из файла необходимо перезагрузить БЛ.
            """
            if self.write_into_file:
                with builtins.open("game/" + self.modID + "/" + self.modID + "_assets.txt", "w+") as log_file:
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
            pass
            self.process_audio()
            self.process_images()
            #self.process_sprites()
            #self.process_sprites_general()
            self.process_files()

