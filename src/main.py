import asyncio
import base64
import binascii
import logging
import shutil
import sys
from collections.abc import Callable
from pathlib import Path

import aiohttp
import pybase64

TIMEOUT = aiohttp.ClientTimeout(10)

fixed_text = """#profile-title: base64:8J+GkyBHaXRodWIgfCBCYXJyeS1mYXIg8J+ltw==
#profile-update-interval: 1
#subscription-userinfo: upload=29; download=12; total=10737418240000000; expire=2546249531
#support-url: https://github.com/thirtysixpw/v2ray-reaper
#profile-web-page-url: https://github.com/thirtysixpw/v2ray-reaper
"""


def decode_base64(encoded: bytes) -> str:
    for encoding in ["utf-8", "iso-8859-1"]:
        try:
            padded_encoded = encoded + b"=" * (-len(encoded) % 4)
            return pybase64.b64decode(padded_encoded).decode(encoding)
        except (UnicodeDecodeError, binascii.Error):
            continue
    return ""


async def fetch_content(
    session: aiohttp.ClientSession, url: str, decode_func: Callable[[bytes], str] | None = None
) -> str | None:
    try:
        async with session.get(url, timeout=TIMEOUT) as response:
            if response.status != 200:
                logging.info("GET %d %s", response.status, url)
            return decode_func(await response.read()) if decode_func else await response.text()
    except (aiohttp.ClientError, TimeoutError):
        return None


async def process_urls(
    urls: list[str], *, decode_func: Callable[[bytes], str] | None = None
) -> list[str]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_content(session, link, decode_func) for link in urls]
        return [result for result in await asyncio.gather(*tasks) if result]


def split_and_encode_configs(
    lines: list[str], output_folder: Path, base64_folder: Path, max_lines_per_file: int = 600
):
    num_lines = len(lines)
    num_files = (num_lines + max_lines_per_file - 1) // max_lines_per_file

    for i in range(1, num_files + 1):
        profile_title = f"🌐 V2Ray Reaper | sub #{i} 🔐"
        encoded_title = base64.b64encode(profile_title.encode()).decode()
        custom_fixed_text = f"""#profile-title: base64:{encoded_title}
#profile-update-interval: 1
#subscription-userinfo: upload=0; download=0; total=10737418240000000; expire=2546249531
#support-url: https://github.com/thirtysixpw/v2ray-reaper
#profile-web-page-url: https://github.com/thirtysixpw/v2ray-reaper
"""

        start_index = (i - 1) * max_lines_per_file
        end_index = min(i * max_lines_per_file, num_lines)
        split_lines = lines[start_index:end_index]

        with (output_folder / str(i)).open("w") as f:
            f.write(custom_fixed_text)
            f.write("\n".join(split_lines) + "\n")

        encoded_config = base64.b64encode(
            (custom_fixed_text + "\n".join(split_lines) + "\n").encode()
        ).decode()
        with (base64_folder / str(i)).open("w") as output_file:
            output_file.write(encoded_config)


async def main() -> None:
    base_path = Path(__file__).parent.parent
    dir_base64 = base_path / "base64"
    dir_normal = base_path / "normal"
    if dir_base64.exists():
        shutil.rmtree(dir_base64)
    if dir_normal.exists():
        shutil.rmtree(dir_normal)
    dir_base64.mkdir()
    dir_normal.mkdir()

    protocols = ["vmess", "vless", "trojan", "ss", "ssr", "hy2", "tuic", "warp"]
    urls_base64 = [
        "https://raw.githubusercontent.com/MrPooyaX/VpnsFucking/main/Shenzo.txt",
        "https://raw.githubusercontent.com/MrPooyaX/SansorchiFucker/main/data.txt",
        "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/xray/base64/mix",
        "https://raw.githubusercontent.com/ALIILAPRO/v2rayNG-Config/main/sub.txt",
        "https://raw.githubusercontent.com/mfuu/v2ray/master/v2ray",
        "https://raw.githubusercontent.com/resasanian/Mirza/main/sub",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/reality",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vless",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/vmess",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/trojan",
        "https://raw.githubusercontent.com/soroushmirzaei/telegram-configs-collector/main/protocols/shadowsocks",
        "https://raw.githubusercontent.com/ts-sf/fly/main/v2",
        "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    ]
    urls_normal = [
        "https://raw.githubusercontent.com/mahdibland/ShadowsocksAggregator/master/Eternity.txt",
        "https://raw.githubusercontent.com/itsyebekhe/HiN-VPN/main/subscription/normal/mix",
        "https://raw.githubusercontent.com/sarinaesmailzadeh/V2Hub/main/merged",
        "https://raw.githubusercontent.com/Everyday-VPN/Everyday-VPN/main/subscription/main.txt",
        "https://mrpooya.top/SuperApi/BE.php",
        "https://servers.astms.com/api/sub?v=2.0.3&ref=bevpn.net",
        # warp
        "https://raw.githubusercontent.com/ircfspace/warpsub/main/export/warp",
        "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/warp/config",
        "https://raw.githubusercontent.com/NiREvil/vless/main/hiddify/auto-gen-warp",
        "https://raw.githubusercontent.com/hiddify/hiddify-next/main/test.configs/warp",
    ]

    configs_base64 = await process_urls(urls_base64, decode_func=decode_base64)
    configs_normal = await process_urls(urls_normal)

    merged_configs = [
        line
        for config in (configs_base64 + configs_normal)
        for line in config.splitlines()
        if any(protocol in line for protocol in protocols)
    ]

    with (dir_normal / "mix").open("w") as f:
        f.write(fixed_text)
        f.writelines(f"{config}\n" for config in merged_configs)

    split_and_encode_configs(merged_configs, dir_normal, dir_base64)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
