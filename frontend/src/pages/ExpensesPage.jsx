import { useEffect, useState } from "react";
import { expensesApi } from "../api/endpoints";
import { DataTable } from "../components/shared/DataTable";
import { FormModal } from "../components/shared/FormModal";
import { PageHeader } from "../components/shared/PageHeader";
import { formatTZS } from "../utils/currency";
import { formatDate } from "../utils/date";

export function ExpensesPage() {
  const [expenses, setExpenses] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ title: "", category: "", amount: "", expense_date: "", vendor: "", notes: "" });

  const loadData = () => expensesApi.list().then(({ data }) => setExpenses(data.results || data));

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await expensesApi.create(form);
    setOpen(false);
    setForm({ title: "", category: "", amount: "", expense_date: "", vendor: "", notes: "" });
    loadData();
  };

  return (
    <div className="page-stack">
      <PageHeader
        title="Expenses"
        description="Track operating costs such as rent, utilities, and purchases."
        action={
          <button type="button" className="button primary" onClick={() => setOpen(true)}>
            Add Expense
          </button>
        }
      />
      <DataTable
        columns={[
          { key: "title", label: "Expense" },
          { key: "category", label: "Category" },
          { key: "amount", label: "Amount", render: (row) => formatTZS(row.amount) },
          { key: "expense_date", label: "Date", render: (row) => formatDate(row.expense_date) },
        ]}
        rows={expenses}
      />
      <FormModal title="Create Expense" open={open} onClose={() => setOpen(false)}>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>
            Title
            <input required value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
          </label>
          <label>
            Category
            <input required value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} />
          </label>
          <label>
            Amount
            <input required type="number" min="0" value={form.amount} onChange={(e) => setForm({ ...form, amount: e.target.value })} />
          </label>
          <label>
            Date
            <input required type="date" value={form.expense_date} onChange={(e) => setForm({ ...form, expense_date: e.target.value })} />
          </label>
          <label>
            Vendor
            <input value={form.vendor} onChange={(e) => setForm({ ...form, vendor: e.target.value })} />
          </label>
          <label>
            Notes
            <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          </label>
          <button type="submit" className="button primary">
            Save Expense
          </button>
        </form>
      </FormModal>
    </div>
  );
}
