import pyodbc 

def get_db_connection():
    """Establish database connection"""
    try:
        cnxn = pyodbc.connect("Driver={SQL Server};"
                            "Server=localhost\\SQLEXPRESS03;"
                            "Database=Pricol_demo;"
                            "Trusted_Connection=yes;")
        return cnxn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

def get_table_columns():
    """Get column names from the process_data_125 table"""
    cnxn = get_db_connection()
    if cnxn:
        cursor = cnxn.cursor()
        cursor.execute("SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'process_data_125'")
        columns = [row.COLUMN_NAME for row in cursor]
        cnxn.close()
        return columns
    return []

def get_machine_details_by_operator(operator_id):
    """Get machine details for a specific operator"""
    cnxn = get_db_connection()
    if cnxn:
        cursor = cnxn.cursor()
        query = "SELECT u_id, model_id, group_no FROM [dbo].[process_data_125] WHERE operator_id = ?"
        cursor.execute(query, (operator_id,))
        details = cursor.fetchone()
        cnxn.close()
        return details
    return None

# Get database structure information
if __name__ == "__main__":
    operator_id = input("Enter Operator ID: ")
    details = get_machine_details_by_operator(operator_id)
    if details:
        print(f"User ID: {details.u_id}")
        print(f"Model ID: {details.model_id}")
        print(f"Group No: {details.group_no}")
    else:
        print("No details found for the given Operator ID.")
