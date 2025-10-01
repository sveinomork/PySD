from pysd.statements import INPLC


def test_inplc_basic():
    """Test the INPLC statement with basic section ranges"""
    inplc = INPLC(id="1",n1=1,n2=2.2,n12=3,m1=4,m2=5,m12=6)
    print(inplc.input)
    assert inplc.input == "INPLC ID=1 N1=1 N2=2.2 N12=3 M1=4 M2=5 M12=6"


if __name__ == "__main__":
    test_inplc_basic()
    print("All tests passed.")