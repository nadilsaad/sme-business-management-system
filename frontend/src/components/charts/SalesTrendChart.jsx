import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { formatTZS } from "../../utils/currency";

export function SalesTrendChart({ data }) {
  return (
    <div className="chart-card">
      <h3>Sales Trend</h3>
      <ResponsiveContainer width="100%" height={280}>
        <AreaChart data={data}>
          <defs>
            <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#17926b" stopOpacity={0.8} />
              <stop offset="95%" stopColor="#17926b" stopOpacity={0.08} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#dfe6dc" />
          <XAxis dataKey="day" />
          <YAxis tickFormatter={(value) => formatTZS(value)} />
          <Tooltip formatter={(value) => formatTZS(value)} />
          <Area type="monotone" dataKey="total" stroke="#17926b" fill="url(#salesGradient)" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
