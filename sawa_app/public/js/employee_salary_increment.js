
// frappe.ui.form.on('Employee', {
//     refresh: function(frm) {
//         updateEmployeeCTC(frm);
//     },

//     employee_salary_increment_history_add: function(frm, cdt, cdn) {
//         let row = locals[cdt][cdn];
//         let currentCtc = Number(frm.doc.ctc || 0);

//         if (!row.old_salary) {
//             frappe.model.set_value(cdt, cdn, 'old_salary', currentCtc, () => {
//                 calculateRowNewSalary(frm, cdt, cdn);
//                 frm.refresh_field('employee_salary_increment_history');
//                 updateEmployeeCTC(frm);
//             });
//         } else {
//             calculateRowNewSalary(frm, cdt, cdn);
//             frm.refresh_field('employee_salary_increment_history');
//             updateEmployeeCTC(frm);
//         }
//     },

//     employee_salary_increment_history_remove: function(frm) {
//         updateEmployeeCTC(frm);
//     },

//     before_save: function(frm) {
//         updateEmployeeCTC(frm);
//     }
// });

// frappe.ui.form.on('Employee Salary Increment History', {
//     old_salary: function(frm, cdt, cdn) {
//         calculateRowNewSalary(frm, cdt, cdn);
//         updateEmployeeCTC(frm);
//     },

//     increment_amount: function(frm, cdt, cdn) {
//         calculateRowNewSalary(frm, cdt, cdn);
//         updateEmployeeCTC(frm);
//     }
// });

// function calculateRowNewSalary(frm, cdt, cdn) {
//     let row = locals[cdt][cdn];
//     let oldSalary = Number(row.old_salary || 0);
//     let incrementAmount = Number(row.increment_amount || 0);
//     let newSalary = oldSalary + incrementAmount;

//     frappe.model.set_value(cdt, cdn, 'new_salary', newSalary);
// }

// function updateEmployeeCTC(frm) {
//     let salaryHistory = frm.doc.employee_salary_increment_history || [];
//     let lastRow = null;

//     if (salaryHistory.length) {
//         // Prefer the most recent dated row, fall back to the last row in the table
//         let datedRows = salaryHistory.filter((row) => row.date);
//         if (datedRows.length) {
//             lastRow = datedRows.reduce((latest, row) => {
//                 return (!latest || row.date > latest.date) ? row : latest;
//             }, null);
//         } else {
//             lastRow = salaryHistory[salaryHistory.length - 1];
//         }
//     }

//     let newCtc = Number(lastRow && lastRow.new_salary ? lastRow.new_salary : 0);
//     frm.set_value('ctc', newCtc);
//     frm.refresh_field('ctc');
// }
frappe.ui.form.on('Employee Salary Increment History', {
    salary_increment_history_add: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        let last_salary = get_last_salary_before_current_row(frm, row);

        frappe.model.set_value(cdt, cdn, 'old_salary', last_salary);
        frappe.model.set_value(cdt, cdn, 'new_salary', last_salary + flt(row.increment_amount));

        update_ctc(frm);
    },

    increment_amount: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        let old_salary = flt(row.old_salary);
        let increment_amount = flt(row.increment_amount);

        frappe.model.set_value(cdt, cdn, 'new_salary', old_salary + increment_amount);

        update_ctc(frm);
    },

    old_salary: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];

        let old_salary = flt(row.old_salary);
        let increment_amount = flt(row.increment_amount);

        frappe.model.set_value(cdt, cdn, 'new_salary', old_salary + increment_amount);

        update_ctc(frm);
    },

    salary_increment_history_remove: function(frm) {
        recalculate_all_rows(frm);
    }
});


function get_last_salary_before_current_row(frm, current_row) {
    let rows = frm.doc.salary_increment_history || [];

    let current_index = rows.findIndex(r => r.name === current_row.name);

    if (current_index > 0) {
        let previous_row = rows[current_index - 1];
        return flt(previous_row.new_salary);
    }

    return flt(frm.doc.ctc);
}


function recalculate_all_rows(frm) {
    let rows = frm.doc.salary_increment_history || [];

    let current_salary = flt(frm.doc.ctc);

    rows.forEach(function(row) {
        frappe.model.set_value(row.doctype, row.name, 'old_salary', current_salary);

        let new_salary = current_salary + flt(row.increment_amount);

        frappe.model.set_value(row.doctype, row.name, 'new_salary', new_salary);

        current_salary = new_salary;
    });

    frm.set_value('ctc', current_salary);
}


function update_ctc(frm) {
    let rows = frm.doc.salary_increment_history || [];

    if (rows.length > 0) {
        let last_row = rows[rows.length - 1];
        frm.set_value('ctc', flt(last_row.new_salary));
    }
}

