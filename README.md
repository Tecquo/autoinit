# AutoInitialization for Ren'Py Mods

## Overview

This module provides a class `autoInitialization_autoinit` for automatic initialization of mod resources (audio, images, sprites) in Ren'Py-based games. It scans your mod's directory, processes resources, and registers them for use in the game, or writes them to a file for later initialization.

## Usage

1. **Place your mod in a subfolder of the game directory.**
   - The folder name should be unique and used as the `modID` parameter.
2. **Organize your resources as follows:**

```renpy
<modID>/
├── images/
│   ├── bg/ (опционально)
│   ├── sprites/
│   │   └── <distance>/
│   │       └── <character>/
│   │           └── <variant>/
│   │               ├── body.png (опционально)
│   │               ├── clothes/ (опционально)
│   │               ├── emo/ (опционально)
│   │               └── acc/ (опционально)
│   └── ...
└── ...
```

- **images/**: папка с изображениями
- **bg**: пример папки, в которой будут фоны для мода (опционально, изображения могут лежать внутри `images`, без дополнительной подпапки)
- **sprites/**: папка со спрайтами, спрайты организованы по дистанции `distance` (например  `normal`, `far`, `close`, или своё название), затем по имени спрайта персонажа `character` (например `dv`, `sl`), затем по вариации спрайта цифрой (например поза `1`), затем по файлам спрайта: файл `body.png` с телом (опционально), папка с одеждой `clothes` (опционально), папка с эмоциями `emo` (опционально), папка с аксессуарами `acc` (опционально).
- аудиофайлы объявляются по всей папке мода, для них не нужно (но желательно для организации) создавать отдельную папку.

### Включение автоинициализации

```python
init python:
    autoInitialization_autoinit("my_mod")
```

- `modID`: The name of your mod's root folder.
- `modPostfix`: (Optional) Postfix for resource names.
- `write_into_file`: (Optional, default False) If True, writes resource definitions to a file instead of initializing immediately.

## Использование инициализированных файлов

### Изображения

`имя_постфикс`
`папка имя_постфикс`
`папка подпапка имя_постфикс`

#### Пример

`example`
`folder example`
`folder subfolder example`

### Спрайты

`название спрайта_постфикс`
`название спрайта_постфикс эмоция`
`название спрайта_постфикс эмоция одежда`
`название спрайта_постфикс эмоция одежда аксессуар`

#### Пример

`dv`
`dv normal`
`dv normal sport`
`dv normal sport jewelry`

### Аудио

`имя_постфикс`

#### Пример

`grenade`

## Важно

При запуске автоинициализации мод:

- создаёт текстовый файл `<modID>Logger.txt` с расчётом времени инициализации файлов
- в случае критической ошибки вызовет `Traceback` (сообщение об ошибке) для быстрого нахождения причины ошибки
