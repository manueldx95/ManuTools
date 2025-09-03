from .collapse_checker import *
from .dissolve_checker import *
from .id_color import *
from .transfer_shapekeys import *
from .origin_edit import *
from .dev_reloader import *
from .renamer_lowpoly import *
from .swap_names import *

def register():
    collapse_checker_register()
    dissolve_checker_register()
    id_color_register()
    transfer_shapekeys_register()
    origin_edit_register()
    dev_reloader_register()
    renamer_lowpoly_register()
    swap_names_register()   

def unregister():
    collapse_checker_unregister()
    dissolve_checker_unregister()
    id_color_unregister()
    transfer_shapekeys_unregister()
    origin_edit_unregister()
    dev_reloader_unregister()
    renamer_lowpoly_unregister()
    swap_names_unregister()
