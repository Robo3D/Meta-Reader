# coding=utf-8
from __future__ import absolute_import
import octoprint.plugin

from .File_Reader import File_Reader
from multiprocessing import Process
from threading import Timer
import traceback



class Meta_reader(octoprint.plugin.SettingsPlugin,
                        octoprint.plugin.AssetPlugin,
                        octoprint.plugin.TemplatePlugin,
                        octoprint.plugin.StartupPlugin,
                        octoprint.plugin.EventHandlerPlugin):

    def __init__(self, **kwargs):
        # super(Meta_Reader,self).__init__(**kwargs)
        self.printing = False
        self.spinning = False
        self.thread = Process(target = self.update, args=() )
        
    
    def on_after_startup(self):
        #self._logger.info("##################### Meta Reader started up")
        self.meta = File_Reader(self)
        pass

    def update(self):
        
        
        try:
            #initialize list
            self.meta.check_files()

            #analyze list
            while len(self.meta.needed_updates) > 0:
                #check if we need to update list
                self.meta.check_files()
                
                #analyze files
                if self.printing == False:
                    self.meta.analyze_files()
                else:
                    break
                    
            self._logger.info("No more files  or printer started printing. Stopped looping")
            self.spinning = False

        except Exception as e:
            self._logger.info("!!!!!!!!!!!!!!!!!!!Exception: " + str(e))
            traceback.print_exc()

    def analyze_files(self):
        self._logger.info("Spinning = " + str(self.thread.is_alive()))
        if self.thread.is_alive() == False:

            self.thread = Process(target = self.update, args=() )
            self.spinning = True
            self._logger.info("Started Analyzing files")
            self.thread.start()
        return
        
    def on_event(self,event, payload):

        if event == 'PrintStarted':
            self.printing = True
        elif event == 'PrintFailed':
            self.printing = False
            self.analyze_files()
        elif event == 'PrintDone':
            self.printing = False
            self.analyze_files()
        elif event == 'PrintCancelled':
            self.printing = False
            self.analyze_files()
        elif event == "FileDeselected":
            self.printing = False
            self.analyze_files()
    ##~~ SettingsPlugin mixin

    def get_settings_defaults(self):
        return dict(
            # put your plugin's default settings here
        )

    ##~~ AssetPlugin mixin

    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return dict(
            js=["js/Meta_Reader.js"],
            css=["css/Meta_Reader.css"],
            less=["less/Meta_Reader.less"]
        )

    ##~~ Softwareupdate hook

    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://github.com/foosel/OctoPrint/wiki/Plugin:-Software-Update
        # for details.
        return dict(
            Meta_Reader=dict(
                displayName="Meta_reader",
                displayVersion=self._plugin_version,

                # version check: github repository
                type="github_release",
                user="Robo3d",
                repo="Meta-Reader",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/Robo3D/Meta-Reader/archive/{target_version}.zip"
            )
        )


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Meta_reader"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Meta_reader()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

    global __plugin_helpers__
    __plugin_helpers__ = dict(start_analysis = __plugin_implementation__.analyze_files)
