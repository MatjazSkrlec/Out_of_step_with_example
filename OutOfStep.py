'''
Author: Matjaz Skrlec
date: 26. 09. 2024
version: 1.0
description: This module is used for creating and operating the powerfactory DSL block, that detects the out of step of a generator.
Out of step means, that the rotor between two generators is seperated by more than 180°. The module also provides a function,
whick helps detecting, which generator is the critical generator.
'''

#support functions

def CreateBlkDef(name: str, folder):
    
    '''This function creates a model type in the designated folder'''

    assert type(name) == str, "name should be string not "+ str(type(name))
    assert folder.GetClassName() in ["Intfolder","IntPrjfolder"], "Given folder is not folder."
    
    return(folder.CreateObject("BlkDef",name))

def CreateOOSDetBlockTyp(name: str, folder):
    '''This function creates the BlockTyp that detects if machines are out-of-step'''

    assert type(name) == str, "name should be string not "+ str(type(name))
    assert folder.GetClassName() in ["Intfolder","IntPrjfolder"], "Given folder is not folder."

    equation_list = ["inc(diff)=0",\
                     "inc(angmax)=0",\
                     "inc(angmin)=0",\
                     "inc(trig)=-1",\
                     "diff = (angmax-angmin)*180/pi()",\
                     "trig = select(diff>180,1,-1)",\
                     "event(1,trig,'create=EvtStop name=stopdsl dtime=0.01')"]

    OOSDetTyp = CreateBlkDef(name, folder)
    OOSDetTyp.SetAttribute("sOutput",["diff"])
    OOSDetTyp.SetAttribute("sInput",["angmax,angmin"])
    OOSDetTyp.SetAttribute("sAddEquat",equation_list)

    return(OOSDetTyp)

def CreateBlkMaxTyp(folder):
    '''This function creates the BlockTyp that returns the bigger of two values'''

    assert folder.GetClassName() in ["Intfolder","IntPrjfolder"], "Given folder is not folder."

    equation_list = ["inc(angmax)=0",\
                     "inc(ang1)=0",\
                     "inc(ang2)=0",\
                     "angmax=max(ang1,ang2)"]

    BlkMaxTyp = CreateBlkDef("BlkMaxTyp",folder)
    BlkMaxTyp.SetAttribute("sOutput",["angmax"])
    BlkMaxTyp.SetAttribute("sInput",["ang1,ang2"])
    BlkMaxTyp.SetAttribute("sAddEquat",equation_list)

    return(BlkMaxTyp)

def CreateBlkMinTyp(folder):
    '''This function creates the BlockTyp that returns the smaller of two values'''

    assert folder.GetClassName() in ["Intfolder","IntPrjfolder"], "Given folder is not folder."

    equation_list = ["inc(angmin)=0",\
                     "inc(ang1)=0",\
                     "inc(ang2)=0",\
                     "angmin=min(ang1,ang2)"]

    BlkMinTyp = CreateBlkDef("BlkMinTyp",folder)
    BlkMinTyp.SetAttribute("sOutput",["angmin"])
    BlkMinTyp.SetAttribute("sInput",["ang1,ang2"])
    BlkMinTyp.SetAttribute("sAddEquat",equation_list)

    return(BlkMinTyp)

def CreateOOSDetFrameTyp(FrmName: str, OOSBlkName: str,folder, n: int):
    '''This function creates the FrameType for the out-of-step detector'''

    assert type(FrmName) == str, "Frame name should be string not"+ str(type(FrmName))
    assert type(OOSBlkName) == str, "Out of step detection block name should be string not"+ str(type(OOSBlkName))
    assert folder.GetClassName() in ["Intfolder","IntPrjfolder"], "Given folder is not folder."
    assert type(n) == int, "n should be intiger not "+str(type(n))

    OOSDetFrmTyp = CreateBlkDef(FrmName,folder)
    OOSDetBlkTyp = CreateOOSDetBlockTyp(OOSBlkName,folder)

    BlkMaxTyp = CreateBlkMaxTyp(folder)
    BlkMinTyp = CreateBlkMinTyp(folder)

    #create angle slots
    angle_slots = []
    for i in range(n):
        curr_ang_slot = OOSDetFrmTyp.CreateObject("BlkSlot","angle_"+str(i))
        curr_ang_slot.SetAttribute("sOutput",["xphi"])
        angle_slots.append(curr_ang_slot)

    #create max slots
    max_slots = []
    for i in range(1,n):
        curr_max_slot = OOSDetFrmTyp.CreateObject("BlkSlot","max_"+str(i))
        curr_max_slot.SetAttribute("pDsl",BlkMaxTyp)
        max_slots.append(curr_max_slot)

    #create min slots
    min_slots = []
    for i in range(1,n):
        curr_min_slot = OOSDetFrmTyp.CreateObject("BlkSlot","min_"+str(i))
        curr_min_slot.SetAttribute("pDsl",BlkMinTyp)
        min_slots.append(curr_min_slot)
    
    #create Out of step detection block
    OOSdetBlk_slot = OOSDetFrmTyp.CreateObject("BlkSlot","OOSdetBlk")
    OOSdetBlk_slot.SetAttribute("pDsl",OOSDetBlkTyp)

    #first ocnnection layer
    sig1_1 = OOSDetFrmTyp.CreateObject("BlkSig","ang1_1")
    sig1_1.SetAttribute("pnodfrom",angle_slots[0])
    sig1_1.SetAttribute("inodfrom",0)
    sig1_1.SetAttribute("pnodto",max_slots[0])
    sig1_1.SetAttribute("iconto",1)
    sig1_1.SetAttribute("inodto",0)

    sig1_2 = OOSDetFrmTyp.CreateObject("BlkSig","ang1_2")
    sig1_2.SetAttribute("pnodfrom",angle_slots[0])
    sig1_2.SetAttribute("inodfrom",0)
    sig1_2.SetAttribute("pnodto",min_slots[0])
    sig1_2.SetAttribute("iconto",1)
    sig1_2.SetAttribute("inodto",0)

    sig2_1 = OOSDetFrmTyp.CreateObject("BlkSig","ang2_1")
    sig2_1.SetAttribute("pnodfrom",angle_slots[1])
    sig2_1.SetAttribute("inodfrom",0)
    sig2_1.SetAttribute("pnodto",max_slots[0])
    sig2_1.SetAttribute("iconto",1)
    sig2_1.SetAttribute("inodto",1)

    sig2_2 = OOSDetFrmTyp.CreateObject("BlkSig","ang2_2")
    sig2_2.SetAttribute("pnodfrom",angle_slots[1])
    sig2_2.SetAttribute("inodfrom",0)
    sig2_2.SetAttribute("pnodto",min_slots[0])
    sig2_2.SetAttribute("iconto",1)
    sig2_2.SetAttribute("inodto",1)

    #middle connection layers
    for i,j in zip(angle_slots[2:],range(2,n)):
        curr_sig1 = OOSDetFrmTyp.CreateObject("BlkSig","ang"+str(j+1)+"_1")
        curr_sig1.SetAttribute("pnodfrom",i)
        curr_sig1.SetAttribute("inodfrom",0)
        curr_sig1.SetAttribute("pnodto",max_slots[j-1])
        curr_sig1.SetAttribute("iconto",1)
        curr_sig1.SetAttribute("inodto",0)

        curr_sig2 = OOSDetFrmTyp.CreateObject("BlkSig","ang"+str(j+1)+"_2")
        curr_sig2.SetAttribute("pnodfrom",i)
        curr_sig2.SetAttribute("inodfrom",0)
        curr_sig2.SetAttribute("pnodto",min_slots[j-1])
        curr_sig2.SetAttribute("iconto",1)
        curr_sig2.SetAttribute("inodto",0)

        curr_max_sig = OOSDetFrmTyp.CreateObject("BlkSig","angmax"+str(j-1))
        curr_max_sig.SetAttribute("pnodfrom",max_slots[j-2])
        curr_max_sig.SetAttribute("inodfrom",0)
        curr_max_sig.SetAttribute("pnodto",max_slots[j-1])
        curr_max_sig.SetAttribute("iconto",1)
        curr_max_sig.SetAttribute("inodto",1)

        curr_min_sig = OOSDetFrmTyp.CreateObject("BlkSig","angmin"+str(j-1))
        curr_min_sig.SetAttribute("pnodfrom",min_slots[j-2])
        curr_min_sig.SetAttribute("inodfrom",0)
        curr_min_sig.SetAttribute("pnodto",min_slots[j-1])
        curr_min_sig.SetAttribute("iconto",1)
        curr_min_sig.SetAttribute("inodto",1)

    #last signal layer
    sig_ang_max = OOSDetFrmTyp.CreateObject("BlkSig","angmax")
    sig_ang_max.SetAttribute("pnodfrom",max_slots[-1])
    sig_ang_max.SetAttribute("inodfrom",0)
    sig_ang_max.SetAttribute("pnodto",OOSdetBlk_slot)
    sig_ang_max.SetAttribute("iconto",1)
    sig_ang_max.SetAttribute("inodto",0)

    sig_ang_min = OOSDetFrmTyp.CreateObject("BlkSig","angmin")
    sig_ang_min.SetAttribute("pnodfrom",min_slots[-1])
    sig_ang_min.SetAttribute("inodfrom",0)
    sig_ang_min.SetAttribute("pnodto",OOSdetBlk_slot)
    sig_ang_min.SetAttribute("iconto",1)
    sig_ang_min.SetAttribute("inodto",1)
    
    return OOSDetFrmTyp,OOSDetBlkTyp,BlkMaxTyp,BlkMinTyp

def CreateComAngBlkTyp(name: str, folder):
    '''This function creates the BlockTyp that returns the actual rotor angle of machines.'''

    assert type(name) == str, "name should be string not "+ str(type(name))
    assert folder.GetClassName() in ["Intfolder","IntPrjfolder"], "Given folder is not folder."

    equation_list = ["inc(ang)=0",\
                     "inc(d_com_ang)=0",\
                     "inc(com_angle)=0",\
                     "d_ang = delay(ang,0.01)",\
                     "diff = ang-d_ang",\
                     "diff_1 = select(diff>5,diff-2*pi(),diff)",\
                     "diff_2 = select(diff<-5,diff+2*pi(),diff)",\
                     "add_diff = select(diff<0,diff_2,diff_1)",\
                     "com_angle = add_diff + d_com_angle",\
                     "d_com_angle = delay(com_angle,0.01)"]
    
    angle_adder = CreateBlkDef(name,folder)
    angle_adder.SetAttribute("sInput",["ang"])
    angle_adder.SetAttribute("sAddEquat",equation_list)
    angle_adder.SetAttribute("sOutput",["com_angle"])

    return(angle_adder)

def CreateComAngFrmTyp(FrmName: str, ComAngBlkName: str, folder):
    '''This function creates the FrameTyp that returns the actual rotor angle of machines.'''

    assert type(FrmName) == str, "Frame name should be string not"+ str(type(FrmName))
    assert type(ComAngBlkName) == str, "Angle adder block name should be string not"+ str(type(ComAngBlkName))
    assert folder.GetClassName() in ["Intfolder","IntPrjfolder"], "Given folder is not folder."

    ComAngFrmTyp = CreateBlkDef(FrmName, folder)
    ComAngBlkTyp = CreateComAngBlkTyp(ComAngBlkName, folder)

    ComAngFrmTyp.SetAttribute("sOutput",["xphi"])

    #create angle (generator) slot
    ang_slot = ComAngFrmTyp.CreateObject("BlkSlot","machine")
    ang_slot.SetAttribute("sOutput",["xphi"])

    #create comulative angle adder slot
    ComAng_slot = ComAngFrmTyp.CreateObject("BlkSlot","OOSdetBlk")
    ComAng_slot.SetAttribute("pDsl",ComAngBlkTyp)

    #signal from angle to logic
    sig1 = ComAngFrmTyp.CreateObject("BlkSig","ang")
    sig1.SetAttribute("pnodfrom",ang_slot)
    sig1.SetAttribute("inodfrom",0)
    sig1.SetAttribute("pnodto",ComAng_slot)
    sig1.SetAttribute("iconto",1)
    sig1.SetAttribute("inodto",0)

    #signal to outpu
    sig_out = ComAngFrmTyp.CreateObject("BlkSig","xphi")
    sig_out.SetAttribute("pnodfrom",ComAng_slot)
    sig_out.SetAttribute("inodfrom",0)
    sig_out.SetAttribute("pnodto",ComAngFrmTyp)
    sig_out.SetAttribute("iconto",2)
    sig_out.SetAttribute("inodto",0)

    return ComAngFrmTyp,ComAngBlkTyp

def CheckIfElmExists(ElmName: str, Grid, iprint: bool):
    '''This function check if the OOS Frame exists in the given Grid.'''

    assert type(ElmName) == str, "ElmName is of type "+str(type(ElmName))+', when it should be of type string.'
    assert Grid.GetClassName() == "ElmNet", "Grid should be 'ElmNet' type."
    assert type(iprint) == bool, "iprint is of type "+str(type(iprint))+', when it should be of type bool'

    for i in Grid.GetContents():
        if i.loc_name == ElmName:
            if(iprint):
                print("Elemnt with name "+ElmName+" already exists in grid "+Grid.loc_name)
            return(True, i)
    if(iprint):
        print("Elemnt with name "+ElmName+" doesn't exists in grid "+Grid.loc_name)
    return(False, 0)

def CheckIfTypExists(TypName: str, folder, iprint: bool):
    '''This function check if the OOS Frame exists in the given Grid.'''

    assert type(TypName) == str, "TypName is of type "+str(type(TypName))+', when it should be of type string.'
    assert folder.GetClassName() in ["Intfolder","IntPrjfolder"], "Given folder is not folder."
    assert type(iprint) == bool, "iprint is of type "+str(type(iprint))+', when it should be of type bool'

    for i in folder.GetContents():
        if i.loc_name == TypName:
            if(iprint):
                print("Emenent type with name "+TypName+" already exists in folder "+folder.loc_name)
            return(True, i)
    if(iprint):
        print("Element type with name "+TypName+" doesn't exists in folder "+folder.loc_name)
    return(False, 0)

def CheckIfComElmEnabled(oFrm, iprint: bool):
    '''This function checks if the a composite model element is already enabled.'''

    assert oFrm.GetClassName() == "ElmComp", "The given element is not of type 'ElmComp'."
    assert type(iprint) == bool, "iprint is of type "+str(type(iprint))+', when it should be of type bool.'

    if (oFrm.GetAttribute("outserv")==0):
        if iprint:
            print("Given composite model is enabled.")
        return(True)
    else:
        if iprint:
            print("Given composite model is disabled.")
        return(False)

def EnableComElm(FrmName: str,Grid):
    '''This function enables the composite model that already exists in the given Grid.'''

    assert type(FrmName) == str, "FrmName is of type "+str(type(FrmName))+", when it should be of type str."
    assert Grid.GetClassName() == "ElmNet", "Grid should be ElmNet type."

    bool_exists, oFrm = CheckIfElmExists(FrmName,Grid,False)

    if (CheckIfComElmEnabled(oFrm,False)):
        print("Given composite model is already enabled.")
        return(oFrm)

    if (bool_exists):
        oFrm.SetAttribute("outserv",0)
        print("Enabled composite model Frame.")
    else:
        print("Composite model Frame doesn't exists in grid "+Grid.loc_name)
    return(oFrm)
    
def DisableComElm(FrmName: str,Grid):
    '''This function disables the composite model that already exists in the given Grid.'''

    assert type(FrmName) == str, "Frame name is of type "+str(type(FrmName))+", when it should be of type str."
    assert Grid.GetClassName() == "ElmNet", "Grid should be ElmNet type."

    bool_exists, oFrm = CheckIfElmExists(FrmName,Grid,False)

    if not (CheckIfComElmEnabled(oFrm,False)):
        print("Composite model is already disabled.")
        return(oFrm)

    if (bool_exists):
        oFrm.SetAttribute("outserv",1)
        print("Disabled composite model Frame.")
    else:
        print("Composite model doesn't exists in grid "+Grid.loc_name)
    return(oFrm)

#main functions

def CreateOOSDet(FrmName: str, TypFolder, grid, sAngles):
    '''This function creates the Frame for the out-of-step detector'''

    assert type(FrmName) == str, "Frame name should be string not "+str(type(FrmName))
    assert TypFolder.GetClassName() in ["Intfolder","IntPrjfolder"], "Given folder is not folder."
    assert grid.GetClassName() == "ElmNet", "grid should be ElmNet type"
    assert type(sAngles) == list, "sGens should be list not "+str(type(sAngles))
    assert len(sAngles) > 1, "There should be mroe than one generator operating in the power system."

    exist_bool, Frm = CheckIfElmExists(FrmName,grid,False)

    if exist_bool:
        print("Given frame name "+FrmName+" already exists, not creating a new frame.")
        return(Frm)

    n = len(sAngles)
    FrmTypName = "OOSFrmTyp"
    OOSBlkTypName = "OODBlkTyp"

    OOSDetFrmTyp,OOSDetBlkTyp,BlkMaxTyp,BlkMinTyp = CreateOOSDetFrameTyp(FrmTypName, OOSBlkTypName, TypFolder, n)

    OOSDetFrm = grid.CreateObject("ElmComp",FrmName)
    OOSDetFrm.SetAttribute("typ_id",OOSDetFrmTyp)

    OOSDetBlk = OOSDetFrm.CreateObject("ElmDsl","OOSDetBlk")
    OOSDetBlk.SetAttribute("typ_id",OOSDetBlkTyp)

    #create blocks for max evaluation
    MaxBlkLst = []
    for i in range(1,n):
        CurrMaxBlk = OOSDetFrm.CreateObject("ElmDsl","max"+str(i))
        CurrMaxBlk.SetAttribute("typ_id",BlkMaxTyp)
        MaxBlkLst.append(CurrMaxBlk)

    #create blocks for min evalutaion
    MinBlkLst = []
    for i in range(1,n):
        CurrMinBlk = OOSDetFrm.CreateObject("ElmDsl","min"+str(i))
        CurrMinBlk.SetAttribute("typ_id",BlkMinTyp)
        MinBlkLst.append(CurrMinBlk)

    pelm_list = sAngles
    pelm_list = pelm_list + MaxBlkLst + MinBlkLst
    pelm_list.append(OOSDetBlk)

    OOSDetFrm.SetAttribute("pelm",pelm_list)

    return(OOSDetFrm)

def DetectCritGenerator(sGenAng: list):
    '''This function detects the generator whose rotor angle is furthest away from the center of inertia angle. It should be noted,
       that this function only works, if an RMS simulation was conducted, previous to calling it.'''

    assert type(sGenAng) == list, "sGenAng is of type"+str(type(sGenAng))+", when it should be of type list."

    
    Sb = 100
    H_COI = 0
    del_num = 0
    #Structure of each Gen info entry: [Generator,H,Sn,delta]
    GenInfo = []
    for i in sGenAng: 
        curr_H = i[0].GetAttribute("typ_id").GetAttribute("h")
        curr_Sn = i[0].GetAttribute("typ_id").GetAttribute("sgn")
        curr_adder = i[1].GetContents()[0]
        curr_del = curr_adder.GetAttribute("c:com_angle")*180/3.14
        curr_H_sys = curr_H*curr_Sn/Sb
        H_COI = H_COI + curr_H_sys
        del_num = del_num + curr_del*curr_H_sys
        GenInfo.append([i[0],curr_H,curr_Sn,curr_del])

    del_COI = del_num/H_COI

    #structure: [generator, distance to del_COI]
    max_dist_gen = [0,0]

    for i in GenInfo:
        dist_to_COI = abs(del_COI-i[3])
        if dist_to_COI > max_dist_gen[1]:
            max_dist_gen = [i[0],dist_to_COI]

    return(max_dist_gen)

def CreateComAng(FrmName: str, TypFolder, grid, Gen): 
    '''This function creates the Frame for the comulative angle adder'''

    assert type(FrmName) == str, "Frame name should be string not "+str(type(FrmName))
    assert TypFolder.GetClassName() in ["Intfolder","IntPrjfolder"], "Given folder is not folder."
    assert grid.GetClassName() == "ElmNet", "grid should be ElmNet type"
    assert Gen.GetClassName() == "ElmSym", "Given Gen is not of type 'ElmSym'."

    FrmBool, Frm = CheckIfElmExists(FrmName,grid,False)

    if FrmBool:
        print("Given frame name "+FrmName+" already exists, not creating a new frame.")
        return(Frm)
    
    FrmTypName = "ComAngFrmTyp"
    ComAngBlkTypName = "ComAngBlkTyp"

    FrmTypBool, ComAngFrmTyp = CheckIfTypExists(FrmTypName, TypFolder, False)
    BlkTypBool, ComAngBlkTyp = CheckIfTypExists(ComAngBlkTypName, TypFolder, False)

    if FrmTypBool != BlkTypBool:
        if FrmTypBool:
            print("Frame type with that name already exists, but the block type doesn't.")
        else:
            print("Block type with that name already exists, but the Frame type doesn't.")

    if (not FrmTypBool) and (not BlkTypBool):
        ComAngFrmTyp,ComAngBlkTyp = CreateComAngFrmTyp(FrmTypName, ComAngBlkTypName, TypFolder)

    ComAngFrm = grid.CreateObject("ElmComp",FrmName)
    ComAngFrm.SetAttribute("typ_id",ComAngFrmTyp)

    ComAngBlk = ComAngFrm.CreateObject("ElmDsl","ComulativeAngleAdder")
    ComAngBlk.SetAttribute("typ_id",ComAngBlkTyp)

    pelm_list = [Gen,ComAngBlk]
    ComAngFrm.SetAttribute("pelm",pelm_list)

    return(ComAngFrm)

    
            

 

        
