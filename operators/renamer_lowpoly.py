import bpy
import bmesh
from mathutils import Vector
import re

def get_object_center(obj):
    """Ottiene il centro geometrico dell'oggetto"""
    if obj.bound_box:
        # Calcola il centro della bounding box
        bbox = obj.bound_box
        center = Vector((
            (bbox[0][0] + bbox[6][0]) / 2,
            (bbox[0][1] + bbox[6][1]) / 2,
            (bbox[0][2] + bbox[6][2]) / 2
        ))
        # Trasforma in coordinate mondo
        return obj.matrix_world @ center
    else:
        return obj.location

def get_bounding_box_volume(obj):
    """Calcola il volume della bounding box"""
    if not obj.bound_box:
        return 0
    
    dimensions = obj.dimensions
    return dimensions.x * dimensions.y * dimensions.z

def get_vertex_count(obj):
    """Ottiene il numero di vertici di una mesh"""
    if obj.type != 'MESH':
        return 0
    
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    vertex_count = len(bm.verts)
    bm.free()
    return vertex_count

def find_matching_hp(lp_obj, potential_hp_objects, max_distance=5.0):
    """Trova l'HP corrispondente per un oggetto LP"""

    prefs = bpy.context.preferences.addons['manutools'].preferences
    lp_suffix = prefs.lowpoly_suffix
    hp_suffix = prefs.highpoly_suffix



    lp_center = get_object_center(lp_obj)
    lp_volume = get_bounding_box_volume(lp_obj)
    lp_vertex_count = get_vertex_count(lp_obj)
    
    # Estrae il nome base dell'LP (rimuove _lp)
    lp_base_name = re.sub(rf'{re.escape(lp_suffix)}$', '', lp_obj.name, flags=re.IGNORECASE)
    
    best_match = None
    best_score = float('inf')
    
    for hp_obj in potential_hp_objects:
        if hp_obj == lp_obj:
            continue
            
        # 1. Controllo per naming convention
        hp_base_name = re.sub(rf'{re.escape(hp_suffix)}$', '', hp_obj.name, flags=re.IGNORECASE)
        name_match = lp_base_name.lower() == hp_base_name.lower()
        
        # 2. Controllo distanza
        hp_center = get_object_center(hp_obj)
        distance = (lp_center - hp_center).length
        
        if distance > max_distance:
            continue
            
        # 3. Controllo volume e vertici
        hp_volume = get_bounding_box_volume(hp_obj)
        hp_vertex_count = get_vertex_count(hp_obj)
        
        # L'HP dovrebbe avere più vertici dell'LP
        if hp_vertex_count < lp_vertex_count:
            continue
            
        # Calcola punteggio (più basso = migliore)
        distance_score = distance
        volume_diff = abs(lp_volume - hp_volume) / max(lp_volume, hp_volume) if max(lp_volume, hp_volume) > 0 else 0
        vertex_ratio = hp_vertex_count / max(lp_vertex_count, 1)
        name_bonus = 0 if name_match else 2
        
        score = distance_score + volume_diff + name_bonus + (1 / vertex_ratio)
        
        if score < best_score:
            best_score = score
            best_match = hp_obj
    
    return best_match

def auto_match_lp_hp():
    """Funzione principale per il matching automatico LP-HP"""

    prefs = bpy.context.preferences.addons['manutools'].preferences
    lp_suffix = prefs.lowpoly_suffix


    # Usa solo gli oggetti selezionati
    mesh_objects = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    # Separa LP e HP
    lp_objects = [obj for obj in mesh_objects if obj.name.lower().endswith(lp_suffix.lower())]
    potential_hp_objects = [obj for obj in mesh_objects if not obj.name.lower().endswith(lp_suffix.lower())]
    
    matches = []
    unmatched_lp = []
    
    # Trova i match
    for lp_obj in lp_objects:
        hp_match = find_matching_hp(lp_obj, potential_hp_objects, prefs.max_matching_distance)
        
        if hp_match:
            matches.append((lp_obj, hp_match))
            # Rinomina l'HP seguendo la convenzione
            expected_hp_name = re.sub(rf'{re.escape(lp_suffix)}$', prefs.highpoly_suffix, lp_obj.name, flags=re.IGNORECASE)
            if hp_match.name != expected_hp_name:
                old_name = hp_match.name
                hp_match.name = expected_hp_name
                print(f"Renamed: {old_name} -> {hp_match.name}")
        else:
            unmatched_lp.append(lp_obj)
    
    # Report risultati
    print(f"\n=== MATCHING LP-HP ===")
    print(f"Matches founds: {len(matches)}")
    for lp, hp in matches:
        print(f"  {lp.name} <-> {hp.name}")
    
    if unmatched_lp:
        print(f"\nLP unmatched: {len(unmatched_lp)}")
        for lp in unmatched_lp:
            print(f"  {lp.name}")
    
    return matches, unmatched_lp

# =============================================================================
# OPERATORI
# =============================================================================

class OBJECT_OT_auto_match_lp_hp(bpy.types.Operator):
    bl_idname = "object.auto_match_lp_hp"
    bl_label = "Auto Match LP-HP"
    bl_description = "Automatically find matches between selected Low Poly and High Poly models"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        matches, unmatched = auto_match_lp_hp()
        
        message = f"Matches found: {len(matches)}, Unmatched LP: {len(unmatched)}"
        self.report({'INFO'}, message)
        
        return {'FINISHED'}

class OBJECT_OT_add_lp_suffix(bpy.types.Operator):
    bl_idname = "object.add_lp_suffix"
    bl_label = "Add _lp"
    bl_description = "Add the _lp suffix to selected objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):


        prefs = context.preferences.addons['manutools'].preferences


        selected_objects = bpy.context.selected_objects
        
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        renamed_count = 0
        for obj in selected_objects:
            # VERSIONE CORRETTA ✨
            # Rimuove suffissi esistenti (prima LP, poi HP)
            clean_name = obj.name
            clean_name = re.sub(rf'{re.escape(prefs.lowpoly_suffix)}$', '', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(rf'{re.escape(prefs.highpoly_suffix)}$', '', clean_name, flags=re.IGNORECASE)
            
            new_name = clean_name + prefs.lowpoly_suffix
            
            if obj.name != new_name:
                obj.name = new_name
                renamed_count += 1
        
        self.report({'INFO'}, f"Renamed {renamed_count} objects with {prefs.lowpoly_suffix}")
        return {'FINISHED'}

class OBJECT_OT_add_hp_suffix(bpy.types.Operator):
    bl_idname = "object.add_hp_suffix"
    bl_label = "Add _hp"
    bl_description = "Add the _hp suffix to selected objects"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        prefs = context.preferences.addons['manutools'].preferences
        
        selected_objects = bpy.context.selected_objects
        
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        renamed_count = 0
        for obj in selected_objects:
            # Rimuove suffissi esistenti (prima LP, poi HP)
            clean_name = obj.name
            clean_name = re.sub(rf'{re.escape(prefs.lowpoly_suffix)}$', '', clean_name, flags=re.IGNORECASE)
            clean_name = re.sub(rf'{re.escape(prefs.highpoly_suffix)}$', '', clean_name, flags=re.IGNORECASE)
            
            new_name = clean_name + prefs.highpoly_suffix
            
            if obj.name != new_name:
                obj.name = new_name
                renamed_count += 1
        
        self.report({'INFO'}, f"Renamed {renamed_count} objects with {prefs.highpoly_suffix}")
        return {'FINISHED'}
    
class OBJECT_OT_batch_rename(bpy.types.Operator):
    bl_idname = "object.batch_rename"
    bl_label = "Batch Rename"
    bl_description = "Rename selected objects with progressive numbering"
    bl_options = {'REGISTER', 'UNDO'}
    
    new_name: bpy.props.StringProperty(
        name="New Name",
        description="Base name for the objects",
        default="Object"
    )
    
    def execute(self, context):
        selected_objects = bpy.context.selected_objects
        
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        if not self.new_name.strip():
            self.report({'WARNING'}, "Enter a valid name")
            return {'CANCELLED'}
        
        base_name = self.new_name.strip()
        renamed_count = 0
        
        for i, obj in enumerate(selected_objects, 1):
            # Formato: nome_01, nome_02, ecc.
            new_name = f"{base_name}_{i:02d}"
            obj.name = new_name
            renamed_count += 1

        self.report({'INFO'}, f"Renamed {renamed_count} objects with '{base_name}_XX'")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # Apre un popup per inserire il nome
        return context.window_manager.invoke_props_dialog(self)


def renamer_lowpoly_register():
    bpy.utils.register_class(OBJECT_OT_auto_match_lp_hp)
    bpy.utils.register_class(OBJECT_OT_add_lp_suffix)
    bpy.utils.register_class(OBJECT_OT_add_hp_suffix)
    bpy.utils.register_class(OBJECT_OT_batch_rename)

def renamer_lowpoly_unregister():
    bpy.utils.unregister_class(OBJECT_OT_auto_match_lp_hp)
    bpy.utils.unregister_class(OBJECT_OT_add_lp_suffix)
    bpy.utils.unregister_class(OBJECT_OT_add_hp_suffix)
    bpy.utils.unregister_class(OBJECT_OT_batch_rename)
