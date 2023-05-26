from faker import Faker

fake = Faker()
list1=[]
dict1={}
for i in range(100):
    name = fake.name()
    address = fake.address()
    list1.append(name)
    list1.append(address)
    dict1[name]= [address]
    #print(f"{name} lives at {address}")
#print(list1)
print(dict1)
for i,j in dict1.items():
    if dict1.keys() == 'Gregory Garcia':
        print("pass")
        print("printing" +  i + ':' + j)
