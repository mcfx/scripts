import os

def get_pattern():
	x=input()
	p=x.find('*')
	return (x[:p],x[p+1:])

def match_pattern(x,y):
	p=x.find(y[0])
	if p==-1:return False
	p+=len(y[0])
	t=x.find(y[1],p)
	if t==-1:return False
	return x[p:t]

def get_file(x):
	p=0
	while x.find('.',p)!=-1:
		p=x.find('.',p)+1
	return (x[:p-1],x[p:])

sa=input()
sb=input()

pa=get_pattern()
pb=get_pattern()

d={}
for i in os.listdir(sa):
	if match_pattern(i,pa)!=False:
		d[match_pattern(i,pa)]=get_file(i)[0]

#for i in d:
#	print i,d[i]

tasks=[]

for i in os.listdir(sb):
	if match_pattern(i,pb)!=False:
		t=match_pattern(i,pb)
		if t in d:
			tasks.append((i,d[t]+'.'+get_file(i)[1]))

for i in tasks:
	print(i[0]+' => '+i[1])

print('Are you sure? (Y/n)')
t=input()
if t=='Y' or t=='y' or t=='':
	for i in tasks:
		os.rename(sb+'/'+i[0],sb+'/'+i[1])
		print(i[0]+' => '+i[1])

print('Press enter to exit')
input()