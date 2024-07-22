from enum import Enum
from abc import ABC, abstractmethod
from threading import Lock


class Coin(Enum):
  ONE = 1
  TWO = 2
  FIVE = 5


class Note(Enum):
  TEN = 10
  TWENTY = 20
  FIFTY = 50
  HUNDRED = 100


class Product:

  def __init__(self, name, price) -> None:
    self.name = name
    self.price = price


class Inventory:

  def __init__(self) -> None:
    self.products = {}

  def add_product(self, product: Product, qty):
    self.products[product] = qty

  def remove_product(self, product: Product):
    del self.products[product]

  def update_product(self, product: Product, qty):
    self.products[product] = qty

  def get_quantity(self, product: Product):
    return self.products.get(product, 0)

  def is_available(self, product: Product):
    return product in self.products and self.get_quantity(product) > 0


class VendingMachine:
  _instance = None
  _lock = Lock()

  def __new__(cls):
    with cls._lock:
      if not cls._instance:
        cls._instance = super().__new__(cls)
        cls._instance.inventory = Inventory()
        cls._instance.idle_state = IdleState(cls._instance)
        cls._instance.ready_state = ReadyState(cls._instance)
        cls._instance.dispense_state = DispenserState(cls._instance)
        cls._instance.return_change_state = ReturnChangeState(cls._instance)
        cls._instance.current_state = cls._instance.idle_state
        cls._instance.selected_product = None
        cls._instance.total_payment = 0
    return cls._instance

  @classmethod
  def get_instance(cls):
    return cls()

  def select_product(self, product: Product):
    self.current_state.select_product(product)

  def insert_coin(self, coin: Coin):
    self.current_state.insert_coin(coin)

  def insert_note(self, note: Note):
    self.current_state.insert_note(note)

  def dispense_product(self):
    self.current_state.dispense_product()

  def return_change(self):
    self.current_state.return_change()

  def set_state(self, state):
    self.current_state = state

  def add_coin(self, coin: Coin):
    self.total_payment += coin.value

  def add_note(self, note: Note):
    self.total_payment += note.value

  def reset_payment(self):
    self.total_payment = 0

  def reset_seleted_product(self):
    self.selected_product = None

class VendingMachineState(ABC):

  @abstractmethod
  def select_product(self, product: Product):
    pass

  @abstractmethod
  def insert_coin(self, coin: Coin):
    pass

  @abstractmethod
  def insert_note(self, note: Note):
    pass

  @abstractmethod
  def dispense_product(self):
    pass

  @abstractmethod
  def return_change(self):
    pass


class IdleState(VendingMachineState):

  def __init__(self, vending_machine: VendingMachine):
    self.vending_machine = vending_machine

  def select_product(self, product: Product):
    if self.vending_machine.inventory.is_available(product):
      self.vending_machine.set_state(self.vending_machine.ready_state)
      print(f"Product selected: {product.name}")
      self.vending_machine.selected_product = product
    else:
      print("Product not available")

  def insert_coin(self, coin: Coin):
    print('Select product first plz')

  def insert_note(self, note: Note):
    print('Select product first plz')
    
  def dispense_product(self):
    print('Select product first plz & make payment')

  def return_change(self):
    print('Nothing to return')


class ReadyState(VendingMachineState):

  def __init__(self, vending_machine: VendingMachine):
    self.vending_machine = vending_machine

  def select_product(self, product: Product):
    print('Product selected , now pay plz')

  def insert_coin(self, coin: Coin):
    self.vending_machine.add_coin(coin)
    print('Coin {} inserted'.format(coin.name))
    self.check_payment_status()

  def insert_note(self, note: Note):
    self.vending_machine.add_note(note)
    print('Note {} inserted'.format(note.name))
    self.check_payment_status()

  def dispense_product(self):
    print('Plz pay first')

  def return_change(self):
    print('Plz pay first')

  def check_payment_status(self):
    if self.vending_machine.total_payment >= self.vending_machine.selected_product.price:
      self.vending_machine.set_state(self.vending_machine.dispense_state)
      

class DispenserState(VendingMachineState):

  def __init__(self, vending_machine: VendingMachine):
    self.vending_machine = vending_machine

  def select_product(self, product: Product):
    print('Plz collect selected product')

  def insert_coin(self, coin: Coin):
    print('Plz collect selected product. Payment Done.')

  def insert_note(self, note: Note):
    print('Plz collect selected product. Payment Done.')

  def dispense_product(self):
    product = self.vending_machine.selected_product
    self.vending_machine.inventory.update_product(product,self.vending_machine.inventory.get_quantity(product) - 1)
    print(f"Product dispensed: {product.name}")
    self.vending_machine.set_state(self.vending_machine.return_change_state)

  def return_change(self):
    print('Plz collect selected product first.')


class ReturnChangeState(VendingMachineState):

  def __init__(self, vending_machine: VendingMachine):
    self.vending_machine = vending_machine

  def select_product(self, product: Product):
    print("Please collect the change first.")

  def insert_coin(self, coin: Coin):
    print("Please collect the change first.")

  def insert_note(self, note: Note):
    print("Please collect the change first.")

  def dispense_product(self, product: Product):
    print("Please collect the change first.")

  def return_change(self):
    change = self.vending_machine.total_payment - self.vending_machine.selected_product.price
    if change > 0:
      print(f"Returning change: {change}")
      self.vending_machine.reset_payment()
    else:
      print('No change to return')
    self.vending_machine.reset_seleted_product()
    self.vending_machine.set_state(self.vending_machine.idle_state)

class VendingMachineDemo:
  @staticmethod
  def run():
      vending_machine = VendingMachine.get_instance()

      # Add products to the inventory
      coke = Product("Coke", 18)
      pepsi = Product("Pepsi", 15)
      water = Product("Water", 10)

      vending_machine.inventory.add_product(coke, 5)
      vending_machine.inventory.add_product(pepsi, 3)
      vending_machine.inventory.add_product(water, 2)

      # Select a product
      vending_machine.select_product(coke)

      # Insert coins
      vending_machine.insert_coin(Coin.FIVE)
      vending_machine.insert_coin(Coin.TWO)
      vending_machine.insert_coin(Coin.TWO)
      vending_machine.insert_coin(Coin.ONE)

      # Insert a note
      vending_machine.insert_note(Note.TEN)

      # Dispense the product
      vending_machine.dispense_product()

      # Return change
      vending_machine.return_change()

      # Select another product
      vending_machine.select_product(pepsi)

      # Insert insufficient payment
      vending_machine.insert_coin(Coin.FIVE)
      vending_machine.insert_coin(Coin.FIVE)

      # Try to dispense the product
      vending_machine.dispense_product()

      # Insert more coins
      vending_machine.insert_coin(Coin.TWO)
      vending_machine.insert_coin(Coin.TWO)
      vending_machine.insert_coin(Coin.TWO)
  

      # Dispense the product
      vending_machine.dispense_product()

      # Return change
      vending_machine.return_change()

if __name__ == "__main__":
  VendingMachineDemo.run()