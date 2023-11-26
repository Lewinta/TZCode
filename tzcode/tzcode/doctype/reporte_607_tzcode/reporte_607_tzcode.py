from __future__ import unicode_literals
import frappe
from frappe.utils import cstr, cint, flt, formatdate, format_datetime
from frappe.model.document import Document
from frappe.utils.csvutils import UnicodeWriter
import time


class Reporte607TZCode(Document):
    pass


class ReferenceNotFound(Exception):
    pass


@frappe.whitelist()
def get_file_address(from_date, to_date):
    # AND sinv.posting_date BETWEEN '%s' AND '%s' """ % ("SINV-%", from_date, to_date), as_dict=True)
    result = frappe.db.sql(f"""
        SELECT 
            sinv.name AS invoice_name,
            cust.tax_id AS customer_tax_id,
            cust.tipo_rnc AS customer_tipo_rnc,
            sinv.tipo_de_ingreso,
            sinv.ncf,
            sinv.return_against_ncf,
            sinv.posting_date,
            pe.isr_rate,
            pe.isr_amount,
            pe.retentiontype,
            pe.retention_category,
            pe.retention_amount
        FROM 
            `tabSales Invoice` AS sinv
        INNER JOIN 
            `tabCustomer` AS cust ON sinv.customer = cust.name
        LEFT JOIN
            `tabPayment Entry Reference` AS per ON per.reference_name = sinv.name
        LEFT JOIN
            `tabPayment Entry` AS pe ON pe.name = per.parent
        WHERE 
            sinv.docstatus = 1
            AND sinv.posting_date BETWEEN {from_date!r} AND {to_date!r}
    """, as_dict=True, debug=True)

    w = UnicodeWriter()
    w.writerow([
        'Nombre de Factura',
        'RNC o Cedula',
        'Tipo Id',
        'Tipo Bienes y Servicios Comprados',
        'NCF',
        'NCF o Documento Modificado',
        'Fecha Comprobante',
        'Tipo de Retención',
        'Categoría de Retención',
        'Monto de Retención',
    ])

    for row in result:
        w.writerow([
            row.invoice_name,
            row.customer_tax_id,
            row.customer_tipo_rnc,
            row.tipo_bienes_y_servicios_comprados,
            row.ncf,
            row.return_against_ncf,
            row.posting_date,
            row.retentiontype,
            row.retention_category,
            row.retention_amount,
        ])

    frappe.response['result'] = cstr(w.getvalue())
    frappe.response['type'] = 'csv'
    frappe.response['doctype'] = "Reporte_607_" + str(int(time.time()))


def get_retention_date(row):
    try:
        reference_row = get_reference_row(row)
    except ReferenceNotFound:
        return 0
    else:
        posting_date = frappe.get_value(
            "Payment Entry", reference_row.parent, "posting_date")
        return frappe.utils.getdate(posting_date).strftime("%Y%m")


def get_retention_amount(row, typeof, from_date):
    retention_date = get_retention_date(row)
    bill_date = frappe.utils.getdate(from_date).strftime("%Y%m")

    if retention_date == 0 or bill_date != retention_date:
        return 0

    if typeof not in ["ITBIS", "ISR"]:
        return 0

    try:
        reference_row = get_reference_row(row, typeof)
    except ReferenceNotFound:
        return 0
    else:
        return reference_row.retention_amount


def get_retention_type(row):
    # will return the retention_category of the retention selected in the Payment Entry
    # if set, else will return empty string
    try:
        reference_row = get_reference_row(row, typeof="ISR")
    except ReferenceNotFound:
        return ""
    else:
        return reference_row.retention_category


def get_reference_row(row, typeof=None):
    # will return the row of the Payment Entry that has the same reference as the Purchase Invoice
    # if set, else will return empty string
    doctype = "Payment Entry Reference"
    filters = {
        "reference_doctype": "Purchase Invoice",
        "reference_name": row.name,
        # "doctatus": "1",
    }

    if typeof is not None:
        filters["retention_type"] = typeof

    if frappe.db.exists(doctype, filters):
        return frappe.get_doc(doctype, filters)

    raise ReferenceNotFound()
