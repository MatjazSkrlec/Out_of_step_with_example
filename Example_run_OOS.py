'''
Author: Matjaz Skrlec
date: 24. 09. 2024
version: 1.0
description: Example for use of OutOfStep module.
'''
#--------------------------------------------------------------------------------------------------
## imports
import OutOfStep
#--------------------------------------------------------------------------------------------------
## variable paramaters of code
#projects/grids
prj = "Test systems\\Nine-bus System"
model_grid_name = "Nine-bus System"

#out of step detection name
OOSFrmName = "OOSFrm" 
#--------------------------------------------------------------------------------------------------
## start power factory application

# Add powerfactory.pyd path to python path
import sys
sys.path.append("C:\\Program Files\\DIgSILENT\\PowerFactory 2024 Preview\\Python\\3.12")

# import PowerFactory module
import powerfactory as pf

# start powerfactory in non-interactive mode

app = pf.GetApplicationExt()

#-------------------------------------------------------------------------------------------------
## code

# activate pf project
print('---------------------------------------------------------------')
print('activating project')
prj = app.ActivateProject(prj)
if prj == 1:
    raise Exception("No project activated. Python Script stopped.")
else:
    print('project sucefully activated')

# get dynamic models library
dyn_folder = app.GetProjectFolder("blk")

#get grid to implement frame
net_data = app.GetProjectFolder("netdat")
for i in net_data.GetContents():
    if i.loc_name == model_grid_name:
        model_grid = i

#get list of all active generators
sAllGen = app.GetCalcRelevantObjects("*.ElmSym",includeOutOfService = 0)

#create list of Frames that calculate absolute angles, and list used to detect critical generator
sGenAng = []
sAng = []
for i in sAllGen:
    currComAngFrm = OutOfStep.CreateComAng("AngleAdder"+str(i.loc_name), dyn_folder, model_grid, i)
    sAng.append(currComAngFrm)
    sGenAng.append([i,currComAngFrm])

#Check if out of step detection exists
OutOfStep.CheckIfElmExists(OOSFrmName,model_grid,True)

#Create OutOfStep detection
OutOfStep.CreateOOSDet(OOSFrmName,dyn_folder,model_grid,sAng)

#Enable of of step detection
OutOfStep.EnableComElm(OOSFrmName,model_grid)

#Get comands for initialising and running RMS simulation
oComInc = app.GetFromStudyCase("ComInc")
oComSim = app.GetFromStudyCase("ComSim")

#Execute initialisation and RMS simulation commands
oComInc.Execute()
oComSim.Execute()

#Run detection of critical generator detection
max_dist_gen = OutOfStep.DetectCritGenerator(sGenAng)

print("-----------------------------------------------------")
print("The critical generator that fell out of step was: "+max_dist_gen[0].GetAttribute("loc_name"))
print("The rotor angle of the generator deviated from the centre of inertia angle for "+str(round(max_dist_gen[1],2))+" degrees.")
