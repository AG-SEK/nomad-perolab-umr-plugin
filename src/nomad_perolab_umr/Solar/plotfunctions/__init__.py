# Please always add new modules in this file with 
# ``` from .<module> import * ```
# so all functions are automaticallly imported in the caller's symbol table, when importing this subpackage

from .update_layout import update_layout_umr
from .jv import *
from .eqe import *
from .connection_test import *
from .mppt import *
from .uv_vis import *
from .stability import *

from .batch_analysis import *
from .helper_functions import *
from .plot_matrix import *
from .boxplots import *
from .best_devices import *
from .luqy import *
from .test import *


# Import module to add Plot Template and make it default 
#import ..plottemplate

