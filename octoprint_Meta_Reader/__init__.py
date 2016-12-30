# coding=utf-8
# Author: Matt Pedler
# 
from __future__ import absolute_import
from Meta_Reader import Meta_Reader


import octoprint.plugin

class Meta_Reader(octoprint.plugin.SettingsPlugin,
                        octoprint.plugin.AssetPlugin,
                        octoprint.plugin.TemplatePlugin,
                        octoprint.plugin.EventHandlerPlugin):

    def __init__(self, **kwargs):
        # super(Meta_Reader,self).__init__(**kwargs)
        self.printing = False

    
    def on_after_startup(self):
        self._logger.info("Meta Reader started up")
        self.meta = Meta_Reader(self)
        self.update()

    def update(self):
        self.meta.check_files()
        
    def on_event(self,event, payload):

        if event == 'PrintStarted':
            self.printing = True
        elif event == 'PrintFailed':
            self.printing = False
        elif event == 'PrintDone':
            self.printing = False
        elif event == 'PrintCancelled':
            self.printing = False
        elif event == "FileDeselected":
            self.printing = False

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
            js=["js/Meta_Reader.js"]
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
                user="Robo3D",
                repo="OctoPrint-Meta_reader",
                current=self._plugin_version,

                # update method: pip
                pip="https://github.com/Robo3D/OctoPrint-Meta_reader/archive/{target_version}.zip"
            )
        )


__plugin_name__ = "Meta_reader"

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = Meta_Reader()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

