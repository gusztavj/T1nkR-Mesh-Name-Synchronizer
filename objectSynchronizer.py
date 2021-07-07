
import bpy
import re
from bpy.props import StringProperty, BoolProperty, EnumProperty, PointerProperty
from bpy.types import Operator, AddonPreferences, PropertyGroup

# Addon settings for add-on preferences
class T1nkerObjectSynchronizerAddonSettings(PropertyGroup):
    prefix: StringProperty(
        name="Object name prefix", 
        description="Prefix to prepend to object names"
    )
    
    suffix: StringProperty(
        name="Object name suffix", 
        description="Suffix to append to object names"
    )

    isTestOnly: BoolProperty(
        name="Just a test", 
        description="Just list planned changes in names, but don't actually change anything",
        default=False
    )

class T1nkerObjectSynchronizerAddonPreferences(AddonPreferences):
    # this must match the add-on name, use '__package__'
    # when defining this in a submodule of a python package.
    bl_idname = __package__
    
    settings : PointerProperty(type=T1nkerObjectSynchronizerAddonSettings)

    # Display addon preferences ===================================================================================================
    def draw(self, context):
             
        layout = self.layout
        layout.label(text="Default settings")                
        layout.prop(self.settings, "prefix")        
        layout.prop(self.settings, "suffix")        


# Main export operator class
class T1NKER_OT_ObjectSynchronizer(Operator):    
    """Export object compilations for Trainz"""
    bl_idname = "t1nker.objectsynchronizer"
    bl_label = "Sync object names with meshes"
    bl_options = {'REGISTER', 'UNDO'}    
    
    # Operator settings
    settings : T1nkerObjectSynchronizerAddonSettings = None        

    # Constructor =================================================================================================================
    def __init__(self):
        self.settings = None
    
    # See if the operation can run ================================================================================================
    @classmethod
    def poll(cls, context):
        return True

    # Draw operator to show export settings during invoke =========================================================================
    def draw(self, context):        
        layout = self.layout        
        layout.prop(self.settings, "prefix")
        layout.prop(self.settings, "suffix")
        layout.prop(self.settings, "isTestOnly")  

    # Show the dialog ======================================================================================================
    def invoke(self, context, event):                
        # For first run in the session, load addon defaults (otherwise use values set previously in the session)
        if self.settings is None:
            self.settings = context.preferences.addons[__package__].preferences.settings
 
        # Show dialog
        result = context.window_manager.invoke_props_dialog(self, width=400)
        
        return result

    # Return the Outliner ==================================================================================================
    # From: https://github.com/K-410/blender-scripts/blob/master/2.8/toggle_hide.py / space_outliner
    def _getSpaceOutliner():
        """Get the outliner. If context area is outliner, return it."""
        context = bpy.context
        if context.area.type == 'OUTLINER':
            return context.space_data
        for w in context.window_manager.windows:
            for a in w.screen.areas:
                if a.type == 'OUTLINER':
                    return a.spaces.active
   
    def _performFindAndReplace(self, object):            
        if object.data and object.data.users == 1:
            synchedName = self.settings.prefix + object.name + self.settings.suffix

            if object.name == synchedName:
                print(f"* '{object.name}' is not affected")
            else:
                print(f"* '{object.name}' --> '{synchedName}'")

            if not self.settings.isTestOnly:
                object.data.name = synchedName

        return object


    # Here is the core stuff ======================================================================================================
    def execute(self, context):              
        
        objects = [i for i in bpy.context.selected_ids if isinstance(i, bpy.types.Object)]

        for objectElement in objects:
            object: bpy.types.Object = objectElement
            self._performFindAndReplace(object)   
                                            
        return {'FINISHED'}
    

