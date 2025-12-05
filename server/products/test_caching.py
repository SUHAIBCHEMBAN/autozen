"""
Test script to verify zero-query caching implementation
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the server directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from django.db import connection
from django.test import TestCase
from products.models import Brand, VehicleModel, PartCategory
from products.cache_utils import (
    get_cached_brands_list, get_cached_models_list, get_cached_categories_list,
    get_cached_brand, get_cached_model, get_cached_category
)


def test_zero_query_implementation():
    """Test that our caching implementation achieves zero queries for reference data"""
    
    print("Testing zero-query caching implementation...")
    
    # Clear any existing cache
    from django.core.cache import cache
    cache.clear()
    
    # Create some test data if it doesn't exist
    brand, _ = Brand.objects.get_or_create(
        name="Toyota",
        defaults={"description": "Japanese automaker"}
    )
    
    model, _ = VehicleModel.objects.get_or_create(
        brand=brand,
        name="Camry",
        defaults={"year_from": 2020, "description": "Mid-size sedan"}
    )
    
    category, _ = PartCategory.objects.get_or_create(
        name="Engine Parts",
        defaults={"description": "Engine components"}
    )
    
    print("\n--- Testing Brand Caching ---")
    
    # Test 1: get_cached_brands_list should hit the database the first time
    print("First call to get_cached_brands_list (should hit DB):")
    with connection.cursor() as cursor:
        initial_queries = len(connection.queries)
    
    brands_list = get_cached_brands_list()
    after_first_call = len(connection.queries)
    
    print(f"Queries before: {initial_queries}")
    print(f"Queries after: {after_first_call}")
    print(f"Queries executed: {after_first_call - initial_queries}")
    
    # Test 2: get_cached_brands_list should NOT hit the database the second time
    print("\nSecond call to get_cached_brands_list (should NOT hit DB):")
    with connection.cursor() as cursor:
        initial_queries = len(connection.queries)
    
    brands_list_second = get_cached_brands_list()
    after_second_call = len(connection.queries)
    
    print(f"Queries before: {initial_queries}")
    print(f"Queries after: {after_second_call}")
    print(f"Queries executed: {after_second_call - initial_queries}")
    
    if after_second_call - initial_queries == 0:
        print("✅ SUCCESS: Zero queries for cached brands list!")
    else:
        print("❌ FAILED: Still hitting database for cached brands list")
    
    print("\n--- Testing Individual Object Caching ---")
    
    # Test 3: get_cached_brand should hit the database the first time
    print("First call to get_cached_brand (should hit DB):")
    with connection.cursor() as cursor:
        initial_queries = len(connection.queries)
    
    cached_brand = get_cached_brand(brand.id)
    after_first_call = len(connection.queries)
    
    print(f"Queries before: {initial_queries}")
    print(f"Queries after: {after_first_call}")
    print(f"Queries executed: {after_first_call - initial_queries}")
    
    # Test 4: get_cached_brand should NOT hit the database the second time
    print("\nSecond call to get_cached_brand (should NOT hit DB):")
    with connection.cursor() as cursor:
        initial_queries = len(connection.queries)
    
    cached_brand_second = get_cached_brand(brand.id)
    after_second_call = len(connection.queries)
    
    print(f"Queries before: {initial_queries}")
    print(f"Queries after: {after_second_call}")
    print(f"Queries executed: {after_second_call - initial_queries}")
    
    if after_second_call - initial_queries == 0:
        print("✅ SUCCESS: Zero queries for cached individual brand!")
    else:
        print("❌ FAILED: Still hitting database for cached individual brand")
    
    print("\n--- Testing Model Caching ---")
    
    # Test 5: get_cached_models_list should hit the database the first time
    print("First call to get_cached_models_list (should hit DB):")
    with connection.cursor() as cursor:
        initial_queries = len(connection.queries)
    
    models_list = get_cached_models_list()
    after_first_call = len(connection.queries)
    
    print(f"Queries before: {initial_queries}")
    print(f"Queries after: {after_first_call}")
    print(f"Queries executed: {after_first_call - initial_queries}")
    
    # Test 6: get_cached_models_list should NOT hit the database the second time
    print("\nSecond call to get_cached_models_list (should NOT hit DB):")
    with connection.cursor() as cursor:
        initial_queries = len(connection.queries)
    
    models_list_second = get_cached_models_list()
    after_second_call = len(connection.queries)
    
    print(f"Queries before: {initial_queries}")
    print(f"Queries after: {after_second_call}")
    print(f"Queries executed: {after_second_call - initial_queries}")
    
    if after_second_call - initial_queries == 0:
        print("✅ SUCCESS: Zero queries for cached models list!")
    else:
        print("❌ FAILED: Still hitting database for cached models list")
    
    print("\n--- Testing Category Caching ---")
    
    # Test 7: get_cached_categories_list should hit the database the first time
    print("First call to get_cached_categories_list (should hit DB):")
    with connection.cursor() as cursor:
        initial_queries = len(connection.queries)
    
    categories_list = get_cached_categories_list()
    after_first_call = len(connection.queries)
    
    print(f"Queries before: {initial_queries}")
    print(f"Queries after: {after_first_call}")
    print(f"Queries executed: {after_first_call - initial_queries}")
    
    # Test 8: get_cached_categories_list should NOT hit the database the second time
    print("\nSecond call to get_cached_categories_list (should NOT hit DB):")
    with connection.cursor() as cursor:
        initial_queries = len(connection.queries)
    
    categories_list_second = get_cached_categories_list()
    after_second_call = len(connection.queries)
    
    print(f"Queries before: {initial_queries}")
    print(f"Queries after: {after_second_call}")
    print(f"Queries executed: {after_second_call - initial_queries}")
    
    if after_second_call - initial_queries == 0:
        print("✅ SUCCESS: Zero queries for cached categories list!")
    else:
        print("❌ FAILED: Still hitting database for cached categories list")
    
    print("\n--- Summary ---")
    print("If all tests show zero queries on second calls, the caching implementation is working correctly!")


if __name__ == "__main__":
    test_zero_query_implementation()
