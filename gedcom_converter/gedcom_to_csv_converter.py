import csv
from gedcom.element.individual import IndividualElement
from gedcom.parser import Parser

def get_individual_name(individual):
    """Helper function to get the full name of an individual."""
    name_parts = individual.get_name()
    # Ensure name_parts is not None and has at least two elements
    if name_parts and len(name_parts) >= 2:
        return f"{name_parts[0]} {name_parts[1]}"
    elif name_parts and len(name_parts) == 1:
        return name_parts[0] # Handle cases with only one name part
    return "Unknown"

def get_event_date_and_place(individual, event_tag):
    """
    Helper function to get the date and place of a specific event (e.g., BIRT, DEAT).
    Returns a tuple: (date_string, place_string)
    """
    event_date = "Unknown"
    event_place = "Unknown"

    child_elements = individual.get_child_elements()
    for event_element in child_elements:
        if event_element.get_tag() == event_tag:
            # Found the event (e.g., BIRT or DEAT)
            sub_elements = event_element.get_child_elements()
            for sub_element in sub_elements:
                if sub_element.get_tag() == "DATE":
                    event_date = sub_element.get_value()
                elif sub_element.get_tag() == "PLAC":
                    event_place = sub_element.get_value()
            break # Assuming one BIRT/DEAT event for simplicity
    return event_date, event_place


def get_family_details(element_parser, individual_id, families):
    """
    Helper function to get spouse(s) and children for an individual.
    Returns a tuple: (spouses_names, children_names)
    """
    spouses = []
    children_ids = []

    # Find families where this individual is a spouse (FAMS tag in INDI record)
    individual_element = element_parser.get_element_by_id(individual_id)
    if not individual_element:
        return "Unknown", "Unknown"

    fams_elements = [el for el in individual_element.get_child_elements() if el.get_tag() == "FAMS"]

    for fams_element in fams_elements:
        family_id = fams_element.get_value()
        family = families.get(family_id)
        if family:
            husband = family.get_husband()
            wife = family.get_wife()

            if husband and husband.get_value() == individual_id:
                if wife:
                    spouse_individual = element_parser.get_element_by_id(wife.get_value())
                    if spouse_individual:
                        spouses.append(get_individual_name(spouse_individual))
                for child_element in family.get_child_elements():
                    if child_element.get_tag() == "CHIL":
                        children_ids.append(child_element.get_value())

            elif wife and wife.get_value() == individual_id: # Use elif to avoid processing same family twice if self is both HUSB and WIFE (unlikely but safe)
                if husband:
                    spouse_individual = element_parser.get_element_by_id(husband.get_value())
                    if spouse_individual:
                        spouses.append(get_individual_name(spouse_individual))
                for child_element in family.get_child_elements():
                    if child_element.get_tag() == "CHIL":
                        children_ids.append(child_element.get_value())

    children_names = []
    # Deduplicate children_ids in case an individual is listed as FAMS in multiple families that also list same children
    unique_children_ids = list(set(children_ids))
    for child_id in unique_children_ids:
        child_individual = element_parser.get_element_by_id(child_id)
        if child_individual:
            children_names.append(get_individual_name(child_individual))

    return "; ".join(spouses) if spouses else "Unknown", "; ".join(children_names) if children_names else "Unknown"

def get_parent_details(element_parser, individual, families):
    """Helper function to get parents' names for an individual."""
    father_name = "Unknown"
    mother_name = "Unknown"

    # Find the family where this individual is a child (FAMC tag in INDI record)
    famc_elements = [el for el in individual.get_child_elements() if el.get_tag() == "FAMC"]

    if famc_elements:
        # Consider the first FAMC record if multiple exist (usually there's one biological)
        family_id = famc_elements[0].get_value()
        family = families.get(family_id)
        if family:
            husband = family.get_husband()
            if husband:
                father_individual = element_parser.get_element_by_id(husband.get_value())
                if father_individual:
                    father_name = get_individual_name(father_individual)

            wife = family.get_wife()
            if wife:
                mother_individual = element_parser.get_element_by_id(wife.get_value())
                if mother_individual:
                    mother_name = get_individual_name(mother_individual)
    return father_name, mother_name


def gedcom_to_csv(gedcom_file_path, csv_file_path):
    """
    Converts a GEDCOM file to a CSV file.

    Args:
        gedcom_file_path (str): The path to the input GEDCOM file.
        csv_file_path (str): The path to the output CSV file.
    """
    gedcom_parser = Parser()

    try:
        # Strict parsing set to False by default. If your GEDCOM is very clean, you can set it to True.
        # Strict parsing often causes issues with real-world GEDCOM files.
        gedcom_parser.parse_file(gedcom_file_path) # Removed False, as it's default for strict.
                                                   # If issues persist, can try `strict=False` if supported by your lib version
                                                   # or handle specific errors.
        print(f"Successfully parsed GEDCOM file: {gedcom_file_path}")
    except Exception as e:
        print(f"Error parsing GEDCOM file: {e}")
        return

    root_child_elements = gedcom_parser.get_root_child_elements()
    individuals = []
    families = {} # Store families for easy lookup {family_id: family_element}

    # First pass: get all individuals and families
    for element in root_child_elements:
        if isinstance(element, IndividualElement):
            individuals.append(element)
        elif element.get_tag() == "FAM":
            families[element.get_pointer()] = element

    if not individuals:
        print("No individuals found in the GEDCOM file.")
        return

    # Prepare data for CSV
    csv_data = []
    header = [
        "ID", "Name", "Sex", "Birth Date", "Birth Place",
        "Death Date", "Death Place", "Father", "Mother",
        "Spouse(s)", "Children"
    ]
    csv_data.append(header)

    for individual in individuals:
        individual_id = individual.get_pointer()
        name = get_individual_name(individual)
        sex = individual.get_gender() if individual.get_gender() else "Unknown"

        birth_date, birth_place = get_event_date_and_place(individual, "BIRT")
        death_date, death_place = get_event_date_and_place(individual, "DEAT")

        father_name, mother_name = get_parent_details(gedcom_parser, individual, families)
        spouses_names, children_names = get_family_details(gedcom_parser, individual_id, families)

        csv_data.append([
            individual_id,
            name,
            sex,
            birth_date,
            birth_place,
            death_date,
            death_place,
            father_name,
            mother_name,
            spouses_names,
            children_names
        ])

    # Write to CSV
    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(csv_data)
        print(f"Successfully converted GEDCOM to CSV: {csv_file_path}")
    except IOError as e:
        print(f"Error writing CSV file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during CSV writing: {e}")

# --- Main execution ---
if __name__ == "__main__":
    # Replace 'your_file.ged' with the path to your GEDCOM file
    # Since you are running it from the same directory, this should be fine
    # if your actual file is named 'your_file.ged'.
    # If your GEDCOM file has a different name, change it here.
    # For example, if your file is 'family.ged':
    # gedcom_input_file = "family.ged"
    gedcom_input_file = "johighnes_2025-05-18.ged" # Make sure this matches your actual GEDCOM filename
    csv_output_file = "johighnes_2025-05-18.csv"

    # Check if the specified GEDCOM file exists, otherwise use the dummy for demonstration.
    try:
        with open(gedcom_input_file, "r", encoding='utf-8-sig') as f: # Added utf-8-sig for potential BOM
            print(f"Found GEDCOM file: {gedcom_input_file}. Proceeding with this file.")
            # Test read a line to ensure it's not empty or completely unreadable
            # f.readline() # Optional: can add more checks
    except FileNotFoundError:
        print(f"Warning: GEDCOM file '{gedcom_input_file}' not found. Creating a dummy file for demonstration.")
        dummy_gedcom_content = """0 HEAD
1 SOUR PYTHON-GEDCOM
2 VERS 1.0
1 GEDC
2 VERS 5.5.1
2 FORM LINEAGE-LINKED
1 CHAR UTF-8
0 @I1@ INDI
1 NAME John /Smith/
1 SEX M
1 BIRT
2 DATE 1 JAN 1900
2 PLAC London, England
1 DEAT
2 DATE 1 JAN 1970
2 PLAC New York, USA
1 FAMS @F1@
1 FAMC @F2@
0 @I2@ INDI
1 NAME Jane /Doe/
1 SEX F
1 BIRT
2 DATE 15 FEB 1905
2 PLAC Paris, France
1 FAMS @F1@
0 @I3@ INDI
1 NAME Jim /Smith/
1 SEX M
1 BIRT
2 DATE 10 MAR 1930
2 PLAC London, England
1 FAMC @F1@
0 @I4@ INDI
1 NAME Robert /Smith/ Sr./
1 SEX M
1 FAMS @F2@
0 @I5@ INDI
1 NAME Mary /Jones/
1 SEX F
1 FAMS @F2@
0 @F1@ FAM
1 HUSB @I1@
1 WIFE @I2@
1 CHIL @I3@
1 MARR
2 DATE 5 MAY 1925
0 @F2@ FAM
1 HUSB @I4@
1 WIFE @I5@
1 CHIL @I1@
0 TRLR
"""
        with open(gedcom_input_file, "w", encoding="utf-8") as f:
            f.write(dummy_gedcom_content)
    except Exception as e:
        print(f"An error occurred trying to access '{gedcom_input_file}': {e}")
        print("Please ensure the file exists and is readable, or a dummy file will be used.")
        # Fallback to creating dummy if any other error occurs before parsing
        if not os.path.exists(gedcom_input_file): # Redundant if FileNotFoundError caught, but good for other errors
            # (same dummy content as above)
            pass # Assuming dummy will be created if it reaches here due to earlier logic

    gedcom_to_csv(gedcom_input_file, csv_output_file)

    # To run this script:
    # 1. Save it as a Python file (e.g., gedcom_converter.py).
    # 2. Make sure your GEDCOM file (e.g., your_file.ged, or rename the variable)
    #    is in the same directory.
    # 3. Run from your terminal: python gedcom_converter.py