Out_of_step_with_example
============

*Author: Matjaž Škrlec*<br>
*date: 27. 09. 2024*<br>
*version: v1.0*<br>
*Description: This repository present the out of step python module used for out of step detection of sychronous machines during RMS simulations in powerfactory. The module creates composite modules, whitch monitor rotor angles of all active synchonos machines durin an RMS simulations and stop the simulation if any two rotor angles differ by 180°.*

Introduction
------------

Powerfactorys' inbuild out-of-step functionalities are limited to detecting a specific angle deviation from the initial operating state (initialisation of the RMS simulation) or by crossing a specific detection angle. Those options are usualy not useful for actual out-of-step detection, since the measured angles are usualy refered to a reference machine, centre of inertia or nominal fequency. Those out-of-step detections are not in line with the out-of-step definition most commonly found in Transient Stability Analysis literature. There, the most common out-of-step criteria is definied as the surplus of the difference between any two rotor angles ($\Delta\delta_{ij} = |\delta_i - \delta_j|, \forall i,j \in n$, where $n$ is the number of generators) above 180° ($\Delta\delta_{ij}>180°$). Therefore I decided to create the python script `OutOfStep.py`, which can create a composite model, which monitors the angles of all active generators during an RMS simulation and stops the simulation when any two generators angle are at least 180° apart. In addition, I've created a script, which can detect which machine was the most critical during loss of synchronism. We define the most critical machine as the machine, whose rotor angle distance to the centre of inertia rotor angle was the biggest during the loss of synchronism: $\delta_{crit} = max\\{|\delta_{i}-\delta_{COI}|, \forall i \in n\\}$.

software specifications
------------

The provided example uses the following software tools:
 * python v3.12.1 64-bit
 * powerfactory 2024 preview<br>
 
*It should be noted that the comands used in python and in powerfacotry are quite basic ones, so they should run on most versions.*

Provided files
------------

The example comes with 3 files:
 * `OutOfStep.py` - the module that brings the new functionalities
 * `Example_run_OOS.py` - a script that runs a simple RMS simulation in powerfactory
 * `Test Nine-bus System.pfd` - a simple powerfactory model that is used in `Example_run_OOS.py`

Description of main OutOfStep functions
------------

The `OutOfStep.py` module provides many functions, but you won't be using most of them. That is why they are subdivided into support functions and main functions. The support functions are there for an easier understanding of the main functions, that you will be using the most. This is why in this section only the main functions and their functionalities are described.

### EnableComElm ###

Attributes:
 * *FrmName* (string type) - the local name of the element that you wish to enable,
 * *Grid* (DataObject type) - the Grid in which the element you wish to enable is located

Returns:
 * *oFrm* (DataObject type) - The object that was enabled, *If the object exists*
 * 0 (bool), *If the object doesn't exists*

The `EnableComElm` funciton checks, whether an Element with the local name *FrmName* exists in the grid *Grid*. If it does exist, the element gets activated (outserv = 0), if it doesn't the function reports that the given element doesn't exist and returns a 0.


### DisableComElm ###

Attributes:
 * *FrmName* (string type) - the local name of the element that you wish to disable,
 * *Grid* (DataObject type) - the Grid in which the element you wish to disable is located

Returns:
 * *oFrm* (DataObject type) - The object that was disabled, *If the object exists*
 * 0 (bool), *If the object doesn't exists*

The `DisableComElm` funciton checks, whether an Element with the local name *FrmName* exists in the grid *Grid*. If it does exist, the element gets deactivated (outserv = 1), if it doesn't the function reports that the given element doesn't exist and returns a 0.

### CreateOOSDet ###

Attributes:
 * *FrmName* (string type) - the local name of the composite model that you wish to create,
 * *TypFolder* (DataObject type) - the folder in which you wish to create the composite model type,
 * *grid* (DataObject type) - the Grid in which you wish to create the composite model,
 * *sAngles* (DataObject type) - The elements whose angle you wish to monitor

Returns:
  * *Frm* (DataObject type) - An element with the name, *If the object exists*
  * *OOSDetFrm* (DataObject type) - The Out of step detection composite model that was created, *If the object doesn't exists*

The `CreateOOSDet` function creates a composite model with the local name *FrmName* in the grid *grid*, which monitors the angles of the elements given with the *sAngles* during a powerfactory simulation. If the biggest and the smallest angle differ by $\pi$ radians, the composite model stops the simulation.

### DetectCritGenerator ###

Attributes:
 * *sGenAng* (list type) - A list which should contain multiple lists of the structure [DataObject, DataObject] The first entry should be the machines whose angles are to be compared and the second entry should be the devices which measure the current angle (also known as ComAng elements, that are created with the function `CreateComAng` below).
   
Returns:
  * *max_dist_gen* (list type) - A list which contains the machine whose rotor angle has the maximum distance to the centre of inertia angle (1st entry) and the distance between the machine rotor angle and the COI angle (2nd entry).

The `DetectCritGenerator` function calculates the distances between the rotor angles of the given machines and the centre of inertia angle of the given machines, then returns the machine whose rotor angle is furthest from the centre of inertia angle and the distance from the machine rotor angle to the centre of inertia angle.

### CreateComAng ###

Attributes:
 * *FrmName* (string type) - the local name of the composite model that you wish to create,
 * *TypFolder* (DataObject type) - the folder in which you wish to create the composite model type,
 * *grid* (DataObject type) - the Grid in which you wish to create the composite model,
 * *Gen* (DataObject type) - the machine whose rotor angle you wish to monitor
   
Returns:
  * *ComAngFrm* (DataObject type) - A composite model which returns the abolute value of the rotor angle

The `CreateComAng` creates a composite model which returns the absolute value of the rotor angle of a given machine. The motivation of that is motivated with the way powerfacotory handles angles. All angles are between -180° and 180° ($-\pi$ rad and $\pi$ rad). If those angles exceed the respective marginal value, they wrap around, which is impractical when calculating differences between angles. For example the angles 170° and 190° have a difference of 20°, but the way powerfactory handles those values, 190° would be wrapped back to -170° and the difference would be 340°, which can become impractical in detecting out-of-step machines and calculating critical machines.

Description of Example
------------

### Description of the powerfactory model ###

The powerfactory model `Test Nine-bus System.pfd` is a simple model of the benchmark IEEE 9Bus system. It is already set up with a 3-phase short circuit on Bus7 and the clearence of the short circuit. The short circuit is set up for the means of demostrating the functionality of the provided `Example_run_OOS.py` script. In order for the script to work all you have to do is import the provided model and make a few adaptations to the example script.

### Before running the script ###

In order to be able to run the `Example_run_OOS.py` script, make sure to first of all import the provided `Test Nine-bus System.pfd` model in your powerfactory application.

Next in order for the script to work on your machine, you will need to change a few lines in the python code. Namely:

line 13:
~~~python
prj = "Test systems\\Nine-bus System"
~~~

Here you have to change the given project name ("Test systems\\Nine-bus System") to the project name inside your own powerfactory application, where you imported the provided `Test Nine-bus System.pfd` model.

line 23:
~~~python
sys.path.append("C:\\Program Files\\DIgSILENT\\PowerFactory 2024 Preview\\Python\\3.12")
~~~

Here you have to change the provided directory ("C:\\Program Files\\DIgSILENT\\PowerFactory 2024 Preview\\Python\\3.12") to the directory, where you have your powerfactory.py file saved on your local machine (Usualy in the installed DIgSILENT directory).

### What the script does ###

If everything is set up correctly the script in `Example_run_OOS.py`:
  * Activates the powerafactory project of the Nine-bus system given with `Test Nine-bus System.pfd`
  * Retrieves the dynamic model library of the project,
  * Retrieves the grid where the Composite models should be stored,
  * Retrieves the list of all active generators (there should be 3 in the given example),
  * Creates Composite models which monitor the rotor angle od all active generators,
  * Checks if the out of step detection composite model already exists,
  * Creates the composite model, which detects if the machines are out of step and stops the simulation
  * Enables the the out of step composite model
  * Retrieves the comads for initialisation and execution of the RMS simulation
  * Runs the initialisation and RMS somulation
  * Detects, which generator rotor angle is furthest from the centre of inertia rotor angle
  * Reports which generator was the critical one and what its deviation from the centre of inertia was.

### Running the script for the first time ###

When you run the script for the first time, the following message should display in your terminal window:

    ---------------------------------------------------------------
    activating project
    project sucefully activated
    Elemnt with name OOSFrm doesn't exists in grid Nine-bus System
    Given composite model is already enabled.
    -----------------------------------------------------
    The critical generator that fell out of step was: G2
    The rotor angle of the generator deviated from the centre of inertia angle for 143.96 degrees.
    
The first two lines report that the project in powerfactory was sucesfully activated.<br>
The third line is the result of the `CheckIfElmExists` function. Since we checked for the existance of the Out-Of-Step composite model before creating it, the function reports that no Out-Of-Step composite model with the name "OOSFrm" exists.<br>
The fourth line is the result of the `EnableComElm` funciton. When creating a new Out-Of-Step composite model, the model is automaticaly enabled, which is why trying to enable it directly after creating it is not necessary.<br>
The final two lines simply report that the machine which was critical during the loss of synchronism was the machine named G2 and that its rotor angle deviated from the centre of inertia angle for aproximately 144°.

### Running the script for the second time ##

When you run the script for the second (or in fact, any subsequntial) time, the following message should display in your terminal window:

    ---------------------------------------------------------------
    activating project
    project sucefully activated
    Given frame name AngleAdderG2 already exists, not creating a new frame.
    Given frame name AngleAdderG3 already exists, not creating a new frame.
    Given frame name AngleAdderG1 already exists, not creating a new frame.
    Elemnt with name OOSFrm already exists in grid Nine-bus System
    Given frame name OOSFrm already exists, not creating a new frame.
    Given composite model is already enabled.
    -----------------------------------------------------
    The critical generator that fell out of step was: G2
    The rotor angle of the generator deviated from the centre of inertia angle for 143.96 degrees.

The message is similar to the previous ones, the only difference is that the functions that create elements report that they are not creating any new elements. That is because before creating new elements, they check if elements that have the same name as given to them already exist. If that is the case the functions will not create a new element and simply return the element with the provided name that already exists.



