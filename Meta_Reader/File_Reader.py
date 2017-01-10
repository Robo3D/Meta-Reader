import subprocess
import re
import os
import octoprint.filemanager
import os.path
import traceback


class File_Reader():
    def __init__(self, oprint):
        #self.filename = _filename
        # self.gcode_name = os.path.basename(_filename)
        #.get_metadata(octoprint.filemanager.FileDestinations.LOCAL, self.gcode_name)
        self.oprint = oprint
        self.logger = self.oprint._logger
        self.needed_updates = {}

    def check_saved_data(self, filename):
        saved_data = self.oprint._file_manager.get_metadata(octoprint.filemanager.FileDestinations.LOCAL, filename)
    
        if 'robo_data' in saved_data:
            return saved_data['robo_data']
        else:
            return False

    #This function will save meta data to the machine
    def save_data(self, data, filename):
        self.oprint._file_manager.set_additional_metadata(octoprint.filemanager.FileDestinations.LOCAL,
                                               filename,
                                               'robo_data',
                                               data)


    def check_files(self):
        #list all files
        files = self.oprint._file_manager.list_files(octoprint.filemanager.FileDestinations.LOCAL)
        
        if 'local' in files:
            for file in files['local']:
                if self.check_saved_data(file) != False:
                    #self.logger.info("Already has Meta Data")
                    pass
                elif file not in self.needed_updates:
                    path = self.oprint._file_manager.path_on_disk(octoprint.filemanager.FileDestinations.LOCAL, file)
                    self.logger.info("adding: " + path)
                    self.needed_updates[file] = path
        return

    def analyze_files(self):
        if len(self.needed_updates) > 0:
            key = self.needed_updates.iterkeys().next()
            path = self.needed_updates[key]
            del self.needed_updates[key]
            self.logger.info("Analyzing file: " + str(key))

            try:
                self.detirmine_slicer(path)
            except Exception as e:
                self.logger.info("!!!!!!!!!!!!!!!!!!!Exception: " + str(e))
                traceback.print_exc()
                #delete all pending files since they will be regenerated
                del self.needed_updates
                self.needed_updates = {}
                return


            
                            

    def detirmine_slicer(self,filename):
        cura = ";Generated with Cura_SteamEngine ([0-9.]+)"
        simplify3d = "Simplify3D"
        meta = None

        #read first 10 lines to detirmine slicer
        with open(filename, 'r') as file:
            for x in range(0,10):
                line  = file.readline()
            
                _cura = re.findall(cura, line)
                _simplify = re.findall(simplify3d, line)
            
                if _cura != []:
                    #self.logger.info("Sliced with Cura")
                    meta = self.cura_meta_reader(filename)
                    break
                elif _simplify != []:
                    #self.logger.info("Sliced with Simplify 3D")
                    meta = self.simplify_meta_reader(filename)
                    break
               
        if meta == None:
            meta = {
                'layer height' : "--",
                'layers' : "--",
                'infill' : "--",
                'time' : {'hours': '0', 
                          'minutes': '0',
                          'seconds': '0'
                          }
            }
        self.save_data(meta, filename)
        return meta
        

    #This method reads the file to get the unread meta data from it. if there is none then it returns nothing
    def cura_meta_reader(self, _filename):
        _layer_height = "--"
        _layers = "--"
        _infill = "--"
        _hours = "0"
        _minutes = "0"
        _time = 0
        _time_dict = {}

        meta = {}

        cura_lh = "layer_height = ([0-9.]+)"
        cura_ls = ";LAYER_COUNT:([0-9.]+)"
        cura_in = "sparse_density = ([0-9.]+)"
        cura_time = ";TIME:([0-9.]+)"

        #read first 200 lines for Layer height
        with open(_filename, 'r') as file:

            for line in file:
                if line[0] == ';':
                    _cura_ls = re.findall(cura_ls, line)
                    _cura_lh = re.findall(cura_lh, line)
                    _cura_in = re.findall(cura_in, line)
                    _cura_time = re.findall(cura_time, line)
    
                    if _cura_lh != []:
                        _layer_height = float(_cura_lh[0])                
    
                    if _cura_ls != []:
                        
                        _layers = int(_cura_ls[0])

                    if _cura_in != []:
                        
                        _infill = float(_cura_in[0])

                    if _cura_time != []:
                        _time = int(_cura_time[0])
                        _time_dict = self.parse_time(_time)
        
        meta = {
            'layer height' : _layer_height,
            'layers' : _layers,
            'infill' : _infill,
            'time' : {'hours': str(_time_dict['hours']), 
                          'minutes': str(_time_dict['minutes']),
                          'seconds': str(_time_dict['seconds'])
                          }
        }
        return meta

    # This takes a number in seconds and returns a dictionary of the hours/minutes/seconds
    def parse_time(self, time):
        m, s = divmod(time, 60)
        h, m = divmod(m, 60)

        time_dict = {'hours': str(h),
                     'minutes': str(m),
                     'seconds': str(s)
                     }

        return time_dict




    #This method reads the file to get the unread meta data from it. if there is none then it returns nothing
    def simplify_meta_reader(self, _filename):
        _layer_height = "--"
        _layers = "--"
        _infill = "--"
        _hours = "0"
        _minutes = "0"
        meta = {}

        s3d_lh = ";   layerHeight,([0-9.]+)"
        s3d_ls = "; layer ([0-9.]+)"
        s3d_in = ";   infillPercentage,([0-9.]+)"

        #looks like ;   Build time: 3 hours 5 minutes

        s3d_time = ";   Build time: ([0-9.]+) hours ([0-9.]+) minutes"

        #read first 200 lines for Layer height
        with open(_filename, 'r') as file:

            for line in file:
                if line[0] == ';':
                    
                    _s3d_lh = re.findall(s3d_lh, line)
                    _s3d_ls = re.findall(s3d_ls, line)
                    _s3d_in = re.findall(s3d_in, line)
                    _s3d_time = re.findall(s3d_time, line)
                   
    
                    if _s3d_lh != []:
                        _layer_height = float(_s3d_lh[0])
    
                    if _s3d_ls != []:
                        _layers = int(_s3d_ls[0])

                    if _s3d_in != []:
                        _infill = int(_s3d_in[0])

                    if _s3d_time != []:
                        _hours = _s3d_time[0][0]
                        _minutes = _s3d_time[0][1]

                    

        meta = {
            'layer height' : _layer_height,
            'layers' : _layers,
            'infill' : _infill,
            'time' : {'hours': str(_hours), 
                          'minutes': str(_minutes),
                          'seconds': '0'
                          }
        }
        return meta

