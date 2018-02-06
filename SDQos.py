# -*- coding: utf-8 -*-  
import os, sys
import time
import server
import tokenBucket
import threading



#搜索空闲服务器
def getfreeserver(tb): 
	tbid=0
	maxtoken=0
	for item in tb:
		if item.get_cur_tokens()>maxtoken:
			maxtoken=item.get_cur_tokens()
			tbid=item.getid()

	return tb[tbid]

#消耗令牌
def consumetoken(tbb,tokennum,id):
	id_old=-1
	curtoken=-1
	if tbb.consume(tokennum):
		curtoken=tbb.get_cur_tokens()
		id_old=id
	else:
		#serverlog.write('server'+str(id)+' IO has been usded up'+'\n')
		while 1: #处理所有服务器IO资源耗尽情况，轮询服务器队列，搜寻空闲服务器
			tbb=getfreeserver(TB)
			if tbb.consume(tokennum):
				curtoken=tbb.get_cur_tokens()
				id_old=id
				id=tbb.getid()
				break;
	return [id_old,id,curtoken]

#控制模块，调整服务当前应用的令牌桶队列
def control(blksize,tb,expectBW,servernum,id):
	tokenperreq=(expectBW/(expectBW*1024/blksize))
	id_old,id,curtoken=consumetoken(TB[id],tokenperreq,TB[id].getid())
	if id_old!=id:
		#tb.remove(TB[id_old])
		tb.append(TB[id])
	return id,curtoken

def pwrite(serverid,appid,blksize,curtoken):
	f=SERVER[serverid].getlog()
	f.write(str(time.asctime(time.localtime(time.time())))+' ,'+appid+' , server'+str(serverid)+' ,'+str(blksize)+'kb ,'+str(curtoken)+'\n')

#应用发起的IO行为
def IO(blksize,totalsize,pattern,tb,expectBW):
	count = totalsize/blksize
	record=0
	countpersec=expectBW*1024/blksize
	time1=time.time()
	while count>0:
		for tbb in tb:
			count = count-1
			record+=1
			id=tbb.getid()
			if(record==countpersec):
				#print record,len(tb)
				time2=time.time()
				if time2-time1 < 1:
					#print 1-(time2-time1)
					print TB[0].get_cur_tokens(),TB[1].get_cur_tokens()
					time.sleep(1-(time2-time1)) #确保一秒内IO请求的时间和令牌生成速度保持同步
					print TB[0].get_cur_tokens(),TB[1].get_cur_tokens()
				time1=time.time()
				record=0
			id,curtoken=control(blksize,tb,expectBW,len(tb),id)
			pwrite(id,pattern,blksize,curtoken)

def application1():
	#compute()
	blksize = 128				#4k
	totalsize = 2*1024*1024 #4GB
	iothread = []
	expectBW = 100.0
	try:
		t = threading.Thread(target=IO,args=(blksize,totalsize,'app1',TB[0:2],expectBW))  #start io request to server 0-1
		t.start()
		if t.isAlive():
			t.join()
	except Exception, e:
		print e
		print 'IO error!'
	
def application2():
	#compute()
	blksize = 128				#kb
	totalsize = 2*1024*1024 #GB
	iothread = []
	expectBW = 100.0
	try:
		t = threading.Thread(target=IO,args=(blksize,totalsize,'app2',TB[0:2],expectBW))  #start io request to server 0-1
		t.start()
		if t.isAlive():
			t.join()
	except Exception, e:
		print e
		print 'IO error!'
	

'''
configure file set application args
'''

def controlplane():
	#while 1:
	pass
		
def dataplane():
	app=[]
	try:
		t = threading.Thread(target=application1)
		app.append(t)
		t = threading.Thread(target=application2)
		app.append(t)
		for th in app:
			th.start()
		for th in app:
			if th.isAlive():
				th.join()
	except:
		print 'start application error!'


SERVER=server.init()
TB=tokenBucket.init(SERVER)


threads = []
if __name__ == "__main__":
	serverlog=open('serverlog.log','w')
	try:
		tc = threading.Thread(target=controlplane)
		threads.append(tc)
	except Exception, e:
		print e
		print 'start contralplane error!'
	try:
		td = threading.Thread(target=dataplane)
		threads.append(td)
	except:
		print 'start dataplane error!'
	for t in threads:
		t.start()
	for t in threads:
		if t.isAlive():
			t.join()
	serverlog.close()
	#for file in f:
	#	file.close()

