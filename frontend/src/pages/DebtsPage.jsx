import { useEffect, useState } from "react";
import { debtsApi } from "../api/endpoints";
import { DataTable } from "../components/shared/DataTable";
import { FormModal } from "../components/shared/FormModal";
import { PageHeader } from "../components/shared/PageHeader";
import { formatTZS } from "../utils/currency";

export function DebtsPage() {
  const [debts, setDebts] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ debt_id: "", amount: "", method: "CASH", reference: "", notes: "" });

  const loadData = () => debtsApi.list().then(({ data }) => setDebts(data.results || data));

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await debtsApi.collectPayment(form);
    setOpen(false);
    setForm({ debt_id: "", amount: "", method: "CASH", reference: "", notes: "" });
    loadData();
  };

  return (
    <div className="page-stack">
      <PageHeader
        title="Debts"
        description="Track open balances, receive partial payments, and monitor customer exposure."
        action={
          <button type="button" className="button primary" onClick={() => setOpen(true)}>
            Receive Payment
          </button>
        }
      />
      <DataTable
        columns={[
          { key: "customer_name", label: "Customer" },
          { key: "sale_receipt_number", label: "Receipt" },
          { key: "total_amount", label: "Total", render: (row) => formatTZS(row.total_amount) },
          { key: "remaining_balance", label: "Remaining", render: (row) => formatTZS(row.remaining_balance) },
          { key: "status", label: "Status" },
        ]}
        rows={debts}
      />
      <FormModal title="Collect Debt Payment" open={open} onClose={() => setOpen(false)}>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>
            Debt
            <select required value={form.debt_id} onChange={(e) => setForm({ ...form, debt_id: Number(e.target.value) })}>
              <option value="">Select debt</option>
              {debts.map((debt) => (
                <option key={debt.id} value={debt.id}>
                  {debt.customer_name} - {formatTZS(debt.remaining_balance)}
                </option>
              ))}
            </select>
          </label>
          <label>
            Amount
            <input required type="number" min="0" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
          </label>
          <label>
            Method
            <select value={form.method} onChange={(e) => setForm({ ...form, method: e.target.value })}>
              <option value="CASH">Cash</option>
              <option value="MOBILE_MONEY">Mobile Money</option>
              <option value="BANK_TRANSFER">Bank Transfer</option>
            </select>
          </label>
          <label>
            Reference
            <input value={form.reference} onChange={(e) => setForm({ ...form, reference: e.target.value })} />
          </label>
          <label>
            Notes
            <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          </label>
          <button type="submit" className="button primary">
            Record Payment
          </button>
        </form>
      </FormModal>
    </div>
  );
}
