from src.pysd.statements import (
    DESEC, RFILE, SHAXE, LOADC, GRECO, FILST, BASCO, LoadCase,
    RETYP, DECAS, RELOC, EXECD, LORES, CMPEC, SHSEC, XTFIL,
    TABLE, RMPEC, CaseBuilder, Cases, HEADING, DEPAR
)
from src.pysd import SD_BASE, ValidationLevel
from src.pysd.helpers import create_axes_based_on_3_points_in_plane
from shapely.geometry import Point

# Note: Global validation mode configuration is no longer needed
# Validation is now controlled per-model via SD_BASE constructor parameters



def create_basic_model_components(sd_model: SD_BASE) -> None:
    """
    Create and add basic model components like FILST and RFILE.
    
    Args:
        sd_model: The SD_BASE model to add components to
    """
    # Add FILST entry
    filst_entry = FILST(
        name="aquapod",
        vers="1.0",
        date="14.aug-2025",
        resp="som"
    )
    sd_model.add(filst_entry)

    #Add RFILE entry
    rfile_definition = RFILE(
        pre=r"C:\Users\nx74\Work\ShellDesign\AquaPod_09\Analyse_file",
        fnm="R1",
        suf="SIN",
        typ="SHE",
    )
    sd_model.add(rfile_definition)

def create_design_sections(sd_model: SD_BASE) -> None:
    """
    Create design sections and axes related design sections.
    """

    #set number on R1.SIN
    # veg_intern_s_e,veg_intern_w,veg_intern_t,vegg_ytre_e,vegg_ytre_n,vegg_ytre_s_e,vegg_ytre_s_w,vegg_ytre_w
    vegg:list[int]=[2,3,4,5,6,7,8,9]
    plate:int=3

    #points in casion used used to define axes.
    p1=Point(-4.9,-2.2,-1.05)
    p2=Point(0.0,-1.6,-1.05)
    p3=Point(4.9,-2.2,-1.05)
    p4=Point(-4.9,-2.2,0.85) 
    p5=Point(4.9,-2.2,0.85) 
    p6=Point(-6,1.6,-1.05)
    p7=Point(6,1.6,-1.05)
    p8=Point(0.0,-1.6,0.85)

    p9=Point(-4.614273,-2.16501302,-0.95)
    p10=Point(4.614273,-2.16501302,-0.95)
    p11=Point(6,1.6,0.85)


    def _shaxe_base_point(part:str,p1:Point, p2:Point, p3:Point) -> SHAXE:
        """private function helping to create SHAXE statement"""
        v1, v2, v3 = create_axes_based_on_3_points_in_plane(p1, p2, p3)
        return SHAXE(pa=part, x1=v1, x2=v2, x3=v3,hs=(1,4))
   
    sd_model.add(SHSEC(pa="PLATE",elset=plate,hs=(1,4)))
   
    sd_model.add(SHAXE( pa="PLATE", x1=(1,0,0),x2=(0,1,0),x3=(0,0,1) ))
    
    for counter,set_number in enumerate(vegg):
        sd_model.add(SHSEC(pa=f"VEGG_{set_number}",elset=set_number,hs=(1+4*counter,4+4*counter)))
     #veg_intern_s_e
    sd_model.add(_shaxe_base_point("VEGG_2", p2, p10, p8))
     #veg_intern_w
    sd_model.add(_shaxe_base_point("VEGG_3", p2, p9, p8))
    sd_model.add(SHAXE(pa="VEGG_4",hs=(1,4),x1=(0,1,0),x2=(0,0,1),x3=(1,0,0)))  
    sd_model.add(_shaxe_base_point("VEGG_5", p7, p3, p11))
    sd_model.add(SHAXE(pa="VEGG_6",hs=(1,4),x1=(1,0,0),x2=(0,0,1),x3=(0,1,0)))
    #7
    sd_model.add(_shaxe_base_point("VEGG_7", p3, p2, p5))
    sd_model.add(_shaxe_base_point("VEGG_8", p2, p1, p8))
    sd_model.add(_shaxe_base_point("VEGG_9", p1, p6, p4))






def create_load_components(sd_model: SD_BASE) -> None:
    """
    Create and add load-related components like LOADC and BASCO.
    """
    
    # Create and add LOADC entries first
    loadc = [
        LOADC(run_number=1, alc=(1,6), olc=(201,206)),
        LOADC(run_number=1, alc=(11,16), olc=(101,106)),
        LOADC(table=True),
        LOADC(pri=True)
    ]
    sd_model.add(loadc)

    # Add LORES entries 
    sd_model.add(LORES(pri_alc=True))  # This generates: LORES PRI=ALC
    sd_model.add(LORES(sin=True))      # This generates: LORES SIN=

    # Add BASCO entries BEFORE GRECO (to satisfy references)
    # First add basco's for greco (211-216)
    for i in range(6):
        load_cases = [LoadCase(lc_type='OLC', lc_numb=101+i, lc_fact=1) ]
        basco = BASCO(id=211+i, load_cases=load_cases)
        sd_model.add(basco)

     # Now add GRECO statement (after BASCO statements it references)
    greco_support = GRECO(
        id='A',
        bas=Cases(ranges=[(211, 216)])
    )
    sd_model.add(greco_support)    
    
    # Create and add more BASCO entries (101-102)  
    load_cases = [
        LoadCase(lc_type='ELC', lc_numb=i+101, lc_fact=1.5)
        for i in range(6)
    ]

    load_cases2 = [
        LoadCase(lc_type='ELC', lc_numb=i+101, lc_fact=1.8)
        for i in range(6)
    ]

    sd_model.add( HEADING(bas_id="101", description="Form Coupled"))
    basco = BASCO(id=101, load_cases=load_cases)
    sd_model.add(basco)
    basco = BASCO(id=102, load_cases=load_cases2)
    sd_model.add(basco)
    
   

def create_material_components(sd_model: SD_BASE) -> None:
    """
    Create and add material-related components like CMPEC, RMPEC, and DEPAR.
    
    """
    # Add design parameters
    depar = DEPAR(
        n_lay=10,      # Number of integration layers through shell thickness
        d_sig=10.0,    # Maximum stress deviation before iteration stops
        d_cod="NS"     # Norwegian standard design code
    )
    sd_model.add(depar)
    
    # Add material properties concrete
    cmpec = CMPEC(id=1, gr="B35")
    sd_model.add(cmpec)

    # Add material properties reinforcement
    rmpec = RMPEC(id=1, gr="500")
    sd_model.add(rmpec)


def create_reinforment_components(sd_model: SD_BASE) -> None:
    """
    Create and add reinforcement-related components.
    """
    # Example of creating a reinforcement type
    sd_model.add( HEADING(statement="Reinforcement types", description="Defining reinforcement types used in the model", comment="Generated by PySD"))
    sd_model.add( RETYP(id=1, mp=1, ar=753.0E-6 , c2=0.055, th=0.014, di=0.012, nr=1, lb="1.0D12_c150"))
    sd_model.add( RETYP(id=2, mp=1, ar=753.0E-6 , os=0.0, th=0.014, di=0.012, nr=1, lb="1.0D12_c150"))

    
    slabs=["PLATE"]
    vegg_parts = ["VEGG_2", "VEGG_3", "VEGG_4", "VEGG_5", "VEGG_6", "VEGG_7", "VEGG_8", "VEGG_9"]
    
    # Add reinforcement for all VEGG parts
    for i, vegg_part in enumerate(vegg_parts):
        sd_model.add(RELOC(id="X12", pa=vegg_part, rt=1, fa=1, al=0))
        sd_model.add(RELOC(id="Y01", pa=vegg_part, rt=2, fa=0, al=90))
        sd_model.add(RELOC(id="X22", pa=vegg_part, rt=1, fa=2, al=0))

    # Add reinforcement for slabs
    for slab in slabs:
        sd_model.add(RELOC(id="Y12", pa=slab, rt=1, fa=1, al=90))
        sd_model.add(RELOC(id="X01", pa=slab, rt=2, fa=0, al=0))
        sd_model.add(RELOC(id="Y22", pa=slab, rt=1, fa=2, al=90))

def create_analysis_components(sd_model: SD_BASE) -> None:
    """
    Create and add analysis-related components like DECAS.
    
    """
    # select the design section to be checked
    parts = ["VEGG_2", "PLATE"]
    for part in parts:
        sd_model.add(DESEC(pa=part))
    

    # select the design load cases to be checked
    # Add DECAS using tuple format with greco
    #sd_model.add(DECAS(ls='ULS', bas=(101,102), greco='A'))
    sd_model.add(DECAS(ls='ULS', bas=(101,102), greco='A'))

    # Add DECAS using string represtation of the load case
    #sd_model.add(DECAS(ls='ULS', bas="400-409"))
    
    # xtract ploting data
  
    for part in parts:
        sd_model.add(XTFIL(fn="AquaPod_09", pa=part, fs=(1,9999),hs=(1,99)))

    # Add table for printing
    sd_model.add(TABLE(tab="GE"))
    sd_model.add(TABLE(tab="AX"))
    sd_model.add(TABLE(tab="DR",pa="PLATE", fs=1, hs=1))
    sd_model.add(TABLE(tab="DR",pa="VEGG_2", fs=1, hs=1))
    sd_model.add(TABLE(tab="EC",pa="VEGG_2", fs=1, hs=1))

    # Add final execution directive
    sd_model.add(EXECD(dm='V'))
    
     

def main(output_file: str = r"turtorial.inp") -> None:
    """
    Main function to create and write the model.
    """
    print(f"Building model to be written to {output_file}...")
    
    # NEW SIMPLIFIED API: No context managers, no manual validation management
    model = SD_BASE(validation_level=ValidationLevel.NORMAL, cross_object_validation=True)
    
    # Create all model components in a structured way
    create_basic_model_components(model)

    # Create load components (BASCO needed by GRECO)
    create_load_components(model)

    # Create design sections
    create_design_sections(model)
        
    # Create materials first (needed by RETYP)
    create_material_components(model)
    
    # Create reinforcement types (needed by RELOC)  
    create_reinforment_components(model)
    
    # Create analysis components last
    create_analysis_components(model)
    
    
    
    
    # CLEAN AND SIMPLE: Just call write()
    model.write(output_file)
    print(f"Model successfully written to {output_file}")

if __name__ == "__main__":
    main()

