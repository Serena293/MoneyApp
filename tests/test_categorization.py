#!/usr/bin/env python3

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))   
from main import categorize_transaction

import json
with open('config/categories.json') as f:
    categories = json.load(f)

def test_aldi():
    result = categorize_transaction("ALDI Supermarket", categories)
    assert result == "supermarket"

def test_starbucks():
    result = categorize_transaction("Starbucks Coffee", categories)
    assert result == "eating_out"

def test_unknown():
    result = categorize_transaction("Random Shop", categories)
    assert result == "Uncategorized"


if __name__ == "__main__":
    test_aldi()
    test_starbucks()
    test_unknown()
    print("All tests passed!")