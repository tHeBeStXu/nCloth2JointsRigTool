# nCloth2JointsRigTool
nCloth to Joints Rig Tool for Game(Maya Plug-in)  
This Maya plug-in is used for simulate dynamic cloth actions for game engine(UE4) by nCloth.  
You can use it to rig the proxy mesh(especially) for original in game mesh.  
It will generate a well skined proxy mesh, then you can transfer the skin weights to the original in game mesh.  
If you're not satisfied with some detailed actions for nCloth sim result, you can Bake the actions to the Ctls and turn them manully.  

# How to install:
1. Download the project file and unzip it somewhere in the computer, make ture to remember the directory of the unzip file location;  
2. Open Maya 2017+ and open script Editor;  
3. New a Python tab, and enter following script;  
Dir = 'X:\WHERE\YOU\PUT\THE\FILE'  
import sys  

if Dir not in sys.path:		
				sys.path.append(r'X:\WHERE\YOU\PUT\THE\FILE') 

import nCloth2JointRigTool  
from nCloth2JointRigTool.UI import Main_UI  
reload(Main_UI)  

ui = Main_UI.MainUI()  

# How to Use:
I will record a video for using this script. To be continued...    

# Bugs:  
If you find any type of bugs, please e-mail me at: razer_mamba@qq.com.    
    
If you like, please STAR this repository. Thank you very much.    
