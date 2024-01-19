from pathlib import Path
from enum import Enum

REPOSITORY_ROOT = (Path(__file__).parent / '..' / '..').resolve()

class DataDirectories(Enum):
    ROOT    : Path = REPOSITORY_ROOT / 'data'
    ONE     : Path = ROOT / '1_initial'
    TWO     : Path = ROOT / '2_intermediate'
    THREE   : Path = ROOT / '3_processed'
    FOUR    : Path = ROOT / '4_final'
    FIVE    : Path = ROOT / '5_content'

class Exams(Enum):
    ENEM = 'Enem'
    FUVEST = 'Fuvest'

class EssaysConfig(Enum):
    YEAR            : str   = '2022'
    REVISION_DIR    : str   = 'revisao'
    NO_REVISION_DIR : str   = 'pronto'
    ASPECT_RATIO    : dict[str, float] = {
        'enem'  : 0.74,
        'fuvest': 0.705,
    }
    THRESHOLD       : dict[str, float] = {
        'enem'  : 0.025,
        'fuvest': 0.010,
    }
    NORMALIZED_CROP_HEIGHT:dict[str, float] = {
        'enem'  : 0.1977,
        'fuvest': 0.1465,
    }
