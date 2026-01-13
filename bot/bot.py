from typing import Annotated

from ape import Contract, chain
from ape.api import BlockAPI
from ape.types import ContractLog
from ape_ethereum import multicall
from silverback import SilverbackBot, StateSnapshot
from taskiq import Context, TaskiqDepends

from bot.config import auctions, chain_key, explorer_tx_url, safe_name
from bot.helpers import execute_take, load_state, save_state
from bot.tg import ERROR_GROUP_CHAT_ID, notify_group_chat

# =============================================================================
# Bot Configuration & Constants
# =============================================================================


bot = SilverbackBot()


# =============================================================================
# Startup / Shutdown
# =============================================================================


@bot.on_startup()
async def bot_startup(startup_state: StateSnapshot) -> None:
    await notify_group_chat(
        f"🟢 🦍 <b>{chain_key()} dutch taker started successfully</b>",
        chat_id=ERROR_GROUP_CHAT_ID,
    )

    # TESTS

    # # TEST on_auction_kick
    # for auction, _ in auctions():
    #     event = auction.AuctionKick
    #     logs = list(event.range(24206878, 24206880))
    #     for log in logs:
    #         await on_auction_kick(log)

    # # TEST on_auction_rekick
    # for auction, _ in auctions():
    #     event = auction.AuctionReKick
    #     logs = list(event.range(24218996, 24218998))
    #     for log in logs:
    #         await on_auction_rekick(log)

    # # TEST on_auction_take
    # for auction, _ in auctions():
    #     event = auction.AuctionTake
    #     logs = list(event.range(24220453, 24220455))
    #     for log in logs:
    #         await on_auction_take(log)


@bot.on_shutdown()
async def bot_shutdown() -> None:
    await notify_group_chat(
        f"🔴 🦍 <b>{chain_key()} dutch taker shutdown successfully</b>",
        chat_id=ERROR_GROUP_CHAT_ID,
    )


# =============================================================================
# Events
# =============================================================================


for auction, _ in auctions():

    @bot.on_(auction.AuctionKick)
    async def on_auction_kick(event: ContractLog) -> None:
        auction_id = int(event.auction_id)
        kick_amount = int(event.kick_amount)

        state = load_state()
        state[str(auction_id)] = {"kick_amount": kick_amount}
        save_state(state)

        auction_contract = Contract(event.contract_address)
        sell_token = Contract(auction_contract.SELL_TOKEN())
        symbol, decimals = multicall.Call().add(sell_token.symbol).add(sell_token.decimals)()

        await notify_group_chat(
            f"🥾 <b>Auction Kicked</b>\n\n"
            f"<b>Auction ID:</b> {auction_id}\n"
            f"<b>Kick Amount:</b> {kick_amount / (10 ** int(decimals)):.4f} {symbol}\n\n"
            f"<a href='{explorer_tx_url()}{event.transaction_hash}'>🔗 View Transaction</a>"
        )

    @bot.on_(auction.AuctionReKick)
    async def on_auction_rekick(event: ContractLog) -> None:
        auction_id = int(event.auction_id)
        kick_amount = int(event.kick_amount)

        state = load_state()
        state[str(auction_id)] = {"kick_amount": kick_amount}
        save_state(state)

        auction_contract = Contract(event.contract_address)
        sell_token = Contract(auction_contract.SELL_TOKEN())
        symbol, decimals = multicall.Call().add(sell_token.symbol).add(sell_token.decimals)()

        await notify_group_chat(
            f"🚨 <b>Auction Re-Kicked</b>\n\n"
            f"<b>Auction ID:</b> {auction_id}\n"
            f"<b>Kick Amount:</b> {kick_amount / (10 ** int(decimals)):.4f} {symbol}\n\n"
            f"<a href='{explorer_tx_url()}{event.transaction_hash}'>🔗 View Transaction</a>"
        )

    @bot.on_(auction.AuctionTake)
    async def on_auction_take(event: ContractLog) -> None:
        auction_id = int(event.auction_id)
        take_amount = int(event.take_amount)
        remaining = int(event.remaining_amount)
        taker_addr = str(event.taker)

        if remaining == 0:
            state = load_state()
            state.pop(str(auction_id), None)
            save_state(state)

        auction_contract = Contract(event.contract_address)
        sell_token = Contract(auction_contract.SELL_TOKEN())
        symbol, decimals = multicall.Call().add(sell_token.symbol).add(sell_token.decimals)()

        status = "fully taken" if remaining == 0 else "partially taken"
        await notify_group_chat(
            f"🎯 <b>Auction {status}!</b>\n\n"
            f"<b>Auction ID:</b> {auction_id}\n"
            f"<b>Take Amount:</b> {take_amount / (10 ** int(decimals)):.4f} {symbol}\n"
            f"<b>Remaining:</b> {remaining / (10 ** int(decimals)):.4f} {symbol}\n"
            f"<b>Taker:</b> {safe_name(taker_addr)}\n\n"
            f"<a href='{explorer_tx_url()}{event.transaction_hash}'>🔗 View Transaction</a>"
        )


# =============================================================================
# Blocks
# =============================================================================


@bot.on_(chain.blocks)
async def check_auctions_and_take(block: BlockAPI, context: Annotated[Context, TaskiqDepends()]) -> None:
    state = load_state()
    if not state:
        return

    auction_ids = [int(auction_id_str) for auction_id_str in state.keys()]

    for auction, taker in auctions():
        call = multicall.Call()
        for auction_id in auction_ids:
            call.add(auction.get_available_amount, auction_id)

        results = call()

        for auction_id, available in zip(auction_ids, results):
            if available == 0:
                state.pop(str(auction_id), None)
                save_state(state)
                continue

            execute_take(taker, auction_id)
