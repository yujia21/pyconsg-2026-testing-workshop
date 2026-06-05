import asyncio
import typing

import aiomqtt
from pydantic import BaseModel


class Order(BaseModel):
    base: typing.Literal["teh", "kopi"]
    sugar: float
    condensed_milk: bool
    evaporated_milk: bool
    ice: bool


def parse_order(user_input: str) -> Order:
    user_input = user_input.lower()

    if "teh" not in user_input and "kopi" not in user_input:
        raise ValueError(f"Input must have either 'teh' or 'kopi' but is {user_input}")

    return Order(
        base="teh" if "teh" in user_input else "kopi",
        sugar=0 if "kosong" in user_input else 0.5 if "siew dai" in user_input else 1,
        condensed_milk=" o" not in user_input and " c" not in user_input,
        evaporated_milk=" c" in user_input,
        ice="png" in user_input or "bing" in user_input,
    )


async def send_order(order: Order) -> None:
    payload = order.model_dump_json()
    async with aiomqtt.Client(hostname="localhost", port=1883) as client:
        await client.publish("kopitiam/orders", payload.encode("utf-8"))
    print(f"Order sent: {payload}")


async def process_input(user_input: str) -> None:
    order = parse_order(user_input)
    await send_order(order)


def main() -> None:
    print("What is your order?")
    user_input = input()
    asyncio.run(process_input(user_input))

if __name__ == "__main__":
    main()
