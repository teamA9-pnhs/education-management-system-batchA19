import string,random,os
id =0 
id1= 100

os.remove('data.txt')
f = open('data.txt', 'w')
n = int(input( "Enter the number of students required :"))

while n != 0: 
    email1 = random.randint(3,8)
    email= ''.join(random.choices(string.ascii_lowercase , k = email1))
    email += "@gmail.com"

    id +=1

    usn = "2SD18CS"+ str(random.randint(0,9))+ str(random.randint(0,9))+str(random.randint(0,9))

    name1 = random.randint(3,10)
    name = ''.join(random.choices(string.ascii_lowercase , k = name1)) +" "+ ''.join(random.choices(string.ascii_lowercase , k = email1))

    id1+=1

    sex1 = [ "Male","Female"]
    sex = random.choice(sex1)

    line = str(id) +"\t" + name+  "\t" + usn + "\t" + str(id1)+ "\t" + email + "\t" + sex

    print("Created")
    n=n-1
    f.write( line + "\n" )

f.close()
print("DONE")

