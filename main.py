import os
import asyncio
import aiohttp
from datetime import datetime

from source._file import *
from source._http import *
from source._discord import *
from source._storage import data
from source._system import system

class Rule34_Main:
    def __init__(self) -> None:
        pass

    async def main(self) -> None:
        print(f' {system.DEFAULT}[{system.GREEN}+{system.DEFAULT}] {system.GREEN}Rule34.xxx{system.DEFAULT} Post Monitor{system.FLUSH}')
        load_config()
        
        while not data.tag_id:
            data.tag_id = input(f' {system.DEFAULT}[{system.GREEN}?{system.DEFAULT}] Tag ID: ').strip()
            if ' ' in data.tag_id:
                data.tag_id = data.tag_id.replace(' ', '_')
        
        await self.get_tag_count()
        self.get_existing_ids(f'./post_ids/{data.tag_id} - Post IDs.json')
        await self.scrape_task()
        save_posts(f'./post_ids/{data.tag_id} - Post IDs.json');print('')
        await self.monitor()

    
    @staticmethod
    async def get_tag_count() -> None:
        async with aiohttp.ClientSession() as session:
            results = await get_results(data.tag_id, session)
        if results:
            if len(results) > 0:
                tag_found = False

                for i in range(len(results)):
                    if results[i]['value'] == data.tag_id:
                        tag_found = True
                        data.tag_posts = int(results[i]['label'].split(' ')[1].replace('(', '').replace(')', ''))
                        break

                if tag_found:
                    print(f' {system.DEFAULT}[{system.GREEN}+{system.DEFAULT}] Tag [{system.GREEN}{data.tag_id}{system.DEFAULT}] Has ({system.YELLOW}{data.tag_posts}{system.DEFAULT}) Posts{system.FLUSH}')
                
                else:
                    q = input(f' {system.DEFAULT}[{system.YELLOW}!{system.DEFAULT}] Specified Tag Not Found. See All Relevant Results (y/n)? ');print('')
                    if q.strip().upper() in ['Y', 'YES']:
                        [print(f' {system.DEFAULT}[{system.GREEN}{results[i]["value"]}{system.DEFAULT}] | Posts: ({system.YELLOW}{results[i]["label"].split(" ")[1].replace("(", "").replace(")", "")}{system.DEFAULT})') for i in range(len(results))]
                        os._exit(0)
                    else:
                        os._exit(0)
            else:
                print(f' {system.DEFAULT}[{system.YELLOW}!{system.DEFAULT}] No Relevant Tags Found Related to [{system.GREEN}{data.tag_id}{system.DEFAULT}]{system.FLUSH}')
                os._exit(0)
        else:
            print(f' {system.DEFAULT}[{system.YELLOW}!{system.DEFAULT}] No Relevant Tags Found Related to [{system.GREEN}{data.tag_id}{system.DEFAULT}]{system.FLUSH}')
            os._exit(0)


    @staticmethod
    def get_existing_ids(path) -> None:
        ids = load_ids(path)
        if ids:
            [
                data.collected_posts['posts'].append(
                    {
                        'id': ids[i]['id'],
                        'url': ids[i]['url'],
                        'thumbnail': ids[i]['thumbnail']
                    }
                ) 
                for i in range(len(ids))
            ]
            print(f'\n {system.DEFAULT}[{system.GREEN}*{system.DEFAULT}] Preloaded Post ID\'s: ({system.YELLOW}{len(data.collected_posts["posts"])}{system.DEFAULT}){system.FLUSH}\n')
        else:
            print(f'\n {system.DEFAULT}[{system.YELLOW}!{system.DEFAULT}] No Pre-Existing ID\'s Found For Tag [{system.GREEN}{data.tag_id}{system.DEFAULT}]{system.FLUSH}\n')


    async def scrape_task(self):
        print(f' {system.DEFAULT}[{system.GREEN}*{system.DEFAULT}] Starting Task to Scrape Post ID\'s{system.FLUSH}')

        data.pre_posts = len(data.collected_posts['posts'])

        while data.pid < data.tag_posts:
            await self.scrape_post_ids(data.pid)

            if (data.tag_posts - data.pid) >= 42:
                data.pid += 42
            else:
                data.pid += (data.tag_posts - data.pid)
        
        print(f' {system.DEFAULT}[{system.GREEN}+{system.DEFAULT}] Scraped ({system.YELLOW}{(len(data.collected_posts["posts"]) - data.pre_posts)}{system.DEFAULT}) New Posts - Total Gathered: ({system.GREEN}{len(data.collected_posts["posts"])}{system.DEFAULT}){system.FLUSH}')
    

    @staticmethod
    async def scrape_post_ids(pid):
        async with aiohttp.ClientSession() as session:
            page_data = await scrape_page(pid, data.tag_id, session)

            if page_data:
                
                if '<h1>Search is overloaded! Try again later...</h1>' not in page_data:
                    posts = (
                        page_data.split('<div class="content">', 1)[1].\
                            split('</div>\n<span data-nosnippet>', 1)[0].\
                                split('<div id="paginator">', 1)[0]
                    )

                    for post in posts.split('<span id="'):
                        if '<div class="image-list">' not in post and 'index.php' in post:
                            id = post.split('"', 1)[0]
                            url = post.split('href="', 1)[1].split('"', 1)[0]
                            thumbnail = post.split('<img src="', 1)[1].split('"', 1)[0]


                            post_exists = False
                            for i in range(len(data.collected_posts['posts'])):
                                if data.collected_posts['posts'][i]['id'] == id:
                                    post_exists = True
                                    break
                                
                            if not post_exists:
                                data.collected_posts['posts'].append(
                                    {
                                        'id': id,
                                        'url': url,
                                        'thumbnail': thumbnail
                                    }
                                )
                        print(f' {system.DEFAULT}[{system.GREEN}+{system.DEFAULT}] Collected Total Posts: ({system.YELLOW}{len(data.collected_posts["posts"]) - data.pre_posts}{system.DEFAULT}) | PID Range: ({system.GREEN}{pid}{system.DEFAULT}/{system.GREEN}{data.tag_posts}{system.DEFAULT}){system.FLUSH}', end='\r', flush=True)
                else:
                    data.pid -= 42
            else:
                data.pid -= 42


    async def monitor(self) -> None:
        asyncio.create_task(self.printer())
        while True:
            async with aiohttp.ClientSession() as session:
                page_results = await scrape_page(0, data.tag_id, session)
                if page_results and '<h1>Search is overloaded! Try again later...</h1>' not in page_results:
                    try:
                        posts = (
                            page_results.split('<div class="content">', 1)[1].\
                                split('</div>\n<span data-nosnippet>', 1)[0].\
                                    split('<div id="paginator">', 1)[0]
                        )

                        for post in posts.split('<span id="'):
                            if '<div class="image-list">' not in post and 'index.php' in post:
                                data.temp_posts['posts'].append(
                                    {
                                        'id': post.split('"', 1)[0],
                                        'url': post.split('href="', 1)[1].split('"', 1)[0],
                                        'thumbnail': post.split('<img src="', 1)[1].split('"', 1)[0]
                                    }
                                )

                        post_found = False
                        for i in range(len(data.temp_posts['posts'])):
                            for x in range(len(data.collected_posts['posts'])):
                                if data.temp_posts['posts'][i]['id'] == data.collected_posts['posts'][x]['id']:
                                    post_found = True

                            if not post_found:
                                print(f' {system.DEFAULT}[{system.GREEN}{str(datetime.now()).split(".", 1)[0]}{system.DEFAULT}] New Post Found - | URL: [{system.GREEN}https://rule34.xxx/{data.temp_posts["posts"][i]["url"]}{system.DEFAULT}] {system.FLUSH}')
                                data.collected_posts['posts'].append(
                                    {
                                        'id': data.temp_posts['posts'][i]['id'],
                                        'url': data.temp_posts['posts'][i]['url'],
                                        'thumbnail': data.temp_posts['posts'][i]['thumbnail']
                                    }
                                )

                                await self.new_post(data.temp_posts['posts'][i]['url'], data.temp_posts['posts'][i]['thumbnail'], session)
                                save_posts(f'./post_ids/{data.tag_id} - Post IDs.json');print('')


                        data.temp_posts['posts'].clear()
                    except:
                        print(f' {system.DEFAULT}[{system.RED}{str(datetime.now()).split(".", 1)[0]}{system.DEFAULT}] Failed to Retrieve Page Results{system.FLUSH}\n')

                else:
                    print(f' {system.DEFAULT}[{system.RED}{str(datetime.now()).split(".", 1)[0]}{system.DEFAULT}] Failed to Retrieve Page Results{system.FLUSH}\n')

            await asyncio.sleep(data.config['app']['refresh_time'])

    @staticmethod
    async def new_post(post_url, post_thumbnail, session: aiohttp.ClientSession) -> None:

        post_info = await find_post(post_url, session)

        if post_info:
            try:
                if '<li><h6>Artist</h6></li>' in post_info:
                    artists = [
                        sub.split('?</a>', 1)[1].split('>', 1)[1].split('</a>', 1)[0].strip() 
                        for sub in post_info.split('<li><h6>Artist</h6></li>', 1)[1].split('<li><h6>General</h6></li>', 1)[0].split('<li class="tag-type-artist tag">') 
                            if 'index.php?' in sub
                    ]
                else:
                    artists = []

                if 'li><h6>Character</h6></li>' in post_info:
                    characters = [
                        sub.split('?</a>', 1)[1].split('>', 1)[1].split('</a>', 1)[0].strip()
                        for sub in post_info.split('li><h6>Character</h6></li>', 1)[1].split(('<li><h6>Artist</h6></li>' if '<li><h6>Artist</h6></li>' in post_info else '<li><h6>General</h6></li>'), 1)[0].split('<li class="tag-type-character tag">')
                            if 'index.php?' in sub
                    ]
                else:
                    characters = []

                media_link = post_info.split('<div class="link-list">\n<h5>Options</h5>')[1].split('Original image', 1)[0].\
                    split('<a href="https://', 1)[1].split('"')[0]

                media_type = media_link.split('images', 1)[1].split('.', 1)[1].split('?', 1)[0]
            
                await notify(post_url, post_thumbnail, artists, characters, f'https://{media_link}', media_type, session)
            except:
                print(f' {system.DEFAULT}[{system.RED}{str(datetime.now()).split(".", 1)[0]}{system.DEFAULT}] Failed to Retrieve Page Info for New Post{system.FLUSH}\n')
        else:
            print(f' {system.DEFAULT}[{system.RED}{str(datetime.now()).split(".", 1)[0]}{system.DEFAULT}] Failed to Retrieve Page Info for New Post{system.FLUSH}\n')


    @staticmethod
    async def printer() -> None:
        counter = 0
        while True:
            print(f' {system.DEFAULT}[{system.GREEN}{data.spinner_array[counter%len(data.spinner_array)]}{system.DEFAULT}] Post Monitor Running for [{system.GREEN}{data.tag_id}{system.DEFAULT}]{system.FLUSH}', end='\r', flush=True)
            counter += 1
            await asyncio.sleep(0.1)
    

if __name__ == '__main__':
    system.cls()
    asyncio.get_event_loop().\
        run_until_complete(
            Rule34_Main().main()
        )
