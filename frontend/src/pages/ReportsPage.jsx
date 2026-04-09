import { useEffect, useState } from "react";
import { reportsApi } from "../api/endpoints";
import { DataTable } from "../components/shared/DataTable";
import { PageHeader } from "../components/shared/PageHeader";
import { StatCard } from "../components/shared/StatCard";
import { formatTZS } from "../utils/currency";

export function ReportsPage() {
  const [filters, setFilters] = useState({ start: "", end: "" });
  const [report, setReport] = useState(null);

  const loadData = () => reportsApi.getReports(filters).then(({ data }) => setReport(data));

  useEffect(() => {
    loadData();
  }, []);

  return (
    <div className="page-stack">
      <PageHeader title="Reports" description="Analyze revenue, expenses, debt, and product performance by date." />
      <div className="filter-card">
        <label>
          Start Date
          <input type="date" value={filters.start} onChange={(e) => setFilters({ ...filters, start: e.target.value })} />
        </label>
        <label>
          End Date
          <input type="date" value={filters.end} onChange={(e) => setFilters({ ...filters, end: e.target.value })} />
        </label>
        <button type="button" className="button primary" onClick={loadData}>
          Apply
        </button>
      </div>
      {report ? (
        <>
          <section className="stats-grid">
            <StatCard label="Sales" value={report.summary.sales_total} />
            <StatCard label="Expenses" value={report.summary.expense_total} tone="warm" />
            <StatCard label="Payments" value={report.summary.payments_total} tone="accent" />
            <StatCard label="Outstanding Debt" value={report.summary.outstanding_debt} tone="alert" />
            <StatCard label="Transactions" value={report.summary.sales_count} currency={false} />
          </section>
          <DataTable
            columns={[
              { key: "items__product__name", label: "Top Product" },
              { key: "quantity", label: "Qty" },
              { key: "revenue", label: "Revenue", render: (row) => formatTZS(row.revenue) },
            ]}
            rows={report.top_products}
            emptyMessage="No top products for this date range."
          />
          <DataTable
            columns={[
              { key: "category", label: "Expense Category" },
              { key: "total", label: "Amount", render: (row) => formatTZS(row.total) },
            ]}
            rows={report.expense_breakdown}
            emptyMessage="No expense breakdown available."
          />
        </>
      ) : (
        <div className="state-card">Loading reports...</div>
      )}
    </div>
  );
}
