#!/usr/bin/env python3
"""One-time helper to seed sips-overrides.json from RSS + manual polish."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sips_common import OVERRIDES_PATH, episodes_with_numbers, extract_rss_sip_paragraph, load_episodes

# Polished display copy for all 32 episodes (chronological ep 1-32)
MANUAL: dict[int, dict] = {
    1: {
        "displayName": "Christmas Morning Loose-Leaf Black Tea",
        "description": "M brewed a loose-leaf black tea with almonds, apple pieces, orange peel, raisins, cinnamon, and warm spices - served in a ceramic pot.",
        "ingredients": ["black tea", "almonds", "apple pieces", "orange peel", "raisins", "cinnamon", "spices"],
        "vessel": "ceramic teapot",
    },
    2: {
        "displayName": "Seasonal Eggnog",
        "description": "Sydney whipped up seasonal eggnog for the second Sips of the Week.",
        "ingredients": ["eggnog", "bourbon", "nutmeg", "cinnamon"],
    },
    3: {
        "displayName": "Cottage Apple Tea",
        "description": "M's Cottage Apple Tea from The Little Tea Company - one of her absolute favorites.",
        "ingredients": ["Cottage Apple tea blend"],
        "needsListen": True,
    },
    4: {
        "displayName": "White Chocolate Coffee + Salted Caramel Cold Foam",
        "description": "White chocolate coffee topped with salted caramel cold foam, served in matching Up mugs.",
        "ingredients": ["white chocolate", "coffee", "salted caramel cold foam"],
        "vessel": "matching Up mugs",
    },
    5: {
        "displayName": "McDonald's Dr Pepper",
        "description": "A nice and good McDonald's Dr Pepper - simple, chaotic, perfect.",
        "ingredients": ["Dr Pepper"],
    },
    6: {
        "displayName": "Nick's Sick Mix",
        "description": "A cozy recipe from Louisville Tea Company called Nick's Sick Mix - and trust us, it was so good.",
        "ingredients": ["Nick's Sick Mix tea"],
    },
    7: {
        "displayName": "Coffee with Buffalo Trace Bourbon Sipping Cream",
        "description": "The ultimate winter treat: coffee with Buffalo Trace bourbon sipping cream.",
        "ingredients": ["coffee", "Buffalo Trace bourbon sipping cream"],
    },
    8: {
        "displayName": "Coffee for the Modern Witch",
        "description": "Coffee inspired by Coffee for the Modern Witch, picked up in Salem. Syd sipped from her Valentine's mug from her hubby.",
        "ingredients": ["coffee"],
        "vessel": "Valentine's mug",
    },
    9: {
        "displayName": "Fresh Strawberry Margaritas",
        "description": "Fresh strawberry margaritas handcrafted by guest Lauren - three bartenders, midday margarita madness.",
        "hosts": [{"host": "Lauren", "drink": "fresh strawberry margaritas (handcrafted)"}],
        "ingredients": ["strawberries", "tequila", "margarita mix"],
        "needsListen": True,
    },
    10: {
        "displayName": "The Raven Tea",
        "description": "The most perfectly moody tea called The Raven - dramatic, mysterious, and fitting for unhinged tangents.",
        "ingredients": ["The Raven tea blend"],
    },
    11: {
        "displayName": "Spicy Tea + Girl Scout Cookies",
        "description": "A spicy tea very scientifically paired with Girl Scout cookies and banana peppers. Syd literally spilled her tea on mic - on brand.",
        "pairedFood": "Girl Scout cookies and banana peppers",
        "ingredients": ["spicy tea"],
    },
    12: {
        "displayName": "Green Tea Jasmine",
        "description": "A cozy cup of green tea jasmine while recapping Sydney's whirlwind trip to Cleveland.",
        "ingredients": ["green tea jasmine"],
    },
    13: {
        "displayName": "Coffee with Homemade Blueberry Creamer",
        "description": "A springy dream - coffee with homemade blueberry creamer. Happy Ostara!",
        "ingredients": ["coffee", "homemade blueberry creamer"],
    },
    14: {
        "displayName": "Mango Tea with Nick's Sick Mix + Honey",
        "description": "Mango tea with Nick's Sick Mix and honey - possibly the best sip they've ever made. Soothing, perfect spring blend.",
        "ingredients": ["mango tea", "Nick's Sick Mix", "honey"],
    },
    15: {
        "displayName": "Mango Tea Sangria with Rosé",
        "description": "A refreshing mango tea sangria infused with rosé, paired with an international snack haul from Jungle Jim's in Cincinnati.",
        "ingredients": ["mango tea", "rosé"],
        "pairedFood": "international snacks from Jungle Jim's",
    },
    16: {
        "displayName": "Black Cat Riesling + Turkish Delight",
        "description": "A surprise find from Jungle Jim's - Riesling in the cutest black cat bottle, paired with Turkish delight.",
        "ingredients": ["Riesling wine"],
        "pairedFood": "Turkish delight",
        "vessel": "black cat bottle",
    },
    17: {
        "displayName": "Spiced Coffee with French Vanilla + Cinnamon Sugar",
        "description": "M whipped up a spiced coffee; Syd made hers extra sweet with French vanilla creamer and cinnamon sugar.",
        "ingredients": ["coffee", "French vanilla creamer", "cinnamon sugar"],
    },
    18: {
        "displayName": "Mango and Spicy Chili Tea",
        "description": "M's elite concoction - mango and spicy chili tea paired with pastries from her homemade breakfast.",
        "ingredients": ["mango tea", "spicy chili tea"],
        "pairedFood": "homemade breakfast pastries",
    },
    19: {
        "displayName": "Japanese Mango Cream Soda + Vodka",
        "description": "Japanese mango cream soda plus vodka - basically a mango screwdriver, and they're not mad about it.",
        "ingredients": ["Japanese mango cream soda", "vodka"],
    },
    20: {
        "displayName": "Brown Sugar Caramel Iced Coffee",
        "description": "Brown sugar caramel iced coffees served in the cutest Dolly Parton cups gifted by Syd's mother-in-law.",
        "ingredients": ["brown sugar", "caramel", "iced coffee"],
        "vessel": "Dolly Parton cups",
    },
    21: {
        "displayName": "Giant Spicy Mango Margarita",
        "description": "Powered by a GIANT spicy mango margarita literally the size of their heads, paired with killer chips and queso.",
        "ingredients": ["spicy mango margarita"],
        "pairedFood": "chips and queso",
    },
    22: {
        "displayName": "Peanut Butter Iced Coffee",
        "description": "Peanut butter iced coffees paired perfectly with chips and queso while their brains rode the struggle bus.",
        "ingredients": ["peanut butter", "iced coffee"],
        "pairedFood": "chips and queso",
    },
    23: {
        "displayName": "Cozy Coffee + Muffin Tin Brownies",
        "description": "Cozy coffee paired with M's homemade muffin tin brownies with walnuts.",
        "ingredients": ["coffee"],
        "pairedFood": "muffin tin brownies with walnuts",
    },
    24: {
        "displayName": "Sunset Sarsaparilla Floats",
        "description": "Boozy Sunset Sarsaparilla floats inspired by the Fallout universe (thank you, Costco).",
        "ingredients": ["Sunset Sarsaparilla", "ice cream", "vodka"],
    },
    25: {
        "displayName": "De-Stress Tea + Bloom Vodka Shot",
        "description": "A much-needed two-parter: de-stress tea that revived their souls, followed by a shot of vodka mixed with Sydney's first Bloom drink.",
        "ingredients": ["de-stress tea", "vodka", "Bloom energy drink"],
    },
    26: {
        "displayName": "Coffee + King Donuts",
        "description": "Cozy coffee paired with an assortment of donuts from King Donuts and chocolate hazelnut-filled beignets.",
        "ingredients": ["coffee"],
        "pairedFood": "King Donuts assortment and chocolate hazelnut beignets",
    },
    27: {
        "displayName": "Passionfruit Margarita",
        "description": "A refreshing passionfruit margarita to welcome the first day of summer.",
        "ingredients": ["passionfruit", "margarita", "tequila"],
        "needsListen": True,
    },
    28: {
        "displayName": "7 Brew Milkshake Concoctions",
        "description": "Sips inspired by 7 Brew - favorite drinks blended with ice cream into delicious milkshake concoctions.",
        "ingredients": ["7 Brew drinks", "ice cream"],
        "needsListen": True,
    },
    29: {
        "displayName": "Brown Sugar Latte + Peach Cobbler",
        "description": "Treat of the Week: M made homemade peach cobbler with fresh roadside peaches. Paired with a classic brown sugar latte.",
        "pairedFood": "homemade peach cobbler",
        "ingredients": ["brown sugar latte", "coffee", "peaches"],
    },
    30: {
        "displayName": "Tea Frog",
        "description": "A summery blend called Tea Frog, served in the new spooky cups Syd brought back from her trip home.",
        "ingredients": ["Tea Frog tea blend"],
        "vessel": "spooky cups from Syd's trip home",
    },
    31: {
        "displayName": "McDonald's Refreshers",
        "description": "McDonald's Refreshers served in their cutest glasses. Syd: Sprite Berry Blast. M: Mango Pineapple.",
        "hosts": [
            {"host": "Syd", "drink": "Sprite Berry Blast Refresher"},
            {"host": "M", "drink": "Mango Pineapple Refresher"},
        ],
        "vessel": "cutest glasses",
    },
    32: {
        "displayName": "Strawberry Watermelon Mint Frozen Margaritas",
        "description": "Strawberry watermelon mint frozen margaritas - because honestly, they deserved this one.",
        "ingredients": ["strawberry", "watermelon", "mint", "tequila", "margarita"],
    },
}


def main() -> int:
    eps = episodes_with_numbers(load_episodes())
    overrides: dict[str, dict] = {}
    for ep in eps:
        n = ep["episodeNumber"]
        if n in MANUAL:
            overrides[str(n)] = MANUAL[n]
        else:
            para = extract_rss_sip_paragraph(ep.get("description", ""))
            entry: dict = {}
            if para.get("displayName"):
                entry["displayName"] = para["displayName"]
            if para.get("description"):
                entry["description"] = para["description"]
            if entry:
                overrides[str(n)] = entry

    payload = {
        "comment": "Hand-edited sip details keyed by episodeNumber. Re-run extract-sips.py to merge.",
        "overrides": overrides,
    }
    OVERRIDES_PATH.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(overrides)} overrides to {OVERRIDES_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
