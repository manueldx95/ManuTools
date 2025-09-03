import bpy
import bmesh
from bpy.props import IntProperty, BoolProperty

class DissolveCheckerRing(bpy.types.Operator):
    bl_idname = "manutools.checker_dissolve_ring"
    bl_label = "Dissolve Ring"
    bl_options = {'REGISTER', 'UNDO'}

    skip: IntProperty(name="Skip", default=1, min=0)
    nth: IntProperty(name="Select", default=1, min=1)
    offset: IntProperty(name="Offset", default=0)
    use_loop: BoolProperty(name="Use Multi Select Loop", default=True)

    _initial_selected_indices = []

    def execute(self, context):
        obj = context.object
        if obj and obj.type == 'MESH' and context.mode == 'EDIT_MESH':
            bm = bmesh.from_edit_mesh(obj.data)
            selected_edges = [e for e in bm.edges if e.select]
            if not selected_edges:
                self.report({'WARNING'}, "No edge selected.")
                return {'CANCELLED'}
            self._initial_selected_indices = [e.index for e in selected_edges]

            bpy.ops.mesh.loop_multi_select(ring=True)
            bpy.ops.mesh.select_nth(skip=self.skip, nth=self.nth, offset=self.offset)

            if self.use_loop:
                bpy.ops.mesh.loop_multi_select(ring=False)

            bpy.ops.mesh.dissolve_mode(use_verts=True)
            return {'FINISHED'}
        else:
            self.report({'WARNING'}, "Select a mesh in Edit Mode.")
            return {'CANCELLED'}

def dissolve_checker_register():
    bpy.utils.register_class(DissolveCheckerRing)

def dissolve_checker_unregister():
    bpy.utils.unregister_class(DissolveCheckerRing)
