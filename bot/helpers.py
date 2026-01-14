import json
import os
from typing import Any, Dict, cast

from ape import accounts
from ape.exceptions import ContractLogicError
from ape_accounts import import_account_from_private_key

STATE_FILE = "bot_state.json"
ACCOUNT_ALIAS = "dutch-taker"
VERY_SECRET_PASSWORD = "42069"


def get_signer() -> Any:
    private_key = os.getenv("TAKER_PRIVATE_KEY")
    if not private_key:
        raise RuntimeError("!TAKER_PRIVATE_KEY")

    try:
        account = import_account_from_private_key(ACCOUNT_ALIAS, VERY_SECRET_PASSWORD, private_key)
    except Exception:
        account = accounts.load(ACCOUNT_ALIAS)

    account.set_autosign(True, passphrase=VERY_SECRET_PASSWORD)

    return account


def execute_take(taker: Any, auction_id: int) -> None:
    try:
        signer = get_signer()
        taker.take(auction_id, sender=signer, confirmations_required=0)
    except ContractLogicError as e:
        print(f"execute_take: {e}")


def load_state() -> Dict[str, Any]:
    try:
        with open(STATE_FILE, "r") as f:
            return cast(Dict[str, Any], json.load(f))
    except FileNotFoundError:
        return {}


def save_state(state: Dict[str, Any]) -> None:
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)
