"""Generates the synthetic business documents used by the demo.

Run once (`python generate_documents.py`) to (re)populate documents/.
The documents are invented but written to look like real contracts,
invoices, and internal memos, each with a small header of Key: Value
fields so extract_field has something structured to pull from.
"""

from pathlib import Path

DOCS_DIR = Path(__file__).parent / "documents"


def render(fields: dict, body: str) -> str:
    header = "\n".join(f"{key}: {value}" for key, value in fields.items())
    return f"{header}\n\n{body.strip()}\n"


DOCUMENTS = {
    "contract_meridian_northwind.txt": render(
        {
            "Document Type": "Service Agreement",
            "Document ID": "CTR-2031",
            "Effective Date": "2024-03-01",
            "Party A": "Meridian Logistics LLC",
            "Party B": "Northwind Freight Co",
            "Term": "24 months",
            "Governing Law": "State of Delaware",
            "Total Contract Value": "$184,500.00",
            "Payment Terms": "Net 30",
            "Status": "Active",
        },
        """
        This Service Agreement ("Agreement") is entered into as of the Effective
        Date by and between Meridian Logistics LLC ("Provider") and Northwind
        Freight Co ("Client"). Provider agrees to furnish warehousing,
        cross-docking, and last-mile delivery services out of the Provider's
        Newark, NJ distribution center.

        Provider shall maintain commercial general liability insurance of no
        less than $2,000,000 per occurrence and shall indemnify Client against
        claims arising from Provider's negligent acts. Either party may
        terminate this Agreement for convenience upon 60 days written notice,
        or immediately for material breach that remains uncured after 15 days.

        Client shall pay all undisputed invoices within the Payment Terms
        stated above. Late payments accrue interest at 1.5% per month. This
        Agreement is governed by the Governing Law listed above, without
        regard to conflict of laws principles.
        """,
    ),
    "contract_harborview_crestline.txt": render(
        {
            "Document Type": "Supply Agreement",
            "Document ID": "CTR-2044",
            "Effective Date": "2024-01-15",
            "Party A": "Crestline Dental Supply Co",
            "Party B": "Harborview Dental Group",
            "Term": "12 months",
            "Governing Law": "State of New York",
            "Total Contract Value": "$96,200.00",
            "Payment Terms": "Net 30",
            "Status": "Active",
        },
        """
        This Supply Agreement governs the recurring purchase of dental
        consumables (composite resin, disposable handpieces, sterilization
        pouches) by Harborview Dental Group from Crestline Dental Supply Co.

        Crestline shall guarantee delivery within 5 business days of a
        purchase order and shall replace any defective product at no cost.
        Harborview commits to a minimum quarterly purchase volume of
        $18,000. Pricing is fixed for the Term above, subject to a single
        renegotiation if raw material costs rise more than 10%.

        Either party may terminate for convenience with 45 days written
        notice. Confidential pricing terms in this Agreement may not be
        disclosed to third parties.
        """,
    ),
    "contract_summit_ridge_lease.txt": render(
        {
            "Document Type": "Office Lease Agreement",
            "Document ID": "CTR-2059",
            "Effective Date": "2023-09-01",
            "Party A": "Summit Ridge Properties LLC",
            "Party B": "Pallas Analytics Inc",
            "Term": "36 months",
            "Governing Law": "State of Massachusetts",
            "Total Contract Value": "$412,800.00",
            "Payment Terms": "Due on the 1st of each month",
            "Status": "Active",
        },
        """
        Summit Ridge Properties LLC ("Landlord") leases approximately 6,200
        square feet of office space at 210 Beacon Street, Suite 400, Boston,
        MA to Pallas Analytics Inc ("Tenant") for use as general office space.

        Monthly base rent is $11,466.67, escalating 3% annually on the
        anniversary of the Effective Date. Tenant is responsible for its
        pro-rata share of common area maintenance and property taxes.
        Tenant may not sublease any portion of the premises without
        Landlord's prior written consent.

        Landlord shall maintain the building's HVAC, elevators, and common
        areas in good working order. Tenant shall carry commercial tenant
        insurance covering its own property and liability.
        """,
    ),
    "invoice_10432.txt": render(
        {
            "Document Type": "Invoice",
            "Invoice Number": "INV-10432",
            "Issue Date": "2024-06-12",
            "Due Date": "2024-07-12",
            "Vendor": "Crestline Dental Supply Co",
            "Bill To": "Harborview Dental Group",
            "Amount Due": "$12,340.00",
            "Payment Terms": "Net 30",
            "Status": "Unpaid",
        },
        """
        Line items:
          - Composite resin cartridges (x40)              $6,200.00
          - Disposable handpieces (x120)                  $4,560.00
          - Sterilization pouches, case of 500 (x6)        $1,580.00

        Subtotal: $12,340.00
        Tax: $0.00 (resale exempt)
        Amount Due: $12,340.00

        Please remit payment by the Due Date to avoid late fees under the
        governing Supply Agreement CTR-2044.
        """,
    ),
    "invoice_10498.txt": render(
        {
            "Document Type": "Invoice",
            "Invoice Number": "INV-10498",
            "Issue Date": "2024-07-02",
            "Due Date": "2024-08-01",
            "Vendor": "Meridian Logistics LLC",
            "Bill To": "Northwind Freight Co",
            "Amount Due": "$28,915.50",
            "Payment Terms": "Net 30",
            "Status": "Paid",
        },
        """
        Line items:
          - Warehousing, June 2024 (per Agreement CTR-2031)   $19,500.00
          - Cross-docking fees (312 pallets)                   $6,240.00
          - Last-mile delivery surcharge (fuel)                $3,175.50

        Subtotal: $28,915.50
        Tax: $0.00
        Amount Due: $28,915.50

        Payment received in full on 2024-07-20 via ACH transfer.
        """,
    ),
    "invoice_10501.txt": render(
        {
            "Document Type": "Invoice",
            "Invoice Number": "INV-10501",
            "Issue Date": "2024-07-05",
            "Due Date": "2024-08-04",
            "Vendor": "Summit Ridge Properties LLC",
            "Bill To": "Pallas Analytics Inc",
            "Amount Due": "$11,466.67",
            "Payment Terms": "Due on receipt",
            "Status": "Unpaid",
        },
        """
        Monthly rent invoice for Suite 400, 210 Beacon Street, Boston, MA,
        covering the period 2024-07-01 through 2024-07-31, per Office Lease
        Agreement CTR-2059.

        Base rent: $11,466.67
        CAM charges: included
        Amount Due: $11,466.67
        """,
    ),
    "invoice_10512.txt": render(
        {
            "Document Type": "Invoice",
            "Invoice Number": "INV-10512",
            "Issue Date": "2024-07-18",
            "Due Date": "2024-08-17",
            "Vendor": "Beacon Office Supply",
            "Bill To": "Pallas Analytics Inc",
            "Amount Due": "$742.16",
            "Payment Terms": "Net 30",
            "Status": "Unpaid",
        },
        """
        Line items:
          - Standing desks (x2)                              $540.00
          - Toner cartridges (x6)                            $162.16
          - Shipping                                          $40.00

        Amount Due: $742.16

        This vendor is not under a standing supply agreement; purchases are
        made on a per-order basis via purchase order PO-3391.
        """,
    ),
    "memo_safety_protocol.txt": render(
        {
            "Document Type": "Internal Memo",
            "Memo ID": "MEMO-0087",
            "Date": "2024-05-02",
            "From": "Priya Sharma, Operations Director",
            "To": "All Staff, Warehouse Division",
            "Subject": "Updated Safety Protocol for Loading Dock",
            "Status": "Final",
        },
        """
        Effective immediately, all personnel operating in the Newark
        distribution center loading dock must complete the revised forklift
        certification before their next shift. This update follows a near-miss
        incident on 2024-04-28 involving a pallet jack and an unmarked
        pedestrian lane.

        Key changes:
          1. Pedestrian lanes will be repainted with high-visibility tape by
             2024-05-10.
          2. Forklift operators must sound the horn at every blind corner.
          3. A dock supervisor must sign off on each shift's pre-operation
             checklist.

        Questions should be directed to the Operations Director. This memo
        supersedes the safety protocol dated 2023-11-01.
        """,
    ),
    "memo_vendor_review.txt": render(
        {
            "Document Type": "Internal Memo",
            "Memo ID": "MEMO-0093",
            "Date": "2024-06-20",
            "From": "David Okafor, Procurement Lead",
            "To": "Finance Committee",
            "Subject": "Q2 Vendor Performance Review",
            "Status": "Draft",
        },
        """
        This memo summarizes vendor performance for Q2 2024. Crestline
        Dental Supply Co met all delivery SLAs under Supply Agreement
        CTR-2044 with an average lead time of 3.2 days, ahead of the
        contractual 5-day guarantee.

        Meridian Logistics LLC experienced one late shipment in May 2024 due
        to a regional weather event; no penalty was assessed per the force
        majeure clause in CTR-2031.

        Recommendation: renew both agreements at current pricing. Beacon
        Office Supply remains an ad hoc vendor and is not recommended for a
        standing agreement given low order volume.
        """,
    ),
    "memo_lease_renewal.txt": render(
        {
            "Document Type": "Internal Memo",
            "Memo ID": "MEMO-0101",
            "Date": "2024-08-05",
            "From": "Lena Ostrowski, Facilities Manager",
            "To": "Executive Team",
            "Subject": "Beacon Street Lease Renewal Options",
            "Status": "Final",
        },
        """
        The Office Lease Agreement CTR-2059 with Summit Ridge Properties LLC
        for 210 Beacon Street enters its final 12 months in September 2025.
        Summit Ridge has verbally offered a renewal at a 5% increase over the
        escalated rate, or a relocation allowance of $15,000 if we vacate by
        the lease end date.

        Facilities recommends beginning renewal negotiations by January 2025
        to preserve leverage, and requests Finance confirm the FY2026 real
        estate budget before then.
        """,
    ),
}


def main() -> None:
    DOCS_DIR.mkdir(exist_ok=True)
    for filename, content in DOCUMENTS.items():
        (DOCS_DIR / filename).write_text(content)
    print(f"Wrote {len(DOCUMENTS)} documents to {DOCS_DIR}/")


if __name__ == "__main__":
    main()
