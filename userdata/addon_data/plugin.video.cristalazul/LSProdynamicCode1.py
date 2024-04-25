# -*- coding: utf-8 -*-
#$pyFunction
from kodi_six import xbmc,xbmcgui,xbmcaddon,xbmcvfs
def GetLSProData(page_data,Cookie_Jar,m):
    dialog = xbmcgui.Dialog()
    d = dialog.input('[COLOR aqua]Cristal Azul[/COLOR] [COLOR red]Buscador Youtube[/COLOR] [COLOR white]Sin Api[/COLOR]', type=xbmcgui.INPUT_ALPHANUM).replace(" ", "+").replace("á", "a").replace("é", "e").replace("í", "i").replace("á", "a").replace("ú", "u")
    return d
