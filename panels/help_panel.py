import bpy
import webbrowser
import urllib

# Operatore per aprire le preferences
class MANUTOOLS_OT_open_preferences(bpy.types.Operator):
    """Open ManuTools addon preferences"""
    bl_idname = "manutools.open_preferences"
    bl_label = "Open Preferences"
    bl_options = {'INTERNAL'}
    
    def execute(self, context):
        # Apre le preferences e seleziona ManuTools
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')
        
        # Naviga alla sezione Add-ons
        context.preferences.active_section = 'ADDONS'
        
        # Cerca e seleziona ManuTools
        bpy.context.window_manager.addon_search = "ManuTools"
        
        return {'FINISHED'}


# Operatore per aprire URL esterni
class MANUTOOLS_OT_open_url(bpy.types.Operator):
    """Open URL in web browser"""
    bl_idname = "manutools.open_url"
    bl_label = "Open URL"
    bl_options = {'INTERNAL'}
    
    url: bpy.props.StringProperty(
        name="URL",
        description="URL to open",
        default=""
    )
    
    def execute(self, context):
        if self.url:
            webbrowser.open(self.url)
            self.report({'INFO'}, f"Opening {self.url}")
        else:
            self.report({'ERROR'}, "No URL specified")
        return {'FINISHED'}

class MANUTOOLS_OT_contact_support(bpy.types.Operator):
    """Open default email client to contact ManuTools support"""
    bl_idname = "manutools.contact_support"
    bl_label = "Contact Support"
    bl_options = {'INTERNAL'}

    def execute(self, context):
        email = "mdonofrio3d@gmail.com"
        subject = urllib.parse.quote("ManuTools Support Request")
        body = urllib.parse.quote("Hi, I need help with ManuTools addon.")
        mailto_link = f"mailto:{email}?subject={subject}&body={body}"
        webbrowser.open(mailto_link)
        self.report({'INFO'}, "Opening email client")
        return {'FINISHED'}



# Pannello Help
class MANUTOOLS_PT_help(bpy.types.Panel):
    bl_label = "Help"
    bl_idname = "MANUTOOLS_PT_help"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ManuTools"
    bl_options = {'DEFAULT_CLOSED'}
    bl_order = 100  # Ultimo pannello
    
    def draw(self, context):
        layout = self.layout
        # Ottieni la versione dall'addon
        addon_name = __name__.split('.')[0]
        if addon_name in bpy.context.preferences.addons:
            addon = bpy.context.preferences.addons[addon_name]
            # Ottieni versione da bl_info
            try:
                import sys
                addon_module = sys.modules.get(addon_name)
                if addon_module and hasattr(addon_module, 'bl_info'):
                    version = addon_module.bl_info.get('version', (1, 0, 0))
                    version_str = f"{version[0]}.{version[1]}.{version[2]}"
                else:
                    version_str = "1.0.0"
            except:
                version_str = "1.0.0"
        else:
            version_str = "Unknown"
        
        # Box versione
        box = layout.box()
        row = box.row(align=True)
        row.label(text=f"Version: {version_str}",)
        row.operator("manutools.open_preferences", text="", icon='PREFERENCES')        
        layout.separator()
        
        # Links esterni
        col = box.column(align=True)
        
        # Documentation
        row = col.row()
        row.scale_y = 1.1
        op = row.operator("manutools.open_url", 
                         text="Documentation", 
                         icon='HELP')
        op.url = "https://extensions.blender.org/add-ons/manutools/"
        
        # Support
        row = col.row()
        row.scale_y = 1.1
        op = row.operator("manutools.contact_support", text="Support", icon='COMMUNITY')
        
        # ArtStation
        row = col.row()
        row.scale_y = 1.1
        op = row.operator("manutools.open_url", 
                         text="Artstation", 
                         icon='WORLD')
        op.url = "https://www.artstation.com/manueldonofrio"
        
        # YouTube
        row = col.row()
        row.scale_y = 1.1
        op = row.operator("manutools.open_url", 
                         text="Youtube", 
                         icon='FILE_MOVIE')
        op.url = "https://www.youtube.com/@jaktorrone"
        
        
        # Altri addon
        box = layout.box()
        box.label(text="Other Addons:", icon='PLUGIN')
        
        col = box.column(align=True)
        row = col.row()
        row.scale_y = 1.1
        op = row.operator("manutools.open_url", 
                         text="Textura", 
                         icon='TEXTURE')
        op.url = "https://superhivemarket.com/products/textura"


