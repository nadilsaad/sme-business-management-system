import { formatTZS } from "../../utils/currency";
import { formatDate } from "../../utils/date";

export function ReceiptPreview({ sale }) {
  if (!sale) return null;

  const printReceipt = () => {
    window.print();
  };

  return (
    <div className="receipt-card">
      <div className="receipt-head">
        <div>
          <p className="eyebrow">Printable Receipt</p>
          <h3>{sale.receipt_number}</h3>
        </div>
        <button type="button" className="button primary" onClick={printReceipt}>
          Print Receipt
        </button>
      </div>
      <p>Date: {formatDate(sale.created_at)}</p>
      <p>Customer: {sale.customer_name || "Walk-in customer"}</p>
      <table>
        <thead>
          <tr>
            <th>Item</th>
            <th>Qty</th>
            <th>Unit Price</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {sale.items?.map((item) => (
            <tr key={item.id}>
              <td>{item.product_name}</td>
              <td>{item.quantity}</td>
              <td>{formatTZS(item.unit_price)}</td>
              <td>{formatTZS(item.line_total)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="receipt-summary">
        <span>Subtotal</span>
        <strong>{formatTZS(sale.subtotal)}</strong>
        <span>Discount</span>
        <strong>{formatTZS(sale.discount)}</strong>
        <span>Total</span>
        <strong>{formatTZS(sale.total_amount)}</strong>
        <span>Paid</span>
        <strong>{formatTZS(sale.amount_paid)}</strong>
        <span>Balance</span>
        <strong>{formatTZS(sale.balance_due)}</strong>
      </div>
    </div>
  );
}
