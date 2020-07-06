import sys
from langconv import *

for t in sys.argv:
	if t!='tra2sim.py':
		with open(t,'r') as f:
			s=f.read()
		s=s.decode('utf-8')
		res=''
		block=10000
		for i in range((len(s)+block-1)/block):
			res+=Converter('zh-hans').convert(s[block*i:min(block*(i+1),len(s))])
		with open(t,'w') as f:
			f.write(res.encode('utf-8'))