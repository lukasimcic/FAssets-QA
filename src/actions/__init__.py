from .mint import *
from .redeem import *
from .pool import *
from .scenarios import *
from .bridge import *
from .action_bundle import ActionBundle

def all_subclasses(cls):
    return set(
        c for c in cls.__subclasses__() if not c.__name__.startswith("_")
    ).union(
        [s for c in cls.__subclasses__() for s in all_subclasses(c) if not s.__name__.startswith("_")]
    )

ACTION_BUNDLE_CLASSES : set[type[ActionBundle]] = all_subclasses(ActionBundle)