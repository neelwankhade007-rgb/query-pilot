from app.services.sql_validator import validate_sql, SQLValidationError

def test_select_allowed():
    sql = "SELECT * FROM customers"

    result = validate_sql(sql)

    print("ALLOWED:", result)

def test_delete_rejected():
    sql = "DELETE FROM customers"

    try:
        validate_sql(sql)
        print("ERROR: Delete was allowed!")
    except SQLValidationError as e:
        print("REJECTED:", e)

def test_join_allowed():
    sql = """
    SELECT c.name, p.name
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN products p ON o.product_id = p.product_id
    WHERE p.name = 'Laptop'
    """
    
    result = validate_sql(sql)

    print("JOIN ALLOWED:", result)

if __name__ == "__main__":
    test_select_allowed()
    test_delete_rejected()
    test_join_allowed()