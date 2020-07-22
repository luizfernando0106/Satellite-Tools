import os
import numpy as np
import rasterio as rio
from subprocess import call
from sdc import SDC_CLASS_ID

#%%
def SIAM_8_CLASS_ID():
    
    CLASS_ID = dict()
    
    CLASS_ID["ND"]   = 0
    
    CLASS_ID["WAT"]  = 1
    CLASS_ID["CLD"]  = 2
    CLASS_ID["SNW"]  = 3
    
    CLASS_ID["SHV"]  = 4
    CLASS_ID["SHB"]  = 5
    
    CLASS_ID["VEG"]  = 6
    CLASS_ID["SOIL"] = 7
    
    CLASS_ID["UNK"]  = 8
    
    
    return CLASS_ID

def SIAM_13_CLASS_ID():
    
    CLASS_ID = dict()
    
    CLASS_ID["ND"]   = 0
    
    CLASS_ID["V"]    = 1
    CLASS_ID["SHV"]  = 2
    CLASS_ID["R"]    = 3    
    CLASS_ID["WR"]   = 4
    CLASS_ID["PB"]   = 5
    
    CLASS_ID["BB"]   = 6
    CLASS_ID["SHB"]  = 7
    
    CLASS_ID["WASH"] = 8
    
    CLASS_ID["TKCL"] = 9
    CLASS_ID["TNCL"] = 10
    CLASS_ID["SN"]   = 11
    CLASS_ID["SHCL"] = 12
    
    CLASS_ID["UNK"]  = 13
    
    
    return CLASS_ID

def FMASK_CLASS_ID():
    # now convert these masks to
    # 0 - null
    # 1 - not null and not mask
    # 2 - cloud
    # 3 - cloud shadow
    # 4 - snow
    # 5 - water
    
    class_id = {'ND': 0,
                'CL': 2,
                'SHD': 3,
                'SI': 4,
                'WAT': 5}
    
    return class_id

#%%
def SIAM_46_7(BAND):    
    
    NO_DATA_MASK = ((BAND["BLUE"] == 0) | (BAND["GREEN"] == 0) | (BAND["RED"] == 0))
            
    err = 0.001
    
    # Vis
    limit = [0.3, 0.5]
    INX = (BAND["BLUE"]+BAND["GREEN"]+BAND["RED"])/3.
    
    HVis = INX>max(limit)
    LVis = INX<min(limit)
#    MVis = (INX<=max(limit))&(INX>=min(limit))
    
    # Bright
    limit = [0.4, 0.6]
    INX = (BAND["BLUE"]+BAND["GREEN"]+2.*BAND["RED"]+2.*BAND["NIR"]+BAND["SWIR1"]+BAND["SWIR2"])/8.
    
    HBright = INX>max(limit)
    LBright = INX<min(limit)
#    MBright = (INX<=max(limit))&(INX>=min(limit))
    
    # NIR
    limit = [0.4, 0.6]
    INX = BAND["NIR"].copy()
    
    HNIR = INX>max(limit)
    LNIR = INX<min(limit)
#    MNIR = (INX<=max(limit))&(INX>=min(limit))
    
    # MIR1
    limit = [0.4, 0.6]
    INX = BAND["SWIR1"].copy()
    
    HMIR1 = INX>max(limit)
    LMIR1 = INX<min(limit)
#    MMIR1 = (INX<=max(limit))&(INX>=min(limit))
    
    # MIR2
    limit = [0.3, 0.5]
    INX = BAND["SWIR2"].copy()
    
    HMIR2 = INX>max(limit)
    LMIR2 = INX<min(limit)
#    MMIR2 = (INX<=max(limit))&(INX>=min(limit))
    
    # TIR
    limit = [0.0, 28.0]
    INX = BAND["TIR"].copy()
    
    HTIR  = INX>max(limit)
    LTIR  = INX<min(limit)
    MTIR  = (INX<=max(limit))&(INX>=min(limit))
    
    
    # NDSI
    limit = [0.0, 0.5]
    INX = ((BAND["BLUE"]+BAND["GREEN"]+BAND["RED"])/3. - BAND["NIR"])/((BAND["BLUE"]+BAND["GREEN"]+BAND["RED"])/3. + BAND["NIR"] + err)
    
    HNDSI = INX>max(limit)
    LNDSI = INX<min(limit)
    MNDSI = (INX<=max(limit))&(INX>=min(limit))
    
    # NDBBBI
    limit = [-0.2, 0.1]
    INX = (BAND["BLUE"]-BAND["SWIR1"])/(BAND["BLUE"]+BAND["SWIR1"] + err)
    
#    HNDBBBI = INX>max(limit)
    LNDBBBI = INX<min(limit)
#    MNDBBBI = (INX<=max(limit))&(INX>=min(limit))
    
    
    # NDVI
    limit = [0.36, 0.70]
    INX = (BAND["NIR"]-BAND["RED"])/(BAND["NIR"]+BAND["RED"] + err)
    
    HNDVI = INX>max(limit)
    LNDVI = INX<min(limit)
    MNDVI = (INX<=max(limit))&(INX>=min(limit))
    
    # NDBSI
    limit = [-0.2, 0.1]
    INX = (BAND["SWIR1"]-BAND["NIR"])/(BAND["SWIR1"]+BAND["NIR"] + err)
    
    HNDBSI = INX>max(limit)
    LNDBSI = INX<min(limit)
    MNDBSI = (INX<=max(limit))&(INX>=min(limit))
    
    INX = None
    
    #%%
    
    MIN = np.minimum(np.minimum(BAND["BLUE"],BAND["GREEN"]),BAND["RED"])
    MAX = np.maximum(np.maximum(BAND["BLUE"],BAND["GREEN"]),BAND["RED"])
    
    #1
    TKCL_SR = (MIN     >= 0.7*MAX)     &\
              (MAX     <= 0.7*BAND["NIR"]) &\
              (BAND["SWIR1"] <= 0.7*BAND["NIR"]) &\
              (BAND["SWIR1"] >= 0.7*MAX)     &\
              (BAND["SWIR2"] <= 0.7*BAND["NIR"])
    
    #2
    TNCL_SR = (MIN     >= 0.7*MAX)     &\
              (BAND["NIR"] >=     MAX)     &\
              (( ((BAND["BLUE"]<=BAND["GREEN"])&(BAND["GREEN"]<=BAND["RED"])&(BAND["RED"]<=BAND["NIR"])) & (BAND["RED"]>=0.70*BAND["NIR"]) )==False)&\
              (BAND["NIR"] >= 0.7*BAND["SWIR1"]) &\
              (BAND["SWIR1"] >= 0.7*BAND["NIR"]) &\
              (BAND["SWIR1"] >= 0.7*MAX)     &\
              (BAND["SWIR1"] >= 0.7*BAND["SWIR2"])
    
    #2.2
    SATCL_SR = (MIN           >= 0.7*MAX)     &\
               (BAND["NIR"]   >=     MAX)     &\
               (BAND["NIR"]   >= 0.7*BAND["SWIR1"]) &\
               (BAND["SWIR1"] >= 0.5*MAX)     &\
               (BAND["SWIR1"] >= 0.7*BAND["SWIR2"]) &\
               ((BAND["NIR"]  >= 0.5)  )
    
    #3
    SNIC_SR = (MIN           >= 0.7*MAX) &\
              (BAND["NIR"]   >= 0.7*MAX) &\
              (BAND["SWIR1"] <= 0.5*BAND["NIR"]) &\
              (BAND["SWIR1"] <= 0.7*MIN) &\
              (BAND["SWIR2"] <= 0.5*BAND["NIR"]) &\
              (BAND["SWIR2"] <= 0.7*MIN)
    
    #4
    WASH_SR = (BAND["BLUE"]>=1.00*BAND["GREEN"]) &\
              (BAND["GREEN"]>=1.00*BAND["RED"]) &\
              (BAND["RED"]>=1.00*BAND["NIR"]) &\
              (BAND["NIR"]>=1.00*BAND["SWIR1"]) &\
              (BAND["NIR"]>=1.00*BAND["SWIR2"])
              
    # #4
    # WASH_SR = (BAND["GREEN"]>=0.90*BAND["RED"]) &\
    #           (BAND["RED"]>=1.00*BAND["NIR"]) &\
    #           (BAND["NIR"]>=1.00*BAND["SWIR1"]) &\
    #           (BAND["NIR"]>=1.00*BAND["SWIR2"])
    
    #5
    PBGH_SR = (BAND["RED"] >= 0.7*BAND["BLUE"]) &\
              (BAND["BLUE"] >= 0.7*BAND["RED"]) &\
              (MAX     <= 0.7*BAND["NIR"]) &\
              (BAND["SWIR1"] <= 0.7*BAND["NIR"]) &\
              (BAND["RED"] >= 0.5*BAND["SWIR1"]) &\
              (MIN     >= 0.7*BAND["SWIR2"])
    
    #6
    DB_SR   = (BAND["BLUE"] >= 0.7*np.maximum(np.maximum(np.maximum(np.maximum(BAND["GREEN"],BAND["RED"]),BAND["NIR"]),BAND["SWIR1"]),BAND["SWIR2"]))
              
    #7
    V_SR    = (BAND["GREEN"] >= 0.5 * BAND["BLUE"]) &\
              (BAND["GREEN"] >= 0.7 * BAND["RED"]) &\
              (BAND["RED"] <  0.7 * BAND["NIR"]) &\
              (BAND["NIR"] >  MAX) &\
              (BAND["SWIR1"] <  0.7 * BAND["NIR"]) &\
              (BAND["SWIR1"] >= 0.7 * BAND["RED"]) &\
              (BAND["SWIR2"] <  0.7 * BAND["SWIR1"])
    
    #8
    R_SR    = (BAND["GREEN"] >= 0.5*BAND["BLUE"]) &\
              (BAND["GREEN"] >= 0.7*BAND["RED"]) &\
              (BAND["NIR"] >      MAX) &\
              (BAND["RED"] <  0.7*BAND["NIR"]) &\
              (BAND["NIR"] >= 0.7*BAND["SWIR1"]) &\
              (BAND["SWIR1"] >= 0.7*BAND["NIR"]) &\
              (BAND["SWIR1"] >      MAX) &\
              (BAND["SWIR2"] <  0.7*np.maximum(BAND["NIR"],BAND["SWIR1"])) &\
              (BAND["SWIR1"] >=     BAND["SWIR2"])
    
    #9
    BBC_SR  = (BAND["RED"] >= 0.5*BAND["BLUE"]) &\
              (BAND["RED"] >= 0.7*BAND["GREEN"]) &\
              (BAND["NIR"] >= 0.7*MAX) &\
              (BAND["SWIR1"] >=     MAX) &\
              (BAND["SWIR1"] >= 0.7*BAND["NIR"]) &\
              (BAND["SWIR1"] >= 0.7*BAND["SWIR2"]) &\
              (BAND["SWIR2"] >= 0.5*np.maximum(BAND["NIR"],BAND["SWIR1"]))
    
    #10
    FBB_SR  = (BAND["SWIR1"] >= 0.7*np.maximum(np.maximum(MAX,BAND["NIR"]),BAND["SWIR2"])) &\
              (np.minimum(np.minimum(MIN,BAND["NIR"]),BAND["SWIR2"]) >= 0.5*BAND["SWIR1"])
    
    #11
    SHB_SR  = (BAND["BLUE"] >=     BAND["GREEN"]) &\
              (BAND["GREEN"] >=     BAND["RED"]) &\
              (BAND["RED"] >= 0.7*BAND["NIR"]) &\
              (BAND["BLUE"] >=     BAND["SWIR1"]) &\
              (BAND["SWIR1"] >= 0.7*BAND["NIR"]) &\
              (BAND["SWIR1"] >= 0.7*BAND["SWIR2"])
    
    #12
    SHV_SR  = (BAND["BLUE"] >=     BAND["GREEN"]) &\
              (BAND["GREEN"] >=     BAND["RED"]) &\
              (BAND["BLUE"] >= 0.5*BAND["NIR"]) &\
              (BAND["RED"] <  0.7*BAND["NIR"]) &\
              (BAND["SWIR1"] <  0.7*BAND["NIR"]) &\
              (BAND["RED"] >= 0.7*BAND["SWIR1"]) &\
              (BAND["SWIR2"] <  0.7*BAND["NIR"])
    
    #13
    SHCLSN_SR = (BAND["BLUE"] >= 0.7*np.maximum(np.maximum(BAND["GREEN"],BAND["RED"]),BAND["NIR"])) &\
                (np.maximum(np.maximum(BAND["GREEN"],BAND["RED"]),BAND["NIR"]) >= 0.7*BAND["BLUE"]) &\
                (BAND["SWIR1"] <      BAND["BLUE"]) &\
                (BAND["SWIR2"] <  0.7*BAND["BLUE"])
    
    #14
    WE_SR     = (BAND["BLUE"] >=     BAND["GREEN"]) &\
                (BAND["GREEN"] >=     BAND["RED"]) &\
                (BAND["BLUE"] >= 0.7*BAND["NIR"]) &\
                (BAND["RED"] <      BAND["NIR"]) &\
                (BAND["NIR"] >= 0.7*BAND["SWIR1"]) &\
                (BAND["SWIR1"] >= 0.7*BAND["NIR"]) &\
                (BAND["RED"] >= 0.5*BAND["SWIR1"]) &\
                (BAND["SWIR1"] >=     BAND["SWIR2"])
    
    #%%
    MASK = np.zeros(TKCL_SR.shape, dtype=int)
    
    # 1
    SC = (TKCL_SR | TNCL_SR | SATCL_SR) & ((LBright | LVis | LNIR | HNDSI | LMIR1 | LMIR2 | HTIR)==False)
    
    MASK[SC & LTIR & (MASK==0)] = 1
    MASK[SC & MTIR & (MASK==0)] = 2
    
    # 2
    SC = (SNIC_SR)  & (LNDBSI) & ((LBright | LVis | LNDSI | LNIR | HMIR1 | HMIR2 | HTIR)==False)
    
    MASK[SC & HNDSI & (MASK==0)] = 3
    MASK[SC & MNDSI & (MASK==0)] = 4
    
    # 3
    SC = (WASH_SR) & (LBright & LVis & LNDVI & LNIR & LMIR1 & LMIR2) & (LTIR == False)
    
    MASK[SC & HNDSI          & (MASK==0)] = 5
    MASK[SC & (HNDSI==False) & (MASK==0)] = 6
    
    # 4
    SC = (PBGH_SR) & (LMIR1 & LMIR2 & LNDBSI) & (LNIR == False)
    
    MASK[SC & HNDVI & (MASK==0)] = 7
    MASK[SC & MNDVI & (MASK==0)] = 8
    MASK[SC & LNDVI & (MASK==0)] = 9
    
    # 5
    SC = (V_SR) & (HNDVI) & ((HMIR1 | HMIR2 | HNDBSI) == False)
    
    MASK[SC & HNIR          & (MASK==0)] = 10
    MASK[SC & (HNIR==False) & (MASK==0)] = 11
    
    # 6
    SC = (V_SR | SHV_SR) & (MNDVI) & ((HMIR1 | HMIR2 | HNDBSI | DB_SR) == False)
    
    MASK[SC & HNIR          & (MASK==0)] = 12
    MASK[SC & (HNIR==False) & (MASK==0)] = 13
    
    # 7
    SC = (V_SR | R_SR | SHV_SR) & (LNDVI & LNDBSI & LMIR1 & LMIR2) & (DB_SR == False)
    
    MASK[SC & HNIR          & (MASK==0)] = 14
    MASK[SC & (HNIR==False) & (MASK==0)] = 15
    
    # 8
    SC = (R_SR) & (HNDVI & MNDBSI)
    
    MASK[SC & HNIR          & (MASK==0)] = 16
    MASK[SC & (HNIR==False) & (MASK==0)] = 17
    
    # 9
    SC = (R_SR) & (MNDVI & MNDBSI) & ((SHV_SR | WE_SR) == False)
    
    MASK[SC & HNIR          & (MASK==0)] = 18
    MASK[SC & (HNIR==False) & (MASK==0)] = 19
    
    # 10
    SC = (R_SR) & (HNDVI & HNDBSI)
    
    MASK[SC & (MASK==0)] = 20
    
    # 11
    SC = (R_SR | BBC_SR) & (MNDVI & HNDBSI)
    
    MASK[SC & (MASK==0)] = 21
    
    # 12
    SC = (V_SR | R_SR) & (LNDVI & LMIR2) & ((HNIR | HMIR1 | LNDBSI) == False)
    
    MASK[SC & (MASK==0)] = 22
    
    # 13
    SC = (BBC_SR) & (HNIR & HMIR2 & LNDVI) & ((LNDBSI | LMIR1) == False)
    
    MASK[SC & HTIR & (LNDBBBI==False) & (MASK==0)] = 23
    MASK[SC & HTIR & (MASK==0)] = 24
    
    MASK[SC & (HTIR==False) & (LNDBBBI==False) & (MASK==0)] = 25
    MASK[SC & (HTIR==False) & (MASK==0)] = 26
    
    # 14
    SC = (BBC_SR | FBB_SR) & (LNDVI & HNDBSI) & ((HNIR | LMIR1) == False)
    
    MASK[SC & HTIR & (DB_SR | FBB_SR) & (MASK==0)] = 27
    MASK[SC & HTIR & (MASK==0)] = 28
    
    MASK[SC & (HTIR==False) & (DB_SR | FBB_SR) & (MASK==0)] = 29
    MASK[SC & (HTIR==False) & (MASK==0)] = 30
    
    # 15
    SC = (BBC_SR | FBB_SR) & (LNDVI & MNDBSI) & ((HNIR | LMIR1) == False)
    
    MASK[SC & HTIR & (LNDBBBI==False) & (MASK==0)] = 31
    MASK[SC & HTIR & (MASK==0)] = 32
    
    MASK[SC & (HTIR==False) & (LNDBBBI==False) & (MASK==0)] = 33
    MASK[SC & (HTIR==False) & (MASK==0)] = 34
    
    # 16
    SC = (BBC_SR | FBB_SR) & (LNDVI & LMIR1) & ((HNIR | HMIR2 | LNDBSI) == False)
    
    MASK[SC & HTIR & (DB_SR | FBB_SR) & (MASK==0)] = 35
    MASK[SC & HTIR & (MASK==0)] = 36
    
    MASK[SC & (HTIR==False) & (DB_SR | FBB_SR) & (MASK==0)] = 37
    MASK[SC & (HTIR==False) & (MASK==0)] = 38
    
    # 17
    SC = (R_SR) & (LNDVI) & (LNDBSI == False)
    
    MASK[SC & (MASK==0)] = 39
    
    # 18
    SC = (DB_SR & SHV_SR) & (LBright & LVis & LNIR & LMIR1 & LMIR2) & (HNDVI == False)
    
    MASK[SC & (MASK==0)] = 40
    
    # 19
    SC = (DB_SR & SHB_SR) & (LBright & LVis & LNDVI & LNIR & LMIR1 & LMIR2)
    
    MASK[SC & (MASK==0)] = 41
    
    # 20
    SC = (DB_SR & SHCLSN_SR) & ((HNDSI | LNIR | LBright | LVis | HNDBSI |HTIR) == False)
    
    MASK[SC & (MASK==0)] = 42
    
    # 21
    SC = (DB_SR & SHCLSN_SR) & (HNDSI & LNIR & LMIR1 & LMIR2) & ((HBright | HVis | HNDBSI | HTIR) == False)
    
    MASK[SC & (MASK==0)] = 43
    
    # 22
    SC = (DB_SR & WE_SR) & (LBright & LVis & LNIR & LMIR1 & LMIR2) & ((HNDVI | HNDBSI | LNDSI) == False)
    
    MASK[SC & (MASK==0)] = 44
    
    # 23
    SC = (DB_SR) & (LNDVI & LMIR1 & LMIR2) & ((HBright | HVis | HNIR | LNDSI)==False)
    
    MASK[SC & (MASK==0)] = 45
        
    
    # 20
    SC = SHCLSN_SR & ((LBright | LVis | LNIR | HNDBSI | HNDSI | HTIR) == False)
    
    MASK[SC & (MASK==0)] = 42
    
    # 1
    MASK[(MASK==0)  & ((LBright | LVis | LNIR | HNDSI | LMIR1 | LMIR2 | HTIR)==False) ] = 2
    
    # 24
    MASK[(MASK==0)] = 46
    
    # 0
    MASK[(NO_DATA_MASK==True)] = 0
    
    return MASK

def SIAM_46_5(band):
    
    BAND = band.copy()
    
    print("\nSIAM ...")
    
    NO_DATA_MASK = ((BAND["BLUE"] == 0) | (BAND["GREEN"] == 0))
    
    
    print("Value ...")
    err = 0.001
    
    # Vis
    limit = [0.3, 0.5]
    INX = np.mean((BAND["BLUE"],BAND["GREEN"],BAND["RED"]), axis=0)
    
    HVis = INX>max(limit)
    LVis = INX<min(limit)
#    MVis = (INX<=max(limit))&(INX>=min(limit))
    
    # Bright
    limit = [0.4, 0.6]
    INX = (BAND["BLUE"]+BAND["GREEN"]+2.*BAND["RED"]+2.*BAND["NIR"])/6.
    
    HBright = INX>max(limit)
    LBright = INX<min(limit)
#    MBright = (INX<=max(limit))&(INX>=min(limit))
    
    # NIR
    limit = [0.4, 0.6]
    INX = BAND["NIR"].copy()
    
    HNIR = INX>max(limit)
    LNIR = INX<min(limit)
#    MNIR = (INX<=max(limit))&(INX>=min(limit))
    
    # TIR
    limit = [0.0, 28.0]
    INX = BAND["TIR"].copy()
    
    HTIR  = INX>max(limit)
    LTIR  = INX<min(limit)
    MTIR  = (INX<=max(limit))&(INX>=min(limit))
    
    BAND["TIR"] = None
    
    # NDSI
    limit = [0.0, 0.5]
    INX = (np.mean((BAND["BLUE"],BAND["GREEN"],BAND["RED"]), axis=0) - BAND["NIR"])/(np.mean((BAND["BLUE"],BAND["GREEN"],BAND["RED"]), axis=0) + BAND["NIR"] + err)
    
    HNDSI = INX>max(limit)
    LNDSI = INX<min(limit)
    MNDSI = (INX<=max(limit))&(INX>=min(limit))
    
    # NDVI
    limit = [0.36, 0.70]
    INX = (BAND["NIR"]-BAND["RED"])/(BAND["NIR"]+BAND["RED"] + err)
    
    HNDVI = INX>max(limit)
    LNDVI = INX<min(limit)
    MNDVI = (INX<=max(limit))&(INX>=min(limit))
    
    
    #%%
    print("Shape ... ")
    
    MIN = np.min((BAND["BLUE"],BAND["GREEN"],BAND["RED"]), axis=0)
    MAX = np.max((BAND["BLUE"],BAND["GREEN"],BAND["RED"]), axis=0)
    
    
    #1
    TKCL_SR = (MIN     >= 0.7*MAX)     &\
              (MAX     <= 0.7*BAND["NIR"])
    
    #2
    TNCL_SR = (MIN     >= 0.7*MAX)     &\
              (BAND["NIR"] >=     MAX)     &\
              (( ((BAND["BLUE"]<=BAND["GREEN"])&(BAND["GREEN"]<=BAND["RED"])&(BAND["RED"]<=BAND["NIR"])) & (BAND["RED"]>=0.70*BAND["NIR"]) )==False)
    
    #3
    SNIC_SR = (MIN     >= 0.7*MAX) &\
              (BAND["NIR"] >= 0.7*MAX)
    
    #4
    WASH_SR = (BAND["BLUE"]>=0.90*BAND["GREEN"]) &\
              (BAND["GREEN"]>=0.90*BAND["RED"]) &\
              (BAND["RED"]>=1.00*BAND["NIR"])
    
    #5
    PBGH_SR = (BAND["RED"] >= 0.7*BAND["BLUE"]) &\
              (BAND["BLUE"] >= 0.7*BAND["RED"]) &\
              (MAX     <= 0.7*BAND["NIR"])
    
    #6
    DB_SR   = (BAND["BLUE"] >= 0.7*np.max((BAND["GREEN"],BAND["RED"],BAND["NIR"]), axis=0) )
    DG_SR   = (BAND["GREEN"] >= 0.7*np.max((BAND["BLUE"],BAND["RED"],BAND["NIR"]), axis=0) )
    DR_SR   = (BAND["RED"] >= 0.7*np.max((BAND["BLUE"],BAND["GREEN"],BAND["NIR"]), axis=0) )
              
    #7
    V_SR    = (BAND["GREEN"] >= 0.5 * BAND["BLUE"]) &\
              (BAND["GREEN"] >= 0.7 * BAND["RED"]) &\
              (BAND["RED"] <  0.7 * BAND["NIR"]) &\
              (BAND["NIR"] >  MAX)
    
    #8
    R_SR    = (BAND["GREEN"] >= 0.5*BAND["BLUE"]) &\
              (BAND["GREEN"] >= 0.7*BAND["RED"]) &\
              (BAND["NIR"] >      MAX) &\
              (BAND["RED"] <  0.7*BAND["NIR"])
    
    #9
    BBC_SR  = (BAND["RED"] >= 0.5*BAND["BLUE"]) &\
              (BAND["RED"] >= 0.7*BAND["GREEN"]) &\
              (BAND["NIR"] >= 0.7*MAX)
        
    #11
    SHB_SR  = (BAND["BLUE"] >=     BAND["GREEN"]) &\
              (BAND["GREEN"] >=     BAND["RED"]) &\
              (BAND["RED"] >= 0.7*BAND["NIR"])
    
    #12
    SHV_SR  = (BAND["BLUE"] >=     BAND["GREEN"]) &\
              (BAND["GREEN"] >=     BAND["RED"]) &\
              (BAND["BLUE"] >= 0.5*BAND["NIR"]) &\
              (BAND["RED"] <  0.7*BAND["NIR"])
    
    #13
    SHCLSN_SR = (BAND["BLUE"] >= 0.7*np.max((BAND["GREEN"],BAND["RED"],BAND["NIR"]), axis=0)) &\
                (np.max((BAND["GREEN"],BAND["RED"],BAND["NIR"]), axis=0) >= 0.7*BAND["BLUE"])
    
    #14
    WE_SR     = (BAND["BLUE"] >=     BAND["GREEN"]) &\
                (BAND["GREEN"] >=     BAND["RED"]) &\
                (BAND["BLUE"] >= 0.7*BAND["NIR"]) &\
                (BAND["RED"] <      BAND["NIR"])
    
    BAND   = None
    
    #%%
    print("Image ...")
    MASK = np.zeros(TKCL_SR.shape, dtype=int)
    
    # 1
    SC = (TKCL_SR | TNCL_SR) & ((LBright | LVis | LNIR | HNDSI | HTIR)==False)
    
    MASK[SC & LTIR & (MASK==0)] = 1
    MASK[SC & MTIR & (MASK==0)] = 2
    
    # 2
    SC = (SNIC_SR)  & ((LBright | LVis | LNDSI | LNIR | HTIR)==False)
    
    MASK[SC & HNDSI & (MASK==0)] = 3
    MASK[SC & MNDSI & (MASK==0)] = 4
    
    # 3
    SC = (WASH_SR) & (LBright & LVis & LNDVI & LNIR) & (LTIR == False)
    
    MASK[SC & HNDSI          & (MASK==0)] = 5
    MASK[SC & (HNDSI==False) & (MASK==0)] = 6
    
    # 4
    SC = (PBGH_SR) & (LNIR == False)
    
    MASK[SC & HNDVI & (MASK==0)] = 7
    MASK[SC & MNDVI & (MASK==0)] = 8
    MASK[SC & LNDVI & (MASK==0)] = 9
    
    # 5
    SC = (V_SR) & (HNDVI)
    
    MASK[SC & HNIR          & (MASK==0)] = 10
    MASK[SC & (HNIR==False) & (MASK==0)] = 11
    
    # 6
    SC = (V_SR | SHV_SR) & (MNDVI) & ((DB_SR) == False)
    
    MASK[SC & HNIR          & (MASK==0)] = 12
    MASK[SC & (HNIR==False) & (MASK==0)] = 13
    
    # 7
    SC = (V_SR | R_SR | SHV_SR) & (LNDVI) & (DB_SR == False)
    
    MASK[SC & HNIR          & (MASK==0)] = 14
    MASK[SC & (HNIR==False) & (MASK==0)] = 15
    
    # 8
    SC = (R_SR) & (HNDVI)
    
    MASK[SC & HNIR          & (MASK==0)] = 16
    MASK[SC & (HNIR==False) & (MASK==0)] = 17
    
    # 9
    SC = (R_SR) & (MNDVI) & ((SHV_SR | WE_SR) == False)
    
    MASK[SC & HNIR          & (MASK==0)] = 18
    MASK[SC & (HNIR==False) & (MASK==0)] = 19
    
    # 10
    SC = (R_SR) & (HNDVI)
    
    MASK[SC & (MASK==0)] = 20
    
    # 11
    SC = (R_SR | BBC_SR) & (MNDVI)
    
    MASK[SC & (MASK==0)] = 21
    
    # 12
    SC = (V_SR | R_SR) & (LNDVI) & ((HNIR) == False)
    
    MASK[SC & (MASK==0)] = 22
    
    # 13
    SC = (BBC_SR) & (HNIR & LNDVI)
    
    MASK[SC & HTIR & (MASK==0)] = 24
    
    MASK[SC & (HTIR==False) & (MASK==0)] = 26
    
    # 14
    SC = (BBC_SR) & (LNDVI ) & ((HNIR) == False)
    
    MASK[SC & HTIR & (DB_SR) & (MASK==0)] = 27
    MASK[SC & HTIR & (MASK==0)] = 28
    
    MASK[SC & (HTIR==False) & (DB_SR) & (MASK==0)] = 29
    MASK[SC & (HTIR==False) & (MASK==0)] = 30
    
    # 15
    SC = (BBC_SR) & LNDVI & ((HNIR) == False)
    
    MASK[SC & HTIR & (MASK==0)] = 32

    MASK[SC & (HTIR==False) & (MASK==0)] = 34
    
    # 16
    SC = (BBC_SR) & (LNDVI) & ((HNIR) == False)
    
    MASK[SC & HTIR & (DB_SR) & (MASK==0)] = 35
    MASK[SC & HTIR & (MASK==0)] = 36
    
    MASK[SC & (HTIR==False) & (DB_SR) & (MASK==0)] = 37
    MASK[SC & (HTIR==False) & (MASK==0)] = 38
    
    # 17
    SC = (R_SR) & (LNDVI)
    
    MASK[SC & (MASK==0)] = 39
    
    # 18
    SC = ((DB_SR|DG_SR) & SHV_SR) & (LBright & LVis & LNIR) & (HNDVI == False)
    
    MASK[SC & (MASK==0)] = 40
    
    # 19
    SC = ((DB_SR|DR_SR) & SHB_SR) & (LBright & LVis & LNDVI & LNIR)
    
    MASK[SC & (MASK==0)] = 41
    
    # 20
    SC = ((DB_SR) & SHCLSN_SR) & ((HNDSI | LNIR | LBright | LVis |HTIR) == False)
    
    MASK[SC & (MASK==0)] = 42
    
    # 21
    SC = ((DB_SR) & SHCLSN_SR) & (HNDSI & LNIR) & ((HBright | HVis | HTIR) == False)
    
    MASK[SC & (MASK==0)] = 43
    
    # 22
    SC = ((DB_SR|DG_SR) & WE_SR) & (LBright & LVis & LNIR) & ((HNDVI | LNDSI) == False)
    
    MASK[SC & (MASK==0)] = 44
    
    # 23
    SC = (DB_SR|DG_SR|DR_SR) & (LNDVI) & ((HBright | HVis | HNIR | LNDSI)==False)
    
    MASK[SC & (MASK==0)] = 45
    
    # 24
    MASK[(MASK==0)] = 46
    
    # 0
    MASK[NO_DATA_MASK] = 0
    
    return MASK

def SIAM_13(SIAM_46):
    
    # -------------------------------------
    #  0 = "ND"
    #  1 = "V"
    #  2 = "SHV"
    #  3 = "R"
    #  4 = "WR"
    #  5 = "PB"    
    #  6 = "BB"
    #  7 = "SHB"
    #  8 = "WASH"    
    #  9 = "TKCL"
    # 10 = "TNCL"
    # 11 = "SN"
    # 12 = "SHCL"
    # 12 = "UNK"
    # -------------------------------------
    
    CLASS_ID = SIAM_13_CLASS_ID()
    
    mask = np.zeros(SIAM_46.shape)
    
    mask[(SIAM_46>=10)&(SIAM_46<=15)] = CLASS_ID["V"]
    mask[(SIAM_46==40)]               = CLASS_ID["SHV"]
    mask[(SIAM_46>=16)&(SIAM_46<=22)] = CLASS_ID["R"]
    mask[(SIAM_46==44)]               = CLASS_ID["R"]
    mask[(SIAM_46==39)]               = CLASS_ID["WR"]
    mask[(SIAM_46>= 7)&(SIAM_46<= 9)] = CLASS_ID["PB"]
    
    mask[(SIAM_46>=23)&(SIAM_46<=38)] = CLASS_ID["BB"]
    mask[(SIAM_46==41)]               = CLASS_ID["SHB"]
    
    mask[(SIAM_46==43)|(SIAM_46==45)] = CLASS_ID["WASH"]
    mask[(SIAM_46== 5)|(SIAM_46== 6)] = CLASS_ID["WASH"]
    
    mask[(SIAM_46== 1)]               = CLASS_ID["TKCL"]
    mask[(SIAM_46== 2)]               = CLASS_ID["TNCL"]
    mask[(SIAM_46== 3)|(SIAM_46== 4)] = CLASS_ID["SN"]
    
    mask[(SIAM_46==42)]               = CLASS_ID["SHCL"]
    mask[(SIAM_46==46)]               = CLASS_ID["UNK"]
    mask[(SIAM_46==0 )]               = CLASS_ID["ND"]
    
    return mask

def SIAM_8(SIAM_13):
    
    # -------------------------------------
    # 0: NO DATA
    
    # 1: WATER
    # 2: CLOUD
    # 3: SNOW
    
    # 4: SHADOW VEGETETION
    # 5: SHADOW SOIL
    
    # 6: VEGETETION
    # 7: SOIL
    
    # 8: UNKNOWN
    # -------------------------------------
    
    CLASS_ID_SIAM_13 = SIAM_13_CLASS_ID()
    CLASS_ID_SIAM_8  = SIAM_8_CLASS_ID()
    
    mask_wat     = (SIAM_13 == CLASS_ID_SIAM_13["WASH"])               
    mask_cld     = (SIAM_13 == CLASS_ID_SIAM_13["TKCL"])  | (SIAM_13 == CLASS_ID_SIAM_13["TNCL"]) | (SIAM_13 == CLASS_ID_SIAM_13["SHCL"])               
    mask_snw     = (SIAM_13 == CLASS_ID_SIAM_13["SN"])    
    mask_shd_veg = (SIAM_13 == CLASS_ID_SIAM_13["SHV"])    
    mask_shd_bsl = (SIAM_13 == CLASS_ID_SIAM_13["SHB"])
    mask_bsl     = (SIAM_13 == CLASS_ID_SIAM_13["BB"])        
    
    mask_veg = (SIAM_13 == CLASS_ID_SIAM_13["V"])  |\
               (SIAM_13 == CLASS_ID_SIAM_13["R"])  |\
               (SIAM_13 == CLASS_ID_SIAM_13["WR"]) |\
               (SIAM_13 == CLASS_ID_SIAM_13["PB"])
               
    mask_unk = (SIAM_13 == CLASS_ID_SIAM_13["UNK"])               
    mask_ndt = (SIAM_13 == CLASS_ID_SIAM_13["ND"])

    #
    MASK = np.zeros(SIAM_13.shape)
    
    MASK[mask_cld     & (MASK==0)] = CLASS_ID_SIAM_8["CLD"]
    MASK[mask_veg     & (MASK==0)] = CLASS_ID_SIAM_8["VEG"]    
    MASK[mask_bsl     & (MASK==0)] = CLASS_ID_SIAM_8["SOIL"]    
    MASK[mask_shd_veg & (MASK==0)] = CLASS_ID_SIAM_8["SHV"]
    MASK[mask_shd_bsl & (MASK==0)] = CLASS_ID_SIAM_8["SHB"]    
    MASK[mask_wat     & (MASK==0)] = CLASS_ID_SIAM_8["WAT"]
    MASK[mask_snw     & (MASK==0)] = CLASS_ID_SIAM_8["SNW"]
    MASK[mask_unk     & (MASK==0)] = CLASS_ID_SIAM_8["UNK"]
    
    MASK[mask_ndt] = CLASS_ID_SIAM_8["ND"]
    
    return MASK

def SIAM_15(BAND, SIAM_8):
    
    #%%    
    err = 0.001
    
    # NDSI
    limit = [0.0, 0.5]
    INX = ( np.mean((BAND["BLUE"],BAND["GREEN"],BAND["RED"]),axis=0) - BAND["NIR"])/( np.mean((BAND["BLUE"],BAND["GREEN"],BAND["RED"]),axis=0) + BAND["NIR"] + err)
    
    # HNDSI = INX>max(limit)
    LNDSI = INX<min(limit)
    # MNDSI = (INX<=max(limit))&(INX>=min(limit))
    
    # NDVI
    limit = [0.36, 0.70]
    INX = (BAND["NIR"]-BAND["RED"])/(BAND["NIR"]+BAND["RED"] + err)
    
    HNDVI = INX>max(limit)
    # LNDVI = INX<min(limit)
    MNDVI = (INX<=max(limit))&(INX>=min(limit))
    
    # MIR1
    limit = [0.4, 0.6]
    INX = BAND["SWIR1"].copy()
    
    HMIR1 = INX>max(limit)
    LMIR1 = INX<min(limit)
    MMIR1 = (INX<=max(limit))&(INX>=min(limit))
    
    INX = None
    
    #%%
    MAX = np.max((BAND["BLUE"],BAND["GREEN"],BAND["RED"]), axis=0)
    
    V_SR    = (BAND["GREEN"] >= 0.5 * BAND["BLUE"]) &\
              (BAND["GREEN"] >= 0.7 * BAND["RED"]) &\
              (BAND["RED"]   <  0.7 * BAND["NIR"]) &\
              (BAND["NIR"]   >  MAX) &\
              (BAND["SWIR1"] <  0.7 * BAND["NIR"]) &\
              (BAND["SWIR1"] >= 0.7 * BAND["RED"]) &\
              (BAND["SWIR2"] <  0.7 * BAND["SWIR1"])
              
    R_SR    = (BAND["GREEN"] >= 0.5*BAND["BLUE"]) &\
              (BAND["GREEN"] >= 0.7*BAND["RED"]) &\
              (BAND["NIR"] >      MAX) &\
              (BAND["RED"] <  0.7*BAND["NIR"]) &\
              (BAND["NIR"] >= 0.7*BAND["SWIR1"]) &\
              (BAND["SWIR1"] >= 0.7*BAND["NIR"]) &\
              (BAND["SWIR1"] >      MAX) &\
              (BAND["SWIR2"] <  0.7*np.maximum(BAND["NIR"],BAND["SWIR1"])) &\
              (BAND["SWIR1"] >=     BAND["SWIR2"])
    
    
    #%%
    CLASS_ID_SIAM_SDC = SIAM_8_CLASS_ID()
    
    MASK = np.zeros(SIAM_8.shape)
    
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["WAT"]) & (MASK==0) & (LNDSI==False)] = 1
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["WAT"]) & (MASK==0) & (LNDSI==True) ] = 2


    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["CLD"]) & (MASK==0)] = 3
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["SNW"]) & (MASK==0)] = 4

    
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["SHV"]) & (MASK==0)] = 5
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["SHB"]) & (MASK==0)] = 6

    
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["VEG"]) & (MASK==0) & (V_SR) & (HNDVI)] = 7
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["VEG"]) & (MASK==0) & (V_SR) & (MNDVI)] = 8
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["VEG"]) & (MASK==0) & (R_SR) & (HNDVI)] = 9
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["VEG"]) & (MASK==0) & (R_SR) & (MNDVI)] = 10
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["VEG"]) & (MASK==0)] = 11
    
    
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["SOIL"]) & (MASK==0) & (HMIR1)] = 12
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["SOIL"]) & (MASK==0) & (MMIR1)] = 13
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["SOIL"]) & (MASK==0) & (LMIR1)] = 14
        
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["UNK"]) & (MASK==0)] = 15
    
    MASK[(SIAM_8==CLASS_ID_SIAM_SDC["ND"])] = 0
    
    return MASK

#%%
def GROUP_SIAM_SDC_46(SIAM_46, SDC_13):
    
    # -------------------------------------
    #  0 = "ND"
    #  1 = "V"
    #  2 = "SHV"
    #  3 = "R"
    #  4 = "WR"
    #  5 = "PB"    
    #  6 = "BB"
    #  7 = "SHB"
    #  8 = "WASH"    
    #  9 = "TKCL"
    # 10 = "TNCL"
    # 11 = "SN"
    # 12 = "SHCL"
    # 12 = "UNK"
    # -------------------------------------
    
    CLASS_ID_SDC  = SDC_CLASS_ID()
    
    #
    MASK = SIAM_46.copy()
    
    MASK[(SIAM_46 == 46) & (SDC_13  == CLASS_ID_SDC["WAT"])] = 6
    MASK[(SIAM_46 == 46) & (SDC_13  == CLASS_ID_SDC["CL"]) ] = 2
    MASK[(SIAM_46 == 46) & (SDC_13  == CLASS_ID_SDC["SI"]) ] = 4
    MASK[(SIAM_46 == 46) & (SDC_13  == CLASS_ID_SDC["SV"]) ] = 40
    MASK[(SIAM_46 == 46) & (SDC_13  == CLASS_ID_SDC["SS"]) ] = 41
    
    mask = (SDC_13  == CLASS_ID_SDC["TCD"]) | (SDC_13  == CLASS_ID_SDC["TCL"])
    
    MASK[(SIAM_46 == 46) & mask ] = 13
    
    mask = (SDC_13  == CLASS_ID_SDC["SHR"]) | (SDC_13  == CLASS_ID_SDC["GRS"]) | (SDC_13  == CLASS_ID_SDC["SPV"])
           
    MASK[(SIAM_46 == 46) & mask ] = 19
    
    mask = (SDC_13  == CLASS_ID_SDC["OLL"]) | (SDC_13  == CLASS_ID_SDC["OLD"])
    
    MASK[(SIAM_46 == 46) & mask ] = 24
    
    
    MASK[((SIAM_46 == 43)|(SIAM_46 == 45)) & (SDC_13  == CLASS_ID_SDC["SV"]) ] = 40
    MASK[((SIAM_46 == 43)|(SIAM_46 == 45)) & (SDC_13  == CLASS_ID_SDC["SS"]) ] = 41
    
    
    return MASK


def GROUP_SIAM_SDC_13(SIAM_13, SDC_13):
    
    # -------------------------------------
    #  0 = "ND"
    #  1 = "V"
    #  2 = "SHV"
    #  3 = "R"
    #  4 = "WR"
    #  5 = "PB"    
    #  6 = "BB"
    #  7 = "SHB"
    #  8 = "WASH"    
    #  9 = "TKCL"
    # 10 = "TNCL"
    # 11 = "SN"
    # 12 = "SHCL"
    # 12 = "UNK"
    # -------------------------------------
    
    CLASS_ID_SDC  = SDC_CLASS_ID()
    CLASS_ID_SIAM = SIAM_13_CLASS_ID()               
    #
    MASK = SIAM_13.copy()
    
    MASK[(SIAM_13 == CLASS_ID_SIAM["UNK"]) & (SDC_13  == CLASS_ID_SDC["WAT"])] = CLASS_ID_SIAM["WASH"]
    MASK[(SIAM_13 == CLASS_ID_SIAM["UNK"]) & (SDC_13  == CLASS_ID_SDC["CL"]) ] = CLASS_ID_SIAM["TNCL"]
    MASK[(SIAM_13 == CLASS_ID_SIAM["UNK"]) & (SDC_13  == CLASS_ID_SDC["SI"]) ] = CLASS_ID_SIAM["SN"]
    MASK[(SIAM_13 == CLASS_ID_SIAM["UNK"]) & (SDC_13  == CLASS_ID_SDC["SV"]) ] = CLASS_ID_SIAM["SHV"]
    MASK[(SIAM_13 == CLASS_ID_SIAM["UNK"]) & (SDC_13  == CLASS_ID_SDC["SS"]) ] = CLASS_ID_SIAM["SHB"]
    MASK[(SIAM_13 == CLASS_ID_SIAM["UNK"]) & (SDC_13  == CLASS_ID_SDC["ND"]) ] = CLASS_ID_SIAM["ND"]
    
    mask = (SDC_13  == CLASS_ID_SDC["TCD"]) |\
           (SDC_13  == CLASS_ID_SDC["TCL"])
    
    MASK[(SIAM_13 == CLASS_ID_SIAM["UNK"]) & mask ] = CLASS_ID_SIAM["V"]
    
    mask = (SDC_13  == CLASS_ID_SDC["SHR"]) |\
           (SDC_13  == CLASS_ID_SDC["GRS"]) |\
           (SDC_13  == CLASS_ID_SDC["SPV"])
           
    MASK[(SIAM_13 == CLASS_ID_SIAM["UNK"]) & mask ] = CLASS_ID_SIAM["R"]
    
    mask = (SDC_13  == CLASS_ID_SDC["OLL"]) |\
           (SDC_13  == CLASS_ID_SDC["OLD"])
    
    MASK[(SIAM_13 == CLASS_ID_SIAM["UNK"]) & mask ] = CLASS_ID_SIAM["BB"]
    
    MASK[(SIAM_13 == CLASS_ID_SIAM["WASH"]) & (SDC_13  == CLASS_ID_SDC["SV"]) ] = CLASS_ID_SIAM["SHV"]
    MASK[(SIAM_13 == CLASS_ID_SIAM["WASH"]) & (SDC_13  == CLASS_ID_SDC["SS"]) ] = CLASS_ID_SIAM["SHB"]
    
    
    return MASK

def GROUP_SIAM_SDC_FMASK_8(SIAM_13, SDC_13, FMASK):
    
    # -------------------------------------
    # 0: NO DATA
    
    # 1: WATER
    # 2: CLOUD
    # 3: SNOW
    
    # 4: SHADOW VEGETETION
    # 5: SHADOW SOIL
    
    # 6: VEGETETION
    # 7: SOIL
    
    # 8: UNKNOWN
    # -------------------------------------
    
    CLASS_ID_SDC      = SDC_CLASS_ID()
    CLASS_ID_SIAM     = SIAM_13_CLASS_ID()
    CLASS_ID_FMASK    = FMASK_CLASS_ID()
    CLASS_ID_SIAM_SDC = SIAM_8_CLASS_ID()
    
    mask_wat = ( 1*(FMASK == CLASS_ID_FMASK["WAT"]) +  1*(SDC_13 == CLASS_ID_SDC["WAT"]) +  1*(SIAM_13 == CLASS_ID_SIAM["WASH"]) ) >= 2
    mask_snw = ( 1*(FMASK == CLASS_ID_FMASK["SI"])  +  1*(SDC_13 == CLASS_ID_SDC["SI"])  +  1*(SIAM_13 == CLASS_ID_SIAM["SN"]) ) >= 2
    
    mask_veg = (SDC_13  == CLASS_ID_SDC["TCD"]) | (SDC_13  == CLASS_ID_SDC["TCL"]) | (SDC_13  == CLASS_ID_SDC["SHR"]) | (SDC_13  == CLASS_ID_SDC["GRS"]) | (SDC_13  == CLASS_ID_SDC["SPV"]) | (SDC_13  == CLASS_ID_SDC["SV"]) |\
               (SIAM_13 == CLASS_ID_SIAM["V"])  | (SIAM_13 == CLASS_ID_SIAM["R"])  | (SIAM_13 == CLASS_ID_SIAM["WR"]) | (SIAM_13 == CLASS_ID_SIAM["PB"]) | (SIAM_13 == CLASS_ID_SIAM["SHV"])
                
    mask_bsl = (SDC_13  == CLASS_ID_SDC["OLL"]) | (SDC_13  == CLASS_ID_SDC["OLD"]) | (SDC_13  == CLASS_ID_SDC["SS"]) |\
               (SIAM_13 == CLASS_ID_SIAM["BB"])  | (SIAM_13 == CLASS_ID_SIAM["SHB"])
                
    mask_shd = (FMASK == CLASS_ID_FMASK["SHD"])
    mask_cld = (FMASK == CLASS_ID_FMASK["CL"]) | (SIAM_13 == CLASS_ID_SIAM["TKCL"]) | (SIAM_13 == CLASS_ID_SIAM["TNCL"])
    # mask_cld = (FMASK == CLASS_ID_FMASK["CL"]) 
    
    MASK = np.zeros_like(mask_wat, dtype=int)
    
    MASK[(MASK==0) & mask_wat] = CLASS_ID_SIAM_SDC["WAT"]
    MASK[(MASK==0) & mask_cld] = CLASS_ID_SIAM_SDC["CLD"]
    MASK[(MASK==0) & mask_snw] = CLASS_ID_SIAM_SDC["SNW"]
    
    MASK[(MASK==0) & mask_veg & mask_shd] = CLASS_ID_SIAM_SDC["SHV"]
    MASK[(MASK==0) & mask_bsl & mask_shd] = CLASS_ID_SIAM_SDC["SHB"]
    
    MASK[(MASK==0) & mask_veg] = CLASS_ID_SIAM_SDC["VEG"]
    MASK[(MASK==0) & mask_bsl] = CLASS_ID_SIAM_SDC["SOIL"]
    
    
    mask_shd = ( (FMASK == CLASS_ID_FMASK["SHD"]) | (SIAM_13 == CLASS_ID_SIAM["SHV"]) | (SIAM_13 == CLASS_ID_SIAM["SHB"]) | (SIAM_13 == CLASS_ID_SIAM["SHCL"]) | (SIAM_13 == CLASS_ID_SIAM["WASH"]) )
    
    MASK[(MASK==0) & mask_veg & mask_shd] = CLASS_ID_SIAM_SDC["SHV"]
    MASK[(MASK==0) & mask_bsl & mask_shd] = CLASS_ID_SIAM_SDC["SHB"]
    
    mask_wat = ( (FMASK == CLASS_ID_FMASK["WAT"]) |  (SDC_13 == CLASS_ID_SDC["WAT"]) |  (SIAM_13 == CLASS_ID_SIAM["WASH"]) )
    mask_snw = ( (FMASK == CLASS_ID_FMASK["SI"]) |  (SDC_13 == CLASS_ID_SDC["SI"]) |  (SIAM_13 == CLASS_ID_SIAM["SN"]) )
    mask_cld = ( (  (SIAM_13 == CLASS_ID_SIAM["SHCL"]) ) )
    # mask_cld = ( ( (SIAM_13 == CLASS_ID_SIAM["TKCL"]) | (SIAM_13 == CLASS_ID_SIAM["TNCL"]) | (SIAM_13 == CLASS_ID_SIAM["SHCL"]) ) )
    
    MASK[(MASK==0) & mask_wat] = CLASS_ID_SIAM_SDC["WAT"]
    MASK[(MASK==0) & mask_snw] = CLASS_ID_SIAM_SDC["SNW"]
    
    MASK[(MASK==0) & (SDC_13 == CLASS_ID_SDC["SV"]) ] = CLASS_ID_SIAM_SDC["SHV"]
    MASK[(MASK==0) & (SDC_13 == CLASS_ID_SDC["SS"]) ] = CLASS_ID_SIAM_SDC["SHB"]
    
    MASK[(MASK==0) & mask_cld] = CLASS_ID_SIAM_SDC["CLD"]
    
    MASK[(MASK==0) & (SIAM_13 != CLASS_ID_SIAM["ND"])] = CLASS_ID_SIAM_SDC["UNK"]
    MASK[(SIAM_13 == CLASS_ID_SIAM["ND"])] = CLASS_ID_SIAM_SDC["ND"]
    
    return MASK

def GROUP_SIAM_SDC_8(SIAM_13, SDC_13):
    
    # -------------------------------------
    # 0: NO DATA
    
    # 1: WATER
    # 2: CLOUD
    # 3: SNOW
    
    # 4: SHADOW VEGETETION
    # 5: SHADOW SOIL
    
    # 6: VEGETETION
    # 7: SOIL
    
    # 8: UNKNOWN
    # -------------------------------------
    
    CLASS_ID_SDC      = SDC_CLASS_ID()
    CLASS_ID_SIAM     = SIAM_13_CLASS_ID()
    CLASS_ID_SIAM_SDC = SIAM_8_CLASS_ID()
    
    mask_wat     = (SIAM_13 == CLASS_ID_SIAM["WASH"])  |\
                   (SDC_13  == CLASS_ID_SDC["WAT"])
               
    mask_cld     = (SIAM_13 == CLASS_ID_SIAM["TKCL"])  | (SIAM_13 == CLASS_ID_SIAM["TNCL"]) | (SIAM_13 == CLASS_ID_SIAM["SHCL"])  |\
                   (SDC_13  == CLASS_ID_SDC["CL"])
               
    mask_snw     = (SIAM_13 == CLASS_ID_SIAM["SN"])  |\
                   (SDC_13  == CLASS_ID_SDC["SI"])
    
    mask_shd_veg = (SIAM_13 == CLASS_ID_SIAM["SHV"])  |\
                   (SDC_13  == CLASS_ID_SDC["SV"])
    
    mask_shd_bsl = (SIAM_13 == CLASS_ID_SIAM["SHB"])  |\
                   (SDC_13  == CLASS_ID_SDC["SS"])
    
    
    mask_veg = (SIAM_13 == CLASS_ID_SIAM["V"])  |\
               (SIAM_13 == CLASS_ID_SIAM["R"])  |\
               (SIAM_13 == CLASS_ID_SIAM["WR"]) |\
               (SIAM_13 == CLASS_ID_SIAM["PB"]) |\
               (SDC_13  == CLASS_ID_SDC["TCD"]) |\
               (SDC_13  == CLASS_ID_SDC["TCL"]) |\
               (SDC_13  == CLASS_ID_SDC["SHR"]) |\
               (SDC_13  == CLASS_ID_SDC["GRS"]) |\
               (SDC_13  == CLASS_ID_SDC["SPV"])
               
    mask_bsl = (SIAM_13 == CLASS_ID_SIAM["BB"]) |\
               (SDC_13  == CLASS_ID_SDC["OLL"]) |\
               (SDC_13  == CLASS_ID_SDC["OLD"])
    
    mask_unk = (SIAM_13 == CLASS_ID_SIAM["UNK"]) |\
               (SDC_13  == CLASS_ID_SDC["UNK"])
               
    mask_ndt = (SIAM_13 == CLASS_ID_SIAM["ND"]) |\
               (SDC_13  == CLASS_ID_SDC["ND"])

               
    #
    MASK = np.zeros(SIAM_13.shape)
    
    MASK[mask_cld     & (MASK==0)] = CLASS_ID_SIAM_SDC["CLD"]
    
    MASK[mask_veg     & (MASK==0)] = CLASS_ID_SIAM_SDC["VEG"]
    
    MASK[mask_bsl     & (MASK==0)] = CLASS_ID_SIAM_SDC["SOIL"]
    
    MASK[mask_shd_veg & (MASK==0)] = CLASS_ID_SIAM_SDC["SHV"]
    MASK[mask_shd_bsl & (MASK==0)] = CLASS_ID_SIAM_SDC["SHB"]
    
    MASK[mask_wat     & (MASK==0)] = CLASS_ID_SIAM_SDC["WAT"]
    MASK[mask_snw     & (MASK==0)] = CLASS_ID_SIAM_SDC["SNW"]
    

    MASK[mask_unk     & (MASK==0)] = CLASS_ID_SIAM_SDC["UNK"]
    
    MASK[mask_ndt] = CLASS_ID_SIAM_SDC["ND"]
    
    return MASK
 
def Group_SIAM_46(orig,dst, simple=True):
    
    ref = orig.copy()
    
    cond = (ref==46)
    ref[cond] = dst[cond]
    
    if (simple is False):
    
        cond = (dst==1)&(ref==2)
        ref[cond] = dst[cond]
        
        cond = (dst==3)&(ref==4)
        ref[cond] = dst[cond]
        
        cond = (dst==5)&(ref==6)
        ref[cond] = dst[cond]
        
        
        cond = (dst<ref)&(dst>=7)&(dst<=9)
        ref[cond] = dst[cond]
        
        
        cond = (dst==10)&(ref==11)
        ref[cond] = dst[cond]
        
        cond = (dst==12)&(ref==13)
        ref[cond] = dst[cond]
        
        cond = (dst==14)&(ref==15)
        ref[cond] = dst[cond]
        
        cond = (dst==16)&(ref==17)
        ref[cond] = dst[cond]
        
        cond = (dst==18)&(ref==19)
        ref[cond] = dst[cond]
        
        
        cond = (dst<ref)&(dst>=23)&(dst<=26)
        ref[cond] = dst[cond]
        
        cond = (dst<ref)&(dst>=27)&(dst<=30)
        ref[cond] = dst[cond]
        
        cond = (dst<ref)&(dst>=31)&(dst<=34)
        ref[cond] = dst[cond]
        
        cond = (dst<ref)&(dst>=35)&(dst<=38)
        ref[cond] = dst[cond]
        
        
        cond = (ref==39)&(dst>=7)&(dst<=38)
        ref[cond] = dst[cond]
        
        cond = (ref==40)&(dst>=7)&(dst<=38)
        ref[cond] = dst[cond]
        
        cond = (ref==41)&(dst>=7)&(dst<=38)
        ref[cond] = dst[cond]
        
        cond = (ref==42)&(dst>=1)&(dst<=38)
        ref[cond] = dst[cond]
        
        cond = (ref==43)&(dst>=1)&(dst<=38)
        ref[cond] = dst[cond]
        
        cond = (ref==44)&(dst>=7)&(dst<=38)
        ref[cond] = dst[cond]
        
        cond = (ref==45)&(dst>=5)&(dst<=6)
        ref[cond] = dst[cond]
        
    return ref

def BITEMPORAL_SIAM_11(SIAM_13_T1, SIAM_13_T2):
    
    # 0: NO DATA
    
    # 1: VEG + (increasing)
    # 2: VEG = (constant)
    # 3: VEG - (decreasing)
    
    # 4: BS + (increasing)
    # 5: BS = (constant)
    # 6: BS - (decreasing)
    
    # 7: WASH + (increasing)
    # 8: WASH = (constant)
    # 9: WASH - (decreasing)
    
    # 10 : CLD | SNOW
    
    # 11: UNKNOWN
    
    
    DIFF = np.zeros(SIAM_13_T1.shape)
    
    DIFF[ ( (SIAM_13_T1==0)  | (SIAM_13_T2==0) ) & (DIFF==0) ] = 0
    
    DIFF[ ( (SIAM_13_T1==13) | (SIAM_13_T2==13) ) & (DIFF==0) ] = 11
    
    
    DIFF[((SIAM_13_T1==9)|(SIAM_13_T1==10)|(SIAM_13_T1==11)|(SIAM_13_T1==12) |\
          (SIAM_13_T2==9)|(SIAM_13_T2==10)|(SIAM_13_T2==11)|(SIAM_13_T2==12)) & (DIFF==0) ] = 10
    
    
    DIFF[ ( (SIAM_13_T1!=8) & (SIAM_13_T2==8) ) & (DIFF==0) ] = 7
    DIFF[ ( (SIAM_13_T1==8) & (SIAM_13_T2==8) ) & (DIFF==0) ] = 8
    DIFF[ ( (SIAM_13_T1==8) & (SIAM_13_T2!=8) ) & (DIFF==0) ] = 9
    
    
    
    DIFF[ ( (SIAM_13_T2==6) & (SIAM_13_T1==7) ) & (DIFF==0) ] = 4
    
    DIFF[ (SIAM_13_T1==SIAM_13_T2) & ( (SIAM_13_T1>=6) & (SIAM_13_T1<=7) ) & (DIFF==0) ] = 5
    
    DIFF[ (SIAM_13_T1!=SIAM_13_T2) & ( (SIAM_13_T1>=6) & (SIAM_13_T1<=7) ) & (DIFF==0) ] = 6
    
    
    
    
    DIFF[ (SIAM_13_T2==1) & ( (SIAM_13_T1>=2) & (SIAM_13_T1<=5) ) & (DIFF==0) ] = 1
    DIFF[ (SIAM_13_T2==3) & ( (SIAM_13_T1==2) | (SIAM_13_T1==4) ) & (DIFF==0) ] = 1
        
    DIFF[ (SIAM_13_T1==SIAM_13_T2) & ( (SIAM_13_T1>=1) & (SIAM_13_T1<=5) ) & (DIFF==0) ] = 2
    
    DIFF[ (SIAM_13_T1!=SIAM_13_T2) & ( (SIAM_13_T1>=1) & (SIAM_13_T1<=5) ) & (DIFF==0) ] = 3

    

    DIFF[ (DIFF==9) & ( (SIAM_13_T2>=1) & (SIAM_13_T2<=5) ) ] = 1
    DIFF[ (DIFF==9) & ( (SIAM_13_T2>=6) & (SIAM_13_T2<=7) ) ] = 4
    DIFF[ (DIFF==6) & ( (SIAM_13_T2>=1) & (SIAM_13_T2<=5) ) ] = 1    
    DIFF[ (DIFF==3) & ( (SIAM_13_T2>=6) & (SIAM_13_T2<=7) ) ] = 4
    
    
    DIFF[ (DIFF==0) & ( (SIAM_13_T2>=1) & (SIAM_13_T2<=5) ) ]  = 2
    DIFF[ (DIFF==0) & ( (SIAM_13_T2>=6) & (SIAM_13_T2<=7) ) ]  = 5
    DIFF[ (DIFF==0) & ( (SIAM_13_T2==8) & (SIAM_13_T2<=8) ) ]  = 8
    DIFF[ (DIFF==0) & ( (SIAM_13_T2==9) & (SIAM_13_T2<=12) ) ] = 10
    
    DIFF[ (DIFF==11) & ( (SIAM_13_T2>=1) & (SIAM_13_T2<=5) ) ]  = 2
    DIFF[ (DIFF==11) & ( (SIAM_13_T2>=6) & (SIAM_13_T2<=7) ) ]  = 5
    DIFF[ (DIFF==11) & ( (SIAM_13_T2==8) & (SIAM_13_T2<=8) ) ]  = 8
    DIFF[ (DIFF==11) & ( (SIAM_13_T2==9) & (SIAM_13_T2<=12) ) ] = 10
    
    
    DIFF[ (DIFF==10) & ( (SIAM_13_T2>=1) & (SIAM_13_T2<=5) ) ]  = 2
    DIFF[ (DIFF==10) & ( (SIAM_13_T2>=6) & (SIAM_13_T2<=7) ) ]  = 5
    DIFF[ (DIFF==10) & ( (SIAM_13_T2==8) & (SIAM_13_T2<=8) ) ]  = 8
    
    
    return DIFF

#%%
def get_8_colormap():
    
    cmap = {0:  (255, 255, 255),
            
            1:  (   0,   0, 255),
            2:  (   0, 204, 255),
            3:  (   0, 255, 255),
            
            4:  (   0, 102,   0),
            5:  ( 102,  51,   0),
            
            6:  (   0, 255,   0),
            7:  ( 230, 115,   0),
            
            8:  ( 255,   0, 255)}
    
    return cmap

def get_11_colormap():
    
    cmap = {0:  (255, 255, 255),
            
            1:  (  0, 255, 0),
            2:  (  0, 170, 0),
            3:  (  0, 90,  0),
            
            4:  (255, 153,   0),
            5:  (179, 179,   0),
            6:  (153,   0,  51),
            
            7:  (  0, 204, 255),
            8:  (  0,   0, 255),
            9:  (  51, 51, 153),
            
            10: (  0, 255, 255),
            
            11: (255,   0, 255)}
    
    return cmap

def get_13_colormap():
    
    cmap = {0:  (255, 255, 255),
            1:  (  0, 255,   0),
            2:  (  0,  80,   0),
            3:  (102, 153,   0),
            4:  (179, 179,   0),
            5:  (  0, 204, 153),
            6:  (204, 153, 102),
            7:  (179, 107,   0),
            8:  (  0,   0, 255),
            9:  (204, 230, 255),
            10: (230, 230, 230),
            11: (  0, 255, 255),
            12: (179, 179, 204),
            13: (255,   0, 255)}
    
    return cmap

def get_15_colormap():
    
    cmap = {0:   ( 255, 255, 255),
            
            1:   (   0,   0, 255),
            2:   ( 102, 102, 255),
            
            3:   ( 210, 230, 230),
            4:   (   0, 255, 255),
            
            5:   (   0, 102, 0),
            6:   ( 102, 34, 0),
            
            7:   (   0, 255, 0),
            8:   (  22, 231, 22),
            9:   (  53, 195, 53),
            10:  ( 113, 175, 55),
            11:  ( 156, 201, 65),
            
            12:  ( 252, 181, 0),
            13:  ( 233, 158, 99),
            14:  ( 190, 138, 97),
            
            15:  ( 255,   0,   0)}
    
    return cmap

def get_46_colormap():
    
    cmap = {0:   (255, 255, 255),
            
            1:   (242, 242, 242),
            2:   (217, 217, 217),
            
            3:   ( 51, 255, 255),
            4:   (153, 255, 255),
            
            5:   (  0,   0, 255),
            6:   ( 77,  77, 255),
            
            7:   (  0, 230, 172),
            8:   (  0, 204, 153),
            9:   (  0, 179, 134),
            
            10:  (  0, 255,   0),
            11:  (  0, 230,   0),
            
            12:  ( 51, 204,   0),
            13:  ( 45, 179,   0),
            
            14:  (172, 230,   0),
            15:  (153, 204,   0),
            
            16:  (153, 204,  51),
            17:  (122, 163,  41),
            
            18:  (127, 160,  70),
            19:  ( 99, 124,  54),
            
            20:  (194, 225, 132),
            21:  (174, 215,  91),
            
            22:  (158, 153,  71),
            
            23:  (255, 204, 153),
            24:  (255, 191, 128),
            25:  (255, 179, 102),
            26:  (255, 166,  77),
            
            27:  (204, 153, 102),
            28:  (198, 140,  83),
            29:  (191, 128,  64),
            30:  (172, 115,  57),
            
            31:  (179,  89,   0),
            32:  (153,  77,   0),
            33:  (128,  64,   0),
            34:  (102,  51,   0),
            
            35:  (153,  51, 102),
            36:  (134,  45,  89),
            37:  (115,  38,  77),
            38:  ( 96,  32,  64),
            
            39:  (153, 153,  77),
            40:  ( 38,  77,   0),
            41:  (128,   0,  64),
            42:  (163, 163, 194),
            43:  (128, 191, 255),
            44:  (  0, 179, 143),
            45:  (173, 173, 235),
            
            46:  (255,   0, 255)}
    
    return cmap

#%%
def raster_save(mask, src, dst, cmap=None):
    
    print("Saving: {}".format(dst))
    
    if (os.path.isfile(dst)):
        print("ERROR -> File already exists: {}".format(dst))
        return
    
    if (os.path.isdir(dst)):
        print("ERROR -> Unknown file extension: {}".format(dst))
        return
    
    if ((os.path.split(dst)[-1]).count(".") == 0):
        print("ERROR -> Unknown file extension: {}".format(dst))
        return
        
    with rio.open(src) as dataset:
        meta = dataset.meta
    
    meta["count"]    = 1
    meta["dtype"]    = "uint8"
    meta["driver"]   = "GTiff"
    meta["compress"] = "deflate"
    
    with rio.open(dst, "w", **meta) as dataset:
        
        dataset.write((mask).astype(meta["dtype"]), 1)
        
        if not(cmap is None):
            dataset.write_colormap(1, cmap)
        
def shape_save(src, dst, vals):
    
    
    img  = rio.open(src).read(1)
    mask = np.zeros(img.shape, dtype=bool)
    
    for val in vals:
        mask = mask | (img==val)
        
    mask = (1*mask).astype(int)
        
    tmp_tif = "/".join(dst.split(".")[:-1])+"_tmp.tif"
    raster_save(mask, src, tmp_tif, opt=None)    
    
    
    mask = None
    img  = None
    
    cmd = "gdal_polygonize.py -mask {} {} {}".format(tmp_tif, tmp_tif, dst)
    
    try:
        call(cmd, shell=True)
    except:
        os.system(cmd)
        
    os.remove(tmp_tif)
        
def image_stretching(img, p=2.0, mask=None):
    
    # =========================================================================
    # INPUTS:
    #
    # img     = Image to be streached (numpy array)        (required)
    # p       = Percentage streaching (int / float)        (optional) (default 2%)
    # mask    = Mask of valid pixels  (numpy array bool)   (optional) (default None)
    #
    # OUTUT:
    #
    # band    = image streached from 0 to 1 (numpy array)
    # =========================================================================
    
    if (mask is None):
        idx = int((img.size)*p/100) 
        x_min, x_max = np.sort(img, axis=None)[[idx-1,-idx]]
    else:
        idx = int(mask.sum()*p/100) 
        x_min, x_max = np.sort(img[mask])[[idx-1,-idx]]
         
    band = img.copy() 
    band[band<x_min] = x_min 
    band[band>x_max] = x_max 
    band = (band-x_min)/(x_max-x_min) 
    band[band>1.] = 1 
    band[band<0.] = 0. 
     
    if not(mask is None): 
        band[mask==False] = 0. 
         
    return band