from mora_api import *

if __name__=='__main__':
	s=getBoughtList()
	#print s[0]
	#exit()
	
	for i in s:
		#print getDownloadName(i)
		download(i,True,True)
	
	#print urls
	#open('t.html','wb').write(r.content)
