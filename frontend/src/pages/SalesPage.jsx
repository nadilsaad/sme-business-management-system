import { useEffect, useState } from "react";
import { customersApi, productsApi, salesApi } from "../api/endpoints";
import { DataTable } from "../components/shared/DataTable";
import { PageHeader } from "../components/shared/PageHeader";
import { ReceiptPreview } from "../components/shared/ReceiptPreview";
import { formatTZS } from "../utils/currency";
import { formatDate } from "../utils/date";

export function SalesPage() {
  const [sales, setSales] = useState([]);
  const [products, setProducts] = useState([]);
  const [customers, setCustomers] = useState([]);
  const [latestSale, setLatestSale] = useState(null);
  const [form, setForm] = useState({
    customer_id: "",
    discount: 0,
    amount_paid: 0,
    payment_method: "CASH",
    payment_reference: "",
    items: [{ product_id: "", quantity: 1 }],
  });

  const loadData = async () => {
    const [salesResponse, productsResponse, customersResponse] = await Promise.all([
      salesApi.list(),
      productsApi.list(),
      customersApi.list(),
    ]);
    setSales(salesResponse.data.results || salesResponse.data);
    setProducts(productsResponse.data.results || productsResponse.data);
    setCustomers(customersResponse.data.results || customersResponse.data);
  };

  useEffect(() => {
    loadData();
  }, []);

  const updateItem = (index, key, value) => {
    const items = [...form.items];
    items[index] = { ...items[index], [key]: value };
    setForm({ ...form, items });
  };

  const addItem = () => setForm({ ...form, items: [...form.items, { product_id: "", quantity: 1 }] });

  const handleSubmit = async (event) => {
    event.preventDefault();
    const { data } = await salesApi.create({
      ...form,
      customer_id: form.customer_id || null,
    });
    setLatestSale(data);
    setForm({
      customer_id: "",
      discount: 0,
      amount_paid: 0,
      payment_method: "CASH",
      payment_reference: "",
      items: [{ product_id: "", quantity: 1 }],
    });
    loadData();
  };

  return (
    <div className="page-stack">
      <PageHeader title="Sales" description="Create multi-item transactions and monitor receipt history." />
      <div className="split-grid">
        <form className="form-card" onSubmit={handleSubmit}>
          <h3>New Sale</h3>
          <label>
            Customer
            <select value={form.customer_id} onChange={(e) => setForm({ ...form, customer_id: Number(e.target.value) || "" })}>
              <option value="">Walk-in customer</option>
              {customers.map((customer) => (
                <option key={customer.id} value={customer.id}>
                  {customer.name}
                </option>
              ))}
            </select>
          </label>
          {form.items.map((item, index) => (
            <div key={index} className="row-inline">
              <label>
                Product
                <select required value={item.product_id} onChange={(e) => updateItem(index, "product_id", Number(e.target.value))}>
                  <option value="">Select product</option>
                  {products.map((product) => (
                    <option key={product.id} value={product.id}>
                      {product.name}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                Qty
                <input type="number" min="1" value={item.quantity} onChange={(e) => updateItem(index, "quantity", Number(e.target.value))} />
              </label>
            </div>
          ))}
          <button type="button" className="button ghost" onClick={addItem}>
            Add Item
          </button>
          <label>
            Discount
            <input type="number" min="0" value={form.discount} onChange={(e) => setForm({ ...form, discount: e.target.value })} />
          </label>
          <label>
            Amount Paid
            <input type="number" min="0" value={form.amount_paid} onChange={(e) => setForm({ ...form, amount_paid: e.target.value })} />
          </label>
          <label>
            Payment Method
            <select value={form.payment_method} onChange={(e) => setForm({ ...form, payment_method: e.target.value })}>
              <option value="CASH">Cash</option>
              <option value="MOBILE_MONEY">Mobile Money</option>
              <option value="BANK_TRANSFER">Bank Transfer</option>
            </select>
          </label>
          <label>
            Reference
            <input value={form.payment_reference} onChange={(e) => setForm({ ...form, payment_reference: e.target.value })} />
          </label>
          <button type="submit" className="button primary">
            Complete Sale
          </button>
        </form>
        <DataTable
          columns={[
            { key: "receipt_number", label: "Receipt" },
            { key: "customer_name", label: "Customer" },
            { key: "total_amount", label: "Total", render: (row) => formatTZS(row.total_amount) },
            { key: "balance_due", label: "Balance", render: (row) => formatTZS(row.balance_due) },
            { key: "created_at", label: "Date", render: (row) => formatDate(row.created_at) },
          ]}
          rows={sales}
        />
      </div>
      <ReceiptPreview sale={latestSale} />
    </div>
  );
}
