from config.setting import BASE_URL


class Urls:
    BASE_URL = BASE_URL
    LOGIN_URL = f"{BASE_URL}/login"
    PRODUCT_URL = f"{BASE_URL}/products"
    CART_URL = f"{BASE_URL}/view_cart"
    TEST_CASES_URL = f"{BASE_URL}/test_cases"
    API_TESTING_URL = f"{BASE_URL}/api_list"
    CONTACT_US_URL = f"{BASE_URL}/contact_us"