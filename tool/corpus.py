#!/usr/bin/env python
# coding:utf8

import sys 
reload(sys)
sys.setdefaultencoding('utf8')
import re

class CorpusGenerator(object):
	def __init__(self, content='', maxlen=5, topK=-1, tfreq=100, tDOA=2, tDOF=2):
		'''
			content: 待成词的文本
			maxlen: 词的最大长度
			topK: 返回的词数量
			tfreq: 频数阈值
			tDOA: 聚合度阈值
			tDOF: 自由度阈值
		'''
		self.content = content
		self.maxlen = maxlen
		self.topK = topK
		self.tfreq = tfreq
		self.tDOA = tDOA
		self.tDOF = tDOF
		self.result = {}

	def get_characters(self):
		# 输入文本，输出全部的单字
		characters = []
		reg = ur'[\u4e00-\u9fa5]'
		reg = re.compile(reg)
		reg = list(set(reg.findall(self.content)))
		for r in reg:
			characters.append(r)
		return characters		

	def get_possible_words(self, characters):
		# 输出以每个单字开始的全部可能词语
		possible_words = []
		for item in characters:
			for x in xrange(0, len(self.content)):
				if self.content[x] == item:
					for n in xrange(0, self.maxlen):
						# 判断是否超出范围
						if x + n < len(self.content):
							# 判断是否包含非汉字
							flag = True
							for i in xrange(0, n + 1):
								if self.content[x + i] < u'\u4e00' or self.content[x + i] > u'\u9fa5':
									flag = False
									break
							if not flag:
								continue
							tw = self.content[x:x + n + 1]
							if not tw in possible_words:
								possible_words.append(tw)
		for p in possible_words:
			self.result[p] = {}
		return possible_words

	def get_frequency(self, possible_words):
		# 统计每个可能词语出现的次数
		for item in possible_words:
			count = 0
			offset = 0
			while True:
				idx = self.content.find(item, offset)
				if idx == -1:
					break
				else:
					count += 1
					offset = idx + len(item)
			self.result[item]['freq'] = count

	def get_doa(self, possible_words):
		# 统计每个词语的聚合度
		for item in possible_words:
			if len(item) == 1:
				self.result[item]['doa'] = 1
				continue
			doa = 99999
			for x in xrange(1, len(item)):
				pa = float(self.result[item]['freq']) / len(self.content)
				pl = float(self.result[item[:x]]['freq']) / len(self.content)
				pr = float(self.result[item[x:]]['freq']) / len(self.content)
				td = pa / (pl * pr)
				if td < doa:
					doa = td
			self.result[item]['doa'] = doa
		
