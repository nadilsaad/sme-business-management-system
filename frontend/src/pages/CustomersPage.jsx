import { useEffect, useState } from "react";
import { customersApi } from "../api/endpoints";
import { DataTable } from "../components/shared/DataTable";
import { FormModal } from "../components/shared/FormModal";
import { PageHeader } from "../components/shared/PageHeader";
import { formatTZS } from "../utils/currency";

export function CustomersPage() {
  const [customers, setCustomers] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", phone: "", email: "", address: "", notes: "" });

  const loadData = () => customersApi.list().then(({ data }) => setCustomers(data.results || data));

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await customersApi.create(form);
    setOpen(false);
    setForm({ name: "", phone: "", email: "", address: "", notes: "" });
    loadData();
  };

  return (
    <div className="page-stack">
      <PageHeader
        title="Customers"
        description="Maintain customer records and keep visibility on debt exposure."
        action={
          <button type="button" className="button primary" onClick={() => setOpen(true)}>
            Add Customer
          </button>
        }
      />
      <DataTable
        columns={[
          { key: "name", label: "Name" },
          { key: "phone", label: "Phone" },
          { key: "email", label: "Email" },
          { key: "current_debt_balance", label: "Debt Balance", render: (row) => formatTZS(row.current_debt_balance) },
        ]}
        rows={customers}
      />
      <FormModal title="Create Customer" open={open} onClose={() => setOpen(false)}>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>
            Name
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
          <label>
            Phone
            <input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
          </label>
          <label>
            Email
            <input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          </label>
          <label>
            Address
            <input value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} />
          </label>
          <label>
            Notes
            <textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
          </label>
          <button type="submit" className="button primary">
            Save Customer
          </button>
        </form>
      </FormModal>
    </div>
  );
}
