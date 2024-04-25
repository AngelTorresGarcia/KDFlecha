import sys
from urllib.parse import urlencode, parse_qsl
import xbmcgui
import xbmcplugin
import resolveurl as urlresolver
from tioanimecontent.anime import *

_URL = sys.argv[0]
_HANDLE = int(sys.argv[1])


def get_url(**kwargs):

    return '{}?{}'.format(_URL, urlencode(kwargs))


def list_categories(categories):

    xbmcplugin.setPluginCategory(_HANDLE, 'Colección de Animes')

    xbmcplugin.setContent(_HANDLE, 'videos')

    for i, category in enumerate(categories):

        list_item = xbmcgui.ListItem(label=category.get('title'))

        list_item.setArt({'thumb': categories[i]['thumb']})

        list_item.setInfo('video', {'title': category.get('title'),
                                    'plot': category.get('synopsis'),
                                    'mediatype': 'video'})

        url = get_url(action='listing', category=category.get('title'))

        is_folder = True

        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)

    window = xbmcgui.Window(10000)

    if window.getProperty('is_search'):
        xbmcplugin.endOfDirectory(_HANDLE)


def get_episodes(category):

    window = xbmcgui.Window(10000)
    page = int(window.getProperty('page'))

    list_titles = get_animes_titles(page)
    list_urls = get_animes_urls(page)
    url_anime = get_url_anime(list_titles, list_urls, category)

    if window.getProperty('is_search'):
        list_animes = search_anime(category)
        url_anime = get_url_anime_search(list_animes, category)

    return get_number_of_episodes(url_anime)


def get_video(episode, category):

    window = xbmcgui.Window(10000)
    page = int(window.getProperty('page'))

    list_titles = get_animes_titles(page)
    list_urls = get_animes_urls(page)
    url_anime = get_url_anime(list_titles, list_urls, category)

    if window.getProperty('is_search'):
        list_animes = search_anime(category)
        url_anime = get_url_anime_search(list_animes, category)

    option = get_video_server_selected(episode, url_anime)

    if not option:
        return
    else:
        if option == 'fembed':
            video = get_url_video(url_anime, episode, 'fembed')
        elif option == 'okru':
            video = get_url_video(url_anime, episode, 'okru')
        elif option == 'yourupload':
            video = get_url_video(url_anime, episode, 'yourupload')
        elif option == 'maru':
            video = get_url_video(url_anime, episode, 'maru')

        return video


def get_url_anime_search(list_animes, category):
    for anime in list_animes:
        if anime.get('title') == category:
            return anime.get('link')


def get_url_anime(list_titles, list_urls, category):
    for i, dict in enumerate(list_titles, 0):
        if dict.get('title') == category:
            return list_urls[i].get('url_anime')


def get_video_server_selected(episode, url_anime):
    servers = get_servers(url_anime, episode)
    show_servers = [
        f'Opción {i+1}: {server.capitalize()}' for i, server in enumerate(servers)]
    option_selected = xbmcgui.Dialog().select(
        'Selecciona un servidor', show_servers)

    if option_selected == -1:
        return []
    else:
        return servers[option_selected]


def list_episodes(category):

    xbmcplugin.setPluginCategory(_HANDLE, category)

    xbmcplugin.setContent(_HANDLE, 'videos')

    episodes = get_episodes(category)
    
    for episode in episodes:

        list_item = xbmcgui.ListItem(label=category)

        list_item.setInfo('video', {'title': category + ' - Episodio ' + str(episode),
                                    'mediatype': 'video'})

        list_item.setProperty('IsPlayable', 'true')

        url = get_url(action='play', episode=str(episode), category=category)

        is_folder = False

        xbmcplugin.addDirectoryItem(_HANDLE, url, list_item, is_folder)

    xbmcplugin.addSortMethod(_HANDLE, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

    xbmcplugin.endOfDirectory(_HANDLE)


def play_video(episode, category):

    path = get_video(episode, category)

    if not path:
        pass
    else:
        play_item = xbmcgui.ListItem(path=path)
        vid_url = play_item.getPath()
        stream_url = resolve_url(vid_url)
        if stream_url:
            play_item.setPath(stream_url)
        xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=play_item)


def resolve_url(url):
    try:
        stream_url = urlresolver.HostedMediaFile(url=url).resolve()
        if not stream_url:
            msg = stream_url.msg
            raise Exception(msg)
        else:
            return stream_url
    except Exception as e:
        msg = str(e)
        xbmcgui.Dialog().notification("URL Resolver Error",
                                      msg, xbmcgui.NOTIFICATION_INFO, 7500)
        return False


def list_animes_by_page(page):
    add_page = page + 1
    data = get_animes(add_page)
    window = xbmcgui.Window(10000)
    window.setProperty('page', str(add_page))
    list_categories(data)
    add_next_page_item(add_page)


def add_search_item():

    search_item = xbmcgui.ListItem(label=f'[COLOR ff694572]Buscar[/COLOR]')
    search_item.setArt(
        {'thumb': 'https://images2.imgbox.com/c1/5f/o66Fp1xK_o.png'})

    url = get_url(action='search')

    xbmcplugin.addDirectoryItem(_HANDLE, url, search_item, True)


def add_next_page_item(page):

    total_pages = get_last_number_of_page()

    if int(page) < total_pages:
        next_page_item = xbmcgui.ListItem(
            label=f'[COLOR ff694572]Siguiente Página[/COLOR]')
        next_page_item.setArt(
            {'thumb': 'https://images2.imgbox.com/f5/f1/0YFqrivu_o.png'})
        url = get_url(action='next_page', page=str(page))
        xbmcplugin.addDirectoryItem(_HANDLE, url, next_page_item, True)

    xbmcplugin.endOfDirectory(_HANDLE)


def get_user_input():
    kb = xbmc.Keyboard('', 'Ingresa el nombre del anime')
    kb.doModal()
    if not kb.isConfirmed():
        return
    query = kb.getText()
    return query


def search():
    query = get_user_input()
    if not query:
        return []
    query = query.lower()
    window = xbmcgui.Window(10000)
    window.setProperty('is_search', str(1))
    data = search_anime(query)
    list_categories(data)


def router(paramstring):

    params = dict(parse_qsl(paramstring))

    if params:
        if params['action'] == 'listing':

            list_episodes(params['category'])

        elif params['action'] == 'play':

            play_video(params['episode'], params['category'])

        elif params['action'] == 'next_page':

            add_search_item()
            list_animes_by_page(int(params['page']))

        elif params['action'] == 'search':

            search()

        else:
            raise ValueError('Invalid paramstring: {}!'.format(paramstring))
    else:
        add_search_item()
        list_animes_by_page(0)


if __name__ == '__main__':
    router(sys.argv[2][1:])
