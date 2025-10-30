import bpy
import bmesh
import mathutils
from mathutils import Vector

def get_new_origin(obj, position):
    verts = [obj.matrix_world @ v.co for v in obj.data.vertices]
    if position == 'CENTER':
        return sum(verts, mathutils.Vector()) / len(verts)
    elif position == 'BOTTOM':
        min_z = min(v.z for v in verts)
        avg_xy = sum((mathutils.Vector((v.x, v.y, 0)) for v in verts), mathutils.Vector()) / len(verts)
        return mathutils.Vector((avg_xy.x, avg_xy.y, min_z))
    else:
        return obj.location


class SetOrigintoSelection(bpy.types.Operator):
    """Set origin to selection median (without moving 3D Cursor)"""
    bl_idname = "manutools.set_origin_to_selection"
    bl_label = "Set Origin to Selection Median"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        obj = context.edit_object
        mesh = bmesh.from_edit_mesh(obj.data)

        selected_verts = [v.co.copy() for v in mesh.verts if v.select]

        if not selected_verts:
            self.report({'WARNING'}, "No selection found.")
            return {'CANCELLED'}

        median_local = sum(selected_verts, Vector()) / len(selected_verts)
        median_world = obj.matrix_world @ median_local
        delta = median_world - obj.matrix_world.translation

        bpy.ops.object.mode_set(mode='OBJECT')

        delta_local = obj.matrix_world.inverted_safe().to_3x3() @ delta

        for v in obj.data.vertices:
            v.co -= delta_local

        obj.location += delta

        bpy.ops.object.mode_set(mode='EDIT')

        self.report({'INFO'}, "Origin set to selection.")
        return {'FINISHED'}





class SnaptoGrid(bpy.types.Operator):
    """Snap mesh to grid (visual geometry)"""
    bl_idname = "manutools.snap_mesh_to_grid"
    bl_label = "Snap Mesh to Grid"
    bl_options = {'REGISTER', 'UNDO'}

    was_in_edit: bool = False

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def execute(self, context):
        obj = context.object

        # Passa a Object Mode se necessario
        self.was_in_edit = (context.mode == 'EDIT_MESH')
        if self.was_in_edit:
            bpy.ops.object.mode_set(mode='OBJECT')

        # Ottieni la mesh valutata (post-modificatori)
        depsgraph = context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        mesh_eval = obj_eval.to_mesh()

        # Trova la z minima dei vertici valutati in spazio mondo
        verts_world = [obj_eval.matrix_world @ v.co for v in mesh_eval.vertices]
        min_z = min(v.z for v in verts_world)

        # Libera la mesh valutata
        obj_eval.to_mesh_clear()

        # Offset da applicare in spazio mondo
        offset_world = mathutils.Vector((0, 0, -min_z))

        # Se l'oggetto è parentato, trasforma in spazio locale
        if obj.parent:
            offset_local = obj.parent.matrix_world.inverted() @ (obj.matrix_world.translation + offset_world) - obj.location
        else:
            offset_local = offset_world

        # Applica lo spostamento
        obj.location += offset_local

        # Torna in Edit Mode se necessario
        if self.was_in_edit:
            bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}




class SetOrigintoBase(bpy.types.Operator):
    """Set origin to base or center of the mesh (modifiers supported, returns to Edit Mode, preserves 3D Cursor)"""
    bl_idname = "manutools.set_origin_to_base"
    bl_label = "Set Origin to Base"
    bl_options = {'REGISTER', 'UNDO'}

    pivot_type: bpy.props.EnumProperty(
        name="Pivot Type",
        items=[
            ('CENTER', "Center", ""),
            ('BOTTOM', "Base", ""),
        ],
        default='BOTTOM'
    )

    @classmethod
    def poll(cls, context):
        return context.object is not None and context.object.type == 'MESH'

    def get_new_origin(self, obj, pivot_type):
        depsgraph = bpy.context.evaluated_depsgraph_get()
        obj_eval = obj.evaluated_get(depsgraph)
        mesh_eval = obj_eval.to_mesh()

        verts_world = [obj_eval.matrix_world @ v.co for v in mesh_eval.vertices]

        min_coord = mathutils.Vector((min(v.x for v in verts_world),
                                      min(v.y for v in verts_world),
                                      min(v.z for v in verts_world)))
        max_coord = mathutils.Vector((max(v.x for v in verts_world),
                                      max(v.y for v in verts_world),
                                      max(v.z for v in verts_world)))
        center = (min_coord + max_coord) / 2

        if pivot_type == 'BOTTOM':
            center.z = min_coord.z

        obj_eval.to_mesh_clear()
        return center

    def execute(self, context):
        obj = context.object
        was_in_edit = (context.mode == 'EDIT_MESH')

        # Salva la posizione originale del 3D Cursor
        original_cursor = context.scene.cursor.location.copy()

        new_origin = self.get_new_origin(obj, self.pivot_type)

        # Passa temporaneamente a Object Mode
        if was_in_edit:
            bpy.ops.object.mode_set(mode='OBJECT')

        # Crea un empty temporaneo all'origine desiderata
        bpy.ops.object.empty_add(type='PLAIN_AXES', location=new_origin)
        empty = bpy.context.object

        # Sposta il cursore solo temporaneamente
        context.scene.cursor.location = empty.location

        # Imposta origine all'oggetto
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CURSOR')

        # Rimuove l'empty
        bpy.data.objects.remove(empty)

        # Ripristina la posizione originale del cursore
        context.scene.cursor.location = original_cursor

        # Torna in Edit Mode se era attivo prima
        if was_in_edit:
            bpy.ops.object.mode_set(mode='EDIT')

        return {'FINISHED'}

    def invoke(self, context, event):
        # AGGIUNGI QUESTO ✨
        try:
            prefs = context.preferences.addons['ManuTools'].preferences
            self.pivot_type = prefs.snap_to_grid_mode
        except:
            pass
        
        return self.execute(context) 



classes = (
    SetOrigintoSelection,
    SnaptoGrid,
    SetOrigintoBase,
)

def origin_edit_register():
    for cls in classes:
        bpy.utils.register_class(cls)

def origin_edit_unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
