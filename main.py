import pymysql
import sys
from getpass import getpass

# =============================================================================
# DATABASE CONNECTION
# =============================================================================

def get_db_connection(db_user, db_pass, db_host, db_name):
    """Establishes a connection to the MySQL database using PyMySQL."""
    try:
        connection = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_pass,
            database=db_name,
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True  # Set to True for simple CLI transaction handling
        )
        print("Database connection successful.")
        return connection
    except pymysql.Error as e:
        print(f"Error connecting to MySQL Database: {e}", file=sys.stderr)
        return None

# =============================================================================
# FUNCTIONAL REQUIREMENTS (5 READS)
# =============================================================================

def list_crew_profiles(connection):
    """READ 1: List crew members with their loyalty and weapon proficiency (JOIN)."""
    print("\n--- [READ 1] Crew Profiles & Weapon Skills ---")
    sql = """
    SELECT c.CodeName, c.Specialization, c.LoyaltyScore, wp.WeaponProficiency 
    FROM CREW_MEMBER c
    LEFT JOIN TACTICAL_CREW wp ON c.CodeName = wp.Codename
    ORDER BY c.LoyaltyScore DESC
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            wp = row['WeaponProficiency'] if row['WeaponProficiency'] is not None else "N/A"
            print(f"Agent: {row['CodeName']} | Spec: {row['Specialization']} | Loyalty: {row['LoyaltyScore']} | Weapon Skill: {wp}")

def find_hostages_by_status(connection):
    """READ 2: Find hostages by status (Parameterized Query)."""
    print("\n--- [READ 2] Find Hostages by Status ---")
    status = input("Enter status (e.g., Cooperative, Hostile, Resistant): ").strip()
    sql = """
    SELECT HostageID, FirstName, LastName, Status, ManagerCodename
    FROM HOSTAGE
    WHERE Status = %s
    """
    with connection.cursor() as cursor:
        cursor.execute(sql, (status,))
        results = cursor.fetchall()
        if not results:
            print(f"No hostages found with status '{status}'.")
        else:
            for row in results:
                print(f"ID: {row['HostageID']} | Hostage: {row['FirstName']} {row['LastName']} | Managed By: {row['ManagerCodename']}")

def view_task_assignments(connection):
    """READ 3: Complex Join (N-ary Relationship) - Task Assignments across phases, crew, resources, and locations."""
    print("\n--- [READ 3] Task Assignment Details (4-way N-ary) ---")
    sql = """
    SELECT 
        pp.Phasecodename,
        cm.CodeName,
        cm.Specialization,
        r.Type as ResourceType,
        hb.LocationName
    FROM TASK_ASSIGNMENT ta
    JOIN PLAN_PHASE pp ON ta.PID = pp.PhaseID
    JOIN CREW_MEMBER cm ON ta.CName = cm.CodeName
    JOIN RESOURCE r ON ta.ResID = r.ResourceID
    JOIN HEIST_BLUEPRINT hb ON ta.BID = hb.BlueprintID
    ORDER BY pp.PhaseID, cm.CodeName
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        results = cursor.fetchall()
        if not results:
            print("No task assignments found.")
        else:
            for row in results:
                print(f"Phase: {row['Phasecodename']} | Crew: {row['CodeName']} ({row['Specialization']}) | Using: {row['ResourceType']} | At: {row['LocationName']}")

def check_phase_requirements(connection):
    """READ 4: Join - What resources does a phase require?"""
    print("\n--- [READ 4] Phase Resource Requirements ---")
    # Note: Using column names from REQUIRES table (Phase, Res_id) and PLAN_PHASE (PhaseID, Planned_Duration)
    sql = """
    SELECT pp.Phasecodename, pp.Planned_Duration, r.Type, r.CurrentQuantity, r.CriticalThreshold
    FROM PLAN_PHASE pp
    JOIN REQUIRES req ON pp.PhaseID = req.Phase
    JOIN RESOURCE r ON req.Res_id = r.ResourceID
    ORDER BY pp.PhaseID
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            status = "CRITICAL" if row['CurrentQuantity'] <= row['CriticalThreshold'] else "OK"
            print(f"Phase '{row['Phasecodename']}' ({row['Planned_Duration']}hrs) needs {row['Type']} (Have: {row['CurrentQuantity']}) [{status}]")

def view_crew_deviations(connection):
    """READ 5: View all crew members who deviated from a plan phase (Using C_id & P_id)."""
    print("\n--- [READ 5] Logged Crew Deviations ---")
    # Note: Using column names from DEVIATES_FROM table (C_id, P_id)
    sql = """
    SELECT cm.CodeName, pp.Phasecodename 
    FROM DEVIATES_FROM df
    JOIN CREW_MEMBER cm ON df.C_id = cm.CodeName
    JOIN PLAN_PHASE pp ON df.P_id = pp.PhaseID
    """
    with connection.cursor() as cursor:
        cursor.execute(sql)
        results = cursor.fetchall()
        if not results:
            print("No deviations logged.")
        else:
            for row in results:
                print(f"Crew: {row['CodeName']} deviated from Phase: {row['Phasecodename']}")

# =============================================================================
# FUNCTIONAL REQUIREMENTS (3 WRITES: INSERT, UPDATE, DELETE/INSERT)
# =============================================================================

def add_new_phase(connection):
    """WRITE 1 (INSERT): Inserts a new PLAN_PHASE record."""
    print("\n--- [WRITE 1] Add New Plan Phase (INSERT) ---")
    try:
        pid = int(input("New Phase ID (e.g., 8): "))
        pcode = input("Phase Codename: ")
        duration = int(input("Planned Duration (hours): "))
        Current_Dissonance = int(input("Current_Dissonance: "))
        
        sql = "INSERT INTO PLAN_PHASE (PhaseID, Phasecodename, Planned_Duration, Current_Dissonance) VALUES (%s, %s, %s, %s)"
        with connection.cursor() as cursor:
            cursor.execute(sql, (pid, pcode, duration,Current_Dissonance ))
        print(f"Phase '{pcode}' added successfully.")
    except Exception as e:
        print(f"Error: {e}")

def update_resource_quantity(connection):
    """WRITE 2 (UPDATE): Updates the CurrentQuantity of a RESOURCE."""
    print("\n--- [WRITE 2] Update Resource Quantity (UPDATE) ---")
    resource_id = input("Enter Resource ID to update (e.g., 2 for Ammunition): ")
    try:
        new_qty = int(input("Enter New Current Quantity: "))
        sql = "UPDATE RESOURCE SET CurrentQuantity = %s WHERE ResourceID = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql, (new_qty, resource_id))
            if cursor.rowcount > 0:
                print("Resource quantity updated.")
            else:
                print("Resource ID not found.")
    except Exception as e:
        print(f"Error: {e}")

def delete_police_unit(connection):
    """WRITE 3 (DELETE): Deletes a POLICE_UNIT record."""
    print("\n--- [WRITE 3] Delete Police Unit (DELETE) ---")
    try:
        unit_id = int(input("Enter Unit ID to delete (e.g., 5 for Tamayo): "))
        
        # Note: Foreign keys in COMMUNICATES_WITH, NEGOTIATION, and MONITORS
        # are set to CASCADE/SET NULL, ensuring integrity.
        sql = "DELETE FROM POLICE_UNIT WHERE UnitID = %s"
        with connection.cursor() as cursor:
            cursor.execute(sql, (unit_id,))
            if cursor.rowcount > 0:
                print(f"Police Unit {unit_id} deleted successfully.")
            else:
                print("Police Unit ID not found.")
    except Exception as e:
        print(f"Error: {e}")

# =============================================================================
# USER INTERFACE (CLI)
# =============================================================================

def main_cli(connection):
    """The main command-line interface loop."""
    while True:
        print("\n========== OPERATION BELLA CIAO: DB INTERFACE ==========")
        print("--- Read Operations (Minimum 5) ---")
        print("1. Crew Profiles & Weapon Skills")
        print("2. Find Hostages by Status")
        print("3. View Task Assignment Details (N-ary)")  
        print("4. Check Phase Resource Requirements")
        print("5. View Crew Deviations (C_id & P_id)")
        print("----------------------------------------------------------")
        print("--- Write Operations (Minimum 3) ---")
        print("6. Add New Plan Phase (INSERT)")
        print("7. Update Resource Quantity (UPDATE)")
        print("8. Delete Police Unit (DELETE)")
        print("q. Quit")
        
        choice = input("Select Option: ").strip().lower()
        
        if choice == '1': list_crew_profiles(connection)
        elif choice == '2': find_hostages_by_status(connection)
        elif choice == '3': view_task_assignments(connection)
        elif choice == '4': check_phase_requirements(connection)
        elif choice == '5': view_crew_deviations(connection)
        elif choice == '6': add_new_phase(connection)
        elif choice == '7': update_resource_quantity(connection)
        elif choice == '8': delete_police_unit(connection)
        elif choice == 'q': 
            print("Bella Ciao! Exiting application...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    DB_HOST = 'localhost'
    DB_NAME = 'bellaciao_db'
    
    print("=== System Access (MySQL Credentials) ===")
    DB_USER = input("User: ").strip()
    DB_PASS = getpass("Password: ")
    
    conn = get_db_connection(DB_USER, DB_PASS, DB_HOST, DB_NAME)
    
    if conn:
        main_cli(conn)
        conn.close()