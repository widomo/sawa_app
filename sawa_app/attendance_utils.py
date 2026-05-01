import frappe
from datetime import timedelta

@frappe.whitelist()
def generate_attendance_from_checkin(from_date, to_date):
    checkins = frappe.get_all(
        "Employee Checkin",
        filters={
            "time": ["between", [from_date, to_date]]
        },
        fields=["employee", "time"],
        order_by="employee, time"
    )

    if not checkins:
        print("No checkins found in the selected date range.")
        return

    grouped = {}
    for entry in checkins:
        emp = entry.employee
        if emp not in grouped:
            grouped[emp] = []
        grouped[emp].append(entry)

    for emp, logs in grouped.items():
        daily = {}
        for log in logs:
            date_str = log.time.date().isoformat()
            if date_str not in daily:
                daily[date_str] = {"in": log.time, "out": log.time}
            else:
                if log.time < daily[date_str]["in"]:
                    daily[date_str]["in"] = log.time
                if log.time > daily[date_str]["out"]:
                    daily[date_str]["out"] = log.time

        for date, times in daily.items():
            if times["in"] and times["out"]:
                exists = frappe.db.exists("Attendance", {
                    "employee": emp,
                    "attendance_date": date
                })
                if exists:
                    continue

                doc = frappe.new_doc("Attendance")
                doc.employee = emp
                doc.attendance_date = date
                doc.status = "Present"
                doc.in_time = times["in"]
                doc.out_time = times["out"]
                doc.save()
                frappe.db.commit()
                print(f"✅ Attendance created for {emp} on {date}")
