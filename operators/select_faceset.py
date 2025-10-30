import bpy
from bpy.types import Operator

class MESH_OT_select_linked_face_set(Operator):
    """Select all faces in the same Face Set"""
    bl_idname = "mesh.select_linked_face_set"
    bl_label = "Select Linked Face Set"
    bl_options = {'REGISTER', 'UNDO'}
    
    mode: bpy.props.EnumProperty(
        name="Mode",
        items=[
            ('SELECT', "Select", "Select Face Set"),
            ('ADD', "Add", "Add Face Set to selection"),
            ('SUBTRACT', "Subtract", "Remove Face Set from selection"),
        ],
        default='SELECT'
    )

    @classmethod
    def poll(cls, context):
        return (context.mode == 'EDIT_MESH' and 
                context.active_object and 
                context.active_object.type == 'MESH')

    def invoke(self, context, event):
        obj = context.active_object
        mesh = obj.data
        
        # Check if Face Sets exist
        if not mesh.attributes.get('.sculpt_face_set'):
            self.report({'WARNING'}, "No Face Sets found on this object")
            return {'CANCELLED'}
        
        # Store current selection for ADD and SUBTRACT modes
        if self.mode in ('ADD', 'SUBTRACT'):
            bpy.ops.object.mode_set(mode='OBJECT')
            stored_selection = [poly.select for poly in mesh.polygons]
            bpy.ops.object.mode_set(mode='EDIT')
        
        # Select face under mouse cursor
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.view3d.select(
            extend=False,
            location=(event.mouse_region_x, event.mouse_region_y)
        )
        
        # Execute selection logic
        result = self.execute(context)
        
        # Restore and modify selection for ADD and SUBTRACT modes
        if result == {'FINISHED'} and self.mode in ('ADD', 'SUBTRACT'):
            bpy.ops.object.mode_set(mode='OBJECT')
            face_set_layer = mesh.attributes['.sculpt_face_set'].data
            
            # Find Face Set IDs from picked face
            picked_face_set_ids = set()
            for poly in mesh.polygons:
                if poly.select:
                    picked_face_set_ids.add(face_set_layer[poly.index].value)
            
            # Apply mode
            for i, poly in enumerate(mesh.polygons):
                if face_set_layer[poly.index].value in picked_face_set_ids:
                    if self.mode == 'ADD':
                        poly.select = True
                    elif self.mode == 'SUBTRACT':
                        poly.select = False
                else:
                    poly.select = stored_selection[i]
            
            bpy.ops.object.mode_set(mode='EDIT')
        
        return result

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
        if self.mode == 'SELECT':
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
    bpy.types.VIEW3D_MT_edit_mesh_select_linked.append(menu_func)
    
    # Controlla se shortcuts sono abilitate
    try:
        addon_name = __name__.split('.')[0]
        prefs = bpy.context.preferences.addons[addon_name].preferences
        if not prefs.enable_faceset_shortcuts:
            return  # Non registrare shortcuts se disabilitati
    except:
        pass  # Se preferences non disponibili, continua comunque
    
    # Add keybindings con valori custom
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        
        # Ottieni i valori dalle preferences
        try:
            key = prefs.faceset_select_key
            select_mod = prefs.faceset_select_modifier
            add_mod = prefs.faceset_add_modifier
            subtract_mod = prefs.faceset_subtract_modifier
        except:
            # Fallback ai valori di default se preferences non disponibili
            key = 'K'
            select_mod = 'CTRL'
            add_mod = 'SHIFT'
            subtract_mod = 'ALT'
        
        # Select shortcut
        kmi = km.keymap_items.new(
            MESH_OT_select_linked_face_set.bl_idname,
            type=key,
            value='PRESS',
            ctrl=(select_mod == 'CTRL'),
            shift=(select_mod == 'SHIFT'),
            alt=(select_mod == 'ALT')
        )
        kmi.properties.mode = 'SELECT'
        addon_keymaps.append((km, kmi))
        
        # Add to selection shortcut
        kmi = km.keymap_items.new(
            MESH_OT_select_linked_face_set.bl_idname,
            type=key,
            value='PRESS',
            ctrl=(add_mod == 'CTRL'),
            shift=(add_mod == 'SHIFT'),
            alt=(add_mod == 'ALT')
        )
        kmi.properties.mode = 'ADD'
        addon_keymaps.append((km, kmi))
        
        # Subtract from selection shortcut
        kmi = km.keymap_items.new(
            MESH_OT_select_linked_face_set.bl_idname,
            type=key,
            value='PRESS',
            ctrl=(subtract_mod == 'CTRL'),
            shift=(subtract_mod == 'SHIFT'),
            alt=(subtract_mod == 'ALT')
        )
        kmi.properties.mode = 'SUBTRACT'
        addon_keymaps.append((km, kmi))


def select_faceset_unregister():
    # Remove keybindings
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
    
    # Remove from menu
    bpy.types.VIEW3D_MT_edit_mesh_select_linked.remove(menu_func)
    
    bpy.utils.unregister_class(MESH_OT_select_linked_face_set)
















