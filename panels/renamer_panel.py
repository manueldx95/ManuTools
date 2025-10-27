import bpy


class MANUTOOLS_PT_lp_hp_matcher(bpy.types.Panel):
    bl_label = "Renamer"
    bl_idname = "MANUTOOLS_PT_lp_hp_matcher"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ManuTools"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout

        # Suffixes section
        box = layout.box()
        box.label(text="Add Suffixes:")
        row = box.row(align=True)
        row.operator("object.add_lp_suffix")
        row.operator("object.add_hp_suffix")
        
        layout.separator()

        # Batch rename section
        box = layout.box()
        box.label(text="Batch Rename:")
        box.operator("object.batch_rename")
        
        layout.separator()
        
      # Matching section
        box = layout.box()
        box.label(text="Auto Matching:")
        box.operator("object.auto_match_lp_hp")
        
        # Quick info
        layout.separator()
        selected = len([obj for obj in context.selected_objects if obj.type == 'MESH'])
        
        if selected > 0:
            layout.label(text=f"Selected Meshes: {selected}")
