import bpy

class MANUTOOLS_PT_ToolsPanel(bpy.types.Panel):
    bl_label = "CustomTools"
    bl_idname = "MANUTOOLS_PT_tools_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "ManuTools"

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if not obj or obj.type != 'MESH':
            layout.label(text="Select a mesh object.")
            return

        # Mostra sempre alcuni tool, anche in Object mode
        layout.label(text="Origin Tools", icon="KEYTYPE_MOVING_HOLD_VEC")
        
        col = layout.column(align=True)
        col.operator("manutools.set_origin_to_base", icon='AXIS_TOP')
        col = layout.column(align=True)
        col.operator("manutools.snap_mesh_to_grid", icon='GRID')

        # Mostra solo in modalità Edit
        if context.mode == 'EDIT_MESH':
            col = layout.column(align=True)
            col.operator("manutools.set_origin_to_selection", icon='PIVOT_MEDIAN')

            layout.label(text="Collapse Tools", icon="KEYTYPE_JITTER_VEC")
            
            col = layout.column(align=True)
            col.operator("manutools.checker_collapse_loop", icon='EDGESEL')
            col = layout.column(align=True)
            col.operator("manutools.checker_dissolve_ring", icon='SNAP_EDGE')

            