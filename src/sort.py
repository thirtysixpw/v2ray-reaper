import base64
from pathlib import Path


def generate_header_text(protocol_name, protocols):
    profile_title = f"🌐 V2Ray Reaper | {protocols.get(protocol_name, '')} 🔐"
    encoded_title = base64.b64encode(profile_title.encode()).decode()
    return f"""#profile-title: base64:{encoded_title}
#profile-update-interval: 1
#subscription-userinfo: upload=0; download=0; total=10737418240000000; expire=2546249531
#support-url: https://github.com/thirtysixpw/v2ray-reaper
#profile-web-page-url: https://github.com/thirtysixpw/v2ray-reaper
"""


def main() -> None:
    protocols = {
        "vmess": "vmess",
        "vless": "vless",
        "trojan": "trojan",
        "ss": "ss",
        "ssr": "ssr",
        "tuic": "tuic",
        "hy2": "hysteria2",
        "warp": "warp",
    }

    base_path = Path(__file__).parent.parent
    split_path = base_path / "protocol"
    split_path.mkdir(exist_ok=True)

    protocol_data = {protocol: generate_header_text(protocol, protocols) for protocol in protocols}

    with (base_path / "normal" / "mix").open("r") as f:
        for config in f.readlines():
            for protocol in protocols:
                if config.startswith(protocol):
                    protocol_data[protocol] += f"{config}"
                    break

    for protocol, data in protocol_data.items():
        encoded_data = base64.b64encode(data.encode()).decode()
        with (split_path / protocols[protocol]).open("w") as file:
            file.write(encoded_data)


if __name__ == "__main__":
    main()
