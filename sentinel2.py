import os
import rasterio
#import cv2
#import numpy as np
#from xml.dom import minidom

#%%
class MSI(object):
    def __init__(self):
        pass
            
    # *************************************************************************
    # PROPERTIES - GETTERS
    # *************************************************************************
    
    @property
    def band_key(self):
        band_key = dict()
        
        band_key["reflectance"]  = ['1', '2', '3', '4', '5', '6', '7', '8', '8A', '9', '10', '11', '12']        
        
        return band_key
    
    @property
    def band_nick_name(self):
        return {'1': 'AEROSOL',
                '2': 'BLUE',
                '3': 'GREEN',
                '4': 'RED',
                '5': 'RED_EDGE1',
                '6': 'RED_EDGE2',
                '7': 'RED_EDGE3',
                '8': 'NIR',
                '8A':'NARROW_NIR',
                '9': 'WATER_VAPOUR',
                '10': 'CIRRUS',
                '11': 'SWIR1',
                '12': 'SWIR2'}
        
    @property
    def wavelength(self):
        wavelength = dict()
        
        wavelength["1"]  = dict()
        wavelength["2"]  = dict()
        wavelength["3"]  = dict()
        wavelength["4"]  = dict()
        wavelength["5"]  = dict()
        wavelength["6"]  = dict()
        wavelength["7"]  = dict()
        wavelength["8"]  = dict()
        wavelength["8A"] = dict()
        wavelength["9"]  = dict()
        wavelength["10"] = dict()
        wavelength["11"] = dict()
        wavelength["12"] = dict()
        
        
        wavelength["1"]["min"]     = 0.4322
        wavelength["1"]["max"]     = 0.4532
        wavelength["1"]["center"]  = 0.4427
        
        wavelength["2"]["min"]     = 0.4594
        wavelength["2"]["max"]     = 0.5254
        wavelength["2"]["center"]  = 0.4924
        
        wavelength["3"]["min"]     = 0.5418
        wavelength["3"]["max"]     = 0.5778
        wavelength["3"]["center"]  = 0.5598
        
        wavelength["4"]["min"]     = 0.6491
        wavelength["4"]["max"]     = 0.6801
        wavelength["4"]["center"]  = 0.6646
        
        wavelength["5"]["min"]     = 0.6966
        wavelength["5"]["max"]     = 0.7116
        wavelength["5"]["center"]  = 0.7041
        
        wavelength["6"]["min"]     = 0.7330
        wavelength["6"]["max"]     = 0.7480
        wavelength["6"]["center"]  = 0.7405
        
        wavelength["7"]["min"]     = 0.7728
        wavelength["7"]["max"]     = 0.7928
        wavelength["7"]["center"]  = 0.7828
        
        wavelength["8"]["min"]     = 0.7798
        wavelength["8"]["max"]     = 0.8858
        wavelength["8"]["center"]  = 0.8328
        
        wavelength["8A"]["min"]    = 0.8542
        wavelength["8A"]["max"]    = 0.8752
        wavelength["8A"]["center"] = 0.8647
        
        wavelength["9"]["min"]     = 0.9351
        wavelength["9"]["max"]     = 0.9551
        wavelength["9"]["center"]  = 0.9451
        
        wavelength["10"]["min"]    = 1.3580
        wavelength["10"]["max"]    = 1.3890
        wavelength["10"]["center"] = 1.3735
        
        wavelength["11"]["min"]    = 1.5682
        wavelength["11"]["max"]    = 1.6592
        wavelength["11"]["center"] = 1.6137
        
        wavelength["12"]["min"]    = 2.1149
        wavelength["12"]["max"]    = 2.2899
        wavelength["12"]["center"] = 2.2024
        
        for key, nick in self.band_nick_name.items():
            wavelength[nick] = wavelength[key]
        
        return wavelength
        
    @property
    def pixel_size(self):
        
        pixel_size = dict()
            
        for key, px_sixe in zip(['1', '2', '3', '4', '5', '6', '7', '8', '8A', '9', '10', '11', '12'], [ 60,  10,  10,  10,  20,  20,  20,  10,  20 ,  60,  60 ,  20,   20 ]):
            pixel_size[key] = px_sixe
            
        for key, nick in self.band_nick_name.items():
            pixel_size[nick] = pixel_size[key]
            
        return pixel_size
            
#%%
class Sentinel2_L1(MSI):
    
    def __init__(self, filepath):
        
        super(Sentinel2_L1, self).__init__()
        
        self._filepath  = None
        self.filepath  = filepath
        
    # *************************************************************************
    # PROPERTIES - GETTERS
    # *************************************************************************
    
    @property
    def filepath(self):
        return self._filepath
    
    @property
    def band_name(self):
        # ---------------------------------------------------------------------
        # Exists a file path (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Sentinel-2 (Level-1) filepath")
        
        # ---------------------------------------------------------------------
        src = self.filepath["img_data"]
        
        # ---------------------------------------------------------------------
        files_name = [x for x in os.listdir(src) if x.endswith(".jp2")]
        
        # ---------------------------------------------------------------------
        # Exists any band at the path?
        if (len(files_name) <= 0):
            raise ValueError("ERROR: No Sentinel-2 (Level-1) bands available at: {}".format(src))
        
        # ---------------------------------------------------------------------
        band_name = dict()
        for file_name in files_name:
            
            key = file_name.split("_")[-1].split(".")[0]
            if key[0] == "B":
                key = key[1:]
            if key[0] == "0":
                key = key[1:]
            
            band_name[key] = os.path.join(src,file_name)
        
        # ---------------------------------------------------------------------
        # Nick Names
        for key, nick in self.band_nick_name.items():
            band_name[nick] = band_name[key]
        
        return band_name
    
    @property
    def clear_mask(self):
        # ---------------------------------------------------------------------
        # Exists a file path (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Sentinel-2 (Level-1) filepath")
        
        # ---------------------------------------------------------------------
        return (rasterio.open(self.band_name["8"]).read(1) != 0)
    
    @property
    def acquisition_date(self):
        # ---------------------------------------------------------------------
        # Exists a file path (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Sentinel-2 (Level-1) filepath")
        
        date = self.filepath["main"].split("/")[-1].split("_")[2].split("T")[0]
        return date[:4]+"-"+date[4:6]+"-"+date[6:]
    
    # *************************************************************************
    # PROPERTIES - SETTERS
    # *************************************************************************
    
    @filepath.setter
    def filepath(self, src):
       
        if not(os.path.isdir(src)):
            raise ValueError("ERROR: Path does not exist: {}".format(src))
        if not(src.endswith(".SAFE")):
            raise ValueError("ERROR: No '.SAFE' found: {}".format(src))
        if not("GRANULE" in os.listdir(src)):
            raise ValueError("ERROR: No GRANULE folder: {}".format(src))
        
        granule_src  = os.path.join(src, "GRANULE")
        img_data_src = os.path.join(granule_src, os.listdir(granule_src)[0],"IMG_DATA")
        
        if not(os.path.isdir(img_data_src)):
            raise ValueError("Invalid filepath: No IMG_DATA folder: {}".format(src))
            
        self._filepath             = dict()
        self._filepath["main"]     = src
        self._filepath["img_data"] = img_data_src        
        
    # *************************************************************************
    # METHODS
    # *************************************************************************
    
    def reflectance(self, key, resampled=False):
        # ---------------------------------------------------------------------
        # Exists a file path (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Sentinel-2 (Level-1) filepath")
        
        # ---------------------------------------------------------------------
        # key is a string?
        if not(isinstance(key,str)):
            raise ValueError("ERROR: 'key' must be a string")
            
        # ---------------------------------------------------------------------
        # resampled is a bool?
        if not(isinstance(resampled,bool)):
            raise ValueError("ERROR: 'resampled' must be a boolean")
            
        # ---------------------------------------------------------------------
        nick_name = self.band_nick_name
        band_name = self.band_name
        band_key  = self.band_key
        
        # ---------------------------------------------------------------------
        # key is it a reflectance or panchromatic key?
        valid_bands = [nick_name[x] for x in band_key["reflectance"]]
        
        if (key in valid_bands):
            key = [x for x  in nick_name.keys() if nick_name[x]==key][0]
        
        valid_bands = band_key["reflectance"]
        
        if not(key in valid_bands):
            raise ValueError("ERROR: Invalid Sentinel-2 (Level-1) key for reflectance data: {}".format(key))
        
        # ---------------------------------------------------------------------
        if (resampled == True):
            with rasterio.open(band_name["NIR"]) as dst:
                meta = dst.meta
                
            with rasterio.open(band_name[key]) as dst:
                ref = dst.read(1, out_shape=(meta["height"], meta["width"])).astype("float")/10000.
            
        else:
            with rasterio.open(band_name[key]) as dst:
                ref = dst.read(1).astype("float")/10000.
            
        # ref = rasterio.open(band_name[key]).read(1).astype("float")/10000
        
        ref[ref>1.] = 1.
        ref[ref<0.] = 0.
        
        return ref
    
#%%
class Sentinel2_L2():
    
    
    def __init__(self, filepath):
        
        self._filepath  = None
        self._band_name = None
        
        self._pixel_size = [10, 20, 60]
        self._band_key_reflectance  = ['1', '2', '3', '4', '5', '6', '7', '8', '8A', '9', '10', '11', '12']
        
        self._band_key_cloud = ["CLDPRB_20m","CLDPRB_60m"]
        self._band_key_snow  = ["SNWPRB_20m","SNWPRB_60m"]
        
        self._set_filepath(filepath)
    
    # *************************************************************************
    # PROPERTIES
    # *************************************************************************
    
    
    @property
    def filepath(self):
        return self._filepath
    
    
    @property
    def band_name(self):
        return self._band_name
    
    # *************************************************************************
    # SETTERS
    # *************************************************************************
    
    
    def _set_filepath(self, src):
        if not(os.path.isdir(src)):
            raise ValueError("ERROR: Path does not exist: {}".format(src))
        if not(src.endswith(".SAFE")):
            raise ValueError("ERROR: No '.SAFE' found: {}".format(src))
        if not("GRANULE" in os.listdir(src)):
            raise ValueError("ERROR: No GRANULE folder: {}".format(src))
        
        granule_src  = os.path.join(src, "GRANULE")
        img_data_src = os.path.join(granule_src, os.listdir(granule_src)[0],"IMG_DATA")
        qi_data_src  = os.path.join(granule_src, os.listdir(granule_src)[0],"QI_DATA")
        R10m_src     = os.path.join(img_data_src, "R10m")
        R20m_src     = os.path.join(img_data_src, "R20m")
        R60m_src     = os.path.join(img_data_src, "R60m")
        
        if not(os.path.isdir(img_data_src)):
            raise ValueError("ERROR: No 'IMG_DATA' folder: {}".format(src))
        
        if not(os.path.isdir(qi_data_src)):
            raise ValueError("ERROR: No 'QI_DATA' folder: {}".format(src))
        
        if not(os.path.isdir(R10m_src)):
            raise ValueError("ERROR: No 'R10m' folder: {}".format(src))
        
        if not(os.path.isdir(R20m_src)):
            raise ValueError("ERROR: No 'R20m' folder: {}".format(src))
        
        if not(os.path.isdir(R60m_src)):
            raise ValueError("ERROR: No 'R60m' folder: {}".format(src))
            
        self._filepath            = dict()
        self._filepath["main"]    = src
        self._filepath["R10m"]    = R10m_src
        self._filepath["R20m"]    = R20m_src
        self._filepath["R60m"]    = R60m_src
        self._filepath["qi_data"] = qi_data_src
        
        self._set_band_name()
        
    
    def _set_band_name(self):
        # ---------------------------------------------------------------------
        # Exists a file path (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Sentinel-2 (Level-2) filepath")
        
        # ---------------------------------------------------------------------
        bands_name = []
        file_ext   = ".jp2"
        
        for folder in ["R10m","R20m","R60m","qi_data"]:
            for x in os.listdir(self.filepath[folder]):
                if x.endswith(file_ext):
                    bands_name.append(os.path.join(self.filepath[folder],x))
                
        # ---------------------------------------------------------------------
        # Exists any band at the path?
        # No
        if (len(bands_name) <= 0):
            raise ValueError("ERROR: No Sentinel-2 (Level-2) bands available at: {}".format(self.filepath["main"]))
        # Yes
        else:
            self._band_name = dict()
            for band_name in bands_name:
                idx1 = self._find_all_occurrences(band_name,"_")
                idx2 = self._find_all_occurrences(band_name,file_ext)
                
                idx1 = idx1[-2]+1
                idx2 = idx2[-1]
                
                # -------------------------------------------------------------
                idx_i = idx1
                idx_f = idx2

                # -------------------------------------------------------------                
                if band_name[idx_i] == "B":
                    idx_i += 1
                if band_name[idx_i] == "0":
                    idx_i += 1
                
                # -------------------------------------------------------------
                key = band_name[idx_i:idx_f]
                self._band_name[key] = band_name

    # *************************************************************************
    # GETTERS
    # *************************************************************************
    
    
    def get_reflectance(self, key):
        # ---------------------------------------------------------------------
        # Check Attributes
        self._check_attribute()
        
        # ---------------------------------------------------------------------
        # key is a string?
        if not(isinstance(key,str)):
            raise ValueError("ERROR: 'key' must be a string")
        
        # ---------------------------------------------------------------------
        # key exists?
        if not(key in self.band_name.keys()):
            raise ValueError("ERROR: Invalid key: {}".format(key))
            
        # ---------------------------------------------------------------------
        # is it a reflectance key?
        ref_key = None
        valid_bands = self._band_key_reflectance
        
        for valid_band in valid_bands:
            if key[:len(valid_band)] in valid_band:
                ref_key = key
                break
            
        if (ref_key is None):
            raise ValueError("ERROR: Invalid Sentinel-2 (Level-2) key for reflectance data: {}".format(key))
            
        # ---------------------------------------------------------------------
        ref = rasterio.open(self.band_name[ref_key]).read(1).astype("float")/10000.
        
        ref[ref>1.] = 1.
        ref[ref<0.] = 0.
        
        return ref

        
    def get_pixel_size(self , key):        
        # ---------------------------------------------------------------------
        # Check Attributes
        self._check_attribute()
        
        # ---------------------------------------------------------------------
        # key is a string?
        if not(isinstance(key,str)):
            raise ValueError("ERROR: 'key' must be a string")
        
        # ---------------------------------------------------------------------
        # key exists?
        if not(key in self.band_name.keys()):
            raise ValueError("ERROR: Invalid key: {}".format(key))
        
        # ---------------------------------------------------------------------
        # Valid pixel size? [10, 20, 60]
        
        pixel_size = key[-3:-1]
        valid_pixel_sizes = [str(x) for x in self._pixel_size]
        
        if not(pixel_size in valid_pixel_sizes):
            raise ValueError("Warning: Key with invalid pixel size: {}".format(key))
        
        return pixel_size

#    
#    def get_clear_mask(self, resolution=20):
#        # ---------------------------------------------------------------------
#        # Check Attributes
#        self._check_attribute()
#        
#        # ---------------------------------------------------------------------
#        # Exists Resolution?
#        valid_resolution = [int(key_cloud[-3:-1]) for key_cloud in self._band_key_cloud]
#        
#        if not(resolution in valid_resolution):
#            raise ValueError("ERROR: Invalid clear mask resolutin: {}".format(resolution))
#        
#        # ---------------------------------------------------------------------
#        key = None
#        for key_cloud in self._band_key_cloud:
#            if (int(key_cloud[-3:-1]) == resolution):
#                key = key_cloud
#                break
#        
#        # ---------------------------------------------------------------------
#        # key exists?
#        if (key is None):
#            raise ValueError("ERROR: Invalid key: {}".format(key))
#        
#        # ---------------------------------------------------------------------
#        # key exists?
#        if not(key in self.band_name.keys()):
#            raise ValueError("ERROR: Invalid key: {}".format(key))
#            
#        mask = rasterio.open(self.band_name[key]).read(1)
#        
#        return mask<25.
    
    
    
    def get_clear_mask(self):
        # ---------------------------------------------------------------------
        # Check Attributes
        self._check_attribute()
        
        # ---------------------------------------------------------------------
        return (self.get_reflectance("8_10m") > 0)
            
        
    
    def _check_attribute(self):
        if (self.filepath == None):
            raise ValueError("ERROR: Empty attribute = 'filepath' ")
            
        if (self.band_name == None):
            raise ValueError("ERROR: Empty attribute = 'band_name' ")
    
    
    def _find_all_occurrences(self, main_str, sub_str):
        return [i for i in range(len(main_str)) if main_str.startswith(sub_str, i)]    
    