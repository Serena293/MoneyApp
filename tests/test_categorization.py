import json
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from main import categorize_transaction

with open('config/categories.json') as f:
    categories = json.load(f)


@pytest.mark.parametrize("merchant, expected", [
    ("ALDI Supermarket", "supermarket"),
    ("Starbucks Coffee", "eating_out"),
    ("Random Shop", "Uncategorized"),
    ("", "Uncategorized"),
    ("aldi supermarket", "supermarket")
])
def test_categorize_transaction(merchant, expected):
    result = categorize_transaction(merchant, categories)
    assert result == expected