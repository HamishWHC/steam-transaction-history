#!./venv/bin/python3

import argparse
import json
import os
import pprint
from collections import defaultdict

from parse_history_page import parse_history_page

CURRENCY_FORMATTERS = {
    "AUD": lambda a: f"${a:.2f}",
    "USD": lambda a: f"${a:.2f}"
}


def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error(f"The file {arg} does not exist!")
    else:
        return open(arg)

DESCRIPTION = """
Reads a Steam transaction history page and sums up how much you've spent over your account's lifetime.
You will need to download/save the page as an HTML file so this script can read it.
Load all the transactions on the page by using the "Load More Transactions" button.
Then, press Ctrl/Cmd + S to save the page.
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=DESCRIPTION)

    parser.add_argument(
        "--dump-json",
        help="dump transaction events to given json file",
        metavar="FILE",
        type=lambda s: open(s, "w")
    )
    parser.add_argument(
        "filename",
        help="filename of account history page's HTML",
        type=lambda s: is_valid_file(parser, s)
    )

    args = parser.parse_args()

    content = args.filename.read()
    args.filename.close()

    events = parse_history_page(content)

    if args.dump_json is not None:
        json.dump(events, args.dump_json)
        args.dump_json.close()

    totals = defaultdict(lambda: 0)

    for event in events:
        if event["type"] == "refund":
            for amount in event["amounts"]:
                totals[amount["currency"]] -= amount["amount"]
        else:
            for amount in event["amounts"]:
                totals[amount["currency"]] += amount["amount"]

    print("Over the lifetime of your Steam amount, you have spent the following:")
    for currency, amount in totals.items():
        print(f" - {currency}: {CURRENCY_FORMATTERS[currency](amount)}")
