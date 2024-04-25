import requests
from bs4 import BeautifulSoup
import re


def get_last_number_of_page():
    query = 'https://tioanime.com/directorio'
    response = requests.get(query, headers={'User-Agent': 'XYZ/3.0'}).text
    web_parser = BeautifulSoup(response, 'html.parser')
    last_number_page = web_parser.find_all(
        'a', {'class': 'page-link'})[-2].get_text()
    return int(last_number_page)


def get_animes_titles(page):
    articles = get_articles_animes(page)
    list_anime_titles = [{'title': article.h3.text} for article in articles]
    return list_anime_titles


def get_animes_urls(page):
    articles = get_articles_animes(page)
    list_anime_urls = [{'url_anime': 'https://tioanime.com' + article.a.get_attribute_list('href')[0]} for article in
                       articles]
    return list_anime_urls


def get_articles_animes(page):
    articles = []

    query = f'https://tioanime.com/directorio?p={page}'
    response = requests.get(query, headers={'User-Agent': 'XYZ/3.0'}).text
    web_parser = BeautifulSoup(response, 'html.parser')
    total_animes_in_page = len(
        web_parser.find_all('article', {'class': 'anime'}))

    for j in range(0, total_animes_in_page):
        articles.insert(j, web_parser.find_all(
            'article', {'class': 'anime'})[j])

    return articles


def get_animes(page):
    list_animes = []
    articles = get_articles_animes(page)

    for article in articles:
        list_animes.append({
            'title': article.h3.text,
            'url_anime': 'https://tioanime.com' + article.a.get_attribute_list('href')[0],
            'thumb': 'https://tioanime.com' + article.div.img.get_attribute_list('src')[0]
        })

    for anime in list_animes:
        anime.update({
            'synopsis': get_synopsis_anime(anime.get('url_anime'))
        })

    return list_animes


def search_anime(name):
    list_search = []
    list_articles = []
    query = 'https://tioanime.com/directorio?q=' + name.replace(' ', '+')
    response = requests.get(query, headers={'User-Agent': 'XYZ/3.0'}).text
    web_parser = BeautifulSoup(response, 'html.parser')
    articles = web_parser.find_all('article', {'class': 'anime'})

    for j, article in enumerate(articles):
        list_articles.insert(j, web_parser.find_all(
            'article', {'class': 'anime'})[j])

    for article in articles:
        list_search.append({'title': article.h3.text,
                            'link': 'https://tioanime.com' + article.a.get_attribute_list('href')[0],
                            'thumb': 'https://tioanime.com' + article.div.img.get_attribute_list('src')[0]
                            })
    return list_search


def get_number_of_episodes(url_anime):
    response = requests.get(url_anime, headers={'User-Agent': 'XYZ/3.0'}).text
    season_parser = BeautifulSoup(response, 'html.parser')
    regex1 = re.compile(
        'var episodes = (\[[\d,]*\])', re.MULTILINE | re.DOTALL)
    script = season_parser.find('script', text=regex1)
    regex2 = re.compile('(\[[\d,]*\])', re.MULTILINE | re.DOTALL)
    list_nums_episodes = regex2.search(script.string).group().replace(
        '[', '').replace(']', '').split(',')
    new_list_episodes = [int(num_episode)
                         for num_episode in list_nums_episodes]
    number_of_episodes = sorted(new_list_episodes)
    return number_of_episodes


def get_synopsis_anime(url_anime):
    response = requests.get(url_anime, headers={'User-Agent': 'XYZ/3.0'}).text
    html_parser = BeautifulSoup(response, 'html.parser')
    p = html_parser.find('p', {'class': 'sinopsis'})
    synopsis = p.text.strip('\n')
    return synopsis


def get_html_episode(url_anime, episode_number):
    episode_format = url_anime.replace('/anime/', '/ver/')
    episode_url = episode_format + '-' + str(episode_number)
    response = requests.get(episode_url, headers={
                            'User-Agent': 'XYZ/3.0'}).text
    episode_parser = BeautifulSoup(response, 'html.parser')
    return episode_parser


def get_url_video(url_anime, episode_number, server):

    episode_parser = get_html_episode(url_anime, episode_number)

    if server == 'fembed':
        return get_url_video_fembed(episode_parser)
    elif server == 'okru':
        return get_url_video_okru(episode_parser)
    elif server == 'yourupload':
        return get_url_video_yourupload(episode_parser)
    else:
        return get_url_video_maru(episode_parser)


def get_servers(url_anime, episode_number):
    episode_parser = get_html_episode(url_anime, episode_number)
    list_servers = re.findall(r'"\w+",', str(episode_parser), flags=0)
    new_list_servers = [server.replace('"', '').replace(
        '"', '').replace(',', '').lower() for server in list_servers]
    supported_servers = [server for server in new_list_servers if server in [
        'fembed', 'okru', 'yourupload', 'maru']]
    return supported_servers


def get_url_video_fembed(episode_parser):
    regex = re.compile(r'www.fembed.com\\/v\\/[a-z0-9-]*', re.MULTILINE | re.DOTALL)
    script = episode_parser.find('script', text=regex)
    url_parsed = regex.search(script.string).group()
    regex = re.compile(r'[a-z0-9-]*$', re.MULTILINE | re.DOTALL)
    url_parsed = regex.search(url_parsed).group()
    return f'https://www.fembed.com/v/{url_parsed}'


def get_url_video_okru(episode_parser):
    regex = re.compile(r'ok.ru\\/videoembed\\/(\d)*', re.MULTILINE | re.DOTALL)
    script = episode_parser.find('script', text=regex)
    url_parsed = regex.search(script.string).group()
    regex = re.compile(r'(\d)*$', re.MULTILINE | re.DOTALL)
    url_parsed = regex.search(url_parsed).group()
    return f'https://ok.ru/videoembed/{url_parsed}'


def get_url_video_yourupload(episode_parser):
    regex = re.compile(r'yourupload.com\\/embed\\/[A-Za-z0-9]*', re.MULTILINE | re.DOTALL)
    script = episode_parser.find('script', text=regex)
    url_parsed = regex.search(script.string).group()
    regex2 = re.compile(r'[A-Za-z0-9]*$', re.MULTILINE | re.DOTALL)
    url_parsed = regex2.search(url_parsed).group()
    return f'https://www.yourupload.com/embed/{url_parsed}'


def get_url_video_maru(episode_parser):
    regex = re.compile(r'my.mail.ru\\/video\\/embed\\/[a-z0-9#]*', re.MULTILINE | re.DOTALL)
    script = episode_parser.find('script', text=regex)
    url_parsed = regex.search(script.string).group()
    regex = re.compile(r'[a-z0-9#]*$', re.MULTILINE | re.DOTALL)
    url_parsed = regex.search(url_parsed).group()
    return f'https://my.mail.ru/video/embed/{url_parsed}'