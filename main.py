from src.pysd.statements import (
    DESEC, RFILE, SHAXE, LOADC, GRECO, FILST, BASCO, LoadCase,
    RETYP, DECAS, RELOC, EXECD, LORES, CMPEC, SHSEC, XTFIL,
    TABLE, RMPEC, CaseBuilder, Cases, HEADING
)
from src.pysd.sdmodel import SD_BASE
from src.pysd.validation import set_validation_mode, ValidationMode
from src.pysd.helpers import create_axes_based_on_3_points_in_plane
from shapely.geometry import Point

# Configure global validation mode for the entire script
# Options: ValidationMode.STRICT, NORMAL, PERMISSIVE, DISABLED
# Set to PERMISSIVE during model building, will validate strictly at the end
set_validation_mode(ValidationMode.PERMISSIVE)









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

    # Add RFILE entry
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
        LOADC(run_number=1, alc=(1,7), olc=(101,107)),
        LOADC(table=True),
        LOADC(pri=True)
    ]
    sd_model.add(loadc)

    # This generates: LORES PRI=ALC
    #sd_model.add(LORES(pri_alc=True))
    # This generates: LORES SIN=
    #sd_model.add(LORES(sin=True))

    # Add BASCO entries BEFORE GRECO (to satisfy references)
    # First add basco's for greco (211-216)
    for i in range(6):
        load_cases = [LoadCase(lc_type='OLC', lc_numb=201+i, lc_fact=1) ]
        basco = BASCO(id=211+i, load_cases=load_cases)
        sd_model.add(basco)
    
    # Create and add more BASCO entries (101-102)  
    load_cases = [
        LoadCase(lc_type='ELC', lc_numb=i, lc_fact=1.5)
        for i in range(101, 107)
    ]

    load_cases2 = [
        LoadCase(lc_type='ELC', lc_numb=i, lc_fact=1.8)
        for i in range(101, 107)
    ]

    sd_model.add( HEADING(bas_id="101", description="Form Coupled"))
    basco = BASCO(id=101, load_cases=load_cases)
    sd_model.add(basco)
    basco = BASCO(id=102, load_cases=load_cases2)
    sd_model.add(basco)
    
    # Now add GRECO statement (after BASCO statements it references)
    greco_support = GRECO(
        id='A',
        bas=Cases(ranges=[(211, 216)])
    )
    sd_model.add(greco_support)

def create_material_components(sd_model: SD_BASE) -> None:
    """
    Create and add material-related components like CMPEC and RETYP.
    
    """
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
        sd_model.add(RELOC(id=f"X1{i+1}", pa=vegg_part, rt=1, fa=1, al=0))
        sd_model.add(RELOC(id=f"Y0{i+1}", pa=vegg_part, rt=2, fa=0, al=90))
        sd_model.add(RELOC(id=f"X2{i+1}", pa=vegg_part, rt=1, fa=2, al=0))

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
    # Import validation context managers here if you want to use them
    # from src.pysd.validation import permissive_validation, no_validation
   
    print(f"Building model to be written to {output_file}...")
    
    # Import here to get the current validation mode
    from src.pysd.validation.core import get_validation_mode
    current_mode = get_validation_mode()
    print(f"Current validation mode: {current_mode}")  # Shows actual current setting
    
    with SD_BASE.create_writer(output_file) as sd_model:
        # Create all model components in a structured way
        
        # Use strict validation for critical components (default behavior)
        create_basic_model_components(sd_model)
        
        # Create materials first (needed by RETYP)
        create_material_components(sd_model)
        
        # Create reinforcement types (needed by RELOC)  
        create_reinforment_components(sd_model)
        
        # For experimental or optional sections, you can use:
        # with permissive_validation():
        create_design_sections(sd_model)
        
        # Create load components (BASCO needed by GRECO)
        create_load_components(sd_model)
        
        # Create analysis components last
        create_analysis_components(sd_model)
        
        # Now perform final strict validation on the complete model
        print("🔍 Performing final strict validation on complete model...")
        set_validation_mode(ValidationMode.STRICT)
        
        # Trigger final validation by calling validate_complete_model
        try:
            sd_model.validate_complete_model()
            print("✅ Final strict validation passed!")
        except ValueError as e:
            print(f"❌ Final strict validation failed:\n{e}")
            # Reset to permissive to allow model output
            set_validation_mode(ValidationMode.PERMISSIVE)
        
        # Get validation summary after model creation
        summary = sd_model.get_validation_summary()
        print(f"Model created with {summary['total_items']} total items")
        
        # Display validation results
        integrity = summary['integrity_issues']
        
        if summary['has_errors']:
            print("❌ Model has validation errors:")
            for error in integrity['errors']:
                print(f"  ERROR: {error}")
        
        if summary['has_warnings']:
            print("⚠️  Model has validation warnings:")
            for warning in integrity['warnings']:
                print(f"  WARNING: {warning}")
        
        if integrity.get('info'):
            print("ℹ️  Model has validation info:")
            for info in integrity['info']:
                print(f"  INFO: {info}")
        
        if not summary['has_warnings'] and not summary['has_errors']:
            print("✅ Model validation passed")
             
    
    print(f"Model successfully written to {output_file}")

if __name__ == "__main__":
    main()

