import frappe
from frappe.utils import getdate

@frappe.whitelist()
def apply_bulk_leave(employees, from_date, to_date, half_day=False, description=""):
	"""
	Create Leave Applications for multiple employees.
	"""
	employees = frappe.parse_json(employees)

	for emp in employees:
		leave_type = get_employee_leave_type(emp.get("employee"))
		if not leave_type:
			frappe.msgprint(f"لم يتم تحديد نوع الإجازة للموظف {emp.get('employee')}")
			continue
					# 🔍 تحقق من الـ Leave Allocation
		allocation = frappe.db.get_value("Leave Allocation", {
				 "employee": emp.get("employee"),
				 "leave_type": leave_type,
				 "docstatus": 1
					}, ["from_date", "to_date"], as_dict=True)

				 # اطبع النتيجة للمراجعة
		frappe.msgprint(f"{emp.get('employee')} allocation: {allocation}")

					# لو مفيش Allocation أو التواريخ برا النطاق – تجاهل الموظف
		if not allocation:
			frappe.msgprint(f"الموظف {emp.get('employee')} لا يوجد له Leave Allocation لنوع الإجازة {leave_type}")
			continue

		if getdate(from_date) < allocation.from_date or getdate(to_date) > allocation.to_date:
			frappe.msgprint(f"التواريخ المطلوبة خارج نطاق الإجازة المخصصة للموظف {emp.get('employee')}")
			continue

		doc = frappe.get_doc({
			"doctype": "Leave Application",
			"employee": emp.get("employee"),
			"leave_type": leave_type,
			"from_date": getdate(from_date),
			"to_date": getdate(to_date),
			"half_day": half_day,
			"description": description,
			#"docstatus": 1  # submitted
		})
		doc.status = "Approved"  # ← دي أهم حاجة علشان يقبل الـ submit
		doc.insert()
		doc.submit()

def get_employee_leave_type(employee):
	"""
	Determine leave type for each employee based on policy or logic.
	You can customize this logic as needed.
	"""
	# مثال: نفرّق بين اعتيادي 30 و 21 حسب Custom Field في Employee
	policy = frappe.db.get_value("Employee", employee, "custom_leave_policy")  # لو فيه فيلد اسمه leave_policy

	print(f"{employee} → policy: {policy}")
	if policy == "HR-LPOL-2025-00001":
		return "اعتيادى 21"
	elif policy == "HR-LPOL-2025-00002":
		return "اعتيادى 30"
	else:
	#	return "اعتيادى 30"  # default fallback
	#if policy.strip() == "30":
	#	return "اعتيادى 30"
	#elif policy.strip() == "21":
	#	return "اعتيادى 21"
	#else:
		frappe.throw(f"الموظف {employee} ليس له سياسة إجازة محددة (leave policy)")
