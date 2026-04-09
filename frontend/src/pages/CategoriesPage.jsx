import { useEffect, useState } from "react";
import { categoriesApi } from "../api/endpoints";
import { DataTable } from "../components/shared/DataTable";
import { FormModal } from "../components/shared/FormModal";
import { PageHeader } from "../components/shared/PageHeader";

export function CategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", description: "" });

  const loadCategories = () => categoriesApi.list().then(({ data }) => setCategories(data.results || data));

  useEffect(() => {
    loadCategories();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    await categoriesApi.create(form);
    setForm({ name: "", description: "" });
    setOpen(false);
    loadCategories();
  };

  return (
    <div className="page-stack">
      <PageHeader
        title="Categories"
        description="Organize stock by business line or product family."
        action={
          <button type="button" className="button primary" onClick={() => setOpen(true)}>
            Add Category
          </button>
        }
      />
      <DataTable
        columns={[
          { key: "name", label: "Name" },
          { key: "description", label: "Description" },
        ]}
        rows={categories}
      />
      <FormModal title="Create Category" open={open} onClose={() => setOpen(false)}>
        <form className="form-grid" onSubmit={handleSubmit}>
          <label>
            Name
            <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
          </label>
          <label>
            Description
            <textarea value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
          </label>
          <button type="submit" className="button primary">
            Save
          </button>
        </form>
      </FormModal>
    </div>
  );
}
