import requests
import getpass
import json
import time
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

useragent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36'
header={'user-agent':useragent}

# return logged requests.Session
def login(u,p):
	url='https://mora.jp/signin'
	sess=requests.Session()
	s=sess.get(url,headers=header).text
	s1='<input type="hidden" name="'
	s2='" value="'
	s3='"'
	data={
		'failCount':0,
		'returnUrl':'',
		'email':u,
		'password':p
	}
	while s.find(s1)!=-1:
		s=s[s.find(s1)+len(s1):]
		key=s[:s.find(s2)]
		s=s[s.find(s2)+len(s2):]
		val=s[:s.find(s3)]
		data[key]=val
	s=sess.post(url,data=data,headers=header).url
	if s=='https://mora.jp/?signedin=true':
		return sess
	return None

def shellLogin():
	print('Email: ',)
	u=input()
	p=getpass.getpass()
	return login(u,p)

def saveSess():
	global sess
	s=requests.utils.dict_from_cookiejar(sess.cookies)
	json.dump(s,open('cookie.txt','w'))
	logging.info('save sess ok')

def loadSess():
	global sess
	try:
		s=json.load(open('cookie.txt','r'))
		sess=requests.Session()
		sess.cookies=requests.utils.cookiejar_from_dict(s)
	except Exception as e:
		logging.info('loadSess:',e)
		sess=shellLogin()
		saveSess()
	url='https://mora.jp/history'
	if sess.get(url,headers=header).url!=url:
		logging.error('Invalid session!')
		return False
	logging.info('load sess ok')
	return True

def getBoughtList():
	global sess
	url='https://mora.jp/historyPerArtist?page=1'
	s=sess.get(url,headers={'user-agent':useragent,'referer':'https://mora.jp/historyArtist','x-requested-with':'XMLHttpRequest'}).json()
	s=s['kindList'][0]['list']
	#print len(s)
	return s

def getPackageMetaByUrl(url):
	global sess
	s=sess.get(url,headers={'user-agent':useragent}).text
	s1='labelId="'
	s2='materialNo="'
	se='"'
	p=s.find(s1)+len(s1)
	labelId=int(s[p:s.find(se,p)])
	p=s.find(s2)+len(s2)
	materialNo=int(s[p:s.find(se,p)])
	#print(labelId,materialNo)
	url_new='https://cf.mora.jp/contents/package/0000/%08d/%04d/%03d/%03d/packageMeta.jsonp'%(labelId,materialNo//10**6,materialNo//10**3%10**3,materialNo%10**3)
	#print(url_new)
	s=sess.get(url_new,headers={'user-agent':useragent,'x-requested-with':'XMLHttpRequest'}).text
	return json.loads(s[13:-2])

def getPackageMeta(item):
	global sess
	url=item['packageUrl']+'packageMeta.jsonp'
	s=sess.get(url,headers={'user-agent':useragent,'x-requested-with':'XMLHttpRequest'}).text
	return json.loads(s[13:-2])

def _getDownloadLink(item):
	global sess
	url='https://mora.jp/historyArtist'
	s=sess.get(url,headers={'user-agent':useragent}).text
	s1='name="__requestToken" value="'
	s2='"'
	s=s[s.find(s1)+len(s1):]
	token=s[:s.find(s2)]
	logging.info('token: '+token)
	
	s3="download_track('"
	s4="'"
	
	
	
	url='https://mora.jp/downloadBrowser?historyId={}&mediaFormatNo={}&mediaFlg={}&remainCnt={}&__requestToken={}'
	url=url.format(item['purchaseId'],item['mediaFormatNo'],item['mediaFlg'],item['remainDownload'],token)
	
	logging.info(url)
	r=sess.get(url,headers={'user-agent':useragent,'referer':'https://mora.jp/historyArtist'})
	s=r.text
	#open('t2.txt','w').write(s.encode('utf-8'))
	if s3 not in s:
		logging.info('get second page')
		oldurl=url
		
		while True:
			su=sess.get('https://mora.jp/reqDownloadUrlRetry',headers={'user-agent':useragent,'referer':url}).json()
			if su['nextStat']=='history':
				url=''
				break
			if su['nextStat']=='complete':
				s=s[s.find(s1)+len(s1):]
				token=s[:s.find(s2)]
				logging.info('token: '+token)
				url='https://mora.jp/downloadBrowser?waitTimeExpired=false&apiResult=&__requestToken='+token
				break
			time.sleep(1)
		if url!='':
			r=sess.get(url,headers={'user-agent':useragent,'referer':oldurl})
		#print r.status_code
		#print r.url
		s=r.text
	urls=[]
	while s.find(s3)!=-1:
		s=s[s.find(s3)+len(s3):]
		urls.append(s[:s.find(s4)])
	return urls

def getDownloadLink(item):
	while True:
		x=_getDownloadLink(item)
		if x!=[]:
			return x
		logging.info('no links fetched, sleep 2s')
		time.sleep(2)

def getDownloadName(item):
	res=item['artistName']+' - '+item['title']
	res=res.replace('/',' ')
	if len(res)>80:
		return item['title'].replace('/',' ')
	return res

def shellquote(s):
	return "'" + s.replace("'", "'\\''") + "'"

def download(item,check=False,rar=False):
	global sess
	path=os.getcwd()
	sn=getDownloadName(item)
	if os.path.exists('download/'+sn):
		logging.info(sn+' already exists')
		return
	meta=getPackageMeta(item)
	tracklist=meta['trackList']
	os.mkdir('download/'+sn)
	os.chdir('download/'+sn)
	s=getDownloadLink(item)
	id_flag=len(s)==len(tracklist)
	if not id_flag:
		print('use id storage:',getDownloadName(item))
		assert len(s)<len(tracklist) or len(tracklist)==0
	s2=[]
	for i in range(len(s)):
		r=sess.get(s[i],headers=header,allow_redirects=False)
		url=r.headers['Location']
		turl=url[:url.find('?')]
		ext=turl[turl.rfind('.'):]
		s2.append(url)
		id='%02d'%(i+1) if len(s)<100 else '%03d'%(i+1)
		if id_flag:
			s2.append('\tout='+id+'. '+tracklist[i]['title']+ext)
	open('list.txt','wb').write(('\n'.join(s2)).encode('utf-8'))
	os.system('aria2c --file-allocation=none -c -i list.txt -x16 -s16')
	os.unlink('list.txt')
	if check:
		os.system('flac -t *.flac')
	if rar:
		os.chdir('..')
		os.system('rar a -m0 -ma5 -t -rr3 -htb '+shellquote(sn+'.rar')+' '+shellquote(sn+'/'))
	os.chdir(path)

if not loadSess():
	exit()