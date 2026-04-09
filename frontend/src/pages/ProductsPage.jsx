import { useEffect, useState } from "react";
import { categoriesApi, productsApi } from "../api/endpoints";
import { DataTable } from "../components/shared/DataTable";
import { FormModal } from "../components/shared/FormModal";
import { PageHeader } from "../components/shared/PageHeader";
import { formatTZS } from "../utils/currency";

export function ProductsPage() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({
    category: "",
    name: "",
    sku: "",
    description: "",
    unit: "pcs",
    selling_price: "",
    cost_price: "",
    stock_quantity: 0,
    low_stock_threshold: 5,
  });

  const loadData = async () => {
    const [productsResponse, categoriesResponse] = await Promise.all([productsApi.list(), categoriesApi.list()]);
    setProducts(productsResponse.data.results || productsResponse.data);
    setCategories(categoriesResponse.data.results || categoriesResponse.data);
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await productsApi.create(form);
    setOpen(false);
    setForm({
      category: "",
      name: "",
      sku: "",
      description: "",
      unit: "pcs",
      selling_price: "",
      cost_price: "",
      stock_quantity: 0,
      low_stock_threshold: 5,
    });
    loadData();
  };

  return (
    <div className="page-stack">
      <PageHeader
        title="Products"
        description="Manage pricing, stock levels, and low-stock thresholds."
        action={
          <button type="button" className="button primary" onClick={() => setOpen(true)}>
            Add Product
          </button>
        }
      />
      <DataTable
        columns={[
          { key: "name", label: "Product" },
          { key: "category_name", label: "Category" },
          { key: "sku", label: "SKU" },
          { key: "selling_price", label: "Price", render: (row) => formatTZS(row.selling_price) },
          { key: "stock_quantity", label: "Stock" },
          { key: "is_low_stock", label: "Alert", render: (row) => (row.is_low_stock ? "Low" : "OK") },
        ]}
        rows={products}
      />
      <FormModal title="Create Product" open={open} onClose={() => setOpen(false)}>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>
            Category
            <select required value={form.category} onChange={(e) => setForm({ ...form, category: Number(e.target.value) })}>
              <option value="">Select a category</option>
              {categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Product Name
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
          <label>
            SKU
            <input required value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} />
          </label>
          <label>
            Selling Price
            <input required type="number" min="0" value={form.selling_price} onChange={(e) => setForm({ ...form, selling_price: e.target.value })} />
          </label>
          <label>
            Cost Price
            <input required type="number" min="0" value={form.cost_price} onChange={(e) => setForm({ ...form, cost_price: e.target.value })} />
          </label>
          <label>
            Stock Quantity
            <input required type="number" min="0" value={form.stock_quantity} onChange={(e) => setForm({ ...form, stock_quantity: Number(e.target.value) })} />
          </label>
          <label>
            Low Stock Threshold
            <input required type="number" min="0" value={form.low_stock_threshold} onChange={(e) => setForm({ ...form, low_stock_threshold: Number(e.target.value) })} />
          </label>
          <label>
            Description
            <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </label>
          <button type="submit" className="button primary">
            Save Product
          </button>
        </form>
      </FormModal>
    </div>
  );
}
