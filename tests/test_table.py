import sys
sys.path.append('C:\\Users\\som\\coding\\PySD\\src')
from pysd.statements import TABLE

def test_table_simple():
    """Test the TABLE statements from main.py"""
    table1 = TABLE(tab="GE")
    assert table1.input == "TABLE TAB=GE"

    table2 = TABLE(tab="AX")
    assert table2.input == "TABLE TAB=AX"

    table3 = TABLE(tab="DR",pa="PLATE", fs=1, hs=1)
    assert table3.input == "TABLE TAB=DR PA=PLATE FS=1 HS=1"

    table4 = TABLE(tab="DR",pa="VEGG_2", fs=1, hs=1)
    assert table4.input == "TABLE TAB=DR PA=VEGG_2 FS=1 HS=1"

    table5 = TABLE(tab="EC",pa="VEGG_2", fs=1, hs=1)
    assert table5.input == "TABLE TAB=EC PA=VEGG_2 FS=1 HS=1"
