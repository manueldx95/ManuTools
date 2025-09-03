import bpy

class MANUTOOLS_PT_DevPanel(bpy.types.Panel):
    bl_label = "DevTools"
    bl_idname = "MANUTOOLS_PT_dev_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ManuTools"
    #bl_options = "DEFAULT_CLOSED"
    
    def draw(self, context):
        layout = self.layout
        
        # Controlla se la proprietà esiste prima di usarla
        if hasattr(context.scene, 'reload_addon_props'):
            props = context.scene.reload_addon_props
            layout.prop(props, "addon_name")
            
            # Due pulsanti: normale e safe reload
            row = layout.row(align=True)
            row.operator("manutools.reload_addon", text="Fast Reload")
            row.operator("manutools.safe_reload_addon", text="Safe Reload", icon='LOCKED')
        else:
            layout.label(text="Reload addon non disponibile")
            layout.label(text="Registra prima ReloadAddonProperties")
        
        # Sezione Quick Reload
        box = layout.box()
        box.label(text="Quick Reload:")
        
        # Prima aggiungi questo addon (manutools) in evidenza
        if hasattr(context.scene, 'reload_addon_props'):
            # Fast reload
            row = box.row()
            row.scale_y = 1.1
            props = row.operator("manutools.set_and_reload_addon", text="🔄 ManuTools (Fast)", icon='FILE_REFRESH')
            props.addon_name = "manutools"
            
            # Safe reload
            row = box.row()
            row.scale_y = 1.1
            props = row.operator("manutools.safe_set_and_reload_addon", text="🔒 ManuTools (Safe)", icon='LOCKED')
            props.addon_name = "manutools"
            
            # Separator per distinguere questo addon dagli altri
            box.separator()
        
        # Poi trova altri addon installati che potrebbero essere in sviluppo
        try:
            import addon_utils
            addon_count = 0
            
            for mod in addon_utils.modules():
                # Salta questo addon (già mostrato sopra) e addon di sistema
                if (mod.__name__ != "manutools" and 
                    mod.__name__ not in ['bl_ui', 'bl_operators', 'cycles', 'bpy', 'mathutils'] and 
                    not mod.__name__.startswith('bl_') and
                    addon_count < 8):  # Ridotto a 8 per lasciare spazio al pulsante manutools
                    
                    row = box.row()
                    if hasattr(context.scene, 'reload_addon_props'):
                        props = row.operator("manutools.set_and_reload_addon", text=f"📦 {mod.__name__}")
                        props.addon_name = mod.__name__
                    else:
                        row.label(text=mod.__name__)
                    addon_count += 1
            
            if addon_count == 0:
                box.label(text="Nessun altro addon trovato")
                
        except Exception as e:
            box.label(text=f"Errore nel listing addon: {str(e)[:40]}")
        
        # Sezione utilities aggiuntive
        box = layout.box()
        box.label(text="Utilities:")
        box.operator("manutools.list_active_addons", text="List Active Addons", icon='CONSOLE')
        
        # Mostra addon correntemente selezionato
        if hasattr(context.scene, 'reload_addon_props'):
            current_addon = context.scene.reload_addon_props.addon_name
            if current_addon:
                box.label(text=f"Current: {current_addon}", icon='RADIOBUT_ON')
            else:
                box.label(text="No addon selected", icon='RADIOBUT_OFF')