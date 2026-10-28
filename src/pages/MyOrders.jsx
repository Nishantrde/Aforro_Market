import { useEffect, useState } from 'react';
import { postJSON } from '../api';

export default function MyOrders({ onBack }) {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    fetch('/store/orders/list', { credentials: 'include' })
      .then((res) => res.json())
      .then((data) => setOrders(data))
      .catch((err) => console.error(err));
    }, []);

  async function cancel(orderId) {
  const { ok, data } = await postJSON(`/store/orders/${orderId}/cancel`, {});
  if (ok) {
    setOrders(prev => prev.map(o => o.id === orderId ? { ...o, status: 'CANCELLED' } : o));
  } else {
    alert(data.error || data.detail || 'Could not cancel');
  }
}

  return (
    <div className="p-6 space-y-4">
      {orders.length === 0 && <p>No orders yet</p>}

      {orders.map(order => (
        <div key={order.id} className="border rounded p-4">
          <p className="font-bold">Order #{order.id} - {order.store}</p>
          <p>Status: {order.status}</p>

          {order.items.map((item, i) => (
            <p key={i}>{item.name} x {item.quantity}</p>
          ))}

          <p>Total: ₹{order.total}</p>

          {(order.status === 'PLACED' || order.status === 'CONFIRMED') && (
            <button onClick={() => cancel(order.id)}>Cancel</button>
          )}
        </div>
      ))}

      <button onClick={onBack}>Back</button>
    </div>
  );
}