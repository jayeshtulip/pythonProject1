list1 = [4,5,3,2,1]
for i in range(0,len(list1)-1):
   for j in range(i):
      if list1[j] < list1[j]+1:
         pass
      else:
         temp = list1[j]
         list1[j] = list1[j+1]
         list1[j+1] = temp

print(list1)
