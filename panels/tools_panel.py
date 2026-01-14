import bpy

class MANUTOOLS_PT_ToolsPanel(bpy.types.Panel):
    bl_label = "Modeling Tools"
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

        box = layout.box()
        row = box.row()
        # Mostra sempre alcuni tool, anche in Object mode
        row.label(text="Origin Tools", icon="KEYTYPE_MOVING_HOLD_VEC")
        
        col = box.column(align=True)
        col.operator("manutools.set_origin_to_base", icon='AXIS_TOP')
        col.operator("manutools.snap_mesh_to_grid", icon='GRID')
       
        if context.mode == 'EDIT_MESH':
            col.operator("manutools.set_origin_to_selection", icon='PIVOT_MEDIAN')



        # Sezione Modifiers (sempre visibile per mesh)
        box = layout.box()
        row = box.row()
        row.label(text="Modifiers", icon="MODIFIER")

        col = box.column(align=True)
        col.operator("manutools.add_bevel_modifier", icon='MOD_BEVEL')

        # Mostra solo in modalità Edit
        if context.mode == 'EDIT_MESH':

            box = layout.box()
            row = box.row()
            row.label(text="Collapse Tools", icon="KEYTYPE_JITTER_VEC")

            col = box.column(align=True)
            col.operator("manutools.checker_collapse_loop", icon='EDGESEL')
            col.operator("manutools.checker_dissolve_ring", icon='SNAP_EDGE')

