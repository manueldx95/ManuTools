import bpy

# Pannello principale con layout del mockup
class MANUTOOLS_PT_shapekeysmanager(bpy.types.Panel):
    bl_label = "Shape Keys Manager"
    bl_idname = "MANUTOOLS_PT_shape_keys_manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'ManuTools'
    bl_options = {'DEFAULT_CLOSED'}


    @classmethod
    def poll(cls, context):
        return context.active_object and context.active_object.type == 'MESH'

    def draw_header(self, context):
        layout = self.layout
        layout.label

    def draw(self, context):
        layout = self.layout
        obj = context.active_object
        mesh = obj.data


        # SEZIONE 1: Shape Keys List
        box = layout.box()
        row = box.row()
        row.label(text="Shape Keys List", icon='SHAPEKEY_DATA')
        
        if mesh.shape_keys:
            # Lista delle shape keys con controlli laterali
            row = box.row()
            col = row.column()
            col.template_list("MESH_UL_shape_keys_custom", "", mesh.shape_keys, "key_blocks", 
                            obj, "active_shape_key_index", rows=4)
            
            # Controlli laterali (aggiungi, rimuovi, sposta)
            col = row.column(align=True)
            col.operator("object.shape_key_add", icon='ADD', text="")
            col.operator("object.shape_key_remove", icon='REMOVE', text="")
            col.separator()
            col.operator("object.shape_key_move", icon='TRIA_UP', text="").type = 'UP'
            col.operator("object.shape_key_move", icon='TRIA_DOWN', text="").type = 'DOWN'
            col.separator()
            col.menu("MESH_MT_shape_key_context_menu", icon='DOWNARROW_HLT', text="")
            
            # Checkbox Relative e bottoni azione sotto la lista
            row = box.row(align=True)
            if mesh.shape_keys:
                row.prop(mesh.shape_keys, "use_relative", text="Relative")
                row.separator()
                
                # Solo Mode button con stato visivo
                solo_icon = 'RESTRICT_VIEW_OFF' if obj.show_only_shape_key else 'RESTRICT_VIEW_ON'
                solo_op = row.operator("shapekeys.solo_mode", text="Solo", icon=solo_icon, depress=obj.show_only_shape_key)
                
                row.prop(obj, "use_shape_key_edit_mode", text="", icon='EDITMODE_HLT')
                row.operator("shapekeys.swap_shape_key_values", text="", icon='UV_SYNC_SELECT')
                row.operator("shapekeys.clear_shape_key", text="", icon='PANEL_CLOSE')
                
            
            # Slider Value con Min/Max e pallini toggle
            if obj.active_shape_key_index >= 0 and obj.active_shape_key:
                sk = obj.active_shape_key
                
                col = box.column(align=True)
                
                # Riga del valore con i pallini toggle
                row = col.row(align=True)
                # Pallino sinistro (min)
                row.operator("shapekeys.set_value_to_min", text="", icon='RADIOBUT_OFF')
                # Slider del valore
                row.prop(sk, "value", text="Value", slider=True)
                # Pallino destro (max)
                row.operator("shapekeys.set_value_to_max", text="", icon='RADIOBUT_ON')
                
                # Min/Max controls
                row = col.row(align=True)
                split = row.split(factor=0.5)
                sub = split.row(align=True)
                sub.label(text="Min")
                sub.prop(sk, "slider_min", text="")
                sub = split.row(align=True)
                sub.label(text="Max")
                sub.prop(sk, "slider_max", text="")
        else:
            box.operator("object.shape_key_add", icon='ADD', text="Add First Shape Key")

        # SEZIONE 2: Shape Key Tools
        if mesh.shape_keys and obj.active_shape_key_index >= 0:
            box = layout.box()
            row = box.row()
            row.label(text="Shape Key Tools", icon='TOOL_SETTINGS')
            
            col = box.column(align=True)
            col.operator("shapekeys.copy_shape_key", text="Duplicate Shape Key", icon='DUPLICATE')
            col.operator("shapekeys.join_as_shapes", text="Join as a Shapes", icon='SELECT_EXTEND')
            col.operator("shapekeys.transfer_shape_keys", text="Transfer Shape Keys", icon='PASTEDOWN')
            col.separator()
            col.operator("shapekeys.delete_all_shape_keys", text="Delete All Shape Keys", icon='PANEL_CLOSE')
            col.operator("shapekeys.apply_all_shape_keys", text="Apply All Shape Keys", icon='CHECKMARK')

        # SEZIONE 3: Edit Operations (solo in Edit Mode)
        if context.mode == 'EDIT_MESH' and mesh.shape_keys and len(mesh.shape_keys.key_blocks) > 0:
            box = layout.box()
            row = box.row()
            row.label(text="Edit Operations", icon='EDITMODE_HLT')
            
            col = box.column(align=True)
            col.operator("shapekeys.propagate_to_shape", text="Propagate to Shape", icon='TRACKING_FORWARDS_SINGLE')
            col.operator("shapekeys.blend_from_shape", text="Blend From Shape", icon='SMOOTHCURVE')
            col.operator("shapekeys.reset_to_basis", text="Reset to Basis", icon='LOOP_BACK')
