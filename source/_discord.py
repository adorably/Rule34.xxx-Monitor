import aiohttp

from source._storage import data

async def notify(post_url, thumbnail, artists: list, characters: list, media_link, media_type, session: aiohttp.ClientSession):
    
    if len(artists) > 0:
        art_str = ''
        for artist in artists:
            art_str += (artist + '\n')
    else:
        art_str = 'None'

    if len(characters) > 0:
        char_str = ''
        for character in characters:
            char_str += (character + '\n')
    else:
        char_str = 'None'


    headers = {
        'content-type': 'application/json'
    }

    payload = {
        'username': data.config['discord']['webhook_username'],
        'content': '',
        'avatar_url': 'https://rule34.xxx/images/r34chibi.png',
        'embeds': [
            {
                'author': {
                    'name': f'Rule34.xxx Monitor | [{data.tag_id}]',
                    'url': 'https://rule34.xxx/',
                    'icon_url': 'https://rule34.xxx/images/r34chibi.png'
                },
                'description': (
                    f'**Post URL:** [__Visit Post Page__](https://rule34.xxx/{post_url})\n'
                    +f'**Media URL:** [__Direct Media Source__]({media_link})\n'
                    +f'**Media Type:** ` {media_type} `\n\n'
                    +f'**Character(s):** ```\n{char_str}```\n'
                    +f'**Artist(s):** ```\n{art_str}```\n\n'
                    +f'**__Media Preview__**'
                ),
                'color': 11199908,
                'image': {
                  'url': thumbnail
                },
                'thumbnail': {
                  'url': 'https://rule34.xxx/images/header2.png'
                },
                'footer': {
                  'text': '[Rule34.xxx]',
                  'icon_url': 'https://rule34.xxx/images/r34chibi.png'
                }
            }
        ]
    }

    async with session.post(data.config['discord']['webhook_url'], headers=headers, json=payload) as hook_req:
        if hook_req.status == 204:
            pass