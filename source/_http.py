import aiohttp
import json

async def scrape_page(pid, tag, session: aiohttp.ClientSession):
    try:
        async with session.get(f'https://rule34.xxx/index.php?page=post&s=list&tags={tag}+&pid={pid}') as page_results:
            if page_results.status == 200:
                return await page_results.text()
            else:
                return None
    except:
        return None


async def get_results(tag, session: aiohttp.ClientSession):
    try:
        async with session.get(f'https://rule34.xxx/public/autocomplete.php?q={tag}') as tag_results:
            if tag_results.status == 200:
                return json.loads(await tag_results.text())
            else:
                return None
    except:
        return None


async def find_post(endpoint, session: aiohttp.ClientSession):
    try:
        async with session.get(f'https://rule34.xxx/{endpoint}', headers={
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.24'
        }) as post_info:
            if post_info.status == 200:
                return await post_info.text()
            else:
                return None
    except:
        return None