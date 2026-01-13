from collections.abc import Mapping, Sequence
from typing import TypedDict, cast

from ape import Contract, chain, networks
from ape.contracts.base import ContractInstance


class AuctionCfg(TypedDict):
    auction: str
    taker: str


class NetworkCfg(TypedDict):
    auctions: Sequence[AuctionCfg]
    explorer: str
    known_addresses: dict[str, str]


NETWORKS: Mapping[str, NetworkCfg] = {
    "ethereum": {
        "auctions": [
            {
                "auction": "0x6E988D3A79Cc4daeDFDC7cef2F76160F81C8f945",
                "taker": "0x8828C676FE14cBEF41F44d7e16a81c1418fe0100",
            },
        ],
        "explorer": "https://etherscan.io/",
        "known_addresses": {
            "0xEf77cc176c748d291EfB6CdC982c5744fC7211c8": "yRoboTreasury",
            "0x16388463d60FFE0661Cf7F1f31a7D658aC790ff7": "SMS",
            "0x9008D19f58AAbD9eD0D60971565AA8510560ab41": "Mooo 🐮",
            "0x1DA3902C196446dF28a2b02Bf733cA31A00A161b": "TradeHandler",
            "0x84483314d2AD44Aa96839F048193CE9750AA66B0": "gekko",
            "0x5CECc042b2A320937c04980148Fc2a4b66Da0fbF": "gekko",
            "0xb911Fcce8D5AFCEc73E072653107260bb23C1eE8": "Yearn veCRV Fee Burner",
            "0xE08D97e151473A848C3d9CA3f323Cb720472D015": "c0ffeebabe.eth",
        },
    },
}


def chain_key() -> str:
    return cast(str, chain.provider.network.ecosystem.name.lower())


def cfg() -> NetworkCfg:
    return NETWORKS.get(chain_key(), NETWORKS["ethereum"])


def auctions() -> list[tuple[ContractInstance, ContractInstance]]:
    return [(Contract(a["auction"]), Contract(a["taker"])) for a in cfg()["auctions"]]


def explorer_address_url() -> str:
    return cfg()["explorer"] + "address/"


def explorer_tx_url() -> str:
    return cfg()["explorer"] + "tx/"


def known_address_name(address: str) -> str:
    w3 = networks.active_provider.web3
    checksum = w3.to_checksum_address(address)
    return cfg()["known_addresses"].get(checksum, checksum)


def safe_name(address: str) -> str:
    # Try contract name
    try:
        return str(Contract(address).name())
    except Exception:
        pass

    # Try ENS
    try:
        ens_name = networks.active_provider.web3.ens.name(address)
        if ens_name:
            return str(ens_name)
    except Exception:
        pass

    # Fallback
    return known_address_name(address)
