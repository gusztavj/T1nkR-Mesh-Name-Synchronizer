# Object Synchronizer
#
# COPYRIGHT **************************************************************************************************
# Creative Commons CC-BY-SA. Simply to put, you can create derivative works based on this script,
# and if you are nice, you don't remove the following attribution:
#
# Original script created by: T1nk-R - na.mondhatod@gmail.com
# Version 2021-05-15
#
# DISCLAIMER *************************************************************************************************
# This script is provided as-is. Use at your own risk. No warranties, no guarantee, no liability,
# no matter what happens. Still I tried to make sure no weird things happen.
#
# 

bl_info = {
    "name": "T1nk-R Object Name Synchronizer",
    "author": "GusJ",
    "version": (1, 0),
    "blender": (2, 91, 0),
    "location": "Edit",
    "description": "Sync object names to mesh names",
    "category": "User Interface",
    "doc_url": "Yet to come, till that just drop a mail to Gus at na.mondhatod@gmail.com",
}

if "bpy" in locals():
    from importlib import reload
    reload(objectSynchronizer)
    del reload

import bpy
from . import objectSynchronizer

# Store keymaps here to access after registration
addon_keymaps = []

# Define menu item
def menuItem(self, context):
    self.layout.operator(objectSynchronizer.T1NKER_OT_ObjectSynchronizer.bl_idname)

# Class registry
classes = [
    objectSynchronizer.T1nkerObjectSynchronizerAddonSettings, 
    objectSynchronizer.T1nkerObjectSynchronizerAddonPreferences, 
    objectSynchronizer.T1NKER_OT_ObjectSynchronizer
]

# Register the plugin
def register():
    
    # Make sure to avoid double registration
    unregister()
    
    # Register classes
    for c in classes:
        bpy.utils.register_class(c)
    
    # Add menu command to File > Export
    bpy.types.TOPBAR_MT_edit.append(menuItem)
    bpy.types.OUTLINER_MT_context_menu.append(menuItem)

    # Set CTRL+SHIFT+Y as shortcut
    wm = bpy.context.window_manager
    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name='Outliner', space_type='OUTLINER')
        kmi = km.keymap_items.new(objectSynchronizer.T1NKER_OT_ObjectSynchronizer.bl_idname, 'F3', 'PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))

# Unregister the plugin
def unregister():

    # Put in try since we perform this as a preliminary cleanup of leftover stuff during registration    
    try:
        # Unregister key mapping
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
        addon_keymaps.clear()

        # Unregister classes (in reverse order)
        for c in reversed(classes):
            bpy.utils.unregister_class(c)
        
        # Delete menu item
        bpy.types.TOPBAR_MT_file_export.remove(menuItem)
    except:
        pass

# Let you run registration without installing. You'll find the command in Edit menu
if __name__ == "__main__":
    register()
