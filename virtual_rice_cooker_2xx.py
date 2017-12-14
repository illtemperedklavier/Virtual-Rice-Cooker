#Author: Alec Robinson 20160416
#uses Fuzzy_Logic_Share_2016, a fuzzy logic library by Robin Dawes
#RUNS ON PRE-3.XX PYTHON (any of the versions where parantheses do not surround print statements)


from Fuzzy_Logic_2016_share import *
from random import *
from math import *


target_final_temp = 40
max_temp = 100
temp_increase = 5 #increase in temperature if the heating plate is on
coil = 1
initial_temp = 10

pos_infinity = 327.5 #rice should never be hotter than the temperature for melting lead
neg_infinity = -pos_infinity



##### define fuzzy sets
## define sets for temperature of the water


#Very_Low_Temperature = Piecewise_Function(name="VLT", pairs=[ (0,1),(5,1),(10,0) ])
Very_Low_Temperature = Piecewise_Function(name="VLT", pairs=[ (0,1),(10,1),(20,0) ]) #AR current

Low_Temperature = Piecewise_Function(name="LT", pairs=[ (10,0),(20,1),(30,0) ])

Almost_Warm_Temperature = Piecewise_Function(name="AWT", pairs=[ (20,0),(30,1),(40,0) ])

Warm_Temperature = Piecewise_Function(name="WT", pairs=[ (35,0),(40,1),(45,0) ])

Slightly_Hot_Temperature = Piecewise_Function(name="SHT", pairs=[ (40,0),(50,1),(60,0) ])


Medium_Temperature = Piecewise_Function(name="MT", pairs=[ (0,25),(50,1),(75,0) ])

High_Temperature = Piecewise_Function(name="HT", pairs=[ (0,50),(70,1),(90,0) ])

Very_High_Temperature = Piecewise_Function(name="VHT", pairs=[ (70,0),(85,1),(100,0) ])


#for phase 1
Near_Boiling_Temperature = Piecewise_Function(name="NBT", pairs=[ (96,0),(100,1),(101,0) ]) # this needs to be a crisp number



#Boiling_Temperature = Piecewise_Function(name="BT", pairs=[ (0,95),(100,1),(110,0) ])



Target_Warming_Temperature = Piecewise_Function(name="TWT", pairs=[ (30,0),(40,1),(45,0) ]) #this is for pre-cooking/phase 2








## Change in Temperature fuzzy sets
#while the delta values can be any number, cooked rice should probably not be hotter than the melting point of lead

#used to be 327.5
Negative_Delta_T = Piecewise_Function(name="NDT", pairs=[ (-30.5-0.001,0),(-30,1),(-2,1),(0,0) ])
Zero_Delta_T = Piecewise_Function(name="ZDT", pairs=[ (-5,0),(0,1),(5,0) ])
Positive_Delta_T = Piecewise_Function(name="PDT",  pairs=[ (0,0),(2,1),(320,1),(327.5 +0.0001,0) ])


#change in delta values

Very_Negative_Delta_R = Piecewise_Function(name="VNDR", pairs=[ (-1.001,0),(-1,1),(-0.5,0) ])

Somewhat_Negative_Delta_R = Piecewise_Function(name="VNDR", pairs=[ (-1.001,0),(-1,1),(-0.25,0) ])
Negative_Delta_R = Piecewise_Function(name="NDR", pairs=[ (-1.001,0),(-1,1),(0,0) ])
Zero_Delta_R = Piecewise_Function(name="ZDR", pairs=[ (-0.5,0),(0,1),(0.5,0) ])
Positive_Delta_R = Piecewise_Function(name="PDR",  pairs=[ (0,0),(1,1),(1.0001,0) ])
Slightly_Positive_Delta_R = Piecewise_Function(name="VPDR",  pairs=[ (0.0,0),(0.5,1),(1.0001,0) ])
Very_Positive_Delta_R = Piecewise_Function(name="VPDR",  pairs=[ (0.5,0),(1,1),(1.0001,0) ])

#######################################

### RULES ######

rice_cooker_rules = Rule_Set()

cooker_rules_phase1 = Rule_Set()
cooker_rules_phase2 = Rule_Set()


####phase 1 cooking rules


cooker_rules_phase1.add_rule(Rule(name = "Very Low Temperature, phase 1",
				clauses = [
						Clause([("current_temperature",Very_Low_Temperature)])
						], 
				consequent=Very_Positive_Delta_R)
				)



cooker_rules_phase1.add_rule(Rule(name = "Low Temperature , phase 1",
				clauses = [
						Clause([("current_temperature", Low_Temperature)])
						], 
				consequent= Very_Positive_Delta_R)
				)



#very high falling

cooker_rules_phase1.add_rule(Rule(name = "Very High, falling , phase 1",
				clauses = [
						Clause([("current_temperature",Very_High_Temperature)]),
						Clause([("delta_t",Negative_Delta_T)]),
						],
				consequent = Very_Positive_Delta_R
                                 )
				)



#very high rising



cooker_rules_phase1.add_rule(Rule(name = "Very High, rising , phase 1",
				clauses = [
						Clause([("current_temperature",Very_High_Temperature)]),
						Clause([("delta_t",Positive_Delta_T)]),
						],
				consequent = Positive_Delta_R
                                  ) #AR just changed
				)

#very high static


cooker_rules_phase1.add_rule(Rule(name = "Very High, static , phase 1",
				clauses = [
						Clause([("current_temperature",Very_High_Temperature)]),
						Clause([("delta_t",Zero_Delta_T)]),
						],
				consequent = Positive_Delta_R
                                  )
				)

##

#near boiling rising Near_Boiling_Temperature

cooker_rules_phase1.add_rule(Rule(name = "Near boiling, rising , phase 1",
				clauses = [
						Clause([("current_temperature",Near_Boiling_Temperature)]),
						Clause([("delta_t",Positive_Delta_T)]),
						],
				consequent = Somewhat_Negative_Delta_R
                                  )
				)


#near boiling falling  Near_Boiling_Temperature

cooker_rules_phase1.add_rule(Rule(name = "Near boiling, falling , phase 1",
				clauses = [
						Clause([("current_temperature",Near_Boiling_Temperature)]),
						Clause([("delta_t",Negative_Delta_T)]),
						],
				consequent = Positive_Delta_R
                                  )
				)

#near boiling static  Near_Boiling_Temperature

cooker_rules_phase1.add_rule(Rule(name = "Near boiling, static , phase 1",
				clauses = [
						Clause([("current_temperature",Near_Boiling_Temperature)]),
						Clause([("delta_t",Zero_Delta_T)]),
						],
				consequent = Zero_Delta_R
                                  )
                             
				)







#######



#phase2/warming cooking rules

cooker_rules_phase2.add_rule(Rule(name = "Very Low Temperature",
				clauses = [
						Clause([("current_temperature",Very_Low_Temperature)])
						], 
				consequent = Very_Positive_Delta_R)
				)
##

#low temp, not changing //Almost_Warm_Temperature

cooker_rules_phase2.add_rule(Rule(name = "Almost Warm, Not Changing",
				clauses = [
						Clause([("current_temperature",Almost_Warm_Temperature)]),
						Clause([("delta_t",Zero_Delta_T)]),
						],
				consequent = Very_Positive_Delta_R,
                                  #)
                                   )  #alternate t-norm
				)



#high temp, not changing,// Slightly_Hot_Temperature 

cooker_rules_phase2.add_rule(Rule(name = "Slightly Hot Temperature, Not Changing",
				clauses = [
						Clause([("current_temperature",Slightly_Hot_Temperature)]),
						Clause([("delta_t",Zero_Delta_T)]),
						],
				consequent = Negative_Delta_R
                                  #)
                                  )
				)




#low temp, rising

cooker_rules_phase2.add_rule(Rule(name = "Almost Warm Temperature, Rising",
				clauses = [
						Clause([("current_temperature",Almost_Warm_Temperature)]),
						Clause([("delta_t",Positive_Delta_T)]),
						],
				consequent = Zero_Delta_R
                                  )
				)


#high temp, falling

cooker_rules_phase2.add_rule(Rule(name = "Slightly Hot Temperature, Falling",
				clauses = [
						Clause([("current_temperature",Slightly_Hot_Temperature)]),
						Clause([("delta_t",Negative_Delta_T)]),
						],
				consequent = Zero_Delta_R)
				)



#high temp, rising

cooker_rules_phase2.add_rule(Rule(name = "Slightly Hot Temperature, Rising",
				clauses = [
						Clause([("current_temperature",Slightly_Hot_Temperature)]),
						Clause([("delta_t",Positive_Delta_T)]),
						],
				consequent = Negative_Delta_R)
				)



#low temp, falling

cooker_rules_phase2.add_rule(Rule(name = "Almost Warm, Falling",
				clauses = [
						Clause([("current_temperature",Almost_Warm_Temperature)]),
						Clause([("delta_t",Negative_Delta_T)]),
						],
				consequent = Positive_Delta_R)
				)





#damping rule

cooker_rules_phase2.add_rule(Rule(name = "Close to Target",
				clauses = [
						Clause([("current_temperature",Warm_Temperature)])
						],
				consequent = Zero_Delta_R)
				)


##



#######







#print "starting the program"

print "Virtual Fuzzy Logic Rice Cooker, starting to cook rice \n" 


initial_temp = 10

delta_t = 0

burnt = 0
done = False

room_temperature = 21 #let's pretend we have a room temperature room... 
delta_r = 0
current_temperature = initial_temp
current_loss = 2 # this is the temperature loss per tick, corresponds to INITIAL_IN
current_r =  0.0

element_on = 5 #degrees gained per tick when the element is all the way on, corresponds to FULL_OUT

phase1_temperatures = []
phase2_temperatures = []



#AR just changed
inputs = {"current_t":current_temperature,
		"delta_t":0
		}


print "COOKING PHASE (phase1) STARTED"
for time in range(100):   #phase 1


    
    if (done == False):
        print time, "\t", "current temp", current_temperature, "\tdelta t", delta_t

        if (current_temperature > 100):
            burnt = burnt*1.05 + 0.02    
            #print ("BURNED")
            
            done = True
        
        if (100-current_temperature) <=5:
            print "the rice is close to boiling"
        
        inputs["current_temperature"] = current_temperature
        inputs["delta_t"] = delta_t
        #print("inputs are :", current_temperature, delta_t)      #AR debugging print statements

        delta_r = cooker_rules_phase1.resolve(inputs)
        #print ("delta_r is ", delta_r)

        new_t = current_temperature
        if (delta_r != None):

            #print("current_r + delta_r ", current_r + delta_r)
            current_r = max(0,min(1, current_r + delta_r,))

            #current_loss = 0.625 * min(current_temperature-room_temperature, 0)
            #print("current_r is ", current_r, "changing temperature by ", current_r*element_on )
            loss = 0.625*(current_temperature - room_temperature)
            #print("changing temperature by ", current_r * element_on - loss)
            new_t= max(0,current_temperature - current_loss + (current_r)*element_on)
            
            print "\n"

            
            

        else:
            #print("in else clause")
            #this is simulating the cooker being on full-power until it hits a temperature threshold
            new_t = current_temperature + 3
            
    
        delta_t = new_t - current_temperature
        current_temperature = new_t
        #current_temperature += 5
        phase1_temperatures.append(current_temperature)
    

        
print "current_temperature after phase 1 is :", current_temperature







 #PHASE 2 WORKS FINE

done = False  #have to reset done

print "\n\n\nWARMING PHASE (phase2) STARTED \n"
for time in range(50):   #phase 2

    
    if (done == False):
        print time, "\t", "current temp", current_temperature, "\tdelta t", delta_t 

        if (current_temperature > 105):
            burnt = burnt*1.05 + 0.02    
            print "BURNED"
            done = True
         

        
        inputs["current_temperature"] = current_temperature
        inputs["delta_t"] = delta_t
        print "inputs are :", current_temperature, delta_t      #AR debugging print statements

        delta_r = cooker_rules_phase2.resolve(inputs)
        #print "delta_r is ", delta_r

        new_t = current_temperature
        if (delta_r != None):   
            current_r = max(0,min(1, current_r + delta_r))

            
            loss = 0.625*(current_temperature - room_temperature)
            #print("changing temperature by ", current_r * element_on - current_loss, "in first if")
            new_t= max(0,current_temperature - current_loss + (current_r)*element_on)
            delta_t = new_t - current_temperature

            #print ("just added delta_t statement to first conditional, has it changed? delta_t is :", delta_t)


        if (current_temperature > 50): #for phase 2 we don't need a fuzzy rule, a crisp one for turning the coil off will do until it cools to applicable temperatures
            #this does the equivalent of turning the coil off

            loss = 0.0625*(current_temperature - room_temperature)

            #print("changing temperature by -", loss, "in second if")
            new_t = current_temperature - loss
            delta_t = new_t - current_temperature

            
        current_temperature = new_t
        phase2_temperatures.append(current_temperature)
        print "\n"

        

i = 0

for x in phase2_temperatures:
	i +=1
	if x < 40:
		break


osc_temp = phase2_temperatures[i-1:]

avg_high = [x for x in osc_temp if x >40]

avg_high = sum([x for x in avg_high])/len(avg_high)


avg_low = [x for x in osc_temp if x <40]

avg_low = sum([x for x in avg_low])/len(avg_low)


print "\nRice is Done!\n\n"

print "Rice Cooker with min as the t-norm:\n"

print "The highest temperature of the rice is", round(phase1_temperatures[-1],1), " degrees Celsius\n"
print "The average high temperature in the warming phase is ", round(avg_high, 1), " degrees Celsius\n"
print "The average low temperature in the warming phase is ", round(avg_low, 1), " degrees Celsius\n"



        
        
        


    
