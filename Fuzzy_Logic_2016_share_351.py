#  Author:  Robin W. Dawes

# 20130707 - bulk of definitions completed
# 20130820 - added NOT

# 20140801 - minor improvements

# 20160204 - fixed "OR"

# 201604014 - modified to run on Python 3.5.1 by Alec Robinson

from math import *

#t_norm = min
#s_norm = max

VERBOSE = False			# setting VERBOSE to True produces tons of diagnostic output
		
class Clause(object):
	# a clause consists of a set of pairs.  Each pair consists of a variable name and a Piecewise_Function() object
	# Clauses are treated as disjunctions for the purpose of evaluation
	
	
	def __init__(self, pairs = []):
		self.terms = {}	# terms is a dictionary that associates piecewise functions with variable names
		for v,f in pairs:
			if v in self.terms:
				self.terms[v].append[f]
			else:
				self.terms[v] = [f]
		
	def Clause_eval(self, vals, s_norm = max):
		# vals is a dictionary of variable names and values
		# it must contain a value for each variable in the self.terms dictionary
		
		fv_list = []
		for v in self.terms:
			for f in self.terms[v]:
			#	print (v,vals[v],self.terms[v].pairs)
				fv_list.append(f.PWF_eval(vals[v])) 
		#print ("function values",fv_list)
		#print ("applying s_norm gives",s_norm(fv_list))
		return s_norm(fv_list)	
		
	# end of Clause class definition	
		
class Rule(object):
	# a rule consists of a set of clauses (antecendents) and a consequent
	# each clause is a disjunction
	# the rule is treated as a conjunction (ie it is in CNF)
	# the consequent is a Piecewise_Function()
	# default action is to clip the consequent

	@staticmethod
	def listify(*args):
		v_list = []
		for x in args:
			if hasattr(x, '__iter__'):
				for z in x:
					v_list.append(z)
			else:
				v_list.append(x)
		return v_list


	@staticmethod
	def dual(f,x,y):
		return 1 - f(1-x,1-y)

# t-norm definitions
	@staticmethod
	def Product(*args):
		v_list = Rule.listify(*args)
		p = v_list[0]
		for v in v_list[1:]:
			p *= v
		return p
		
	@staticmethod
	def Lukasiewics(*args):
		v_list = Rule.listify(*args)
		L = v_list[0]
		for v in v_list[1:]:
			L = max(0,L+v - 1)
		return L

	@staticmethod
	def Drastic_t(*args):
		v_list = Rule.listify(*args)
		D = v_list[0]
		for v in v_list[1:]:
			if max(D,v) == 1:
				D = min(D,v)
			else:
				D = 0
		return D
		
	@staticmethod
	def Nilpotent_min(*args):
		v_list = Rule.listify(*args)
		N = v_list[0]
		for v in v_list[1:]:
			if N+v > 1:
				N = min(N,v)
			else:
				N = 0
		return N

	@staticmethod
	def Hamacher_prod(*args):
		v_list = Rule.listify(*args)
		H = v_list[0]
		for v in v_list[1:]:
			if (H == 0) and (v == 0):
				H == 0
			else:
				H = H*v*1.0/(H + v - H*v)
		return H
		
# s-norm definitions
	@staticmethod
	def Probabilistic_sum(*args):
		v_list = Rule.listify(*args)
		P = v_list[0]
		for v in v_list[1:]:
			P = P + v - P*v
		return P

	@staticmethod
	def Bounded_sum(*args):
		v_list = Rule.listify(*args)
		B = v_list[0]
		for v in v_list[1:]:
			B = min(B + v, 1)
		return B

	@staticmethod
	def Drastic_s(*args):
		v_list = Rule.listify(*args)
		D = v_list[0]
		for v in v_list[1:]:
			if min(D,v) == 0:
				D = max(D,v)
			else:
				D = 1
		return D

	@staticmethod
	def Nilpotent_max(*args):
		v_list = Rule.listify(*args)
		N = v_list[0]
		for v in v_list[1:]:
			if N + v < 1:
				N = max(N,v)
			else:
				N = 1
		return N
		
	@staticmethod
	def Einstein_sum(*args):
		v_list = Rule.listify(*args)
		E = v_list[0]
		for v in v_list[1:]:
			E = (E+v)*1.0/(1 + E*v)
		return E
	
	
	# instance methods
	
	def __init__(self, name = "",clauses = [], consequent = None, t_norm= min, s_norm = max):
		self.name = name
		self.clauses = clauses[:]
		self.consequent = consequent
		self.implication = consequent.PWF_clip
		self.t_norm = t_norm
		self.s_norm = s_norm
		
	def scale(self):
		# change the implication action to scaling
		self.implication = self.consequent.PWF_scale
		
	def apply(self, vals, t_norm = min):  #AR current, using Lukasiewics instead of 'min'
		# apply this rule
		
		# vals is a dictionary of variable names and values
		
		if VERBOSE: 
			print ("\nApplying",self.name)
		
		# evaluate all the clauses
		cv_list = []
		for c in self.clauses:
			cv_list.append(c.Clause_eval(vals, s_norm = self.s_norm))
		if VERBOSE: 
			print ("Clause values",cv_list)	
			
		# compute the combined value of the clauses
		x = self.t_norm(cv_list)
	
		
		# report that the rule has been activated - this is really just for demonstration
		# and testing
		if x > 0:
			print ("\t\t",self.name,"rule activated")
		if VERBOSE:
			self.consequent.display()
			print ("Truth value of antedents",x)
			
		# apply the combined value of the clauses to the consequent	
		o_f = self.implication(x)
		if VERBOSE: 
			print ("Resultant consequent")
			o_f.display()
		return o_f
		
		
# end of Rule class definition		
		
class Rule_Set(object):
	# each instance contains a set of rules
	# each rule's consequent is a fuzzy set for the same variable
	
	
	# instance methods
	
	def __init__(self):
		self.rules = []
		
	def add_rule(self,new_rule = None):
		self.rules.append(new_rule)
		
	def resolve(self,vals):
		# vals is a dictionary of variable names and values
		# resolve the rules using Centre of Mass method:
		#      find the centre of area for the output function for each rule
		#      take the weighted average of those centres of area
		
		# apply each rule
		fuzzy_consequents = []
		for r in self.rules:
			#print ("Applying",r.name)
			x = r.apply(vals)
			#print ("Rule_Set.resolve received",)
			#x.display()
			fuzzy_consequents.append(x)
			
		#print ("fuzzy_consequents has",len(fuzzy_consequents),"elements")
		#print (fuzzy_consequents)
		coas = []	
		# find the coa and total area of the output from each rule
		if VERBOSE:
			print ("Modified consequent functions")
		for c in fuzzy_consequents:
			if VERBOSE: 
				c.display()
				print ("coa = ",c.PWF_coa())
			coas.append(c.PWF_coa())
		weighted_sum, sum_of_weights = 0,0	
		# find the combined coa of all the rules
		if VERBOSE:
			print ("coas = ",coas)
		for x,w in coas:
			weighted_sum += x*w
			sum_of_weights += w
		if sum_of_weights == 0:
			return None
		else:
			return weighted_sum*1.0/sum_of_weights
			
	# end of Rule_Set class Definition		
		
class Piecewise_Function(object):
	
	POS_INF = 10000
	NEG_INF = -POS_INF
	
	
	@staticmethod
	def area(x1,x2,y1,y2):
		# assumes x1 <= x2
		# returns area of the quadrilateral
		return abs((x2 - x1)*(y2 + y1)/2.0)
	
	@staticmethod
	def quadratic(a,b,c):
		# find roots of a*x^2 + b*x + c
		if a == 0:
			if b == 0:
				return None
			else:
				return [-c*1.0/b]
		elif b*b < 4*a*c:
			return None
		else:
			return ( (-b + sqrt(b*b - 4.0*a*c))/(2.0*a), (-b - sqrt(b*b - 4.0*a*c))/(2.0*a) )
		
	@staticmethod
	def centre_of_area(x1,x2,y1,y2):
		# assumes x1 <= x2
		# returns x co-ordinate of balance point for the quadrilateral with corners (x1,0), (x2,0), (x2,y2), (x1,y1)
		if x1 == x2:
			return x1
		else:
			if y1 == y2:
				return (x1+x2)*1.0/2
			delta_x = (x2 - x1)*1.0
			delta_y = (y2 - y1)*1.0
			a = delta_y/delta_x
			b = 2.0*(y1 - x1*delta_y/delta_x)
			c = x1*x1*delta_y/delta_x - 2.0*x1*y1 - delta_x*(y1+y2)/2.0
			#print a,b,c,quadratic(a,b,c)
			s = Piecewise_Function.quadratic(a,b,c)
			if s == None:
				#return None
				return 0
			elif len(s) == 1:
				return s[0]
			elif (x1 <= s[0]) and (s[0] <= x2):
				return s[0]
			else:
				return s[1]
		

	# instance methods
	
	def __init__(self,name='',pairs=[]):
		self.name = name
		# make sure that the y value in the first pair is 0
		#~ if pairs[0][1] != 0:
			#~ self.pairs = [(pairs[0][0]-0.001,0)]
			#~ self.pairs.extend(pairs[:])
		#~ else:
			#~ self.pairs=pairs[:]
		#~ #print "in init, just before checking final pair, self.pairs = ",self.pairs	
		#~ # make sure that the y value in the last pair is 0
		#~ if pairs[-1][1] != 0:
			#~ self.pairs.append( (pairs[-1][0]+0.001,0) )
		if pairs[0][0]  != Piecewise_Function.NEG_INF:
			self.pairs = [(Piecewise_Function.NEG_INF,pairs[0][1])]
			self.pairs.extend(pairs[:])
		else:
			self.pairs = pairs[:]
		if self.pairs[-1][0] != Piecewise_Function.POS_INF:
			self.pairs.append((Piecewise_Function.POS_INF,self.pairs[-1][1]))
		
	def NOT(self):
		# create the inverse function
		# this function is still under development and should be used with extreme caution
		not_name = "NOT_"+self.name
		not_pairs = []
		
		
		for p in self.pairs:
			not_pairs.append((p[0],1-p[1]))
			
		#print "in NOT, not_pairs =",not_pairs	
		return Piecewise_Function(name=not_name,pairs = not_pairs)
		
	def display(self):
		print (self.name, self.pairs)
		
	def PWF_eval(self,x):
		if len(self.pairs) == 0:
			return 0
		else:
			if x <= self.pairs[0][0]:
				return self.pairs[0][1]
			else:
				prev_x,prev_y = self.pairs[0]
				for cur_x,cur_y in self.pairs[1:]:
					if x <= cur_x:
						return prev_y + 1.0* (cur_y - prev_y) * (x - prev_x) / (cur_x - prev_x)
					else:
						prev_x,prev_y = cur_x,cur_y
				return self.pairs[-1][1]
				
	def PWF_area(self):
		# computes and returns the area under the function
		if VERBOSE:
			print (self.name,"evaluating area")
		a = 0
		prev_x,prev_y = self.pairs[0]
		for x,y in self.pairs[1:]:
			a += Piecewise_Function.area(prev_x,x,prev_y,y)
			prev_x,prev_y = x,y
		if VERBOSE:
			print (a)
		return a
				
	def PWF_clip(self,c):
		# Assumption: all functions are 0 at the extremities
		#print ("Clipping",self.name)
		#print ("pairs",self.pairs)
		#print ("clipping value",c)
		if c == 0:
			return Piecewise_Function(name = self.name+"_Clipped",pairs = [(Piecewise_Function.NEG_INF,0),(Piecewise_Function.POS_INF,0)])
		else:
			# modify this so that if the first pair is (NEG_INF,y) and y > c, things are handled
			# appropriately (first pair becomes (NEG_INF,c).  Similarly if the last pair is (POS_INF,y) and y > c, 
			# then the last pair becomes (POS_INF,c)
			
			# all functions will have a (NEG_INF,y) pair first, and a (POS_INF,y) pair last
			
			n_p = [(self.pairs[0][0],self.pairs[0][1])]
			if n_p[0][1] > c:
				# function is clipped at NEG_INF
				n_p[0]= (Piecewise_Function.NEG_INF,c)
				prev_x,prev_y = n_p[0]
				i = 1
				while i < len(self.pairs):
					x,y = self.pairs[i]
					if y < c:
						# crossed the clipping line
						xc = prev_x + 1.0*(c - prev_y)*(x - prev_x)/(y - prev_y)
						n_p.append((xc,c))
						break
					else:
						i += 1
						prev_x,prev_y = x,y
				prev_x,prev_y =n_p[-1]
			else:
				i = 1
			# 3 possibilities:
			#    	- NEG_INF point is <= c:
			#		this point is in n_p, and i = 1		
			#	- all points are > c:
			#		(NEG_INF,c) added, (POS_INF,c) still to be added
			#	- NEG_INF point was > c:
			#		we have just added the first un-clipped point
			#		- this case is the same as case 1
			while i < len(self.pairs):
				#print ("n_p",n_p)
				x,y = self.pairs[i]
				#print ("current point",x,y)
				if y > c:
					# compute point between last point in n_p and this point where the function
					# achieves c
					xc = prev_x + 1.0*(c - prev_y)*(x - prev_x)/(y - prev_y)
					n_p.append((xc,c))
					#print "n_p with new point added",n_p
					while (i < len(self.pairs)) and (self.pairs[i][1] >= c):
						#print ("stepping past point",self.pairs[i])
						prev_x,prev_y = self.pairs[i]
						i += 1
					if i < len(self.pairs):
						# previous point was >= c, this one is < c ... find the cross-over
						#(print "now looking at",self.pairs[i])
						x,y = self.pairs[i]
						#(print "prev_x,prev_y",prev_x,prev_y)
						xc = prev_x + 1.0*(c - prev_y)*(x - prev_x)/(y - prev_y)
						n_p.append((xc,c))
				else:
					n_p.append(self.pairs[i])
					prev_x,prev_y = self.pairs[i]
					i += 1
			# add POS_INF point to n_p, if necessary
			if n_p[-1][0] != Piecewise_Function.POS_INF:
				# add the POS_INF point
				if self.pairs[-1][1] <= c:
					n_p.append((Piecewise_Function.POS_INF,self.pairs[-1][1]))
				else:
					n_p.append((Piecewise_Function.POS_INF,c))
				
			
						
			return Piecewise_Function(name=self.name+"_Clipped",pairs=n_p)
		
	def PWF_scale(self,s):
		n_p = []
		for x,y in self.pairs:
			n_p.append((x,y*s))
		return Piecewise_Function(n_p)
		
	def PWF_coa(self):
		#points = self.pairs
		coas_and_weights = []
		weighted_sum = 0
		sum_of_weights = 0
		x1,y1 = self.pairs[0]
		for x2,y2 in self.pairs[1:] :
			xc = Piecewise_Function.centre_of_area(x1,x2,y1,y2)
			a = Piecewise_Function.area(x1,x2,y1,y2)
			coas_and_weights.append((xc,a))
			#print ("(xc,a)",(xc,a))
			weighted_sum += xc*a
			sum_of_weights += a
			x1,y1 = x2,y2
		#print (self.name,"evaluating coa")
		#print ("w_s,s_of_w",weighted_sum, sum_of_weights)
		if sum_of_weights == 0:
			return 0,0
		else:
			return 1.0*weighted_sum / sum_of_weights, sum_of_weights	
		
				
# end of Piecewise_Function class definition				



	
#~ # Examples:

#~ # Rule 1:  If pressure is low and temperature is high, speed is low
#~ # Rule 2:  If pressure is moderate and temperature is moderate, speed is moderate
#~ # Rule 3:  If temperature is high and humidity is moderate, speed is high
#~ # Rule 4:  If pressure is high or  temperature is low, speed is very high


#~ # Valid pressure values can be in the range [0,10]
#~ Low_Pressure = Piecewise_Function( name="LP", pairs=[ (-0.0001,0),(0,1),(2,1),(5,0) ] )
#~ Moderate_Pressure = Piecewise_Function(name = "MP",pairs= [ (2,0), (5,1), (8,0) ] )
#~ High_Pressure = Piecewise_Function(name = "HP", pairs= [ (5,0),(8,1),(10,1),(10.001,0) ] )


#~ # Valid temperature values can be in the range [0,10]
#~ Low_Temp = Piecewise_Function( pairs=[ (-0.0001,0),(0,1),(2,1),(5,0) ] )
#~ Moderate_Temp = Piecewise_Function( pairs=[ (3,0), (5,1), (7,0) ] )
#~ High_Temp = Piecewise_Function( pairs = [ (5,0),(8,1),(10,1),(10.001,0) ] ) 

#~ # Valid humidity values can be in the range [0,10]
#~ Low_Humidity = Piecewise_Function( pairs = [ (-0.0001,0),(0,1),(2,1),(5,0) ] )
#~ Moderate_Humidity = Piecewise_Function(pairs = [ (3,0), (5,1), (7,0) ] )
#~ High_Humidity = Piecewise_Function( pairs = [ (5,0),(8,1),(10,1),(10.001,0) ] )

#~ # Valid speed values can be in the range [0,25]
#~ Low_Speed = Piecewise_Function( name="LS",pairs = [ (-0.0001,0),(0,1),(5,1),(10,0) ] )
#~ Moderate_Speed = Piecewise_Function(name="MS",pairs = [ (5,0), (10,1), (15,0) ] )
#~ High_Speed = Piecewise_Function( name="HS",pairs =[(10,0), (15,1), (20,0)  ] )
#~ Very_High_Speed = Piecewise_Function( name="VHS",pairs =[ (15,0),(20,1),(25,1),(25.001,0) ] )
	
#~ Rule_1 = Rule(name = "Rule 1",
			#~ clauses = [
					#~ Clause([("pressure",Low_Pressure)]),
					#~ Clause([("temperature",High_Temp)])
					#~ ], 
		      #~ consequent=Low_Speed)

#~ Rule_2 = Rule(name="Rule 2",
			#~ clauses = [
					#~ Clause([("pressure",Moderate_Pressure)]),
					#~ Clause([("temperature",Moderate_Temp)])	# 2016
					#~ ], 
		      #~ consequent = Moderate_Speed)						# 2016

#~ Rule_3 = Rule(name="Rule 3",
			#~ clauses = [
					#~ Clause([("temperature",High_Temp)]),
					#~ Clause([("humidity",Moderate_Humidity)])
					#~ ],
		      #~ consequent = High_Speed)					# 2016
		      
#~ Rule_4 = Rule(name = "Rule 4",
			#~ clauses = [
					
					#~ Clause(  [ ("pressure",High_Pressure) , ("temperature",Low_Temp)] )
					#~ ],
		      #~ consequent = Very_High_Speed)
		      
		      
		      

		      
#~ speed_rules = Rule_Set()

#~ speed_rules.add_rule(Rule_1)
#~ speed_rules.add_rule(Rule_2)
#~ speed_rules.add_rule(Rule_3)
#~ speed_rules.add_rule(Rule_4)

#~ measurements = { 	"pressure" : 2,
				#~ "temperature" : 4,
				#~ "humidity" : 7 
				#~ }
				
#~ for p in range(0,40):
	#~ measurements["pressure"] += 0.1
	#~ measurements["temperature"] += 0.1
	#~ measurements["humidity"] -= 0.1
	#~ print ("Measurements",measurements)
	#~ speed = speed_rules.resolve(measurements)
	#~ print ("\nResultant Speed",speed)
	#~ print ("\n")
				
#~ #print (speed_rules.resolve(measurements))


#~ Rule_5 = Rule(name= "Rule 5",
			#~ clauses = [
					#~ Clause( [ ("pressure",Low_Pressure) ] )
					#~ ],
			#~ consequent = High_Speed)
			
#~ Rule_6 = Rule(name = "Rule 6",
			#~ clauses = [
					#~ Clause( [ ("pressure",Moderate_Pressure) ] )
					#~ ],
			#~ consequent = Moderate_Speed)
			
#~ Rule_7 = Rule(name = "Rule 7",
			#~ clauses = [
					#~ Clause( [ ("pressure",High_Pressure) ] )
					#~ ],
			#~ consequent = Low_Speed)




#~ speed_rules_2 = Rule_Set()
#~ speed_rules_2.add_rule(Rule_5)
#~ speed_rules_2.add_rule(Rule_6)
#~ speed_rules_2.add_rule(Rule_7)

#~ for r in speed_rules_2.rules:
	#~ print (r.name)
#~ result = speed_rules_2.resolve(measurements)
#~ print ("Final result", result)


#~ # Rule 8: if pressure is low or temp is low or temp is moderate, speed is low
#~ # Rule 9: if pressure is moderate or humidity is low, speed is moderate
#~ # Rule 10: if pressure is high, speed is high
#~ # Rule 11: if pressure is high and temp is high, speed is very hight
#~ Rule_8 = Rule(name = "Rule 8",
			#~ clauses = [
					#~ Clause( [ ("pressure",Low_Pressure),
					              #~ ("temperature",Low_Temp),
						      #~ ("temperature",Moderate_Temp)
						      #~ ]
						      #~ )
					#~ ],
					#~ consequent = Low_Speed)
					
#~ Rule_9 = Rule(name = "Rule 9",
			#~ clauses = [
					#~ Clause( [ ("pressure",Moderate_Pressure),
						      #~ ("humidity",Low_Humidity)
						      #~ ]
						      #~ )
					#~ ],
					#~ consequent = Moderate_Speed)
					
#~ Rule_10 = Rule(name = "Rule 10",
			#~ clauses = [
					#~ Clause( [ ("pressure",High_Pressure) ] )
					#~ ],
			#~ consequent = High_Speed)
			
#~ Rule_11 = Rule(name = "Rule 11",
			#~ clauses = [
					#~ Clause( [ ("pressure",High_Pressure) ] ),
					#~ Clause( [ ("temperature",High_Temp) ] )
					#~ ],
			#~ consequent = Very_High_Speed)
			
#~ speed_rules_3 = Rule_Set()
#~ for r in (Rule_8,Rule_9,Rule_10,Rule_11):
	#~ speed_rules_3.add_rule(r)
	
#~ for p in (0,2,4,6,8,10):
	#~ measurements["pressure"] = p
	#~ for t in (1,3,5,7,9):
		#~ measurements["temperature"] = t
		#~ for h in (2,5,8):
			#~ measurements["humidity"] = h
			#~ print (measurements)
			#~ print ("speed =",speed_rules_3.resolve(measurements))
			
#~ measurements['pressure'] = 2
#~ measurements['temperature'] = 10
#~ measurements['humidity'] = 70
#~ print (measurements)
#~ print ('speed =',speed_rules_3.resolve(measurements))



