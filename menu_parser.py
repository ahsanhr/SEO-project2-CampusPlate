# menu_parser.py — pulls nutrition numbers out of a raw api item

# the dineoncampus api returns a "nutrients" list on each item like:
# [{ "name": "Protein (g)", "valueNumeric": "8" }, ...]
# this file just grabs the values we care about from that list


def extract_nutrients(item):
    # item is one dict from the api's categories[].items[] array
    nutrients = item.get('nutrients', [])

    # some locations skip the nutrients array and put calories directly on the item
    # use that as a fallback but make sure it's a real number (not '' or None)
    fallback_cal = _to_float(item.get('calories'))

    # serving size is usually "1 cup", "4 oz" etc — lives on the item, not nutrients list
    portion = item.get('portion') or item.get('serving_size') or item.get('portionSize') or None

    return {
        'serving_size': portion,
        'calories':  _get(nutrients, 'calories') or fallback_cal,
        'protein_g': _get(nutrients, 'protein'),
        'carbs_g':   _get(nutrients, 'total carbohydrate'),
        'fat_g':     _get(nutrients, 'total fat'),
    }


def _get(nutrients, keyword):
    # find the first nutrient whose name contains keyword (case-insensitive)
    for n in nutrients:
        if keyword in n.get('name', '').lower():
            return _to_float(n.get('valueNumeric'))
    return None


def _to_float(value):
    # safely convert a value to float — returns None if it's empty or not a number
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
