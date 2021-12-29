import bs4
import datetime
import re

CURRENCY_PARSING = {
    "AUD": "A\$ (\d+.\d\d)",
    "USD": "\$(\d+.\d\d) USD"
}

CURRENCY_PARSING = {key: re.compile(value)
                    for key, value in CURRENCY_PARSING.items()}

# See https://strftime.org.
DATE_FORMAT = "%d %b, %Y"


def parse_payment(s, source_key):
    for currency, pattern in CURRENCY_PARSING.items():
        m = pattern.match(s)
        if m:
            return {
                "currency": currency,
                "amount": float(m.group(1)),
                "source": source_key(m)
            }
    return None


def parse_row(row):
    raw_type = row.find("td", attrs={"class": "wht_type"}).div.string.strip()

    event = {
        "type": raw_type.lower().replace(" ", "_").replace("-", "_"),
        "amounts": [],
        "date": datetime.datetime.strptime(row.find("td", {"class": "wht_date"}).string.strip(), DATE_FORMAT).date().isoformat(),
        # "_row": row
    }

    items_cell = row.find("td", {"class": "wht_items"})

    if event["type"] == "conversion":
        # Conversions are only when purchasing/adding wallet credit - they do not have associated amounts,
        # and are applied at the same time as the actual purchase.
        return None
    elif event["type"] == "gift_purchase":
        link = items_cell.find("div", {"class": "wth_payment"}).div.a

        if link is not None:
            event["gift_info"] = {
                "sent_to": {
                    "link": link.attrs["href"],
                    "name": link.string
                }
            }
        else:
            event["gift_info"] = "stored_in_gift_inventory"

    elif event["type"].endswith("_market_transactions") or event["type"] == "market_transaction":
        event["market_info"] = {
            "count": 1 if event["type"] == "market_transaction" else int(event["type"].split("_")[0])
        }
        event["type"] = "market_transactions"
    elif event["type"] not in ["refund", "purchase", "in_game_purchase"]:
        print(f'Unknown transaction/event type: "{raw_type}"')
        return None

    total = row.find("td", attrs={"class": "wht_total"})
    if total.string is None:
        return None

    payment_sources = row.find("td", attrs={"class": "wht_type"}).find(
        "div", attrs={"class": "wth_payment"})
    if len(payment_sources.contents) > 1:
        for el in payment_sources.children:
            s = el.string.strip()
            if not s:
                continue
            payment = parse_payment(s, lambda m: s[m.end(0):].strip())
            if payment is not None:
                event["amounts"].append(payment)
            else:
                print(
                    f'Unknown currency in transaction: "{s}" - please add a parser for this!')
    else:
        # Single source/destination.
        s = total.string.strip()
        payment = parse_payment(s, lambda _: payment_sources.string.strip().replace(
            "\t\t\t\t\t\t\t\t\t\t\t\t\t", " "))
        if payment is not None:
            event["amounts"].append(payment)
        else:
            print(
                f'Unknown currency in transaction: "{s}" - please add a parser for this!')

    if event["type"] in ["refund", "gift_purchase", "purchase"]:
        event["items"] = []
        for el in items_cell.find_all("div", {"class": ""}):
            if el.string is not None:
                event["items"].append(el.string.strip())
    elif event["type"] in ["in_game_purchase"]:
        event["items"] = {
            "game": items_cell.div.string.strip(),
            "items": []
        }
        for el in items_cell.find_all("div", {"class": "wth_payment"}):
            event["items"]["items"].append(el.string.strip())

    return event


def parse_history_page(content: str):
    soup = bs4.BeautifulSoup(content, "html.parser")

    events = []

    for row in soup.find_all("tr", attrs={"class": "wallet_table_row"}):
        event = parse_row(row)

        if event is None:
            continue

        events.append(event)

    return events
