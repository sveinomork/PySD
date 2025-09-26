
from pysd.statements.shext import SHEXT

def test_shext_basic():
    """
     
     SHEXT(pa="WY2",efs=(1,4,3,2),hs=1,xp=(-31.6,0,0),xa=(-1,0,0))
     → 'SHEXT PA=WY2 EF=1,4,3,2 HS=1 XP=-31.6,0,0 XA=-1,0,0'
    
    """
    shext = SHEXT(pa="WY2", efs=(1,4,3,2), hs=1, xp=(-31.6,0,0), xa=(-1,0,0))
    print(shext.input)
    assert shext.input == 'SHEXT PA=WY2 EF=1,4,3,2 HS=1 XP=-31.6,0,0 XA=-1,0,0'

if __name__ == "__main__":
    test_shext_basic()
    print("All tests passed.")