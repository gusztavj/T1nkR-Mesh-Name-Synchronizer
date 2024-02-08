# T1nk-R's Mesh Name Synchronizer add-on for Blender
# - part of T1nk-R Utilities for Blender
#
# Version: Please see the version tag under bl_info in __init__.py.
#
# This module holds the key UI and business logic.
#
# Module and add-on authored by T1nk-R (https://github.com/gusztavj/)
#
# PURPOSE & USAGE *****************************************************************************************************************
# You can use this add-on to synchronize the names of meshes with the names of their parent objects.
#
# Help, support, updates and anything else: https://github.com/gusztavj/T1nkR-Mesh-Name-Synchronizer
#
# COPYRIGHT ***********************************************************************************************************************
#
# ** MIT License **
# 
# Copyright (c) 2023-2024, T1nk-R (Gusztáv Jánvári)
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, 
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE 
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# ** Commercial Use **
# 
# I would highly appreciate to get notified via [janvari.gusztav@imprestige.biz](mailto:janvari.gusztav@imprestige.biz) about 
# any such usage. I would be happy to learn this work is of your interest, and to discuss options for commercial support and 
# other services you may need.
#
# DISCLAIMER **********************************************************************************************************************
# This add-on is provided as-is. Use at your own risk. No warranties, no guarantee, no liability,
# no matter what happens. Still I tried to make sure no weird things happen:
#   * This add-on is intended to change the name of the meshes and other data blocks under your Blender objects.
#   * This add-on is not intended to modify your objects and other Blender assets in any other way.
#   * You shall be able to simply undo consequences made by this add-on.
#
# You may learn more about legal matters on page https://github.com/gusztavj/T1nkR-Mesh-Name-Synchronizer
#
# *********************************************************************************************************************************

from datetime import datetime
import bpy
from . import updateChecker
from bpy.props import StringProperty, BoolProperty, PointerProperty
from bpy.types import Operator, AddonPreferences, PropertyGroup


# Addon settings for add-on preferences ###########################################################################################
class T1nkerMeshNameSynchronizerSettings(PropertyGroup):
    """
    Settings for the T1nk-R Mesh Name Synchronizer add-on.
    """
        
    
    prefix: StringProperty(
        name="Mesh name prefix", 
        description="Prefix to prepend to mesh names"
    )
    """
    A prefix for the mesh name. This is appended before the parent object's name. Leave empty to not add anything.
    """
    
    suffix: StringProperty(
        name="Mesh name suffix", 
        description="Suffix to append to mesh names"
    )
    """
    A suffix for the mesh name. This is appended after the parent object's name. Leave empty to not add anything.
    """
    
    meshesOnly: BoolProperty(
        name="Apply only to meshes, leave others",
        description="Check to sync only mesh names, clear to include cameras, lights etc.",
        default=False
    )
    """
    If `True`, only meshes of objects of the mesh type will be processed, otherwise data blocks of everything,
    such as cameras and lights.
    """

    isVerbose: BoolProperty(
        name="Verbose mode",
        description="Check to get a detailed log on what happened and what not. Non-verbose mode only reports what actually happened.",
        default=False
    )
    """
    Controls log verbosity.
    """
    
    isTestOnly: BoolProperty(        
        name="Just a test", 
        description="Don't do anything, just show what you would do",
        default=False
    )    
    """
    Controls if actions are actually taken or just simulated.
    """
    
    everInitialized: BoolProperty(        
        name="Already initialized", 
        description="",
        default=False
    )    
    """
    This is not intended for the UI. This stores whether the add-on has been initialized for the scene or not, to get
    default values set in add-on preferences.
    """
        

# Addon preferences ###############################################################################################################
class T1nkerMeshNameSynchronizerAddonPreferences(AddonPreferences):    
    """
    Preferences of the add-on.
    """
    
    # Properties required by Blender ==============================================================================================
    bl_idname = __package__
    """
    Blender's ID name for it to know to which add-on this class belongs. This must match the add-on name, 
    so '__package__' shall be used when defining this in a submodule of a python package.
    """
    
    # Other properties ============================================================================================================
    settings: PointerProperty(type=T1nkerMeshNameSynchronizerSettings)
    """
    The default settings stored at add-on level (insted of scene level).
    """
    
    updateInfo: PointerProperty(type=updateChecker.T1nkerMeshNameSynchronizerUpdateInfo)
    """
    Information about the current version and the latest available
    """
    
    # Public functions ============================================================================================================

    # Display addon preferences ---------------------------------------------------------------------------------------------------
    def draw(self, context):
        """
        Draws the UI of the add-on preferences (default settings)

        Args:
            context (bpy.types.Context): A context object passed on by Blender for the current context.
        """
        
        layout = self.layout
        layout.label(text="Default settings")                
        layout.prop(self.settings, "prefix")        
        layout.prop(self.settings, "suffix")
        
        # Log verbosity and test mode is intentionally not added
                
        # Update available button
        #
        
        try: # to see if we know anything about updates
            updateInfo = context.preferences.addons[__package__].preferences.updateInfo
            
            # Note that checking update is part of executing the main operator, that is, performing at least
            # one synchronization. Until that no updates will be detected. Updates are not checked each time
            # this dialog is drawn, but as set in `updateInfo.T1nkerMeshNameSynchronizerUpdateInfo.checkFrequencyDays`.
            if updateInfo.updateAvailable:
                # Draw update button and tip
                opUpdate = layout.column().row().operator(
                        'wm.url_open',
                        text=f"Update available",
                        icon='URL'
                        )            
                opUpdate.url = updateChecker.RepoInfo.repoReleasesUrl
                layout.row().label(text=f"You can update from {updateInfo.currentVersion} to {updateInfo.latestVersion}")
        except:
            # Do nothing, if we could not check updates, probably this is the first time of enabling the add-on
            # and corresponding data structures are not yet available.
            pass

# Main operator class #############################################################################################################
class T1NKER_OT_MeshNameSynchronizer(Operator):    
    """
    Synchronize mesh names with parent object names
    """
    
    # Properties ==================================================================================================================
    
    # Blender-specific stuff ------------------------------------------------------------------------------------------------------    
    bl_idname = "t1nker.meshnamesynchronizer"
    bl_label = "Synchronize Mesh Names (T1nk-R Utils)"
    bl_description = "Synchronize mesh names with parent object names"
    bl_options = {'REGISTER', 'UNDO'}    
    bl_location = "Outliner"
    bl_space_type = "OUTLINER"
    bl_region_type = "WINDOW"
    bl_category = "T1nk-R Utils"
        
    # Lifecycle management ========================================================================================================
    
    # Initialize object -----------------------------------------------------------------------------------------------------------
    def __init__(self):
        """
        Make an instance and create a scene-level copy of the settings.
        """
        
        self.settings: T1nkerMeshNameSynchronizerSettings = None
        """
        Copy of the operator settings specific to the Blender file (scene)
        """
            
    # Public functions ============================================================================================================
        
    # See if the operation can run ------------------------------------------------------------------------------------------------
    @classmethod
    def poll(cls, context):
        """
        Tell if the operator can run.

        Args:
            context (bpy.types.Context): A context object passed on by Blender for the current context.

        Returns:
            bool: `True` if the operator can run, `False` otherwise.
        """
        # No reason to not run it. If the user is not in the outliner, we'll try to get them there.
        
        return True

    # Draw operator to show export settings during invoke =========================================================================
    def draw(self, context):        
        """
        Draw the UI.

        Args:
            context (bpy.types.Context): A context object passed on by Blender for the current context.
        """
        
        # Get shortcut for scene-specific settings
        self.settings = context.scene.T1nkerMeshNameSynchronizerSettings
        
        layout = self.layout        
        
        # Forming names
        #
        box = layout.box()
        box.row(heading = "Forming names")
        
        # Fix that heading specified above is not shown
        box.row().label(text="Forming names")
        
        box.row().prop(self.settings, "prefix")
        box.row().prop(self.settings, "suffix")        
        
        # Setting scope
        #
        box = layout.box()
        box.row(heading = "Scope")
        
        # Fix that heading specified above is not shown
        box.row().label(text="Scope")
        
        box.row().prop(self.settings, "meshesOnly")  
        
        # Operation settings
        #
        box = layout.box()
        box.row(heading = "Operation settings")
        
        # Fix that heading specified above is not shown
        box.row().label(text="Operation settings")
        
        box.row().prop(self.settings, "isTestOnly")  
        box.row().prop(self.settings, "isVerbose")
        
        # Help and update buttons
        #
        box = layout.box()
        buttonRow = box.row()
        
        # Help button
        #
        
        opHelp = buttonRow.column().row().operator(
            'wm.url_open',
            text='Help',
            icon='URL'
            )
        opHelp.url = updateChecker.RepoInfo.repoUrl       
        
        # Update available button
        #
        
        try:
            updateInfo = context.preferences.addons[__package__].preferences.updateInfo
            
            # Note that checking update is part of executing the main operator, that is, performing at least
            # one synchronization. Until that no updates will be detected. Updates are not checked each time
            # this dialog is drawn, but as set in `updateInfo.T1nkerMeshNameSynchronizerUpdateInfo.checkFrequencyDays`.
            if updateInfo.updateAvailable:
                # Update button            
                opUpdate = buttonRow.column().row().operator(
                        'wm.url_open',
                        text=f"Update available",
                        icon='URL'
                        )            
                opUpdate.url = updateChecker.RepoInfo.repoReleasesUrl
                box.row().label(text=f"You can update from {updateInfo.currentVersion} to {updateInfo.latestVersion}")
        except:
            # Fail silently if we cannot check for updates or draw the UI
            pass    
        


    # Show the UI -----------------------------------------------------------------------------------------------------------------
    def invoke(self, context, event):                
        """
        React to invocation by showing the properties dialog.

        Args:
            context (bpy.types.Context): A context object passed on by Blender for the current context.
            event: The event triggering the operation, as passed on by Blender.

        Returns:
            {'FINISHED'} or {'ERROR'}, indicating success or failure of the operation.
        """
        
        self.settings = context.scene.T1nkerMeshNameSynchronizerSettings
        
        # For first run in the session, load default settings
        if not self.settings.everInitialized:
            self.settings.prefix = context.preferences.addons[__package__].preferences.settings.prefix
            self.settings.suffix = context.preferences.addons[__package__].preferences.settings.suffix
            self.settings.everInitialized = True
            
 
        # Show dialog
        result = context.window_manager.invoke_props_dialog(self, width=400)
        
        return result


    # Perform the operation -------------------------------------------------------------------------------------------------------
    def execute(self, context):              
        """
        Execute the operation

        Args:
            context (bpy.types.Context): A context object passed on by Blender for the current context.

        Returns:
            {'FINISHED'} or {'ERROR'}, indicating success or failure of the operation.
        """
        
        # Call the update checker to check for updates time to time, as specified in 
        # `updateInfo.T1nkerMeshNameSynchronizerUpdateInfo.checkFrequencyDays`
        try:
            bpy.ops.t1nker.meshnamesynchronizerupdatechecker(forceUpdateCheck = True)            
        except:
            # Don't mess up anything if update checking doesn't work, just ignore the error
            pass
        
        operationStarted = f"{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')}"
        
        status = None
        meshesRenamed = 0
        numberOfObjects = 0
        
        self.settings = context.scene.T1nkerMeshNameSynchronizerSettings
        
        print("")
        print("")
        print(f"=" * 80)
        print(f"T1nk-R Mesh Name Synchronizer started ({operationStarted})")
        print(f"-" * 80)        
        print("")
        
        if self.settings.isTestOnly:
            print(f"Operating in test mode, nothing will actually be changed")
        else:
            print(f"Operating in production mode, requested changes will apply")        
        
        if self.settings.isVerbose:
            if self.settings.meshesOnly:
                print(f"\t- Processing only mesh objects")
            else:
                print(f"\t- Processing all kinds of objects")
        
        print("")

        try:
            # Grab selected objects            
            objects = [i for i in bpy.context.selected_ids if isinstance(i, bpy.types.Object)]
            
            # Narrow down to mesh objects if requested so
            if self.settings.meshesOnly:
                objects = [o for o in objects if o.type == "MESH"]
                
            numberOfObjects = len(objects)

            # Iterate selected objects
            for obj in objects:            
                
                # Only process objects with data blocks (meshes), and ignore linked items
                if obj.data:
                    # Construct mesh name
                    meshName = self.settings.prefix + obj.name + self.settings.suffix
                    
                    if obj.data.name == meshName:
                        if self.settings.isVerbose or self.settings.isTestOnly:
                            print(f"- NEEDS NO CHANGE...: Mesh of '{obj.name}': '{obj.data.name}'")
                    else:
                        if self.settings.isTestOnly:
                            print(f"+ WOULD RENAME......: Mesh of '{obj.name}': '{obj.data.name}' --> '{meshName}'")
                        else:
                            obj.data.name = meshName                            
                            if self.settings.isVerbose:
                                print(f"+ RENAMED...........: Mesh of '{obj.name}': '{obj.data.name}' --> '{meshName}'")
                else:
                    if self.settings.isVerbose or self.settings.isTestOnly:
                        print(f"- IGNORED...........: '{obj.name}' is ignored for having no mesh")

            status = {'FINISHED'}
        
        except Exception as ex:            
            print(f"{ex}")
            self.report({'ERROR'}, f"{ex}")
            status = {'CANCELLED'}
        
        finally: # Print some summary
            # Leave here instead of moving toward the end of the try block as some things might have been changed
            # even if an error occurred afterwards
            summary = \
                f"No mesh has been renamed for a total of {numberOfObjects} object(s)" \
                if meshesRenamed == 0 else \
                f"Renamed {meshesRenamed} meshes(s) for a total of {numberOfObjects} object(s)" \
            
            self.report({'INFO'}, summary)
            
            print("")
            print(f"-" * 80)        
            print(summary)
            print(f"-" * 80)
            print(f"T1nk-R Mesh Name Synchronizer finished")                                            
            print(f"=" * 80)
            print("")
        
        return status
    

