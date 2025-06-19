import sqlite3
import json

def db_to_json(db_filepath, table_name):
    """
    Converts data from a specified table in a SQLite .db file to a JSON string.

    Args:
        db_filepath (str): The path to the SQLite .db file.
        table_name (str): The name of the table to convert.

    Returns:
        str: A JSON string representing the data from the table, or None if an error occurs.
    """
    try:
        conn = sqlite3.connect(db_filepath)
        cursor = conn.cursor()

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Get column names from cursor description
        column_names = [description[0] for description in cursor.description]

        data = []
        for row in rows:
            row_dict = {}
            for i, col_name in enumerate(column_names):
                row_dict[col_name] = row[i]
            data.append(row_dict)

        json_output = json.dumps(data, indent=4)
        return json_output

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    finally:
        if conn:
            conn.close()

# Example Usage:
if __name__ == "__main__":
    # Create a dummy database for demonstration
    dummy_db_filepath = "cinema.db"
    dummy_table_name = "customers"


    # Convert the dummy database table to JSON
    json_data = db_to_json(dummy_db_filepath, dummy_table_name)

    if json_data:
        print(json_data)

        # You can also save it to a file
        with open("output.json", "w") as f:
            f.write(json_data)
        print("\nData successfully saved to output.json")
    else:
        print("Failed to convert database to JSON.")