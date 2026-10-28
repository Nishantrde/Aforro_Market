import { useEffect, useState } from 'react';
import { postJSON } from '../api';
import { ui, statusStyle } from '../theme';

export default function MyOrders({ onBack }) {
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    fetch('/store/orders/list', { credentials: 'include' })
      .then(res => res.json())
      .then(data => setOrders(data))
      .catch(err => console.error(err));
  }, []);

  async function cancel(orderId) {
    const { ok, data } = await postJSON(`/store/orders/${orderId}/cancel`, {});
    if (ok) {
      setOrders(prev => prev.map(o => (o.id === orderId ? { ...o, status: 'CANCELLED' } : o)));
    } else {
      alert(data.error || data.detail || 'Could not cancel');
    }
  }

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-stone-900">My orders</h1>
        <button onClick={onBack} className={ui.btnGhost}>Back</button>
      </div>

      {orders.length === 0 && <p className={ui.card + ' text-center ' + ui.muted}>No orders yet</p>}

      {orders.map(order => (
        <div key={order.id} className={ui.card + ' space-y-3'}>
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="font-bold text-stone-900">Order #{order.id}</p>
              <p className={ui.muted}>{order.store}</p>
            </div>
            <span className={'rounded-full px-3 py-1 text-xs font-semibold ' + (statusStyle[order.status] || 'bg-stone-100')}>
              {order.status.replaceAll('_', ' ')}
            </span>
          </div>

          <div className="space-y-1 text-sm">
            {order.items.map((item, i) => (
              <p key={i} className="flex justify-between">
                <span>{item.name} × {item.quantity}</span>
              </p>
            ))}
          </div>

          <div className="flex items-center justify-between border-t border-stone-100 pt-3">
            <p className="font-bold">₹{order.total}</p>
            {(order.status === 'PLACED' || order.status === 'CONFIRMED') && (
              <button onClick={() => cancel(order.id)} className={ui.btnDanger}>Cancel order</button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}