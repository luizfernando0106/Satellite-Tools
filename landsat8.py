import os
import rasterio
import numpy as np
from xml.dom import minidom

#%%
class OLI(object):
    
    def __init__(self):
        pass
            
    # *************************************************************************
    # PROPERTIES - GETTERS
    # *************************************************************************
    
    @property
    def band_key(self):
        band_key = dict()
        
        band_key["reflectance"]  = ['1', '2', '3', '4', '5', '6', '7', '9']
        band_key["temperature"]  = ['10', '11']
        band_key["panchromatic"] = ['8']
        band_key["quality"]      = ['QA']
        
        return band_key
    
    @property
    def band_nick_name(self):
        return {'1': 'AEROSOL',
                '2': 'BLUE',
                '3': 'GREEN',
                '4': 'RED',
                '5': 'NIR',
                '6': 'SWIR1',
                '7': 'SWIR2',
                '8': 'PAN',
                '9': 'CIRRUS',
                '10':'TIR1',
                '11':'TIR2'}
        
    @property
    def wavelength(self):
        wavelength = dict()
        
        wavelength["1"] = dict()
        wavelength["2"] = dict()
        wavelength["3"] = dict()
        wavelength["4"] = dict()
        wavelength["5"] = dict()
        wavelength["6"] = dict()
        wavelength["7"] = dict()
        wavelength["8"] = dict()
        wavelength["9"] = dict()
        
        wavelength["1"]["min"]    = 0.433
        wavelength["1"]["max"]    = 0.453
        wavelength["1"]["center"] = 0.443
        
        wavelength["2"]["min"]    = 0.450
        wavelength["2"]["max"]    = 0.515
        wavelength["2"]["center"] = 0.482
        
        wavelength["3"]["min"]    = 0.525
        wavelength["3"]["max"]    = 0.600
        wavelength["3"]["center"] = 0.562
        
        wavelength["4"]["min"]    = 0.630
        wavelength["4"]["max"]    = 0.680
        wavelength["4"]["center"] = 0.655
        
        wavelength["5"]["min"]    = 0.845
        wavelength["5"]["max"]    = 0.885
        wavelength["5"]["center"] = 0.865
        
        wavelength["6"]["min"]    = 1.560
        wavelength["6"]["max"]    = 1.660
        wavelength["6"]["center"] = 1.610
        
        wavelength["7"]["min"]    = 2.100
        wavelength["7"]["max"]    = 2.300
        wavelength["7"]["center"] = 2.200
        
        wavelength["8"]["min"]    = 0.500
        wavelength["8"]["max"]    = 0.680
        wavelength["8"]["center"] = 0.590
        
        wavelength["9"]["min"]    = 1.360
        wavelength["9"]["max"]    = 1.390
        wavelength["9"]["center"] = 1.3372
        
        for key, nick in self.band_nick_name.items():
            wavelength[nick] = wavelength[key]
        
        return wavelength
    
    @property
    def pixel_size(self):
        pixel_size = dict()
            
        for key in self.band_key["quality"]:
            pixel_size[key] = 30
            
        for key in self.band_key["reflectance"]:
            pixel_size[key] = 30
        
        for key in self.band_key["temperature"]:
            pixel_size[key] = 30
            
        for key in self.band_key["panchromatic"]:
            pixel_size[key] = 15
            
        for key, nick in self.band_nick_name.items():
            pixel_size[nick] = pixel_size[key]
            
        return pixel_size
              
#%%
class Landsat8_L1(OLI):
    
    def __init__(self, filepath):
        
        super(Landsat8_L1, self).__init__()
        
        self._filepath = None
        self.filepath  = filepath
        
    # *************************************************************************
    # PROPERTIES - GETTERS
    # *************************************************************************
    
    @property
    def filepath(self):
        return self._filepath
    
    @property
    def metadata(self):
        # ---------------------------------------------------------------------
        # File path exists (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Landsat-8 (Level-1) filepath")
        
        # ---------------------------------------------------------------------
        # Exists a *_MTL.txt file at the path? (txt_file == [] ?)
        txt_file = [x for x in os.listdir(self.filepath) if x.endswith("_MTL.txt")]
        
        # None *_MTL.txt?
        if (len(txt_file) <= 0):
            raise ValueError("ERROR: No Landsat-8 (Level-1) metadata (*_MTL.txt) at: {}".format(self.filepath))
        # More than one *_MTL.txt?
        elif (len(txt_file) > 1):
            raise ValueError("ERROR: More than one Landsat-8 (Level-1) metadata (*_MTL.txt) at: {}".format(self.filepath))
        # Only one *_MTL.txt?
        else:            
            txt_file = txt_file[0]
            
        return os.path.join(self.filepath, txt_file)
    
    @property
    def band_name(self):
        # ---------------------------------------------------------------------
        # File path exists (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Landsat-8 (Level-1) filepath")
        
        # ---------------------------------------------------------------------
        LC8_file_extension   = ".TIF"
        LC8_file_starts_with = "LC08"
        bands_name = [x for x in os.listdir(self.filepath) if ( x.startswith(LC8_file_starts_with) & x.endswith(LC8_file_extension) )]
        
        # ---------------------------------------------------------------------
        # Exists any band at the path?
        # No
        if (len(bands_name) <= 0):
            raise ValueError("ERROR: No Landsat-8 (Level-1) bands at: {}".format(self.filepath))
        # Yes
        else:
            band_name_dict = dict()
            for band_name in bands_name:
                idx1 = self._find_all_occurrences(band_name,"_B")
                idx2 = self._find_all_occurrences(band_name,LC8_file_extension)
                
                idx1 = idx1[-1]
                idx2 = idx2[-1]
                key  = band_name[idx1+2:idx2]
                
                band_name_dict[key] = os.path.join(self.filepath,band_name)
                
        # ---------------------------------------------------------------------
        # Nick Names
        for key, nick in self.band_nick_name.items():
            band_name_dict[nick] = band_name_dict[key]
        
        return band_name_dict
    
    @property
    def quality_band(self):
        # ---------------------------------------------------------------------
        # File path exists (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Landsat-8 (Level-1) filepath")
            
        # ---------------------------------------------------------------------
        band_name = self.band_name
        band_key  = self.band_key
        filepath  = self.filepath
        
        # ---------------------------------------------------------------------
        key = band_key["quality"][0]
        
        if not(key in band_name.keys()):
            raise ValueError("ERROR: No Landsat-8 (Level-1) quality band ('BQA') available at: {}".format(filepath))
        else:
            with rasterio.open(band_name[key]) as dataset:
                bqa = dataset.read(1)
                
        return bqa
    
    @property
    def clear_mask(self):
        # ---------------------------------------------------------------------
        # File path exists (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Landsat-8 (Level-1) filepath")
        
        # ---------------------------------------------------------------------
        bqa = self.quality_band
        
        # ---------------------------------------------------------------------
        mask = np.zeros(bqa.shape, dtype=bool)
        valid_pixels = [2720,2724,2728,2732]
        
        for valid_pixel in valid_pixels:
            mask |= (bqa==valid_pixel)
            
        return mask
    
    # *************************************************************************
    # PROPERTIES - SETTERS
    # *************************************************************************
    
    @filepath.setter
    def filepath(self, src):
        if (isinstance(src, str) & os.path.isdir(src)):
            self._filepath = src
        else:
            raise ValueError("ERROR: Invalid Landsat-8 (Level-1) path: {}".format(src))
            
    # *************************************************************************
    # METHODS
    # *************************************************************************
    
    def reflectance(self, key, DOS=False):
        
        # ---------------------------------------------------------------------
        # File path exists (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Landsat-8 (Level-1) filepath")
                
        # ---------------------------------------------------------------------
        # key´is a string?
        if not(isinstance(key,str)):
            raise ValueError("ERROR: 'key' must be a string")
            
        # ---------------------------------------------------------------------
        nick_name = self.band_nick_name
        band_name = self.band_name
        band_key  = self.band_key
        BQA       = self.quality_band
        
        # ---------------------------------------------------------------------
        # key is it a reflectance or panchromatic key?
        
        
        valid_bands = [nick_name[x] for x in band_key["reflectance"]] + [nick_name[x] for x in band_key["panchromatic"]]
        
        if (key in valid_bands):
            key = [x for x  in nick_name.keys() if nick_name[x]==key][0]
        
        
        valid_bands = band_key["reflectance"]  + band_key["panchromatic"]
        
        if not(key in valid_bands):
            raise ValueError("ERROR: Invalid Landsat-8 (Level-1) key for reflectance data: {}".format(key))
        
        # ---------------------------------------------------------------------
        # MAIN
        add_factor = self._get_matadata_var("REFLECTANCE_ADD_BAND_"  + key)
        mlt_factor = self._get_matadata_var("REFLECTANCE_MULT_BAND_" + key)
        sun_elevt  = self._get_matadata_var("SUN_ELEVATION")
        
        with rasterio.open(band_name[key]) as dataset:
            DN  = dataset.read(1)
            ref = (mlt_factor * DN + add_factor)/np.sin(np.deg2rad(sun_elevt))
        
        ref[ref > 1.] = 1.
        ref[ref < 0.] = 0.
        ref[DN == 0 ] = 0.
        
        # Masking nodata (quality band == 1), Band 8 = Pancromatic (15m =! 30m)
        if (key in band_key["reflectance"]):
            ref[BQA == 1] = 0.
            
        # Dark Object Subtraction
        if(DOS==True):
            ref_min, _ = streaching(ref, BQA!=1, p=0.01)
            # ref_min = ref[ref>0.].min()            
            
            ref = ref - (ref_min-0.01)
            
            ref[ref > 1.] = 1.
            ref[ref < 0.] = 0.
            ref[DN == 0]  = 0.
            
            if (key in band_key["reflectance"]):
                ref[BQA == 1] = 0.
        
        return ref
    
    def temperature(self, key):
        # ---------------------------------------------------------------------
        # File path exists (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Landsat-8 (Level-1) filepath")
        
        # ---------------------------------------------------------------------
        # key is a string?
        if not(isinstance(key,str)):
            raise ValueError("ERROR: 'key' must be a string")
        
        # ---------------------------------------------------------------------
        nick_name = self.band_nick_name
        band_name = self.band_name
        band_key  = self.band_key
        BQA       = self.quality_band
        
        # ---------------------------------------------------------------------
        # is it a temperature key?
        valid_bands = [nick_name[x] for x in band_key["temperature"]]
        
        if (key in valid_bands):
            key = [x for x  in nick_name.keys() if nick_name[x]==key][0]
        
        valid_bands = band_key["temperature"]
        
        if not(key in valid_bands):
            raise ValueError("ERROR: Invalid Landsat-8 (Level-1) key for temperature data: {}".format(key))
        
        # ---------------------------------------------------------------------
        # radiance
        add_factor = self._get_matadata_var("RADIANCE_ADD_BAND_"  + key)
        mlt_factor = self._get_matadata_var("RADIANCE_MULT_BAND_" + key)
        
        with rasterio.open(band_name[key]) as dataset:
            DN  = dataset.read(1)
            rad = (mlt_factor * DN + add_factor)
        
        # temperature -> planck's equation
        k1 = self._get_matadata_var("K1_CONSTANT_BAND_" +key)
        k2 = self._get_matadata_var("K2_CONSTANT_BAND_" +key)
        
        err = 0.00001
        tmp = k2/np.log(k1/(rad + err) + 1.)
        
        # Masking nodata (quality band == 1)
        tmp[DN  == 0] = 0.
        tmp[BQA == 1] = 0.
        
        return tmp
    
    # *************************************************************************
    # HIDDEN METHODS
    # *************************************************************************
    
    def _find_all_occurrences(self, main_str, sub_str):
        return [i for i in range(len(main_str)) if main_str.startswith(sub_str, i)]
    
    def _get_matadata_var(self, var):
        with open(self.metadata) as MTL:
            for line in MTL:
                try:
                    key, val = line.split(" = ", 2)
                    key = key.split()[0]
                    if (key.count(var) > 0):
                        if val.endswith("\n"):
                            val = val[:-1]
                        return float(val)
                except:
                    pass
            return None
        
#%%
class Landsat8_L2():
    
    def __init__(self, filepath):
        
        self._filepath  = None
        self._metadata  = None
        self._band_name = None
        
        self._band_key_reflectance = ['1', '2', '3', '4', '5', '6', '7']
        self._band_key_quality     = ['pixel_qa','radsat_qa']
        self._band_key_aerosol     = ['aerosol']
        
        self._pixel_size = dict()
        for key in self._band_key_quality:
            self._pixel_size[key] = 30
            
        for key in self._band_key_reflectance:
            self._pixel_size[key] = 30
        
        for key in self._band_key_aerosol:
            self._pixel_size[key] = 30
            
        
        self._set_filepath(filepath)
    
    # *************************************************************************
    # PROPERTIES
    # *************************************************************************
    
    # =========================================================================
    @property
    def filepath(self):
        return self._filepath
    
    # =========================================================================
    @property
    def metadata(self):
        return self._metadata
    
    # =========================================================================
    @property
    def band_name(self):
        return self._band_name
    
    # *************************************************************************
    # SETTERS
    # *************************************************************************
    
    # =========================================================================
    def _set_filepath(self, src):
        if os.path.isdir(src):
            self._filepath = src
            self._set_metadata()
            self._set_band_name()
        else:
            raise ValueError("ERROR: Not Landsat-8 (Level-2) valid path: {}".format(src))
    
    # =========================================================================
    def _set_metadata(self):
        # ---------------------------------------------------------------------
        # File path exists (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Landsat-8 (Level-2) filepath")
        # ---------------------------------------------------------------------
        
        # ---------------------------------------------------------------------
        xml_file = [x for x in os.listdir(self.filepath) if ( (x.count(".")==1) and (x.endswith(".xml")) )]
        
        # ---------------------------------------------------------------------
        # Exists a *.xml file at the path? (xml_file == [] ?)
        if (len(xml_file) <= 0):
            raise ValueError("ERROR: No Landsat-8 (Level-2) metadata (*.xml) at: {}".format(self.filepath))
        # Exists more than one *.xml file at the path?
        elif (len(xml_file) > 1):
            raise ValueError("ERROR: More than one Landsat-8 (Level-2) metadata (.xml) at: {}".format(self.filepath))
        # Exists only one *.xml file at the path? OK
        else:            
            xml_file = xml_file[0]
            self._metadata = os.path.join(self.filepath,xml_file)
    
    # =========================================================================
    def _set_band_name(self):
        # ---------------------------------------------------------------------
        # File path exists (self.filepath)?
        if (self.filepath == None):
            raise ValueError("ERROR: No Landsat-8 (Level-2) filepath")
        # ---------------------------------------------------------------------
        
        # ---------------------------------------------------------------------
        band_name = dict()
        mydoc     = minidom.parse(self._metadata)
        items     = mydoc.getElementsByTagName('band')
        
        for item in items:
            key = item.attributes["name"].value
            
            if (key[:3] == "sr_"):  key = key[3:]
            if (key[:4] == "band"): key = key[4:]
            
            for node in item.childNodes:
                if node.nodeName == "file_name":
                    band_full_path = os.path.join(self.filepath,node.childNodes[0].data)
                    if os.path.isfile(band_full_path):
                        band_name[key] = band_full_path
                        break
        
        # ---------------------------------------------------------------------
        if (len(band_name) <= 0):
            raise ValueError("ERROR: No Landsat-8 (Level-2) bands at: {}".format(self.filepath))
        # Yes
        else:
            self._band_name = band_name
        
    # *************************************************************************
    # GETTERS
    # *************************************************************************
    
    # =========================================================================
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
        valid_bands = self._band_key_reflectance
        
        if not(key in valid_bands):
            raise ValueError("ERROR: Invalid Landsat-8 (Level-2) key for reflectance data: {}".format(key))
        
        # ---------------------------------------------------------------------
        # Reflectance
        ref = rasterio.open(self.band_name[key]).read(1)
        ref = ref*0.000100
        
        ref[ref>1.] = 1.
        ref[ref<0.] = 0.
        
        # ---------------------------------------------------------------------
        # Masking non-data (quality band == 1)
        bqa = self.get_quality_band()
        ref[bqa==1] = 0.
        
        return ref
    
    # =========================================================================
    def get_quality_band(self, opt='pixel'):
        # ---------------------------------------------------------------------
        # Check Attributes
        self._check_attribute()
        
        # ---------------------------------------------------------------------
        key = None
        for key_qa in self._band_key_quality:
            if opt in key_qa:
                key = key_qa
                break
        # ---------------------------------------------------------------------
        if (key is None):
            raise ValueError("ERROR: No Landsat-8 (Level-2) quality band ('pixel_qa' or 'radsat_qa') available at: {}".format(self.filepath))
        else:
            return rasterio.open(self.band_name[key]).read(1)
    
    # =========================================================================
    def get_clear_mask(self):
        # ---------------------------------------------------------------------
        # Check Attributes
        self._check_attribute()
        
        # ---------------------------------------------------------------------
        bqa  = self.get_quality_band()

        valid_pixels = [322,324]        
        mask = np.zeros(bqa.shape, dtype=bool)
        
        for valid_pixel in  valid_pixels:
            mask |= (bqa==valid_pixel)
            
        return mask
    
    # =========================================================================
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
        
        return self._pixel_size[key]

    # *************************************************************************
    # CHECKS
    # *************************************************************************
    
    # =========================================================================
    def _check_attribute(self):
        if (self.filepath == None):
            raise ValueError("ERROR: Empty attribute = 'filepath' ")
            
        if (self.metadata == None):
            raise ValueError("ERROR: Empty attribute = 'metadata' ")
            
        if (self.band_name == None):
            raise ValueError("ERROR: Empty attribute = 'band_name' ")
            

def streaching(img, mask=None, p=1.):
        
    if (mask is None):
        mask = np.ones(img.shape,dtype=bool)
    
    
    IMG = img[mask].copy()
    X   = sorted(np.unique(IMG))
    N   = len(IMG)
    L   = 200
    
    # -------------------------------------------------------------------------
    x_min = None
    for x in X[::L]:
        if ((IMG<=x).sum()/N*100) >= p:
            x_min = x
            break
        
    idx   = np.argwhere(X==x_min)[0][0]
    idx_i = int(idx - (3/2*L))
    idx_f = int(idx + (3/2*L))
    
    if (idx_i<0): idx_i = 0
    
    x_min = None
    for x in X[idx_i:idx_f:int(L/4)]:
        if ((IMG<=x).sum()/N*100) >= p:
            x_min = x
            break
        
    idx   = np.argwhere(X==x_min)[0][0]
    idx_i = int(idx - (3/2*L/4))
    idx_f = int(idx + (3/2*L/4))
    
    if (idx_i<0): idx_i = 0
    
    x_min = None
    for x in X[idx_i:idx_f]:
        if ((IMG<=x).sum()/N*100) >= p:
            x_min = x
            break
        
    # -------------------------------------------------------------------------
    X = np.flip(X)
    
    x_max = None
    for x in X[::L]:
        if ((IMG>=x).sum()/N*100) >= p:
            x_max = x
            break
        
    idx   = np.argwhere(X==x_max)[0][0]
    idx_i = int(idx - (3/2*L))
    idx_f = int(idx + (3/2*L))
    
    if (idx_i<0): idx_i = 0
    
    x_max = None
    for x in X[idx_i:idx_f:int(L/4)]:
        if ((IMG>=x).sum()/N*100) >= p:
            x_max = x
            break
        
    idx   = np.argwhere(X==x_max)[0][0]
    idx_i = int(idx - (3/2*L/4))
    idx_f = int(idx + (3/2*L/4))
    
    if (idx_i<0): idx_i = 0
    
    x_max = None
    for x in X[idx_i:idx_f]:
        if ((IMG>=x).sum()/N*100) >= p:
            x_max = x
            break
    
    return x_min,x_max