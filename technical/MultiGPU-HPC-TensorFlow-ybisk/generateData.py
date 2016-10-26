
data = open("data.txt",'w')
num_examples = 100000
for i in range(num_examples):
  data.write('{0:08b}'.format(i) + " " + ("01\n" if i%2 ==0 else "10\n"))
data.close()
