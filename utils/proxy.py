import requests
import asyncio
import aiohttp
import random
from urllib.parse import urlparse
from loguru import logger


def check_proxy(p):
    proxy_url = format_proxy(p)
    try:
        requests.adapters.DEFAULT_RETRIES = 3
        res = requests.get(
            url="http://icanhazip.com/", timeout=(10, 10), proxies={"http": proxy_url}
        )
        proxy_ip = res.text.strip()
        if ("127.0.0.1" in proxy_url or "localhost" in proxy_url) and proxy_ip:
            print(f"代理IP: {proxy_url},  实际IP:{proxy_ip}, 代理成功")
            return True
        elif proxy_ip and proxy_ip in proxy_url:
            print(f"代理IP: '{proxy_ip}' 有效")
            return True

        print(f"{p} 代理IP无效")
        return False
    except requests.RequestException as e:
        print(f"{p} 代理IP无效!")
        return False


async def check_proxy_async(session, proxy):
    try:
        proxy = format_proxy(proxy)
        async with session.post(
            "http://icanhazip.com/", timeout=10, proxy=proxy
        ) as response:
            result = await response.text()
            proxy_ip = result.strip()
            if ("127.0.0.1" in proxy or "localhost" in proxy) and proxy_ip:
                print(f"代理IP: {proxy},  实际IP:{proxy_ip}, 代理成功")
                return 1
            elif proxy_ip and proxy_ip in proxy:
                print(f"代理IP: {proxy},  实际IP:'{proxy_ip}', 代理成功")
                return 1

            print(f"{proxy} 代理IP无效")
            return 0
    except Exception as e:
        print(f"{proxy} 代理IP无效! {e}")
        return 0


# 异步批量检查代理
async def _check_proxies_async(proxies):
    async with aiohttp.ClientSession() as session:
        tasks = [check_proxy_async(session, proxy) for proxy in proxies]
        result = await asyncio.gather(*tasks)

        return result


def format_proxy(proxy_str):
    # 解析代理字符串
    parts = proxy_str.split(":")

    # 检查是否有足够的部分
    if len(parts) == 2:
        return f"http://{proxy_str}"

    # 检查是否有足够的部分
    if len(parts) != 4:
        return proxy_str

    proxy_url = parts[0]
    proxy_port = parts[1]
    user = parts[2]
    password = parts[3]

    # 构建 URL 对象
    url_parts = urlparse(proxy_url)
    scheme = url_parts.scheme or "http"

    # 构建包含用户和密码的代理 URL
    formatted_proxy = f"{scheme}://{user}:{password}@{proxy_url}:{proxy_port}"

    return formatted_proxy


proxies = []


def random_choice_proxy():
    global proxies
    event_loop = asyncio.get_event_loop()
    coro = get_proxies()
    if len(proxies) == 0:
        proxies = event_loop.run_until_complete(coro)

    proxy = random.choice(proxies)
    proxies.remove(proxy)

    return proxy


# 返回可用的代理列表
async def get_proxies():
    proxies = []
    for port in range(42000, 42145):
        ip = f"127.0.0.1:{port}"
        proxies.append(ip)

    results = await _check_proxies_async(proxies)
    success_proxies = []
    count = 0
    for r in results:
        if r == 1:
            success_proxies.append(proxies[count])
        count = count + 1

    return success_proxies
