from __future__ import annotations
from . import bl_info
import requests
import re
from datetime import datetime
from bpy.types import PropertyGroup, Operator, Context
from bpy.props import StringProperty, BoolProperty, IntProperty

# Repository information for help and updates #####################################################################################
class RepoInfo:
    """
    Information to access the repository for update checking and help access.
    """
    
    _repoBase = "https://github.com/gusztavj/"
    """Base address of my repositories"""
    
    _repoApiBase = "https://api.github.com/repos/gusztavj/"
    """Base address of my repositories for API calls"""
    
    _repoSlug = "T1nkR-Mesh-Name-Synchronizer/"
    """Slug for the repository"""

    repoUrl = _repoBase + _repoSlug
    """URL of the repository"""
    
    repoReleasesUrl = _repoBase + _repoSlug + "releases"
    """URL of the releases page of the repository"""
    
    repoReleaseApiUrl = _repoApiBase + _repoSlug + "releases/latest"
    """API URL to get latest release information"""
    
    username = "gusztavj"
    """My username for API access"""
    
    token = "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"
    """A token restricted only to read code from Blender add-on repos (public anyway)"""
    
# Structured update info ##########################################################################################################
class T1nkerMeshNameSynchronizerUpdateInfo(PropertyGroup):
    """
    Information about the current and the latest update
    """
    
    checkFrequencyDays: IntProperty(
        name="Update check frequency (days)",
        default=3
    )
    """
    Frequency of checking for new updates (days).
    """
    
    updateAvailable: BoolProperty(
        name="Is update available",
        default=False
    )
    """
    Tells whether an update is available (`True`).
    """
        
    currentVersion: StringProperty(
        name="Installed version",
        default=""
    )
    """
    Version number of the current version running in x.y.z format.
    """
        
    latestVersion: StringProperty(
        name="Latest available version",
        default=""
    )
    """
    Version number of the latest release (the release tag from the repo).
    """
    
    latestVersionName: StringProperty(
        name="Name of latest version",
        default=""
    )
    """
    Name of the latest release.
    """
    
    lastCheckedTimestamp: StringProperty(
        name="When last successful check for updates happened",
        default=""
    )
    """
    Date and time of last successful check for updates.
    """
        
# Operator for checking updates ###################################################################################################
class T1NKER_OT_MeshNameSynchronizerUpdateChecker(Operator):    
    """
    Synchronize mesh names with parent object names
    """
    
    # Properties ==================================================================================================================
    
    # Blender-specific stuff ------------------------------------------------------------------------------------------------------    
    bl_idname = "t1nker.meshnamesynchronizerupdatechecker"
    bl_label = "Check updates for T1nk-R Mesh Names Synchronizer"
    bl_description = "Check updates for T1nk-R Mesh Names Synchronizer"
    bl_options = {'REGISTER', 'UNDO'}    
    bl_category = "T1nk-R Utils"

    # Public functions ============================================================================================================
    
    # Perform the operation -------------------------------------------------------------------------------------------------------
    def execute(self, context: Context):
        """
        Performs update check for the add-on and caches results. The cache expires in some days as specified in
        `updateInfo.T1nkerMeshNameSynchronizerUpdateInfo.checkFrequencyDays`, and then new check is performed. Until that the
        cached information is served.

        Args:
            context (bpy.types.Context): A context object passed on by Blender for the current context.
            event: The event triggering the operation, as passed on by Blender.

        Returns:
            {'FINISHED'} or {'ERROR'}, indicating success or failure of the operation.
        """
                
        updateInfo = context.preferences.addons[__package__].preferences.updateInfo
        
        # Check if update check shall be performed based on frequency
        try:                        
            lastCheckDate = datetime.strptime(updateInfo.lastCheckedTimestamp, '%Y-%m-%d %H:%M:%S')
            delta = datetime.now() - lastCheckDate
            if delta.days < updateInfo.checkFrequencyDays: # Successfully checked for updates in the last checkFrequencyDays number of days
                # Do not flood the repo API, use cached info
                return
        except: # For example, lastCheck is None as no update check was ever performed yet
            # Could not determine when last update check was performed, do nothing (check it now)
            pass
                
        
        try: # if anything goes wrong we silently fail, no need to perform double-checks
            response = requests.get(RepoInfo.repoReleaseApiUrl, timeout=5, auth=(RepoInfo.username, RepoInfo.token))            
        
            updateInfo.latestVersionName = response.json()["name"]
            updateInfo.latestVersion = response.json()["tag_name"]
            
            # Trim leading v and eventual trailing qualifiers such as -alpha
            latestVersionCleaned = re.match("[v]((\d+\.)*(\d+)).*", updateInfo.latestVersion)[1]
            
            # Parse into a list
            latestVersionTags = [int(t) for t in latestVersionCleaned.split(".")]
            
            # Get installed version (already stored as a list by Blender)
            installedVersionTags = bl_info["version"]
            updateInfo.currentVersion = ".".join([str(i) for i in installedVersionTags])
            
            updateInfo.updateAvailable = False
            
            if latestVersionTags[0] > installedVersionTags[0]:
                updateInfo.updateAvailable = True
            else:
                if latestVersionTags[1] > installedVersionTags[1]:
                    updateInfo.updateAvailable = True
                else:
                    if len(installedVersionTags) > 2 and latestVersionTags[2] > installedVersionTags[2]:
                        updateInfo.updateAvailable = True
                        
            # Save timestamp
            updateInfo.lastCheckedTimestamp = f"{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')}"
            
        except requests.exceptions.Timeout as tex:
            # Timeout, let's not bother the user
            print("Version checking timed out")
            updateInfo.updateAvailable = False
        except Exception as ex: 
            print(f"Error during version check: {ex}")
            updateInfo.updateAvailable = False
                
        return {'FINISHED'}