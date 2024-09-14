from datetime import datetime, timedelta, timezone
import json
import sys

import requests_cache
from pyquery import PyQuery

NOW = datetime.now(timezone.utc)


# Web API call wrappers
session = requests_cache.CachedSession(
    "partcad_gobilda",
    use_cache_dir=True,  # Save files in the default user cache dir
    cache_control=True,  # Use Cache-Control response headers for expiration, if available
    expire_after=timedelta(days=1),  # Otherwise expire responses after one day
    allowable_codes=[
        200,
        400,
    ],  # Cache 400 responses as a solemn reminder of your failures
    allowable_methods=["GET", "POST"],  # Cache whatever HTTP methods you want
)

if not "request" in globals():
    request = {
        "api": "caps",
    }


def api_get_cart():
    global request
    global session

    url = "https://www.gobilda.com/cart.php"
    partcad_version = request["partcad_version"]

    headers = {
        "User-Agent": "partcad/" + partcad_version,
    }
    response = session.get(
        url,
        headers=headers,
    )
    response_obj = {"items": {}}
    try:
        token = response.cookies["SHOP_SESSION_TOKEN"]
        response_obj["token"] = token

        body = response.text
        #
        # An example of an empty cart:
        #
        # <div class="cartResultWrapper">
        #  <div class="previewCart" data-cart-total-quantity="0">
        #    <h2>Cart Preview</h2>
        #          <div class="previewCart-emptyBody">
        #              Your cart is empty
        #          </div>
        #  </div>
        # </div>
        pq = PyQuery(body)
        empty = pq.find("div.previewCart-emptyBody")
        if empty:
            return response_obj
    except Exception as e:
        global exception
        exception = e

        sys.stderr.write(
            "Failed to parse response: %d: %s: %s\n"
            % (response.status_code, str(response.headers), response.text)
        )

    return response_obj


def api_search(sku):
    global request
    global session

    url = "https://www.gobilda.com/search.php?search_query=" + sku
    partcad_version = request["partcad_version"]

    headers = {
        "User-Agent": "partcad/" + partcad_version,
        "Referer": "https://www.gobilda.com/bulk-order",
        "Origin": "https://www.gobilda.com",
        "X-Requested-With": "XMLHttpRequest",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Stencil-Config": "{}",
        "Stencil-Options": '{"render_with":"search/bulk-order-results"}',
    }
    response = session.get(
        url,
        headers=headers,
    )
    if response.status_code != 200:
        raise Exception("Part not found: %s" % sku)

    response_obj = {}
    try:
        body = response.text
        #
        # An example of an item in the result list:
        #
        # <div class="results">
        #   <div class="result"
        #   data-sku="4103-0032-0043"
        #   data-pid="638"
        #   has_options="false"
        #   data-variantID=""
        #   add_to_cart_url="https://www.gobilda.com/cart.php?action=add&amp;product_id=638"
        #   data-url="https://www.gobilda.com/4103-series-gotube-43mm-length/"
        #   data-stock-level=""
        #   >

        pq = PyQuery(body)
        product_id = -1

        def check_sku(e):
            nonlocal product_id
            if sku == PyQuery(e).attr("data-sku"):
                product_id = PyQuery(e).attr("data-pid")

        pq.find("div.results div.result").each(lambda _i, e: check_sku(e))

        response_obj["product_id"] = product_id
    except Exception as e:
        global exception
        exception = e

        sys.stderr.write(
            "Failed to parse response: %d: %s: %s\n"
            % (response.status_code, str(response.headers), response.text)
        )

    return response_obj


def api_add_item(name, item, count):
    global request
    global session

    url = "https://www.gobilda.com/remote/v1/cart/add"
    partcad_version = request["partcad_version"]

    headers = {
        "User-Agent": "partcad/" + partcad_version,
    }
    response = session.post(
        url,
        headers=headers,
        files={
            "product_id": (None, item),
            "qty[]": (None, count),
            "action": (None, "add"),
        },
    )

    if response.status_code != 200:
        raise Exception("Failed to add item to cart: %s: %s" % (name, str(item)))

    response_obj = {}
    try:
        obj = json.loads(response.text)
        response_obj["price"] = obj["data"]["product_value"]
        response_obj["cart_id"] = obj["data"]["cart_id"]
    except Exception as e:
        global exception
        exception = e

        sys.stderr.write(
            "Failed to parse response: %d: %s: %s\n"
            % (response.status_code, str(response.headers), response.text)
        )
        raise e

    return response_obj


if __name__ == "caps":
    raise Exception("Not suported by stores")

elif __name__ == "avail":
    vendor = request.get("vendor", None)
    sku = request.get("sku", None)

    if vendor == "gobilda":
        output = {
            "available": True,
        }
    else:
        output = {
            "available": False,
        }

elif __name__ == "quote":
    parts = request["cart"]["parts"]

    # First, get the shopping session initialized
    # TODO(clairbee): empty the shopping session???
    cart = api_get_cart()

    price = 0.0
    for part_spec in parts.values():
        vendor = part_spec.get("vendor", None)
        if vendor != "gobilda":
            sys.stderr.write("Unknown vendor: {}\n".format(vendor))
            continue
        sku = part_spec.get("sku", None)
        count_per_sku = part_spec["count_per_sku"]
        count = part_spec["count"]

        # FIXME(clairbee): find the product id
        found = api_search(sku)
        product_id = found["product_id"]

        item_count = (count + count_per_sku - 1) // count_per_sku
        added = api_add_item(sku, product_id, item_count)
        price += added["price"]
        cart_id = added["cart_id"]

    output = {
        "qos": request["cart"]["qos"],
        "price": price,
        "expire": (NOW + timedelta(hours=1)).timestamp(),
        "cartId": cart_id,
        "etaMin": (NOW + timedelta(hours=1)).timestamp(),
        "etaMax": (NOW + timedelta(hours=2)).timestamp(),
    }

elif __name__ == "order":
    raise Exception("Not implemented")

else:
    raise Exception("Unknown API: {}".format(__name__))
