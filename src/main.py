# def sum(x,y):
#     return x+y

# def sub(x,y):
#     return x-y

# def division(x,y):
#     if y==0:
#         raise ValueError("No se puede")
#     return x/y

from typing import List

class ShoppingCart:
    def __init__(self) -> None:
        self.items: List[str] =[]
    
    def add_item(self,item: str):
        if item is None:
            print("Item cannot be None")
            return
        
        if not isinstance(item, str):
            print("Item must be a string")
            return
        
        if not item.strip():
            print("Item cannot be empty or just whitespace")
            return
        
        if item in self.items:
            print("Item already exists in the cart")
            return
        
        self.items.append(item)
        
    def size(self)->int:
        return len(self.items)
    
    def get_items(self)->List[str]:
        print(self.items)
        return 
    
#Asi no se debe de hacer
cart = ShoppingCart()
cart.add_item("book")
cart.add_item("book2")
cart.add_item("book")
cart.add_item("bo ok a")
cart.add_item(None)
cart.get_items()