import os
import shutil
def md(x):
	#print x
	if os.path.exists(x):return
	md(x[:x.rfind('\\')])
	#print x
	#exit()
	os.mkdir(x)
def getfs(x):
	if len(x)>256:return 'naive'
	#print x
	#print type(x)
	#print x.decode('gbk','ignore').encode('gbk','ignore')
	x=x.decode('gbk','ignore')
	md(x[:x.rfind('\\')])
	if not os.path.exists(x):return 0
	return os.stat(x).st_size

cnt=0

def walk(root,root2):
	global cnt
	print 'walk:',root
	if len(root)>256:return
	for i in os.listdir(root):
		path=os.path.join(root,i)
		path2=os.path.join(root2,i)
		if os.path.isdir(path):
			walk(path,path2)
		else:
			cnt+=1
			if cnt%100==0:print cnt,root
			u=getfs(path);v=getfs(path2)
			if v!='naive' and getfs(path)!=getfs(path2):
				print 'copy:',path,path2
				#exit()
				shutil.copyfile(path,path2)


a=raw_input()
b=raw_input()

walk(a,b)