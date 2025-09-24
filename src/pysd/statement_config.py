"""
Simple statement registry - just data, no complex logic.
"""

# Simple list of statements - add new ones here
STATEMENT_CLASSES = [
    'GRECO', 'BASCO', 'LOADC', 'SHSEC', 'SHAXE', 'DESEC',
    'CMPEC', 'RMPEC', 'RETYP', 'SRTYP', 'RELOC', 'DECAS', 
    'DEPAR', 'LORES', 'TABLE', 'XTFIL', 'RFILE', 'FILST', 
    'INCDF', 'HEADL', 'EXECD', 'HEADING'
]

# Non-statement classes that need to be exported
UTILITY_CLASSES = ['Cases', 'CaseBuilder', 'normalize_cases', 'LoadCase']

# All exports
ALL_STATEMENTS = STATEMENT_CLASSES + UTILITY_CLASSES

