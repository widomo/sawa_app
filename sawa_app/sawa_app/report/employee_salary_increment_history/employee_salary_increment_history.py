import frappe
from datetime import datetime

def execute(filters=None):
    if not filters:
        filters = {}

    # تعيين القيم الافتراضية
    filters.setdefault("employee", "")
    filters.setdefault("start_date", "")
    filters.setdefault("end_date", datetime.today().strftime('%Y-%m-%d'))

    columns = get_columns()
    data = get_data(filters)
    
    return columns, data

def get_columns():
    return [
        {"label": "Employee", "fieldname": "employee", "fieldtype": "Link", "options": "Employee", "width": 200},
        {"label": "Old Salary", "fieldname": "old_salary", "fieldtype": "Currency", "width": 120},
        {"label": "Increment Amount", "fieldname": "increment_amount", "fieldtype": "Currency", "width": 120},
        {"label": "New Salary", "fieldname": "new_salary", "fieldtype": "Currency", "width": 120},
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
        {"label": "Reason", "fieldname": "reason", "fieldtype": "Data", "width": 150},
    ]

def get_data(filters):
    query = """
        SELECT
            parent AS employee,
            old_salary,
            increment_amount,
            new_salary,
            date,
            reason
        FROM
            `tabEmployee Salary Increment History`
        WHERE
            (%(employee)s = "" OR %(employee)s IS NULL OR parent = %(employee)s)
        AND 
            (date BETWEEN %(start_date)s AND %(end_date)s)
        ORDER BY date DESC;
    """

    return frappe.db.sql(query, values=filters, as_dict=True)

