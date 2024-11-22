#PRUEBAS UNITARIAS

# from src.main import ShoppingCart, sum, sub, division
# from src.main import ShoppingCart
# import pytest

# def test_sum():
#     assert sum(1, 2) == 3
    
# def test_sub():
#     assert sub(3,1) ==2
    
# @pytest.mark.parametrize("a, b, expected",[
#     (6,3,2),
#     (10,2,5),
#     (7,2,3.5),
#     (0,5,0),
#     (5,1,5),
# ])

# def test_basic_division(a,b,expected):
#     assert division(a,b)==pytest.approx(expected)

# @pytest.fixture
# def cart():
#     return ShoppingCart()

# def test_add_item(cart):
#     cart.add_item("Apple")
#     assert cart.size() == 1
#     assert "Apple" in cart.get_items()

# def test_add_item_duplicate(cart):
#     cart.add_item("Apple")
#     with pytest.raises(ValueError):
#         cart.add_item("Apple")

# def test_add_item_empty(cart):
#     with pytest.raises(ValueError):
#         cart.add_item("")

# def test_add_item_whitespace(cart):
#     with pytest.raises(ValueError):
#         cart.add_item("   ")

# def test_add_item_non_string(cart):
#     with pytest.raises(TypeError):
#         cart.add_item(123)

# def test_size(cart):
#     cart.add_item("Apple")
#     cart.add_item("Banana")
#     assert cart.size() == 2

# def test_get_items(cart):
#     items = ["Apple", "Banana", "Orange"]
#     for item in items:
#         cart.add_item(item)
#     assert cart.get_items() == items