import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { formatTZS } from "../../utils/currency";

const COLORS = ["#17926b", "#f2a900", "#0d6e6e", "#ef6f3c", "#5a714f"];

export function CategoryMixChart({ data }) {
  const chartData = data.map((item) => ({
    name: item["items__product__category__name"] || "Uncategorized",
    value: Number(item.total),
  }));

  return (
    <div className="chart-card">
      <h3>Category Revenue Mix</h3>
      <ResponsiveContainer width="100%" height={280}>
        <PieChart>
          <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={65} outerRadius={95} paddingAngle={3}>
            {chartData.map((entry, index) => (
              <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(value) => formatTZS(value)} />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
