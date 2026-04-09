import { useEffect, useState } from "react";
import { inventoryApi, productsApi } from "../api/endpoints";
import { DataTable } from "../components/shared/DataTable";
import { FormModal } from "../components/shared/FormModal";
import { PageHeader } from "../components/shared/PageHeader";
import { formatDate } from "../utils/date";

export function InventoryPage() {
  const [movements, setMovements] = useState([]);
  const [products, setProducts] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ product_id: "", movement_type: "IN", quantity: 1, reference: "", notes: "" });

  const loadData = async () => {
    const [movementsResponse, productsResponse] = await Promise.all([inventoryApi.movements(), productsApi.list()]);
    setMovements(movementsResponse.data.results || movementsResponse.data);
    setProducts(productsResponse.data.results || productsResponse.data);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await inventoryApi.adjust(form);
    setOpen(false);
    setForm({ product_id: "", movement_type: "IN", quantity: 1, reference: "", notes: "" });
    loadData();
  };

  return (
    <div className="page-stack">
      <PageHeader
        title="Inventory"
        description="Track stock movement history and manual stock adjustments."
        action={
          <button type="button" className="button primary" onClick={() => setOpen(true)}>
            Record Movement
          </button>
        }
      />
      <DataTable
        columns={[
          { key: "product_name", label: "Product" },
          { key: "movement_type", label: "Type" },
          { key: "quantity", label: "Quantity" },
          { key: "reference", label: "Reference" },
          { key: "created_at", label: "Date", render: (row) => formatDate(row.created_at) },
        ]}
        rows={movements}
      />
      <FormModal title="Stock Adjustment" open={open} onClose={() => setOpen(false)}>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>
            Product
            <select required value={form.product_id} onChange={(e) => setForm({ ...form, product_id: Number(e.target.value) })}>
              <option value="">Select product</option>
              {products.map((product) => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Movement Type
            <select value={form.movement_type} onChange={(e) => setForm({ ...form, movement_type: e.target.value })}>
              <option value="IN">Stock In</option>
              <option value="OUT">Stock Out</option>
              <option value="ADJUSTMENT">Adjustment</option>
            </select>
          </label>
          <label>
            Quantity
            <input type="number" min="1" value={form.quantity} onChange={(e) => setForm({ ...form, quantity: Number(e.target.value) })} />
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
            Submit
          </button>
        </form>
      </FormModal>
    </div>
  );
}
