# Please always add new modules in this file with 
# ``` from .<module> import * ```
# so all functions are automaticallly imported in the caller's symbol table, when importing this subpackage

from .batch_analysis import *
from .best_devices import *
from .boxplots import *
from .connection_test import *
from .eqe import *
from .helper_functions import *
from .jv import *
from .luqy import *
from .mppt import *
from .plot_matrix import *
from .stability import *
from .test import *
from .update_layout import update_layout_umr
from .uv_vis import *


# Import module to add Plot Template and make it default 
#import ..plottemplate

