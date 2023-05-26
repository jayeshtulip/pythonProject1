# define the Animal class This program defines three classes: Animal, Dog, and Cat.
# The Animal class serves as the base class, and the Dog and Cat classes are derived from it,
# inheriting all of its attributes and methods. The Dog and Cat classes also have their own unique attributes and methods.
#
# When the program is run, it creates instances of the Dog and Cat classes and demonstrates how to access
# the inherited attributes and methods, as well as the subclass-specific attributes and methods.
class Animal:
  def __init__(self, name, species):
    self.name = name
    self.species = species

  def make_sound(self, sound):
    print(f"This animal says {sound}")

# define the Dog class, which inherits from the Animal class
class Dog(Animal):
  def __init__(self, name, breed, toy):
    super().__init__(name, species="Dog") # call the super class's constructor
    self.breed = breed
    self.toy = toy

  def play(self):
    print(f"{self.name} plays with their {self.toy}")

# define the Cat class, which also inherits from the Animal class
class Cat(Animal):
  def __init__(self, name, breed, toy):
    super().__init__(name, species="Cat") # call the super class's constructor
    self.breed = breed
    self.toy = toy

  def play(self):
    print(f"{self.name} plays with their {self.toy}")

# create instances of the Dog and Cat classes
dog1 = Dog("Fido", "Labrador", "Bone")
cat1 = Cat("Fluffy", "Siamese", "String")

# access the inherited attributes and methods
print(dog1.name)
print(dog1.species)
dog1.make_sound("Bark")

# access the inherited attributes and methods
print(cat1.name)
print(cat1.species)
cat1.make_sound("Meow")

# access the subclass-specific attributes and methods
print(dog1.breed)
dog1.play()

# access the subclass-specific attributes and methods
print(cat1.breed)
cat1.play()
