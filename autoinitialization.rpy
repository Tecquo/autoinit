init -1500 python:
    import time
    import builtins
    import os

    class autoInitialization_autoinit:
        """
        Класс для автоматической инициализации файлов мода.
        Инициализирует аудио, шрифты и изображения (включая спрайты).
        """

        def __init__(self, modID, modPostfix="", write_into_file=False, initialize_images=True, initialize_sprites=True, initialize_audio=True, initialize_fonts=True):
            """
            Параметры класса:

                :param modID: str
                    название корневой папки Вашего мода
                :param modPostfix: str, optional, :default value: ""
                    постфикс, добавляемый к именам объявлённых ресурсов.
                :param write_into_file: boolean, optional, :default value: False
                    если True — вместо немедленной инициализации записывает ресурсы мода
                    в файл `autoinit_assets.rpy`; затем потребуется перезагрузка БЛ.
                    если False — ресурсы мода инициализируются сразу при загрузке БЛ.
                :param initialize_images: boolean, optional, :default value: True
                    включить обработку обычных изображений из `images/` (кроме `images/sprites`).
                :param initialize_sprites: boolean, optional, :default value: True
                    включить обработку спрайтов из `images/sprites` и их комбинаций.
                :param initialize_audio: boolean, optional, :default value: True
                    включить обработку аудио-файлов (.wav, .mp2, .mp3, .ogg, .opus).
                :param initialize_fonts: boolean, optional, :default value: True
                    включить обработку шрифтов (.ttf, .otf).
            """

            self.modID = modID
            self.modPostfix = ("_" + modPostfix if modPostfix else "")
            self.modFiles = []
            self.write_into_file = write_into_file
            self.initialize_images = initialize_images
            self.initialize_sprites = initialize_sprites
            self.initialize_audio = initialize_audio
            self.initialize_fonts = initialize_fonts
            # кэширование файлов и директорий RenPy, чтобы не вызывать renpy.list_files() и renpy.loader.listdirfiles() каждый раз
            # да, как оказалось, это сильно сказывается на производительности
            try:
                self.renpyFiles = list(renpy.list_files())
                self.renpyDirs = list(renpy.loader.listdirfiles(False))
            except Exception as e:
                self.renpyFiles = []
                self.renpyDirs = []
                self.error("Error caching RenPy files/dirs: {}".format(e))
            self.modPath = self.process_mod_path()
            self.modImagesPath = self.process_images_path()
            self.modDist = self.process_distances()

            self.check_class_name()
            self.check_duplicate()

            self.logger_create()

            self.initialize()

        def check_duplicate(self):
            # Проверка на дублирование: класс с таким именем уже объявлен или объект уже создан
            try:
                registry = getattr(renpy.store, "_autoinit_registry", None)
                if registry is None:
                    registry = {"class_name_to_class_obj": {}, "initialized_class_names": set()}
                    setattr(renpy.store, "_autoinit_registry", registry)

                class_name = self.__class__.__name__

                if class_name in registry.get("initialized_class_names", set()):
                    self.error("Instance of '{}' already exists. Rename the class (change postfix).".format(class_name))

                existing_cls = registry.get("class_name_to_class_obj", {}).get(class_name)
                if existing_cls is not None and existing_cls is not self.__class__:
                    self.error("Duplicate class name '{}' detected from another file. Rename the class postfix to include your mod folder name.".format(class_name))

                registry["class_name_to_class_obj"][class_name] = self.__class__
            except Exception as e:
                self.error("Duplicate-name guard failed: {}".format(e))

        def record_instance(self):
            # Помечаем успешное создание объекта класса, чтобы запретить повторные инстансы того же имени
            try:
                registry = getattr(renpy.store, "_autoinit_registry", None)
                if registry is not None:
                    registry_class_name = getattr(renpy.store, "_autoinit_registry['initialized_class_names']", None)
                    if not registry_class_name:
                        registry.setdefault("initialized_class_names", set()).add(self.__class__.__name__)
                    else:
                        registry.add(self.__class__.__name__)
                    
            except Exception as e:
                self.error("Failed to record instance creation: {}".format(e))

        def check_class_name(self):
            if not(self.__class__.__name__.endswith(self.modID) or self.__class__.__name__.startswith(self.modID)):
                self.error("The auto-initialization class name ({}) must be unique and contain the mod root folder name".format(self.__class__.__name__))

        def error(self, txt):
            renpy.error(self.modID.upper() + " AUTOINITIALIZATION ERROR: {}".format(txt))

        #region Функции-аналоги с отловом ошибок и с заменой "\\" на "/" для RenPy
        def _join_path(self, *args):
            return os.path.join(*args).replace(os.sep, "/")

        def _isfile(self, path):
            try:
                return os.path.isfile(path)
            except Exception as e:
                self.error("Error checking if file '{}': {}".format(path, e))
                return False

        def _listdir(self, path):
            try:
                return os.listdir(path)
            except Exception as e:
                self.error("Error listing directory '{}': {}".format(path, e))
                return []

        def _walk(self, path):
            try:
                for root, dirs, files in os.walk(path):
                    yield root, dirs, files
            except Exception as e:
                self.error("Error walking directory '{}': {}".format(path, e))
                return

        def _relpath(self, path, base):
            try:
                return os.path.relpath(path, base).replace(os.sep, "/")
            except Exception as e:
                self.error("Error getting relative path from '{}' to '{}': {}".format(base, path, e))
                return path
        #endregion Функции-аналоги с отловом ошибок и с заменой "\\" на "/" для RenPy

        def logger_create(self):
            if renpy.windows:
                try:
                    with builtins.open(self.modID + "Logger.txt", "w+") as logger:
                        logger.write(self.modID.upper() + " AUTOINITIALIZATION\n")
                except Exception as e:
                    self.error("Error while trying to create logger: {}".format(e))
        
        def logger_write(self, txt):
            if renpy.windows:
                try:
                    with builtins.open(self.modID + "Logger.txt", "a+") as logger:
                        logger.write(txt + "\n")
                except Exception as e:
                    self.error("Error while trying to write into logger: {}".format(e))

        def timer(func):
            def wrapper(self, *args, **kwargs):
                start = time.time()
                result = func(self, *args, **kwargs)
                end = time.time()
                self.logger_write("{} took {:.2f} seconds".format(func.__name__, end - start))
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

        def process_mod_path(self):
            """
            Находит путь до папки мода.

            :return: str
            """
            for dir, fn in self.renpyDirs:
                if self.modID in fn:
                    return os.path.join(dir, self.modID).replace(os.sep, "/")
                else:
                    for root, dirs, files in os.walk(dir):
                        if self.modID in dirs:
                            return os.path.join(root, self.modID).replace(os.sep, "/")

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
                full_path = os.path.join(path, name).replace(os.sep, "/")
                if os.path.isdir(full_path):
                    for root, dirs, files in os.walk(full_path):
                        for file in files:
                            relative_path = os.path.relpath(os.path.join(root, file), self.renpyDirs[0][0]).replace(os.sep, "/")
                            image_size = renpy.image_size(relative_path)
                            folder_names[name] = (name if name != "normal" else "", image_size)
                            break
                        else:
                            continue
                        break
            return folder_names

        @timer
        def process_audio(self):
            """
            Обрабатывает аудио. Поддерживает расширения (".wav", ".mp2", ".mp3", ".ogg", ".opus")

            Имя аудио для вызова будет в формате:
            [имя][_постфикс]

            Пример:
            newmusic_mymod
            """
            audio_extensions = {".wav", ".mp2", ".mp3", ".ogg", ".opus"}
            for file in self.renpyFiles:
                if self.modID in file:
                    file_name = os.path.splitext(os.path.basename(file))[0] + self.modPostfix
                    if file.endswith(tuple(audio_extensions)):
                        self.count_file("sound", file_name, file)
        @timer
        def process_fonts(self):
            """
            Обрабатывает шрифты. Поддерживает расширения (".ttf", ".otf")

            Имя шрифта для вызова будет в формате:
            [имя][_постфикс]

            Пример:
            newfont_mymod
            """
            font_extensions = {".ttf", ".otf"}
            for file in renpy.list_files():
                if self.modID in file:
                    file_name = os.path.splitext(os.path.basename(file))[0] + self.modPostfix
                    if file.endswith(tuple(font_extensions)):
                        self.count_file("font", file_name, file)

        @timer
        def process_image(self, file_path, image_name):
            rel_path = self._relpath(file_path, self.renpyDirs[0][0])
            self.count_file("image", image_name, rel_path)

        @timer
        def process_images(self):
            """
            Обрабатывает изображения. Поддерживает изображения в подпапках.

            Имя изображения для вызова будет в формате:
            [папка] [подпапка] [имя][_постфикс]

            Пример:
            bg background_mymod
            bg subfolder background_mymod
            bg subfolder subsubfolder background_mymod
            """
            for folder in self._listdir(self.modImagesPath):
                path = os.path.join(self.modImagesPath, folder).replace(os.sep, "/")
                if self._isfile(path):
                    image_name = os.path.splitext(os.path.basename(path))[0] + self.modPostfix
                    self.process_image(path, image_name)
                else:
                    if folder != 'sprites':
                        for root, dirs, files in self._walk(path):
                            for file in files:

                                image_path = os.path.join(root, file).replace("\\", "/")
                                image_name = os.path.splitext(file)[0]
                                relative_path = os.path.relpath(root, self.modImagesPath) # Получаем полный путь к изображению и удаляем путь к корню
                                folder_structure = relative_path.split(os.sep) # Разделяем путь на компоненты и объединяем их в имя изображения
                                folder_index = folder_structure.index(folder)
                                folder_structure = folder_structure[folder_index:] + [image_name] # Оставляем только элементы после папки folder
                                image_name_with_folder = ' '.join(folder_structure).replace('/', '').replace('\\', '') + self.modPostfix
                                image_path = os.path.relpath(image_path, self.renpyDirs[0][0]).replace(os.sep, "/")
                                self.count_file("image", image_name_with_folder, image_path)

        def process_sprite_clothes_emo_acc(self, emo_l, clothes_l, acc_l, who, file_body, dist):
            """Обрабатывает спрайт [тело] [эмоция] [одежда] [аксессуар]"""
            for emotion in emo_l:
                for clothes in clothes_l:
                    for acc in acc_l:
                        file_name = who + self.modPostfix + ' ' + emotion[0] + ' ' + clothes[0] + ' ' + acc[0] + ' ' + self.modDist[dist][0]
                        file = """
                            ConditionSwitch(
                                "persistent.sprite_time=='sunset'",
                                im.MatrixColor(im.Composite({0},
                                                            (0, 0), {1},
                                                            (0, 0), "{2}",
                                                            (0, 0), "{3}",
                                                            (0, 0), "{4}"),
                                                im.matrix.tint(0.94, 0.82, 1.0)
                                            ),
                                "persistent.sprite_time=='night'",
                                im.MatrixColor(im.Composite({0},
                                                            (0, 0), {1},
                                                            (0, 0), "{2}",
                                                            (0, 0), "{3}",
                                                            (0, 0), "{4}"),
                                                im.matrix.tint(0.63, 0.78, 0.82)
                                            ),
                                True,
                                im.Composite({0},
                                            (0, 0), {1},
                                            (0, 0), "{2}",
                                            (0, 0), "{3}",
                                            (0, 0), "{4}")
                            )
                        """.format(self.modDist[dist][1], file_body, clothes[1], emotion[1], acc[1])
                        self.count_file("sprite", file_name, file)

            self.process_sprite_clothes_emo(emo_l, clothes_l, who, file_body, dist)
            self.process_sprite_clothes_acc(clothes_l, acc_l, who, file_body, dist)
            self.process_sprite_emo_acc(emo_l, acc_l,  who, file_body, dist)
            self.process_sprite_emo(emo_l, who, file_body, dist)
            self.process_sprite_acc(acc_l, who, file_body, dist)
            self.process_sprite_clothes(clothes_l, who, file_body, dist)

        def process_sprite_clothes_emo(self, emo_l, clothes_l, who, file_body, dist):
            """Обрабатывает спрайт [тело] [эмоция] [одежда]"""
            for clothes in clothes_l:
                for emotion in emo_l:
                    file_name = who + self.modPostfix + ' ' + emotion[0] + ' ' + clothes[0] + ' ' + self.modDist[dist][0]
                    file = """
                        ConditionSwitch(
                            "persistent.sprite_time=='sunset'",
                            im.MatrixColor(im.Composite({0},
                                                        (0, 0), {1},
                                                        (0, 0), "{2}",
                                                        (0, 0), "{3}"),
                                            im.matrix.tint(0.94, 0.82, 1.0)
                                        ),
                            "persistent.sprite_time=='night'",
                            im.MatrixColor(im.Composite({0},
                                                        (0, 0), {1},
                                                        (0, 0), "{2}",
                                                        (0, 0), "{3}"),
                                            im.matrix.tint(0.63, 0.78, 0.82)
                                        ),
                            True,
                            im.Composite({0},
                                        (0, 0), {1},
                                        (0, 0), "{2}",
                                        (0, 0), "{3}")
                        )
                    """.format(self.modDist[dist][1], file_body, clothes[1], emotion[1])
                    self.count_file("sprite", file_name, file)
            self.process_sprite_clothes(clothes_l, who, file_body, dist)
            self.process_sprite_emo(emo_l, who, file_body, dist)

        def process_sprite_clothes_acc(self, clothes_l, acc_l, who, file_body, dist):
            """Обрабатывает спрайт [тело] [одежда] [аксессуар]"""
            for clothes in clothes_l:
                for acc in acc_l:
                    file_name = who + self.modPostfix + ' ' + clothes[0] + ' ' + acc[0] + ' ' + self.modDist[dist][0]
                    file = """
                        ConditionSwitch(
                            "persistent.sprite_time=='sunset'",
                            im.MatrixColor(im.Composite({0},
                                                        (0, 0), {1},
                                                        (0, 0), "{2}",
                                                        (0, 0), "{3}"),
                                            im.matrix.tint(0.94, 0.82, 1.0)
                                        ),
                            "persistent.sprite_time=='night'",
                            im.MatrixColor(im.Composite({0},
                                                        (0, 0), {1},
                                                        (0, 0), "{2}",
                                                        (0, 0), "{3}"),
                                            im.matrix.tint(0.63, 0.78, 0.82)
                                        ),
                            True,
                            im.Composite({0},
                                        (0, 0), {1},
                                        (0, 0), "{2}",
                                        (0, 0), "{3}")
                        )
                    """.format(self.modDist[dist][1], file_body, clothes[1], acc[1])
                    self.count_file("sprite", file_name, file)
            self.process_sprite_clothes(clothes_l, who, file_body, dist)
            self.process_sprite_acc(acc_l, who, file_body, dist)

        def process_sprite_emo_acc(self, emo_l, acc_l, who, file_body, dist):
            """Обрабатывает спрайт [тело] [эмоция] [аксессуар]"""
            for emotion in emo_l:
                for acc in acc_l:
                    file_name = who + self.modPostfix + ' ' + emotion[0] + ' ' + acc[0] + ' ' + self.modDist[dist][0]
                    file = """
                        ConditionSwitch(
                            "persistent.sprite_time=='sunset'",
                            im.MatrixColor(im.Composite({0},
                                                        (0, 0), {1},
                                                        (0, 0), "{2}",
                                                        (0, 0), "{3}"),
                                            im.matrix.tint(0.94, 0.82, 1.0)
                                        ),
                            "persistent.sprite_time=='night'",
                            im.MatrixColor(im.Composite({0},
                                                        (0, 0), {1},
                                                        (0, 0), "{2}",
                                                        (0, 0), "{3}"),
                                            im.matrix.tint(0.63, 0.78, 0.82)
                                        ),
                            True,
                            im.Composite({0},
                                        (0, 0), {1},
                                        (0, 0), "{2}",
                                        (0, 0), "{3}")
                        )
                    """.format(self.modDist[dist][1], file_body, emotion[1], acc[1])
                    self.count_file("sprite", file_name, file)
            self.process_sprite_emo(emo_l, who, file_body, dist)
            self.process_sprite_acc(acc_l, who, file_body, dist)

        def process_sprite_clothes(self, clothes_l, who, file_body, dist):
            """Обрабатывает спрайт [тело] [одежда]"""
            for clothes in clothes_l:
                file_name = who + self.modPostfix + ' ' + clothes[0] + ' ' + self.modDist[dist][0]
                file = """
                    ConditionSwitch(
                        "persistent.sprite_time=='sunset'",
                        im.MatrixColor(im.Composite({0},
                                                    (0, 0), {1},
                                                    (0, 0), "{2}"),
                                        im.matrix.tint(0.94, 0.82, 1.0)
                                    ),
                        "persistent.sprite_time=='night'",
                        im.MatrixColor(im.Composite({0},
                                                    (0, 0), {1},
                                                    (0, 0), "{2}"),
                                        im.matrix.tint(0.63, 0.78, 0.82)
                                    ),
                        True,
                        im.Composite({0},
                                    (0, 0), {1},
                                    (0, 0), "{2}")
                    )
                """.format(self.modDist[dist][1], file_body, clothes[1])
                self.count_file("sprite", file_name, file)

        def process_sprite_acc(self, acc_l, who, file_body, dist):
            """Обрабатывает спрайт [тело] [аксессуар]"""
            for acc in acc_l:
                file_name = who + self.modPostfix + ' ' + acc[0] + ' ' + self.modDist[dist][0]
                file = """
                    ConditionSwitch(
                        "persistent.sprite_time=='sunset'",
                        im.MatrixColor(im.Composite({0},
                                                    (0, 0), {1},
                                                    (0, 0), "{2}"),
                                        im.matrix.tint(0.94, 0.82, 1.0)
                                    ),
                        "persistent.sprite_time=='night'",
                        im.MatrixColor(im.Composite({0},
                                                    (0, 0), {1},
                                                    (0, 0), "{2}"),
                                        im.matrix.tint(0.63, 0.78, 0.82)
                                    ),
                        True,
                        im.Composite({0},
                                    (0, 0), {1},
                                    (0, 0), "{2}")
                    )
                """.format(self.modDist[dist][1], file_body, acc[1])
                self.count_file("sprite", file_name, file)

        def process_sprite_emo(self, emo_l, who, file_body, dist):
            """Обрабатывает спрайт [тело] [эмоция]"""
            for emotion in emo_l:
                file_name = who + self.modPostfix + ' ' + emotion[0] + ' ' + self.modDist[dist][0]
                file = """
                    ConditionSwitch(
                        "persistent.sprite_time=='sunset'",
                        im.MatrixColor(im.Composite({0},
                                                    (0, 0), {1},
                                                    (0, 0), "{2}"),
                                        im.matrix.tint(0.94, 0.82, 1.0)
                                    ),
                        "persistent.sprite_time=='night'",
                        im.MatrixColor(im.Composite({0},
                                                    (0, 0), {1},
                                                    (0, 0), "{2}"),
                                        im.matrix.tint(0.63, 0.78, 0.82)
                                    ),
                        True,
                        im.Composite({0},
                                    (0, 0), {1},
                                    (0, 0), "{2}")
                    )
                """.format(self.modDist[dist][1], file_body, emotion[1])
                self.count_file("sprite", file_name, file)

        def process_sprite(self, who, file_body, dist):
            """Обрабатывает спрайт [тело]"""
            file_name = "{}{} {}".format(who, self.modPostfix, self.modDist[dist][0])
            file = """
                ConditionSwitch(
                    "persistent.sprite_time=='sunset'",
                    im.MatrixColor(im.Composite({0},
                                                (0, 0), {1}),
                                    im.matrix.tint(0.94, 0.82, 1.0)
                                ),
                    "persistent.sprite_time=='night'",
                    im.MatrixColor(im.Composite({0},
                                                (0, 0), {1}),
                                    im.matrix.tint(0.63, 0.78, 0.82)
                                ),
                    True,
                    im.Composite({0},
                                (0, 0), {1})
                )
            """.format(self.modDist[dist][1], file_body)
            self.count_file("sprite", file_name, file)

        @timer
        def process_sprites(self):
            """Обрабатывает спрайты и все их комбинации

            Имя спрайта для вызова будет в формате:
            [название спрайта][_постфикс]
            [название спрайта][_постфикс] [эмоция]
            [название спрайта][_постфикс] [эмоция] [одежда]
            [название спрайта][_постфикс] [эмоция] [одежда] [аксессуар]
            и любые другие комбинации.

            Пример:
            dv_mymod
            dv_mymod normal
            dv_mymod normal sport
            dv_mymod normal sport jewelry
            """
            for folder in self._listdir(self.modImagesPath):
                if folder == "sprites":
                    path = os.path.join(self.modImagesPath, folder).replace(os.sep, "/")
                    for dist in os.listdir(path):
                        who_path = os.path.join(path, dist).replace(os.sep, "/")
                        for who in os.listdir(who_path):
                            who_path_num = os.path.join(who_path, who).replace(os.sep, "/")
                            for numb in os.listdir(who_path_num):
                                sprite_folders = os.listdir(os.path.join(who_path_num, numb).replace(os.sep, "/"))

                                for i in sprite_folders:
                                    if 'body' in i:
                                        file_body = "\"" + str(os.path.relpath(os.path.join(who_path_num, numb, i).replace(os.sep, "/"), self.renpyDirs[0][0]).replace(os.sep, "/")) + "\""
                                        break
                                else:
                                    file_body = 'im.Alpha("images/misc/soviet_games.png", 0.0)' # Заглушка, если не нашли тело

                                clothes_l = []
                                emo_l = []
                                acc_l = []

                                if 'clothes' in sprite_folders:
                                    clothes_l = [(os.path.splitext(clothes)[0].split('_'+numb+"_", 1)[-1], os.path.relpath(os.path.join(who_path_num, numb, 'clothes', clothes).replace(os.sep, "/"), self.renpyDirs[0][0]).replace(os.sep, "/")) for clothes in os.listdir(os.path.join(who_path_num, numb, 'clothes'))]

                                if 'emo' in sprite_folders:
                                    emo_l = [(os.path.splitext(emo)[0].split('_'+numb+"_", 1)[-1], os.path.relpath(os.path.join(who_path_num, numb, 'emo', emo).replace(os.sep, "/"), self.renpyDirs[0][0]).replace(os.sep, "/")) for emo in os.listdir(os.path.join(who_path_num, numb, 'emo'))]

                                if 'acc' in sprite_folders:
                                    acc_l = [(os.path.splitext(acc)[0].split('_'+numb+"_", 1)[-1], os.path.relpath(os.path.join(who_path_num, numb, 'acc', acc).replace(os.sep, "/"), self.renpyDirs[0][0]).replace(os.sep, "/")) for acc in os.listdir(os.path.join(who_path_num, numb, 'acc'))]

                                self.process_sprite(who, file_body, dist)
                                if clothes_l and emo_l and acc_l:
                                    self.process_sprite_clothes_emo_acc(emo_l, clothes_l, acc_l, who, file_body, dist)
                                elif clothes_l and emo_l:
                                    self.process_sprite_clothes_emo(emo_l, clothes_l, who, file_body, dist)
                                elif clothes_l and acc_l:
                                    self.process_sprite_clothes_acc(clothes_l, acc_l, who, file_body, dist)
                                elif emo_l and acc_l:
                                    self.process_sprite_emo_acc(emo_l, acc_l,  who, file_body, dist)
                                elif clothes_l:
                                    self.process_sprite_clothes(clothes_l, who, file_body, dist)
                                elif acc_l:
                                    self.process_sprite_acc(acc_l, who, file_body, dist)
                                elif emo_l:
                                    self.process_sprite_emo(emo_l, who, file_body, dist)

        def process_files(self):
            """
            Обрабатывает файлы мода.

            Если write_into_file равно True, вместо инициализации записывает ресурсы мода в отдельный файл. Для дальнейшей инициализации ресурсов мода из файла необходимо перезагрузить БЛ.
            """
            if self.write_into_file:
                with builtins.open(self.modPath + "/autoinit_assets.rpy", "w") as log_file:
                    log_file.write("init -1499:\n    ")
                    for type, file_name, file in self.modFiles:
                        if type == "sound":
                            log_file.write("$ %s = \"%s\"\n    " % (file_name, file))
                        elif type == "font":
                            log_file.write("$ %s = \"%s\"\n    " % (file_name, file))
                        elif type == "image":
                            log_file.write("image %s = \"%s\"\n    " % (file_name, file))
                        if type == "sprite":
                            log_file.write("image %s = %s\n    " % (file_name, file.strip()))
            else:
                for type, file_name, file in self.modFiles:
                    if type == "sound":
                        setattr(store, file_name, file)
                    elif type == "font":
                        setattr(store, file_name, file)
                    elif type == "image":
                        renpy.image(file_name, file)
                    if type == "sprite":
                        renpy.image(file_name, eval(file))
        @timer
        def initialize(self):
            """
            Инициализация ресурсов мода и запись создания объекта класса
            """
            if self.initialize_audio:
                self.process_audio()
            if self.initialize_fonts:
                self.process_fonts()
            if self.initialize_images:
                self.process_images()
            if self.initialize_sprites:
                self.process_sprites()
            self.process_files()
            self.record_instance()