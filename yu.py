import numpy as np
from pyFTS import *

class WeightedFLRG(fts.FTS):
	def __init__(self,LHS):
		self.LHS = LHS
		self.RHS = []
		self.count = 1.0

	def append(self,c):
		self.RHS.append(c)
		self.count = self.count + 1.0

	def weights(self):
		tot = sum( np.arange(1.0,self.count,1.0) )
		return np.array([ k/tot for k in np.arange(1.0,self.count,1.0) ])
        
	def __str__(self):
		tmp = self.LHS + " -> "
		tmp2 = ""
		cc = 1.0
		tot = sum( np.arange(1.0,self.count,1.0) )
		for c in self.RHS:
			if len(tmp2) > 0:
				tmp2 = tmp2 + ","
			tmp2 = tmp2 + c + "(" + str(round(cc/tot,3)) + ")"
			cc = cc + 1.0
		return tmp + tmp2
		

class WeightedFTS(fts.FTS):
	def __init__(self,name):
		super(WeightedFTS, self).__init__(1,name)
		
	def generateFLRG(self, flrs):
		flrgs = {}
		for flr in flrs:
			if flr.LHS.name in flrgs:
				flrgs[flr.LHS.name].append(flr.RHS)
			else:
				flrgs[flr.LHS.name] = WeightedFLRG(flr.LHS);
				flrgs[flr.LHS.name].append(flr.RHS)
		return (flrgs)

	def train(self, data, sets):
		self.sets = sets
		tmpdata = common.fuzzySeries(data,sets)
		flrs = common.generateRecurrentFLRs(tmpdata)
		self.flrgs = self.generateFLRG(flrs)
        
	def forecast(self,data):
        l = 1
		
		ndata = np.array(data)
		
		l = len(ndata)
		
		ret = []
		
		for k in np.arange(1,l):
			
			mv = common.fuzzyInstance(ndata[k], self.sets)
		
			actual = self.sets[ np.argwhere( mv == max(mv) )[0,0] ]
        
			if actual.name not in self.flrgs:
				ret.append(actual.centroid)
			else:
				flrg = self.flrgs[actual.name]
				mp = self.getMidpoints(flrg)
				
				ret.append( mi.dot( flrg.weights() ))
			
		return ret
