# Fix OMP perfmance issue on ARM platform (Jetson)
import os
import platform

if platform.machine().startswith("aarch64"):
    os.environ["OMP_NUM_THREADS"] = "1"

# ====== Conda environment check ======
_REQUIRED_CONDA_ENV = "robojudo_sar"
_current_env = os.environ.get("CONDA_DEFAULT_ENV", "")
if _current_env and _current_env != _REQUIRED_CONDA_ENV:
    import warnings
    warnings.warn(
        f"Expected conda environment '{_REQUIRED_CONDA_ENV}', "
        f"but '{_current_env}' is active. "
        f"Run: conda activate {_REQUIRED_CONDA_ENV}"
    )
elif not _current_env:
    # Not running inside any conda env - common on bare Python or container
    pass
# ====================================

# Fix libgomp issue on ARM platform (Jetson)
import torch  # noqa: F401, I001
import numpy  # noqa: F401, I001
import scipy.spatial.transform.rotation  # noqa: F401, I001

# load all packages
import robojudo.config  # ensure configs are registered first  # noqa: E402, F401, I001

import robojudo.controller  # ensure controllers are registered  # noqa: E402, F401, I001
import robojudo.environment  # ensure environments are registered  # noqa: E402, F401, I001
import robojudo.pipeline  # ensure pipelines are registered  # noqa: E402, F401, I001
import robojudo.policy  # ensure policies are registered  # noqa: E402, F401, I001

# Initialize the global logger
from robojudo.utils.logger import setup_logger  # noqa: E402, I001

logger = setup_logger()

# Print version info
__version__ = "1.5.0"
logger.debug(f"{'=' * 10} robojudo-{__version__} init done {'=' * 10}\n")
