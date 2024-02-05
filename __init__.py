# T1nk-R's Mesh Name Synchronizer add-on for Blender
# - part of T1nk-R Utilities for Blender
#
# Version: Please see the version tag under bl_info below.
#
# This module is responsible for managing add-on and settings lifecycle.
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

bl_info = {
    "name": "T1nk-R Mesh Name Synchronizer (T1nk-R Utilitiesí)",
    "author": "T1nk-R (GusJ)",
    "version": (2, 1, 0),
    "blender": (3, 6, 0),
    "location": "Outliner > Context menu, Outliner > Context menu of objects and meshes",
    "description": "Synchronize mesh names with parent object names",
    "category": "Object",
    "doc_url": "https://github.com/gusztavj/T1nkR-Mesh-Name-Synchronizer",
}

# Lifecycle management ============================================================================================================

# Reload the main module to make sure it's up to date
if "bpy" in locals():
    from importlib import reload
    reload(meshNameSynchronizer)
    reload(updateChecker)
    del reload

import bpy
from . import meshNameSynchronizer
from . import updateChecker

# Properties ======================================================================================================================

addon_keymaps = []
"""
Store keymaps here to access after registration.
"""

classes = [
    updateChecker.T1nkerMeshNameSynchronizerUpdateInfo,
    updateChecker.T1NKER_OT_MeshNameSynchronizerUpdateChecker,
    meshNameSynchronizer.T1nkerMeshNameSynchronizerSettings, 
    meshNameSynchronizer.T1nkerMeshNameSynchronizerAddonPreferences, 
    meshNameSynchronizer.T1NKER_OT_MeshNameSynchronizer    
]
"""
List of classes requiring registration and unregistration.
"""

menuLocations = [
    bpy.types.OUTLINER_MT_context_menu,
    bpy.types.OUTLINER_MT_object,
    bpy.types.OUTLINER_MT_edit_datablocks
]
"""
Location to add the menu to.
"""


# Public functions ================================================================================================================

# Register menu item --------------------------------------------------------------------------------------------------------------
def menuItem(self, context):
    """
    Add a menu item.

    Args:
        context (bpy.types.Context): A context object passed on by Blender for the current context.
    """
    
    self.layout.operator_context = 'INVOKE_DEFAULT'
    self.layout.operator(meshNameSynchronizer.T1NKER_OT_MeshNameSynchronizer.bl_idname)



# Register the plugin -------------------------------------------------------------------------------------------------------------
def register():
    """
    Perform registration of the add-on when being enabled.
    """
    
    # Make sure to avoid double registration
    unregister()
    
    # Register classes
    for c in classes:
        bpy.utils.register_class(c)
    
    bpy.types.Scene.T1nkerMeshNameSynchronizerSettings = bpy.props.PointerProperty(type=meshNameSynchronizer.T1nkerMeshNameSynchronizerSettings)
    
    # Add menus to locations specified above
    for location in menuLocations:
        location.append(menuItem)
    
    # bpy.types.OUTLINER_MT_context_menu.append(menuItem)
    # bpy.types.OUTLINER_MT_object.append(menuItem)
    # bpy.types.OUTLINER_MT_edit_datablocks.append(menuItem)

    # Configure hotkey
    #
    
    # Set CTRL+SHIFT+Y as shortcut
    wm = bpy.context.window_manager
    
    # Note that in background mode (no GUI available), keyconfigs are not available either,
    # so we have to check this to avoid nasty errors in background case.
    
    kc = wm.keyconfigs.addon
    if kc: # Blender runs with GUI
        # The hotkey will only be available when the mouse is within an Outliner
        km = wm.keyconfigs.addon.keymaps.new(name='Outliner', space_type='OUTLINER')
        kmi = km.keymap_items.new(meshNameSynchronizer.T1NKER_OT_MeshNameSynchronizer.bl_idname, 'F3', 'PRESS', ctrl=True, shift=True)
        addon_keymaps.append((km, kmi))

# Unregister the plugin -----------------------------------------------------------------------------------------------------------
def unregister():
    """
    Delete/unregister what has once been registered, such as menus, hotkeys, classes and so on.
    """

    # Put in try since we perform this as a preliminary cleanup of leftover stuff during registration,
    # and it may be normal that unregistering something simply does not work without being registered first.
    try:
        # Unregister key mapping
        for km, kmi in addon_keymaps:
            km.keymap_items.remove(kmi)
            
        addon_keymaps.clear()
        
        del bpy.types.Scene.T1nkerMeshNameSynchronizerSettings

        # Unregister classes (in reverse order)
        for c in reversed(classes):
            try:
                bpy.utils.unregister_class(c)
            except:
                # Don't panic, it was probably not registered
                pass
        
        # Delete menu items
        for location in menuLocations:
            # Delete menu items in separate try blocks so if one fails others may still be attempted to be removed
            try:
                location.remove(menuItem)
            except:
                pass
            
    except:
        # Don't panic, we can't do anything. Probably something was not registered either
        pass

# Developer mode ##################################################################################################################

# Let you run registration without installing. You'll find the command in Edit menu
if __name__ == "__main__":
    register()
