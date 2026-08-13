from app.services.sql_validator import validate_sql, SQLValidationError

schema = {
    "customers": {},
    "products": {},
    "orders": {}
}

def test_valid_table():
    sql = "SELECT * FROM customers"

    result = validate_sql(sql, schema)

    print("ALLOWED:", result)

def test_unknown_table():
    sql = "SELECT * FROM imaginary_table"

    try:
        validate_sql(sql, schema)
        print("ERROR: Unknown table was allowed!")
    except SQLValidationError as e:
        print("REJECTED:", e)

if __name__ == "__main__":
    test_valid_table()
    test_unknown_table()