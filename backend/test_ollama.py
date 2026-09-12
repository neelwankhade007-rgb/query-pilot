from app.services.sql_generator import generate_sql


context = """
Dataset: employees.csv
Table: employees

Rows: 25

Columns:
- Name → string, not nullable
- Age → integer, not nullable
- Salary → integer, not nullable
- Interesting_Field → string, not nullable
"""


question = "What are the employees earning more than 60000?"

sql = generate_sql(question, context)

print("\nGenerated SQL:")
print(sql)