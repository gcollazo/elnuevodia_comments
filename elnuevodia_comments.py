# Requirements:
#
# beautifulsoup4==4.3.2
# lxml==3.3.0
# requests==2.2.1


import requests
from bs4 import BeautifulSoup

RSS_FEED = 'http://elnuevodia.feedsportal.com/c/34275/f/623466/index.rss'
COMMENT_URL = 'http://www.elnuevodia.com/XStatic/endi/template/'
COMMENTS_PER_PAGE = 5


def _request(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_1) '
               'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1700.102 Safari/537.36'}
    response = requests.get(url, headers=headers)
    return response.text


def _calculate_pages(comment_count):
    pages = comment_count / COMMENTS_PER_PAGE
    if comment_count % COMMENTS_PER_PAGE > 0:
        pages = pages + 1

    return int(pages)


def get_stories():
    """
    Downloads their rss feed and extracts relevant information
    """
    soup = BeautifulSoup(_request(RSS_FEED), 'lxml')

    stories = []
    for item in soup.findAll('item'):
        story_id = item.guid.contents[0].split('/')[-1].split('.')[0].split('-')[-1]
        stories.append({
            'title': item.title.contents[0],
            'url': item.guid.contents[0],
            'id': story_id
        })

    return stories


def get_comment_count(story_id):
    """
    Returns an int of how many comments in a story
    """
    count_url = COMMENT_URL + 'cargaComentarios.aspx?intElementId={0}&intConfigurationId=12275'
    soup = BeautifulSoup(_request(count_url.format(story_id)))

    count = soup.findAll('span', attrs={'id': 'comentarios2'})[0].contents[0].strip()
    return int(count)


def get_comment_page(story_id, page):
    """
    Gets a specific page of comments from a story
    """
    comment_url = COMMENT_URL + \
        'cargaListaComentarios.aspx?intConfigurationId=12275&intElementId={0}&p={1}'

    soup = BeautifulSoup(_request(comment_url.format(story_id, page)))
    comentarios = soup.findAll('div', attrs={'class': 'comentarios'})

    comments = []

    for c in comentarios:
        username = c.findAll('h2')[0].contents[-1].strip()

        if username != 'No existen comentarios':
            comment = c.findAll('p', attrs={'class': 'copete clearfix'})[0].contents[0].strip()
            date = c.findAll('div', attrs={'class': 'fl'})[0].contents[0].strip()
            num = int(c.findAll('span',
                      attrs={'class': 'cantComentariosVideos'})[0].contents[0].strip())

            comments.append({
                'num': num,
                'username': username,
                'comment': comment,
                'date': date
            })

    return comments


def get_all_comments(story_id, reverse=False):
    """
    Gets all stories for a given story_id
    """
    count = get_comment_count(story_id)
    pages = _calculate_pages(count)

    comments = []
    for page in range(pages):
        current_page = page + 1
        print('--> Getting page: {0} of {1}'.format(current_page, pages))
        comments.extend(get_comment_page(story_id, current_page))

    return sorted(comments, key=lambda k: k['num'], reverse=reverse)


def get_all_stories_with_comments():
    """
    This will fetch all comments in stories found on the rss feed
    """
    stories = get_stories()

    for story in stories:
        print('--> Story [{0}]: {1}'.format(story['id'], story['title']))
        story['comments'] = get_all_comments(story['id'])

        print('')

    return stories


def get_all_missing_stories_with_comments(saved_stories=[]):
    """
    Takes a list of story_id to skip when fetching comments
    """
    stories = get_stories()
    result = []

    for story in stories:
        if story['id'] not in saved_stories:
            print('--> Story [{0}]: {1}'.format(story['id'], story['title']))
            story['comments'] = get_all_comments(story['id'])
            result.append(story)

            print('')
    return result


if __name__ == '__main__':
    print(get_all_stories_with_comments())
