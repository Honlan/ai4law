#!/usr/bin/env python
# coding:utf8

import sys 
reload(sys)
sys.setdefaultencoding('utf8')
import warnings
warnings.filterwarnings("ignore")
import regex as re
import numpy as np
import math

class CorpusGenerator(object):
	def __init__(self, content='', maxlen=10, topK=-1, tfreq=10, tDOA=0, tDOF=0):
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
		# 输出全部的单字
		characters = []
		reg = ur'[\u4e00-\u9fa5]'
		reg = list(set(re.findall(reg, self.content, overlapped=True)))
		for r in reg:
			characters.append(r)
		return characters		

	def get_possible_words(self):
		# 输出全部的可能的词语，最大长度为maxlen
		possible_words = []
		for x in xrange(0, self.maxlen):
			reg = ur'[\u4e00-\u9fa5]{' + unicode(x + 1) + '}'
			reg = list(set(re.findall(reg, self.content, overlapped=True)))
			for r in reg:
				possible_words.append(r)
		return possible_words

	def get_frequency(self):
		# 统计每个可能词语出现的频数
		print 'Calculate Frequency for each possible words'
		for x in xrange(0, self.maxlen):
			reg = ur'[\u4e00-\u9fa5]{' + unicode(x + 1) + '}'
			reg = re.findall(reg, self.content, overlapped=True)
			for r in reg:
				if self.result.has_key(r):
					self.result[r]['freq'] += 1
				else:
					self.result[r] = {'left':[], 'right':[]}
					self.result[r]['freq'] = 1

	def get_doa(self, base=2):
		# 使用信息熵衡量每个词语的聚合度
		print 'Calculate DOA for each possible words'
		for key, value in self.result.items():
			if len(key) == 1:
				self.result[key]['doa'] = 0
				continue
			doa = 99999
			for x in xrange(1, len(key)):
				try:
					pa = float(self.result[key]['freq']) / len(self.content)
					pl = float(self.result[key[:x]]['freq']) / len(self.content)
					pr = float(self.result[key[x:]]['freq']) / len(self.content)
					td = math.log(pa / (pl * pr), base)
					if td < doa:
						doa = td
				except Exception, e:
					print e, Exception
				else:
					pass
				finally:
					pass
			self.result[key]['doa'] = doa

	def get_dof(self):
		# 使用信息熵衡量每个词语的自由度
		print 'Calculate DOF for each possible words'
		for x in xrange(0, self.maxlen):
			reg = ur'(\S)([\u4e00-\u9fa5]{' + unicode(x + 1) + '})(\S)'
			reg = re.findall(reg, self.content, overlapped=True)
			for r in reg:
				self.result[r[1]]['left'].append(r[0])
				self.result[r[1]]['right'].append(r[2])
		for key, value in self.result.items():
			left = self.get_entropy(value['left'])
			right = self.get_entropy(value['right'])
			if left < right:
				self.result[key]['dof'] = left
			else:
				self.result[key]['dof'] = right

	def get_entropy(self, data, base=2):
		tmp = {}
		for item in data:
			if not tmp.has_key(item):
				tmp[item] = 1.0
			else:
				tmp[item] += 1.0
		for key, value in tmp.items():
			tmp[key] /= float(len(data))
		result = 0.0
		for key, value in tmp.items():
			result += value * math.log(value, base)
		if result < 0:
			result = -result
		return result

	def get_score(self):
		# 将频数、聚合度、自由度归一化，并计算总得分
		print 'Calculate Score for each possible words'
		for key, value in self.result.items():
			if value['freq'] <= self.tfreq or value['doa'] <= self.tDOA or value['dof'] <= self.tDOF:
				self.result[key]['score'] = 0
			else:	
				self.result[key]['score'] = value['freq'] * value['doa'] * value['dof']

	def distribution(self):
		# 绘制频数、聚合度、自由度分布
		import pandas as pd
		import matplotlib
		import matplotlib.pyplot as plt
		matplotlib.use('TkAgg')
		import seaborn as sns
		sns.set(style="white", color_codes=True)

		df = []
		for key, value in self.result.items():
			df.append([value['freq'], value['doa'], value['dof']])
		df = pd.DataFrame(data=df, columns=['frequency', 'doa', 'dof'])
		sns.pairplot(df)
		plt.show()
		
	def generate(self):
		self.get_frequency()
		self.get_doa()
		self.get_dof()
		self.get_score()
		result = sorted(self.result.items(), key=lambda d:d[1]['score'], reverse=True)
		if self.topK == -1:
			return result
		else:
			return result[:self.topK]

