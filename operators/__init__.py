from .collapse_checker import *
from .dissolve_checker import *
from .id_color import *
from .transfer_shapekeys import *
from .origin_edit import *
from .dev_reloader import *
from .renamer_lowpoly import *
from .swap_names import *
from .select_faceset import *

def register():
    collapse_checker_register()
    dissolve_checker_register()
    id_color_register()
    transfer_shapekeys_register()
    origin_edit_register()
    dev_reloader_register()
    renamer_lowpoly_register()
    swap_names_register()   
    select_faceset_register()   

def unregister():
    select_faceset_unregister()
    swap_names_unregister()
    renamer_lowpoly_unregister()
    dev_reloader_unregister()
    origin_edit_unregister()
    transfer_shapekeys_unregister()
    id_color_unregister()
    dissolve_checker_unregister()
    collapse_checker_unregister()
