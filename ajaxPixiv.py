import sys
import requests
import os
import time
import datetime

# 代理设置
proxies={
	'http':'127.0.0.1:1280',
	'https':'127.0.0.1:1280'
}

# 屏蔽warning信息，因为下面verify=False会报警告信息
requests.packages.urllib3.disable_warnings()

def download(url, file_path,headers_dl):
	start2 = datetime.datetime.now()
	# 第一次请求是为了得到文件总大小
	r1 = requests.get(url, proxies=proxies, stream=True, verify=False, headers=headers_dl)
	total_size = int(r1.headers['Content-Length'])
	# print(r1.headers,r1.status_code)

	# 这重要了，先看看本地文件下载了多少
	if os.path.exists(file_path):
		temp_size = os.path.getsize(file_path)  # 本地已经下载的文件大小
	else:
		temp_size = 0
	# 显示一下下载了多少   
	#print(temp_size)
	#print(total_size)
	dlspeed = 0
	dltime = time.time()
	# 核心部分，这个是请求下载时，从本地文件已经下载过的后面下载
	headers = {'Range': 'bytes=%d-' % temp_size}  
	# 重新请求网址，加入新的请求头的
	r = requests.get(url, proxies=proxies, stream=True, verify=False, headers=headers_dl)

	# 下面写入文件也要注意，看到"ab"了吗？
	# "ab"表示追加形式写入文件
	with open(file_path, "ab") as f:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk:
				temp_size += len(chunk)
				f.write(chunk)
				f.flush()
				
				###这是下载实现进度显示####
				done = int(50 * temp_size / total_size)
				### sys.stdout.write("\r[%s%s] %d%%" % ('█' * done, ' ' * (50 - done), 100 * temp_size / total_size))
				sys.stdout.write("\r[%s%s] %d%% %dKb|%dKb" % ('-' * done, '_' * (50 - done), 100 * temp_size / total_size,temp_size / 1024 ,total_size / 1024))
				### sys.stdout.write("\r%dKb %dKb" % (temp_size / 1024 ,total_size / 1024))
	print()  # 避免上面\r 回车符
	end2 = datetime.datetime.now()
	t1 = (end2 - start2).seconds
	print('下载用时:',str(t1) + "s","平均下载速度(大约):",str('%.2fKb/s'%((total_size / 1024)/t1)))

headers = {
	'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
}

if __name__ == '__main__':
	# https://www.pixiv.net/ajax/illust/
	# url='http://127.0.0.1:90/2.json'
	if len(sys.argv) > 2:
		if sys.argv[1] == 'url':
			str1 = sys.argv[2]
			spl = str1.split('/')
			ids = spl[len(spl)-1]
		elif sys.argv[1] == 'id':
			ids = sys.argv[2]
		else:
			print('没有类型!')
	
		print('id',ids)
		url = 'https://www.pixiv.net/ajax/illust/' + ids
		print('正在获取信息...')
		r = requests.get(url,proxies=proxies,headers=headers,verify=False) #发get请求
		print('状态码',r.status_code)
		
		refs = 'https://www.pixiv.net/artworks/' + ids
		
		# 图片保存目录
		savePath = os.path.abspath('.')
		print('下载路径:',savePath)
		
		# 头部
		headersdl = {
			'accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
			'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
			'referer': refs,
		}
		
		jl = r.json()
		#print(r.json())#将返回的json串转为字典

		print('页数',jl['body']['pageCount'])
		print('作者',jl['body']['userName'])
		print('标题',jl['body']['title'])
		print(' ')
		print('标签')
		for i in jl['body']['tags']['tags']:
			print(' ',i['tag'])
		print(' ')
		print('说明',jl['body']['description'])
		print(' ')
		
		iurl = jl['body']['urls']['original']
		urlList = []
		fileNList = []
		
		count = 0
		
		while count < jl['body']['pageCount']:
			c = iurl
			urlList.append(c.replace("p0", "p" + str(count),1))
			#print(urlList[count])
			spl = urlList[count].split('/')
			fileNList.append(spl[len(spl)-1])
			#print('文件名',fileNList[count])
			count = count + 1
			
		count = 0
		start = datetime.datetime.now()
		for i in urlList:
			print(' ')
			print('正在下载',count + 1,'/',len(urlList))
			download(urlList[count], os.path.join(savePath,fileNList[count]),headersdl)
			count = count + 1
		
		end = datetime.datetime.now()
		print(' ')
		print('全部下载完成')
		print('下载用时: ' + str((end - start).seconds) + "s")
		'''
		str1 = r'http://127.0.0.1:90/pixiv/79014502_p0.jpg'
		spl = str1.split('/')
		print(spl,len(spl),spl[len(spl)-1])
		'''
		#download(r'http://127.0.0.1:90/pixiv/79014502_p0.jpg',r'D:\Python\79014502_p0.jpg',headersdl)
	else:
		print('参数不正确')
