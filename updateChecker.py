# T1nk-R's Mesh Name Synchronizer add-on for Blender
# - part of T1nk-R Utilities for Blender
#
# Version: Please see the version tag under bl_info in __init__.py.
#
# This module is responsible for checking if updates are available.
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

from __future__ import annotations
from . import bl_info
import requests
import json
import contextlib
from datetime import datetime, timedelta
from bpy.types import PropertyGroup, Operator, Context
from bpy.props import StringProperty, BoolProperty, IntProperty


# Repository information for help and updates #####################################################################################
class UpdateCheckingInfo:
    """
    Information to access the GitHub Update Checker service
    """
        
    _repoSlug = "T1nkR-Mesh-Name-Synchronizer"
    """Slug for the repository"""
        
    
    _repoBase = "https://github.com/gusztavj"
    """Base address of my repositories"""
    
    _repoApiBase = "https://api.github.com/repos/gusztavj"
    """Base address of my repositories for API calls"""        

    @staticmethod
    def _stripSlashes(uriSegment) -> str:
        """Strips leading and trailing slashes"""
        return uriSegment.lstrip("/").rstrip("/")
    
    @staticmethod
    def _combineUri(*args: str) -> str:        
        """Combines strings into an URI by stripping all leading and trailing slashes beforehand"""
        return "/".join( f"{UpdateCheckingInfo._stripSlashes(segment)}" for segment in args )
        

    @staticmethod
    def repoUrl() -> str:
        """URL of the repository"""
        return UpdateCheckingInfo._combineUri(UpdateCheckingInfo._repoBase, UpdateCheckingInfo._repoSlug)
    
    def repoReleasesUrl() -> str:
        """URL of the releases page of the repository"""
        return UpdateCheckingInfo._combineUri(UpdateCheckingInfo._repoBase, UpdateCheckingInfo._repoSlug, "releases")
    
    def repoReleaseApiUrl() -> str:
        """API URL to get latest release information"""
        return UpdateCheckingInfo._combineUri(UpdateCheckingInfo._repoApiBase, UpdateCheckingInfo._repoSlug, "releases", "latest")
    
    currentVersion: str = ""
    """Version number of the current version running in `x.y.z` format"""
    
    forceUpdateCheck: bool = False
    
    @staticmethod
    def getUpdateCheckingServiceUrl() -> str:
        """URL to the service endpoint of tge GitHub Update Checker service"""
        
        # Production URL
        return "https://apps.imprestige.biz/gitHubUpdateChecker/getUpdateInfo"
        
        # Test URL
        #return "http://localhost:5000/getUpdateInfo"
    
    
    @staticmethod
    def getRequestBody():
        return {
                "appInfo": 
                    {
                        "repoSlug": UpdateCheckingInfo._repoSlug,
                        "currentVersion": UpdateCheckingInfo.currentVersion
                    },
                    "forceUpdateCheck": UpdateCheckingInfo.forceUpdateCheck
            }
        
            
    
# Structured update info ##########################################################################################################
class T1nkerMeshNameSynchronizerUpdateInfo(PropertyGroup):
    """
    Information about the current and the latest update
    """
    
    checkFrequencyDays: IntProperty(
        name="Update check frequency (days)",
        default=1
    ) # type: ignore
    """
    Frequency of checking for new updates (days).
    """
    
    updateAvailable: BoolProperty(
        name="Is update available",
        default=False
    ) # type: ignore
    """
    Tells whether an update is available (`True`).
    """
        
    currentVersion: StringProperty(
        name="Installed version",
        default=""
    ) # type: ignore
    """
    Version number of the current version running in x.y.z format.
    """
        
    latestVersion: StringProperty(
        name="Latest available version",
        default=""
    ) # type: ignore
    """
    Version number of the latest release (the release tag from the repo).
    """
    
    latestVersionName: StringProperty(
        name="Name of latest version",
        default=""
    ) # type: ignore
    """
    Name of the latest release.
    """
    
    lastCheckedTimestamp: StringProperty(
        name="When last successful check for updates happened",
        default=""
    ) # type: ignore
    """
    Date and time of last successful check for updates.
    """
        
# Operator for checking updates ###################################################################################################
class T1NKER_OT_MeshNameSynchronizerUpdateChecker(Operator):    
    """
    Checks for updates
    """
    
    # Properties ==================================================================================================================
    
    # Blender-specific stuff ------------------------------------------------------------------------------------------------------    
    bl_idname = "t1nker.meshnamesynchronizerupdatechecker"
    bl_label = "Check updates for T1nk-R Mesh Names Synchronizer"
    bl_description = "Check updates for T1nk-R Mesh Names Synchronizer"
    bl_options = {'REGISTER', 'UNDO'}    
    bl_category = "T1nk-R Utils"

    # Other properties ------------------------------------------------------------------------------------------------------------
    forceUpdateCheck: BoolProperty(default = False) # type: ignore
    """
    Whether to force update check. Use only for testing. Once the operator is called,
    this is set back to False to prevent accidental flooding of GitHub.
    """

    # Public functions ============================================================================================================
    
    # Perform the operation -------------------------------------------------------------------------------------------------------
    def execute(self, context: Context):  # sourcery skip: extract-method
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

        # Check cache expiry only if update check is not forced
        if not self.forceUpdateCheck:            
            # Check if update check shall be performed based on frequency
            with contextlib.suppress(Exception):
                lastCheckDate = datetime.strptime(updateInfo.lastCheckedTimestamp, '%Y-%m-%d %H:%M:%S')
                delta = datetime.now() - lastCheckDate
                if delta.days < updateInfo.checkFrequencyDays: # Successfully checked for updates in the last checkFrequencyDays number of days
                    # Do not flood the repo API, use cached info
                    return
        else: # turn forcing check off to prevent accidental flooding                
            self.forceUpdateCheck = False

        try: # if anything goes wrong we silently fail, no need to perform double-checks
            print(f"{__package__}: Trying to check for updates")
            
            # Get installed version (already stored as a list by Blender)

            installedVersionTags = bl_info["version"]
            updateInfo.currentVersion = ".".join([str(i) for i in installedVersionTags])

            UpdateCheckingInfo._repoSlug = "T1nkR-Mesh-Name-Synchronizer"
            UpdateCheckingInfo.currentVersion = updateInfo.currentVersion
            headers = {'Content-Type': 'application/json'}
            payload = UpdateCheckingInfo.getRequestBody()
            response = requests.post(UpdateCheckingInfo.getUpdateCheckingServiceUrl(), headers=headers, json=payload, timeout=5)

            # For errors, enable raising exceptions
            if response.status_code != 200:
                response.raise_for_status()

            # Being here means a response has been received successfully

            repoInfo = response.json()["repository"]

            updateInfo.latestVersionName = repoInfo["latestVersionName"]
            updateInfo.latestVersion = repoInfo["latestVersion"]                        
            updateInfo.releaseUrl = repoInfo["latestVersion"]
            updateInfo.repoUrl = repoInfo["repoUrl"]
            updateInfo.updateAvailable = response.json()["updateAvailable"]

            # Save timestamp
            updateInfo.lastCheckedTimestamp = f"{datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')}"
            
            print(f"{__package__}: Checking for updates completed, there is {'a' if updateInfo.updateAvailable else 'no' } new version available")

        except requests.exceptions.Timeout as tex:
            # Timeout, let's not bother the user
            print(f"{__package__}: Version checking timed out")
            updateInfo.updateAvailable = False
        except Exception as ex: 
            print(f"{__package__}: Error during version check: {ex}")
            updateInfo.updateAvailable = False

        return {'FINISHED'}