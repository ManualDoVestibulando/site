import os
import sys

sys.stdout = open(os.devnull, 'w')
try:
    from mdv.notebooks import a_parse_forms
    # from mdv.notebooks import b_parse_essays
except:
    raise Exception('Execution failed')
finally:
    sys.stdout.close()
    sys.stdout = sys.__stdout__
