"""Crime label normalization - standardized across all modules

Migrated from NIBRS_SVA_Dashboard/logic/logic_label_normalization.py
"""

CRIME_MAP = {
    # Assaults
    "Aggravated Assault": "Aggravated Assault",
    "Aggravated_Assault": "Aggravated Assault",
    "Simple Assault": "Simple Assault",
    "Simple_Assault": "Simple Assault",

    # Robbery / Burglary / Theft
    "Robbery": "Robbery",
    "Burglary": "Burglary",
    "Theft": "Theft",

    # Motor Vehicle Theft
    "Motor Vehicle Theft": "Motor Vehicle Theft",
    "Motor_Vehicle_Theft": "Motor Vehicle Theft",

    # Arson
    "Arson": "Arson",

    # Drug / Narcotics
    "Drug/Narcotic Violations": "Drug/Narcotic Violations",
    "Drug_Narcotic Violations": "Drug/Narcotic Violations",
    "Narcotic Violations": "Drug/Narcotic Violations",

    # Weapons
    "Weapons Law Violations": "Weapons Law Violations",
    "Weapons_Law_Violations": "Weapons Law Violations",
    "Weapons Violations": "Weapons Law Violations",

    # Other categories
    "Law Violations": "Law Violations",
    "Domestic Violence": "Domestic Violence",
    "Traffic Law Violations": "Traffic Law Violations",

    # Violent crimes
    "Murder": "Murder",
    "Rape": "Rape",
}


def normalize_crime_label(label: str) -> str:
    """
    Normalize inconsistent crime labels to canonical form.
    
    Parameters
    ----------
    label : str
        Crime label to normalize
    
    Returns
    -------
    str
        Normalized crime label
    """
    if not isinstance(label, str):
        return label
    return CRIME_MAP.get(label.strip(), label.strip())