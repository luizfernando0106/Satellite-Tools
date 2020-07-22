import os
import numpy as np
import rasterio as rio
from subprocess import call

#%%
def SDC_CLASS_ID():
    
    CLASS_ID = dict()
    
    CLASS_ID["ND"]  = 0
    
    CLASS_ID["WAT"] = 1
    
    CLASS_ID["CL"]  = 2
    CLASS_ID["SI"]  = 3
    
    CLASS_ID["TCD"] = 4
    CLASS_ID["TCL"] = 5
    
    CLASS_ID["SHR"] = 6
    CLASS_ID["GRS"] = 7
    CLASS_ID["SPV"] = 8
    
    CLASS_ID["OLL"] = 9
    CLASS_ID["OLD"] = 10
    
    CLASS_ID["SV"]  = 11
    CLASS_ID["SS"]  = 12
    
    CLASS_ID["UNK"] = 13
    
    
    return CLASS_ID

#%%
def SDC_13_6(BAND):
    
    # BAND["BLUE"]
    # BAND["GREEN"]
    # BAND["RED"]
    # BAND["NIR"]
    # BAND["SWIR1"]
    # BAND["SWIR2"]
    
    NO_DATA_MASK = ((BAND["BLUE"] == 0) | (BAND["GREEN"] == 0))
    
    CLASS_ID = SDC_CLASS_ID()
    
    err = 0.0000001
    
    #
    S_WATER = ((BAND["BLUE"]-BAND["GREEN"]) > -0.2)
    S_WATER = (S_WATER) & (BAND["GREEN"] >= BAND["RED"]) & (BAND["RED"] >= BAND["NIR"]) & (BAND["NIR"] >= BAND["SWIR1"])
    
    S_WATER_OTHER = (    BAND["BLUE"]  >=     BAND["GREEN"]) &\
                    (    BAND["GREEN"] >=     BAND["RED"]  ) &\
                    (    BAND["RED"]   <=     BAND["NIR"]  ) &\
                    (    BAND["NIR"]   <  1.3*BAND["RED"]  ) &\
                    (1.3*BAND["RED"]   <  0.12             ) &\
                    (0.12              >      BAND["SWIR1"]) &\
                    (    BAND["SWIR1"] >      BAND["SWIR2"])
    
    S_WATER_OTHER = (S_WATER_OTHER) &\
                (0.039 < BAND["NIR"]) &\
                (BAND["NIR"] < BAND["GREEN"])
                
#    S_GROWING_14 = (BAND["BLUE"] < BAND["GREEN"]) & (BAND["GREEN"] < BAND["RED"]) & (BAND["RED"] < BAND["NIR"])
    
#    S_GROWING_15 = (S_GROWING_14) & (BAND["NIR"] < BAND["SWIR1"])
                
    NDSI = (BAND["GREEN"]-BAND["SWIR1"])/(BAND["GREEN"]+BAND["SWIR1"] + err)
    
    WETNESS =  66.96*BAND["BLUE"]  +\
               53.55*BAND["GREEN"] +\
               23.61*BAND["RED"]   +\
               16.72*BAND["NIR"]   -\
              194.53*BAND["SWIR1"] -\
              137.19*BAND["SWIR2"]
              
    WETNESS = WETNESS > 5.
              
#    BRIGHTSOIL = (BAND["BLUE"] < 0.27) & (S_GROWING_15)
#    BRIGHTSOIL = (BRIGHTSOIL) | ((BAND["BLUE"] < 0.27) & (S_GROWING_14) & ((BAND["SWIR1"]-BAND["SWIR2"]) > 0.038) )
    
    MAX = np.maximum(np.maximum(BAND["GREEN"],BAND["RED"]),BAND["NIR"])
    MIN = np.minimum(np.minimum(BAND["GREEN"],BAND["RED"]),BAND["NIR"])
    
    SATURATION = (MAX-MIN)/(MAX+err)
                      
    
    
    MIN = np.minimum(np.minimum(np.minimum(BAND["BLUE"],BAND["GREEN"]),BAND["RED"]),BAND["NIR"])
    
    S_SNOW = (MIN>0.3) & (NDSI > 0.65)
    
    
    MIN = np.minimum(np.minimum(BAND["BLUE"],BAND["GREEN"]),BAND["RED"])
    
    MAX = np.maximum(np.maximum(np.maximum(BAND["BLUE"],BAND["GREEN"]),BAND["RED"]),BAND["NIR"])
    
    S_CLOUD = (MIN > 0.17) &\
              (MAX > 0.30) &\
              (BAND["NIR"]/(BAND["RED"]+err)   >= 1.30) &\
              (BAND["NIR"]/(BAND["GREEN"]+err) >= 1.30) &\
              (BAND["NIR"]/(BAND["SWIR1"]+err) >= 0.95) &\
              (BAND["SWIR1"] > MIN) &\
              (NDSI < 0.65)
              
              
    MAX = np.maximum(np.maximum(np.maximum(BAND["BLUE"],BAND["GREEN"]),BAND["RED"]),BAND["NIR"])
    MAX = np.maximum(np.maximum(MAX,BAND["SWIR1"]),BAND["SWIR2"])
    
    MIN = np.minimum(np.minimum(np.minimum(BAND["BLUE"],BAND["GREEN"]),BAND["RED"]),BAND["NIR"])
    
    S_CLOUD_1 = (MAX > 0.47) & (MIN > 0.37)
    
    
    MIN = np.minimum(np.minimum(BAND["BLUE"],BAND["GREEN"]),BAND["RED"])
    MAX = np.maximum(np.maximum(BAND["GREEN"],BAND["RED"]),BAND["NIR"])
    
    S_CLOUD_2 = (MIN > 0.21) & (BAND["SWIR1"] > MIN) & (SATURATION >= 0.2) & (SATURATION <= 0.4) &\
                (MAX >= 0.35) & (NDSI > -0.)
    
    MAX        = None
    MIN        = None
    NDSI       = None
    SATURATION = None
    
    #%%
    NDVI = (BAND["NIR"] - BAND["RED"])/(BAND["NIR"] + BAND["RED"] + err)
    
    NDVI_L = (NDVI <= 0.00)
    NDVI_H = (NDVI >= 0.45)
    NDVI_M = (NDVI >= 0.00) & (NDVI <= 0.45)
    
    #%%
    MASK = np.zeros(BAND["RED"].shape) + CLASS_ID["UNK"]
    
    #%% NDVI_L
    
    # CLASS_ID["SI"]
    
    MASK[(NDVI_L) &\
         (S_SNOW) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SI"]
    
    # CLASS_ID["WAT"] DWAT
    MAX = np.maximum(BAND["SWIR1"],BAND["SWIR2"])
    
    MASK[(NDVI_L)  &\
         (S_WATER) &\
         (BAND["BLUE"] >=0.078) &\
         (BAND["GREEN"]>=0.040) &\
         (BAND["GREEN"]<=0.120) &\
         (MAX<=0.040) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["WAT"]
        
    # CLASS_ID["WAT"] SWAT
    MAX = np.maximum(np.maximum(BAND["NIR"],BAND["SWIR1"]),BAND["SWIR2"])
    
    MASK[(NDVI_L)  &\
         (BAND["RED"]   >= MAX)   &\
         (BAND["RED"]   >= 0.040) &\
         (BAND["RED"]   <= 0.190) &\
         (BAND["BLUE"]  >  0.078) &\
         (BAND["SWIR1"] <  0.040) &\
         (BAND["SWIR2"] <  0.040) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["WAT"]
    
    # CLASS_ID["CL"] 
    
    MASK[(NDVI_L)  &\
         (BAND["BLUE"]  > 0.94) &\
         (BAND["GREEN"] > 0.94) &\
         (BAND["RED"]   > 0.94) &\
         (BAND["NIR"]   > 0.94) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["CL"]
        
    # CLASS_ID["WAT"] DWAT
    
    MASK[(NDVI_L)  &\
         (WETNESS) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["WAT"]
        
    # CLASS_ID["SS"]
    
    MASK[(NDVI_L)  &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SS"]
        
        
    #%% NDVI_M
    
    # CLASS_ID["SI"]
    
    MASK[(NDVI_M) &\
         (S_SNOW) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SI"]
        
    # CLASS_ID["CL"]
    
    MASK[(NDVI_M) &\
         (BAND["BLUE"]  > 0.94) &\
         (BAND["GREEN"] > 0.94) &\
         (BAND["RED"]   > 0.94) &\
         (BAND["NIR"]   > 0.94) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["CL"]
        
    # CLASS_ID["WAT"] SWAT
    MAX = np.maximum(BAND["SWIR1"],BAND["SWIR2"])
    
    MASK[(NDVI_M) &\
         (S_WATER_OTHER) &\
         (BAND["BLUE"] > 0.078) &\
         (MAX < 0.058) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["WAT"]
    
    # CLASS_ID["CL"]
    
    MASK[(NDVI_M) &\
         (S_CLOUD | S_CLOUD_1 | S_CLOUD_2) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["CL"]
        
    # CLASS_ID["CL"]
    
    MASK[(NDVI_M) &\
         (BAND["BLUE"]  > BAND["GREEN"]) &\
         (BAND["GREEN"] > BAND["RED"]) &\
         (BAND["NIR"]   > 0.254) &\
         (BAND["BLUE"]  > 0.165) &\
         (NDVI          < 0.400) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["CL"]
        
    # CLASS_ID["CL"]
    
    MASK[(NDVI_M) &\
         (BAND["BLUE"]  > BAND["GREEN"]) &\
         (BAND["BLUE"]  > 0.270) &\
         (BAND["GREEN"] > 0.210) &\
         (np.abs(BAND["RED"]-BAND["GREEN"]) <= 0.100) &\
         (BAND["NIR"]   > 0.350) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["CL"]
        
    # CLASS_ID["SV"]
    
    MASK[(NDVI_M) &\
         (0.130         > BAND["BLUE"])  &\
         (BAND["BLUE"]  > BAND["GREEN"]) &\
         (BAND["GREEN"] > BAND["RED"])   &\
         (BAND["RED"]   < 0.050)         &\
         ((BAND["BLUE"]-BAND["NIR"]) < -0.04) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SV"]
        
    # CLASS_ID["WAT"] DWAT
    
    MASK[(NDVI_M)  &\
         (WETNESS) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["WAT"]
        
    # CLASS_ID["SV"]
    
    MASK[(NDVI_M) &\
         (0.130         > BAND["BLUE"])  &\
         (BAND["BLUE"]  > BAND["GREEN"]) &\
         (BAND["GREEN"] > BAND["RED"])   &\
         (BAND["RED"]   < 0.050)         &\
         ((BAND["BLUE"]-BAND["NIR"]) < 0.04) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SV"]
        
    # CLASS_ID["SS"]
    
    MASK[(NDVI_M) &\
         ((np.abs(BAND["NIR"]-BAND["GREEN"]) < 0.010) | ((BAND["BLUE"]-BAND["NIR"]) < 0.010)) &\
         (BAND["BLUE"]  > BAND["GREEN"]) &\
         (BAND["GREEN"] > BAND["RED"])   &\
         (BAND["NIR"]   > 0.060) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SS"]
        
    # CLASS_ID["OLD"] OLD2
    
    MASK[(NDVI_M) &\
         (NDVI <= 0.09) &\
         (BAND["NIR"]   < 0.400) &\
         (BAND["GREEN"] <= BAND["RED"])   &\
         (BAND["RED"]   <= BAND["NIR"])   &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["OLD"]
        
    # CLASS_ID["OLD"] OLD1
    
    MASK[(NDVI_M) &\
         (NDVI <= 0.20) &\
         (BAND["NIR"]   > 0.300) &\
         (BAND["BLUE"]  <= BAND["GREEN"]) &\
         (BAND["GREEN"] <= BAND["RED"])   &\
         (BAND["RED"]   <= BAND["NIR"])   &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["OLD"]
        
    # CLASS_ID["SPV"]
    
    MASK[(NDVI_M) &\
         (NDVI >= 0.35) &\
         (BAND["BLUE"]  >= BAND["GREEN"]) &\
         (np.abs(BAND["RED"]-BAND["GREEN"]) < 0.040) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SPV"]
        
    # CLASS_ID["OLD"]
    
    MASK[(NDVI_M) &\
         (NDVI >= 0.20) &\
         (np.abs(BAND["RED"]-BAND["GREEN"]) < 0.050) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["OLD"]
        
    # CLASS_ID["OLL"]
    
    MASK[(NDVI_M) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["OLL"]
        
    
    #%% NDVI_H
    
    # CLASS_ID["SPV"]
    
    MASK[(NDVI_H) &\
         (NDVI        <  0.500) &\
         (BAND["NIR"] >= 0.150) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SPV"]
        
    # CLASS_ID["SV"]
    
    MASK[(NDVI_H) &\
         (NDVI        < 0.500) &\
         (BAND["NIR"] < 0.150) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SV"]
        
    # CLASS_ID["SV"]
    
    MASK[(NDVI_H) &\
         (NDVI         < 0.550) &\
         (BAND["BLUE"] <= BAND["NIR"]) &\
         (BAND["NIR"]  <= 0.150) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SV"]
        
    # CLASS_ID["GRS"]
    
    MASK[(NDVI_H) &\
         (NDVI         < 0.550) &\
         (BAND["BLUE"] <= BAND["NIR"]) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["GRS"]
        
    # CLASS_ID["SV"]
    
    MASK[(NDVI_H) &\
         (NDVI         < 0.550) &\
         (BAND["BLUE"] > BAND["NIR"]) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SV"]
        
    # CLASS_ID["TCL"]
    
    MASK[(NDVI_H) &\
         (NDVI        <  0.650) &\
         (BAND["NIR"] >= 0.220) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["TCL"]
        
    # CLASS_ID["TCD"] TCD2
    
    MASK[(NDVI_H) &\
         (NDVI        <  0.650) &\
         (BAND["NIR"] >= 0.165) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["TCD"]
        
    # CLASS_ID["TCD"] TCD1
    
    MASK[(NDVI_H) &\
         (NDVI        <  0.650) &\
         (BAND["NIR"] <  0.165) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["TCD"]
        
    # CLASS_ID["TCD"]
    
    MASK[(NDVI_H) &\
         (NDVI        <  0.780) &\
         (BAND["NIR"] <  0.300) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["TCD"]
        
    # CLASS_ID["SHR"]
    
    MASK[(NDVI_H) &\
         (NDVI        >=  0.780) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SHR"]
        
    # CLASS_ID["TCL"]
    
    MASK[(NDVI_H) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["TCL"]
        
    
    MASK[NO_DATA_MASK] = CLASS_ID["ND"]
    return MASK

def SDC_13_4(BAND):
    
    # BAND["BLUE"]
    # BAND["GREEN"]
    # BAND["RED"]
    # BAND["NIR"]
        
    print("SDC_13 ...")
    
    NO_DATA_MASK = ((BAND["BLUE"] == 0) | (BAND["GREEN"] == 0))
    
    CLASS_ID = SDC_CLASS_ID()
    
    err = 0.0000001
    
    #
    S_WATER = ((BAND["BLUE"]-BAND["GREEN"]) > -0.2)
    S_WATER = (S_WATER) & (BAND["GREEN"] >= BAND["RED"]) & (BAND["RED"] >= BAND["NIR"])
    
    S_WATER_OTHER = (BAND["BLUE"] >= BAND["GREEN"]) &\
                (BAND["GREEN"] >= BAND["RED"]) &\
                (BAND["RED"] <= BAND["NIR"]) &\
                (BAND["NIR"] < 1.3*BAND["RED"]) &\
                (1.3*BAND["RED"] < 0.12)
    
    S_WATER_OTHER = (S_WATER_OTHER) &\
                (0.039 < BAND["NIR"]) &\
                (BAND["NIR"] < BAND["GREEN"])
                
    S_GROWING_14 = (BAND["BLUE"] < BAND["GREEN"]) & (BAND["GREEN"] < BAND["RED"]) & (BAND["RED"] < BAND["NIR"])
    
    S_GROWING_15 = (S_GROWING_14)
              
    BRIGHTSOIL = (BAND["BLUE"] < 0.27) & (S_GROWING_15)
    BRIGHTSOIL = (BRIGHTSOIL) | ((BAND["BLUE"] < 0.27) & (S_GROWING_14) )
    
    MAX = np.max((BAND["GREEN"],BAND["RED"],BAND["NIR"]), axis=0)
    MIN = np.min((BAND["GREEN"],BAND["RED"],BAND["NIR"]), axis=0)
    
    SATURATION = (MAX-MIN)/(MAX+err)
                      
    
    MIN = np.min((BAND["BLUE"],BAND["GREEN"],BAND["RED"],BAND["NIR"]), axis=0)
    
    S_SNOW = (MIN>0.3)
    
    
    MIN = np.min((BAND["BLUE"],BAND["GREEN"],BAND["RED"]), axis=0)
    MAX = np.max((BAND["BLUE"],BAND["GREEN"],BAND["RED"],BAND["NIR"]), axis=0)
    
    S_CLOUD = (MIN > 0.17) &\
              (MAX > 0.30) &\
              (BAND["NIR"]/(BAND["RED"]+err)   >= 1.30) &\
              (BAND["NIR"]/(BAND["GREEN"]+err) >= 1.30)
              
              
    MAX = np.max((BAND["BLUE"],BAND["GREEN"],BAND["RED"],BAND["NIR"]), axis=0)
    MIN = np.min((BAND["BLUE"],BAND["GREEN"],BAND["RED"],BAND["NIR"]), axis=0)
    
    S_CLOUD_1 = (MAX > 0.47) & (MIN > 0.37)
    
    
    MIN = np.min((BAND["BLUE"],BAND["GREEN"],BAND["RED"]), axis=0)
    MAX = np.max((BAND["GREEN"],BAND["RED"],BAND["NIR"]), axis=0)
    
    S_CLOUD_2 = (MIN > 0.21) & (SATURATION >= 0.2) & (SATURATION <= 0.4) &\
                (MAX >= 0.35)
                
    #%%
    NDVI = (BAND["NIR"] - BAND["RED"])/(BAND["NIR"] + BAND["RED"] + err)
    
    NDVI_L = (NDVI <= 0.00)
    NDVI_H = (NDVI >= 0.45)
    NDVI_M = (NDVI >= 0.00) & (NDVI <= 0.45)
    
    #%%
    MASK = np.zeros(BAND["RED"].shape) + CLASS_ID["UNK"]
    
    #%% NDVI_L
    
    print("\tNDVI LOW ...")
    
    # CLASS_ID["SI"]
    
    MASK[(NDVI_L) &\
         (S_SNOW) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SI"]
    
    # CLASS_ID["WAT"] DWAT
    
    MASK[(NDVI_L)  &\
         (S_WATER) &\
         (BAND["BLUE"] >=0.078) &\
         (BAND["GREEN"]>=0.040) &\
         (BAND["GREEN"]<=0.120) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["WAT"]
        
    # CLASS_ID["WAT"] SWAT
    
    MASK[(NDVI_L)  &\
         (BAND["RED"]   >= BAND["NIR"])   &\
         (BAND["RED"]   >= 0.040) &\
         (BAND["RED"]   <= 0.190) &\
         (BAND["BLUE"]  >  0.078) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["WAT"]
    
    # CLASS_ID["CL"] 
    
    MASK[(NDVI_L)  &\
         (BAND["BLUE"]  > 0.94) &\
         (BAND["GREEN"] > 0.94) &\
         (BAND["RED"]   > 0.94) &\
         (BAND["NIR"]   > 0.94) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["CL"]
        
    # # CLASS_ID["WAT"] DWAT
    
    # MASK[(NDVI_L)  &\
    #      (WETNESS > 5.) &\
    #      (MASK == CLASS_ID["UNK"])] = CLASS_ID["WAT"]
        
    # CLASS_ID["SS"]
    
    MASK[(NDVI_L)  &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SS"]
        
        
    #%% NDVI_M
    print("\tNDVI MEDIUM ...")
    
    # CLASS_ID["SI"]
    
    MASK[(NDVI_M) &\
         (S_SNOW) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SI"]
        
    # CLASS_ID["CL"]
    
    MASK[(NDVI_M) &\
         (BAND["BLUE"]  > 0.94) &\
         (BAND["GREEN"] > 0.94) &\
         (BAND["RED"]   > 0.94) &\
         (BAND["NIR"]   > 0.94) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["CL"]
        
    # CLASS_ID["WAT"] SWAT
    
    MASK[(NDVI_M) &\
         (S_WATER_OTHER) &\
         (BAND["BLUE"] > 0.078) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["WAT"]
    
    # CLASS_ID["CL"]
    
    MASK[(NDVI_M) &\
         (S_CLOUD | S_CLOUD_1 | S_CLOUD_2) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["CL"]
        
    # CLASS_ID["CL"]
    
    MASK[(NDVI_M) &\
         (BAND["BLUE"]  > BAND["GREEN"]) &\
         (BAND["GREEN"] > BAND["RED"]) &\
         (BAND["NIR"]   > 0.254) &\
         (BAND["BLUE"]  > 0.165) &\
         (NDVI          < 0.400) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["CL"]
        
    # CLASS_ID["CL"]
    
    MASK[(NDVI_M) &\
         (BAND["BLUE"]  > BAND["GREEN"]) &\
         (BAND["BLUE"]  > 0.270) &\
         (BAND["GREEN"] > 0.210) &\
         (np.abs(BAND["RED"]-BAND["GREEN"]) <= 0.100) &\
         (BAND["NIR"]   > 0.350) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["CL"]
        
    # CLASS_ID["SV"]
    
    MASK[(NDVI_M) &\
         (0.130         > BAND["BLUE"])  &\
         (BAND["BLUE"]  > BAND["GREEN"]) &\
         (BAND["GREEN"] > BAND["RED"])   &\
         (BAND["RED"]   < 0.050)         &\
         ((BAND["BLUE"]-BAND["NIR"]) < -0.04) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SV"]
        
    # # CLASS_ID["WAT"] DWAT
    
    # MASK[(NDVI_M)  &\
    #      (WETNESS > 5.) &\
    #      (MASK == CLASS_ID["UNK"])] = CLASS_ID["WAT"]
        
    # CLASS_ID["SV"]
    
    MASK[(NDVI_M) &\
         (0.130         > BAND["BLUE"])  &\
         (BAND["BLUE"]  > BAND["GREEN"]) &\
         (BAND["GREEN"] > BAND["RED"])   &\
         (BAND["RED"]   < 0.050)         &\
         ((BAND["BLUE"]-BAND["NIR"]) < 0.04) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SV"]
        
    # CLASS_ID["SS"]
    
    MASK[(NDVI_M) &\
         ((np.abs(BAND["NIR"]-BAND["GREEN"]) < 0.010) | ((BAND["BLUE"]-BAND["NIR"]) < 0.010)) &\
         (BAND["BLUE"]  > BAND["GREEN"]) &\
         (BAND["GREEN"] > BAND["RED"])   &\
         (BAND["NIR"]   > 0.060) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SS"]
        
    # CLASS_ID["OLD"] OLD2
    
    MASK[(NDVI_M) &\
         (NDVI <= 0.09) &\
         (BAND["NIR"]   < 0.400) &\
         (BAND["GREEN"] <= BAND["RED"])   &\
         (BAND["RED"]   <= BAND["NIR"])   &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["OLD"]
        
    # CLASS_ID["OLD"] OLD1
    
    MASK[(NDVI_M) &\
         (NDVI <= 0.20) &\
         (BAND["NIR"]   > 0.300) &\
         (BAND["BLUE"]  <= BAND["GREEN"]) &\
         (BAND["GREEN"] <= BAND["RED"])   &\
         (BAND["RED"]   <= BAND["NIR"])   &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["OLD"]
        
    # CLASS_ID["SPV"]
    
    MASK[(NDVI_M) &\
         (NDVI >= 0.35) &\
         (BAND["BLUE"]  >= BAND["GREEN"]) &\
         (np.abs(BAND["RED"]-BAND["GREEN"]) < 0.040) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SPV"]
        
    # CLASS_ID["OLD"]
    
    MASK[(NDVI_M) &\
         (NDVI >= 0.20) &\
         (np.abs(BAND["RED"]-BAND["GREEN"]) < 0.050) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["OLD"]
        
    # CLASS_ID["OLL"]
    
    MASK[(NDVI_M) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["OLL"]
        
    
    #%% NDVI_H
    print("\tNDVI HIGH ...")
    
    # CLASS_ID["SPV"]
    
    MASK[(NDVI_H) &\
         (NDVI        <  0.500) &\
         (BAND["NIR"] >= 0.150) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SPV"]
        
    # CLASS_ID["SV"]
    
    MASK[(NDVI_H) &\
         (NDVI        < 0.500) &\
         (BAND["NIR"] < 0.150) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SV"]
        
    # CLASS_ID["SV"]
    
    MASK[(NDVI_H) &\
         (NDVI         < 0.550) &\
         (BAND["BLUE"] <= BAND["NIR"]) &\
         (BAND["NIR"]  <= 0.150) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SV"]
        
    # CLASS_ID["GRS"]
    
    MASK[(NDVI_H) &\
         (NDVI         < 0.550) &\
         (BAND["BLUE"] <= BAND["NIR"]) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["GRS"]
        
    # CLASS_ID["SV"]
    
    MASK[(NDVI_H) &\
         (NDVI         < 0.550) &\
         (BAND["BLUE"] > BAND["NIR"]) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SV"]
        
    # CLASS_ID["TCL"]
    
    MASK[(NDVI_H) &\
         (NDVI        <  0.650) &\
         (BAND["NIR"] >= 0.220) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["TCL"]
        
    # CLASS_ID["TCD"] TCD2
    
    MASK[(NDVI_H) &\
         (NDVI        <  0.650) &\
         (BAND["NIR"] >= 0.165) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["TCD"]
        
    # CLASS_ID["TCD"] TCD1
    
    MASK[(NDVI_H) &\
         (NDVI        <  0.650) &\
         (BAND["NIR"] <  0.165) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["TCD"]
        
    # CLASS_ID["TCD"]
    
    MASK[(NDVI_H) &\
         (NDVI        <  0.780) &\
         (BAND["NIR"] <  0.300) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["TCD"]
        
    # CLASS_ID["SHR"]
    
    MASK[(NDVI_H) &\
         (NDVI        >=  0.780) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["SHR"]
        
    # CLASS_ID["TCL"]
    
    MASK[(NDVI_H) &\
         (MASK == CLASS_ID["UNK"])] = CLASS_ID["TCL"]
        
    
    MASK[NO_DATA_MASK] = CLASS_ID["ND"]
    
    return MASK

#%%
def BITEMPORAL_SDC_13(img1,img2):
    
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
    
    CLASS_ID = SDC_CLASS_ID()
    
    DIFF = np.zeros(img1.shape)
    
    DIFF[ ( (img1==CLASS_ID["ND"])  |\
            (img2==CLASS_ID["ND"])  ) & (DIFF==0) ] = 0
    
        
    DIFF[ ( (img1==CLASS_ID["UNK"]) |\
            (img2==CLASS_ID["UNK"]) ) & (DIFF==0) ] = 11
    
        
    DIFF[ ( (img1==CLASS_ID["CL"]) | (img1==CLASS_ID["SI"]) |\
            (img2==CLASS_ID["CL"]) | (img2==CLASS_ID["SI"]) ) & (DIFF==0) ] = 10
    
    
    DIFF[ ( (img1!=CLASS_ID["WAT"]) &\
            (img2==CLASS_ID["WAT"]) ) & (DIFF==0) ] = 7
        
    DIFF[ ( (img1==CLASS_ID["WAT"]) &\
            (img2==CLASS_ID["WAT"]) ) & (DIFF==0) ] = 8
        
    DIFF[ ( (img1==CLASS_ID["WAT"]) &\
            (img2!=CLASS_ID["WAT"]) ) & (DIFF==0) ] = 9
        
    
        
        
    DIFF[ ( (img1==CLASS_ID["OLD"]) & (img2==CLASS_ID["OLL"]) ) & (DIFF==0) ] = 4
    DIFF[ ( (img1==CLASS_ID["SS"] ) & (img2==CLASS_ID["OLL"]) ) & (DIFF==0) ] = 4
    DIFF[ ( (img1==CLASS_ID["SS"] ) & (img2==CLASS_ID["OLD"]) ) & (DIFF==0) ] = 4
    
    DIFF[  (img1 == img2) &\
         ( (img1 == CLASS_ID["OLL"]) |\
           (img1 == CLASS_ID["OLD"]) |\
           (img1 == CLASS_ID["SS "]) ) & (DIFF==0) ] = 5
    
    DIFF[  (img1 != img2) &\
         ( (img1 == CLASS_ID["OLL"]) |\
           (img1 == CLASS_ID["OLD"]) |\
           (img1 == CLASS_ID["SS "]) ) & (DIFF==0) ] = 6
    
    
                 
        
    DIFF[ ( (img2 == CLASS_ID["TCD"]) ) &\
          ( (img1 == CLASS_ID["TCL"])
            (img1 == CLASS_ID["SHR"]) |\
            (img1 == CLASS_ID["GRS"]) |\
            (img1 == CLASS_ID["SPV"]) |\
            (img1 == CLASS_ID["SV "]) ) & (DIFF==0) ] = 1
        
    DIFF[ ( (img2 == CLASS_ID["TCL"]) ) &\
          ( (img1 == CLASS_ID["SHR"]) |\
            (img1 == CLASS_ID["GRS"]) |\
            (img1 == CLASS_ID["SPV"]) |\
            (img1 == CLASS_ID["SV "]) ) & (DIFF==0) ] = 1
        
    DIFF[ ( (img2 == CLASS_ID["SHR"]) ) &\
          ( (img1 == CLASS_ID["GRS"]) |\
            (img1 == CLASS_ID["SPV"]) |\
            (img1 == CLASS_ID["SV "]) ) & (DIFF==0) ] = 1
        
    DIFF[ ( (img2 == CLASS_ID["GRS"]) ) &\
          ( (img1 == CLASS_ID["SPV"]) |\
            (img1 == CLASS_ID["SV "]) ) & (DIFF==0) ] = 1
        
    DIFF[ ( (img2 == CLASS_ID["SPV"]) ) &\
          ( (img1 == CLASS_ID["SV "]) ) & (DIFF==0) ] = 1
        
    DIFF[  (img1 == img2) &\
         ( (img1 == CLASS_ID["TCD"]) |\
           (img1 == CLASS_ID["TCL"]) |\
           (img1 == CLASS_ID["SHR"]) |\
           (img1 == CLASS_ID["GRS"]) |\
           (img1 == CLASS_ID["SPV"]) |\
           (img1 == CLASS_ID["SV "]) ) & (DIFF==0) ] = 2        
    
    DIFF[  (img1 != img2) &\
         ( (img1 == CLASS_ID["TCD"]) |\
           (img1 == CLASS_ID["TCL"]) |\
           (img1 == CLASS_ID["SHR"]) |\
           (img1 == CLASS_ID["GRS"]) |\
           (img1 == CLASS_ID["SPV"]) |\
           (img1 == CLASS_ID["SV "]) ) & (DIFF==0) ] = 3
    


    #
    DIFF[  (DIFF == 11) &\
         ( (img2 == CLASS_ID["TCD"]) |\
           (img2 == CLASS_ID["TCL"]) |\
           (img2 == CLASS_ID["SHR"]) |\
           (img2 == CLASS_ID["GRS"]) |\
           (img2 == CLASS_ID["SPV"]) |\
           (img2 == CLASS_ID["SV "]) )] = 1
    
    DIFF[  (DIFF == 9) &\
         ( (img2 == CLASS_ID["TCD"]) |\
           (img2 == CLASS_ID["TCL"]) |\
           (img2 == CLASS_ID["SHR"]) |\
           (img2 == CLASS_ID["GRS"]) |\
           (img2 == CLASS_ID["SPV"]) |\
           (img2 == CLASS_ID["SV "]) )] = 1
        
    DIFF[  (DIFF == 6) &\
         ( (img2 == CLASS_ID["TCD"]) |\
           (img2 == CLASS_ID["TCL"]) |\
           (img2 == CLASS_ID["SHR"]) |\
           (img2 == CLASS_ID["GRS"]) |\
           (img2 == CLASS_ID["SPV"]) |\
           (img2 == CLASS_ID["SV "]) )] = 1
    
    
        
    DIFF[  (DIFF == 11) &\
         ( (img2 == CLASS_ID["OLL"]) |\
           (img2 == CLASS_ID["OLD"]) |\
           (img2 == CLASS_ID["SS "]) )] = 4
        
    DIFF[  (DIFF == 9) &\
         ( (img2 == CLASS_ID["OLL"]) |\
           (img2 == CLASS_ID["OLD"]) |\
           (img2 == CLASS_ID["SS "]) )] = 4
    
    DIFF[  (DIFF == 3) &\
         ( (img2 == CLASS_ID["OLL"]) |\
           (img2 == CLASS_ID["OLD"]) |\
           (img2 == CLASS_ID["SS "]) )] = 4
        
        
        
    DIFF[  (DIFF == 11) &\
         ( (img2 == CLASS_ID["WAT"]) )] = 7
        
    DIFF[  (DIFF == 6) &\
         ( (img2 == CLASS_ID["WAT"]) )] = 7
        
    DIFF[  (DIFF == 3) &\
         ( (img2 == CLASS_ID["WAT"]) )] = 7
    
    
    
    #  
    DIFF[  (DIFF == 0) &\
         ( (img1 == CLASS_ID["TCD"]) |\
           (img1 == CLASS_ID["TCL"]) |\
           (img1 == CLASS_ID["SHR"]) |\
           (img1 == CLASS_ID["GRS"]) |\
           (img1 == CLASS_ID["SPV"]) |\
           (img1 == CLASS_ID["SV "]) )] = 2
        
    DIFF[  (DIFF == 0) &\
         ( (img2 == CLASS_ID["TCD"]) |\
           (img2 == CLASS_ID["TCL"]) |\
           (img2 == CLASS_ID["SHR"]) |\
           (img2 == CLASS_ID["GRS"]) |\
           (img2 == CLASS_ID["SPV"]) |\
           (img2 == CLASS_ID["SV "]) )] = 2
        
    
    DIFF[  (DIFF == 0) &\
         ( (img1 == CLASS_ID["OLL"]) |\
           (img1 == CLASS_ID["OLD"]) |\
           (img1 == CLASS_ID["SS "]) )] = 5
        
    DIFF[  (DIFF == 0) &\
         ( (img2 == CLASS_ID["OLL"]) |\
           (img2 == CLASS_ID["OLD"]) |\
           (img2 == CLASS_ID["SS "]) )] = 5
        
        
    DIFF[  (DIFF == 0) &\
         ( (img1 == CLASS_ID["WAT"]) )] = 8
        
    DIFF[  (DIFF == 0) &\
         ( (img2 == CLASS_ID["WAT"]) )] = 8
        
    
    DIFF[  (DIFF == 0) &\
         ( (img2 == CLASS_ID["CL "]) |\
           (img2 == CLASS_ID["SI "]) )] = 10
        
    DIFF[  (DIFF == 0) &\
         ( (img1 == CLASS_ID["CL "]) |\
           (img1 == CLASS_ID["SI "]) )] = 10
    
    
    #          
    DIFF[  (DIFF == 10) &\
         ( (img2 == CLASS_ID["TCD"]) |\
           (img2 == CLASS_ID["TCL"]) |\
           (img2 == CLASS_ID["SHR"]) |\
           (img2 == CLASS_ID["GRS"]) |\
           (img2 == CLASS_ID["SPV"]) |\
           (img2 == CLASS_ID["SV "]) )] = 2
        
    DIFF[  (DIFF == 10) &\
         ( (img2 == CLASS_ID["OLL"]) |\
           (img2 == CLASS_ID["OLD"]) |\
           (img2 == CLASS_ID["SS "]) )] = 5
        
    DIFF[  (DIFF == 10) &\
         ( (img2 == CLASS_ID["WAT"]) )] = 8
        
    
    return DIFF

#%%
def get_13_colormap():
    
    cmap = {0:  (255,   0, 255),
            
            1:  ( 85, 141, 215),
            2:  (195, 195, 195),
            3:  (184, 221, 230),
            
            4:  ( 79,  99,  40),
            5:  (120, 145,  62),
            6:  (216, 228, 192),
            7:  (230, 234, 184),
            8:  (221, 219, 198),
            
            9:  (241, 219, 221),
            10: (229, 183, 183),
            11: (  4,  77,  21),
            12: (171,   4,  56),
            
            13: (255, 255, 255)}
    
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

#%%
def raster_save(mask, src, dst, opt):
    
    print("Saving ...")
    
    
    if os.path.isfile(dst):
        os.remove(dst)
        
    print(dst)
        
    # if os.path.isfile(dst.split(".")[0]+"xml"):
    #     os.remove(dst.split(".")[0]+"xml")
    
    tiff_obj  = rio.open(src)
    crs       = tiff_obj.crs
    transform = tiff_obj.transform
    tiff_obj.close()
    
    height = mask.shape[0]
    width  = mask.shape[1]
    
    if (len(mask.shape) == 2):
        count = 1
    else:
        count = mask.shape[2]    
    
    indic_obj = rio.open(dst, "w",\
                              
                         crs       = crs,\
                         width     = width,\
                         height    = height,\
                         transform = transform,\
                                
                         count     = count,\
                         dtype     = "uint8",\
                         driver    = "GTiff",\
                         compress  = None)
        
    
    if (opt==13):
        NULL = SDC_CLASS_ID()["ND"]
        indic_obj.write_colormap( 1, get_13_colormap())
        
    elif (opt==11):
        NULL = 0
        indic_obj.write_colormap( 1, get_11_colormap())
    
    elif (opt==8):
        NULL = 0
        indic_obj.write_colormap( 1, get_8_colormap())
        
    else:
        NULL = 0
    
    indic_obj.nodata = NULL
    if (count==1):
        indic_obj.write(np.ma.array(mask,mask=mask!=NULL).astype("uint8"),1)
    else:
        for i in range(count):
            indic_obj.write(np.ma.array(mask[:,:,i],mask=mask[:,:,i]!=NULL).astype("uint8"),i+1)
            
    indic_obj.close()

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
