from app.services.sql_validator import validate_sql


table_name = "dataset_5a4dedf1_ae7d_4dc9_8e0f_a8426deb79ea"


tests = [
    f"SELECT * FROM {table_name} WHERE Salary > 60000",

    f"DELETE FROM {table_name}",

    f"DROP TABLE {table_name}",

    f"SELECT * FROM {table_name}; DELETE FROM {table_name}",

    "SELECT * FROM employees"
]


for sql in tests:

    valid, message = validate_sql(sql, table_name)

    print("\nSQL:", sql)
    print("Valid:", valid)
    print("Message:", message)