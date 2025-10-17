from .collapse_checker import *
from .dissolve_checker import *
from .id_color import *
from .shape_key_manager import *
from .origin_edit import *
from .renamer_lowpoly import *
from .swap_names import *
from .select_faceset import *

def register():
    collapse_checker_register()
    dissolve_checker_register()
    id_color_register()
    shape_key_manager_register()
    origin_edit_register()
    renamer_lowpoly_register()
    swap_names_register()   
    select_faceset_register()   

def unregister():
    select_faceset_unregister()
    swap_names_unregister()
    renamer_lowpoly_unregister()
    origin_edit_unregister()
    shape_key_manager_unregister()
    id_color_unregister()
    dissolve_checker_unregister()
    collapse_checker_unregister()
