init:
    $ mods["autoinit_label"] = "Авто инит"
    $ autoinitialization_autoinit = autoInitialization_autoinit("autoinit", "mymod", write_into_file=True)

label autoinit_label:

    $ persistent.sprite_time = "day"

    "Авто инит"

    play music init_music_mymod

    "Звук"

    "{font=[bios_mymod]}Шрифт{/font}"

    show bg_mymod

    "БГ без папки"

    show bg insidebg_mymod

    "БГ в папке"

    show bg subfolder insidesubbg_mymod
    "Вложенный БГ"

    show mt_mymod normal intro jewelry at fleft
    show fiz_mymod normal far at cleft
    show el_mymod normal pioneer
    show dv_mymod cry swim close at cright

    "Спрайты"

    hide fiz_mymod
    hide el_mymod
    hide dv_mymod
    hide mt_mymod

    camera:
        subpixel True perspective True
    show mt_mymod normal as mt:
        subpixel True zpos -477.0 pos (-0.33, -279)
    show mt_mymod normal jewelry as mt2:
        subpixel True zpos -477.0 pos (-0.21, -279)
    show mt_mymod normal intro as mt3:
        subpixel True zpos -477.0 pos (-0.09, -279)
    show mt_mymod normal intro jewelry as mt4:
        subpixel True zpos -477.0 pos (0.03, -279) 

    show mt_mymod as mt5:
        subpixel True zpos -477.0 pos (0.32, -279) 
    show mt_mymod jewelry as mt6:
        subpixel True zpos -477.0 pos (0.67, -279) 
    show mt_mymod intro as mt7:
        subpixel True zpos -477.0 pos (0.33, 486) 
    show mt_mymod intro jewelry as mt8:
        subpixel True zpos -477.0 pos (0.68, 486) 
    "Комбинации спрайтов"

    return
