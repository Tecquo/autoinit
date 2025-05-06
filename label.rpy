init:
    $ mods["autoinit_label"] = "Авто инит"
    $ autoinitialization_mymod = autoInitialization_mymod("mymod", write_into_file=True)

label autoinit_label:

    $ persistent.sprite_time = "day"

    "Авто инит"

    play music init_music

    "Звук"

    show bg

    "БГ без папки"

    show bg insidebg

    "БГ в папке"

    show bg subfolder insidesubbg
    "Вложенный БГ"

    show mt normal intro jewelry at fleft
    show fiz normal far at cleft
    show el normal pioneer
    show dv cry swim close at cright

    "Спрайты"

    hide fiz
    hide el
    hide dv
    hide mt

    camera:
        subpixel True perspective True
    show mt normal as mt:
        subpixel True zpos -477.0 pos (-0.33, -279)
    show mt normal jewelry as mt2:
        subpixel True zpos -477.0 pos (-0.21, -279)
    show mt normal intro as mt3:
        subpixel True zpos -477.0 pos (-0.09, -279)
    show mt normal intro jewelry as mt4:
        subpixel True zpos -477.0 pos (0.03, -279) 

    show mt as mt5:
        subpixel True zpos -477.0 pos (0.32, -279) 
    show mt jewelry as mt6:
        subpixel True zpos -477.0 pos (0.67, -279) 
    show mt intro as mt7:
        subpixel True zpos -477.0 pos (0.33, 486) 
    show mt intro jewelry as mt8:
        subpixel True zpos -477.0 pos (0.68, 486) 
    "Комбинации спрайтов"

    return
