from dataclasses import dataclass, field
from typing import Optional


@dataclass
class FILST:
    """
    Represents the FILST statement for providing file status information.

    This can be used to define a new file status entry or to print all
    existing FILST entries.

    Purpose:
    --------
    Give file status for input files. The status will be printed at the end
    of the ShellDesign output file.

    Modes:
    ------
    1. Define a new entry by providing 'name'. Other parameters are optional.
       Example: FILST(name="RETYP_Lower_domes", vers="1.0", date="8jan-94", resp="kf")

    2. Print all entries by setting 'pri' to True.
       Example: FILST(pri=True)

    Parameters:
    -----------
    name : Optional[str]
        File identity (max 48 characters). Required for new entries.

    vers : Optional[str]
        File version (max 8 characters).

    date : Optional[str]
        Date of last revision (max 12 characters).

    resp : Optional[str]
        Responsible person/group (max 4 characters).

    pri : bool
        If True, prints all current FILST lines. Mutually exclusive with
        other parameters. Default is False.
    """
    name: Optional[str] = "sd"
    vers: Optional[str] = None
    date: Optional[str] = None
    resp: Optional[str] = None
    pri: bool = False
    input: str = field(init=False, default="FILST")

    def __post_init__(self):
        # Validation
        if self.pri and any([self.name, self.vers, self.date, self.resp]):
            raise ValueError("When 'pri' is True, no other parameters should be set.")
        if not self.pri and self.name is None:
            raise ValueError("'name' is required unless 'pri' is True.")

        if self.name and len(self.name) > 48: raise ValueError("NAME cannot exceed 48 characters.")
        if self.vers and len(self.vers) > 8: raise ValueError("VERS cannot exceed 8 characters.")
        if self.date and len(self.date) > 12: raise ValueError("DATE cannot exceed 12 characters.")
        if self.resp and len(self.resp) > 4: raise ValueError("RESP cannot exceed 4 characters.")

        # Build input string
        parts = ["FILST"]
        if self.pri:
            parts.append("PRI=")
        else:
            # The 'name' is mandatory in this case, validation already checked this.
            parts.append(f"NAME={self.name}")
            if self.vers is not None:
                parts.append(f"VERS={self.vers}")
            if self.date is not None:
                parts.append(f"DATE={self.date}")
            if self.resp is not None:
                parts.append(f"RESP={self.resp}")

        self.input = " ".join(parts)

    def __str__(self) -> str:
        return self.input