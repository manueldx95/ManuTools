import bpy
from bpy.types import Operator

class MESH_OT_select_linked_face_set(Operator):
    """Select all faces in the same Face Set"""
    bl_idname = "mesh.select_linked_face_set"
    bl_label = "Select Linked Face Set"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH' and 
                context.active_object and 
                context.active_object.type == 'MESH')

    def invoke(self, context, event):
        # Select face under mouse cursor
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.view3d.select(
            extend=False,
            location=(event.mouse_region_x, event.mouse_region_y)
        )
        
        return self.execute(context)

    def execute(self, context):
        obj = context.active_object
        mesh = obj.data
        
        # Check if Face Sets exist
        if not mesh.attributes.get('.sculpt_face_set'):
            self.report({'WARNING'}, "No Face Sets found on this object")
            return {'CANCELLED'}
        
        # Switch to Object Mode temporarily
        bpy.ops.object.mode_set(mode='OBJECT')
        
        face_set_layer = mesh.attributes['.sculpt_face_set'].data
        
        # Find all selected faces and their Face Set IDs
        selected_face_set_ids = set()
        for poly in mesh.polygons:
            if poly.select:
                selected_face_set_ids.add(face_set_layer[poly.index].value)
        
        if not selected_face_set_ids:
            self.report({'WARNING'}, "No face selected")
            bpy.ops.object.mode_set(mode='EDIT')
            return {'CANCELLED'}
        
        # Select all faces with the same Face Set IDs
        for poly in mesh.polygons:
            if face_set_layer[poly.index].value in selected_face_set_ids:
                poly.select = True
        
        # Return to Edit Mode
        bpy.ops.object.mode_set(mode='EDIT')
        
        self.report({'INFO'}, "Face Set selected")
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(MESH_OT_select_linked_face_set.bl_idname, text="Face Sets")

addon_keymaps = []


def select_faceset_register():
    bpy.utils.register_class(MESH_OT_select_linked_face_set)
    
    # Add to Select Linked menu
    bpy.types.VIEW3D_MT_edit_mesh_select_linked.append(menu_func)
    
    # Add keybinding Ctrl + <
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        
        kmi = km.keymap_items.new(
            MESH_OT_select_linked_face_set.bl_idname,
            type='COMMA',
            value='PRESS',
            ctrl=True
        )
        addon_keymaps.append((km, kmi))


def select_faceset_unregister():
    # Remove keybindings
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    # Remove from menu
    bpy.types.VIEW3D_MT_edit_mesh_select_linked.remove(menu_func)
    
    bpy.utils.unregister_class(MESH_OT_select_linked_face_set)














