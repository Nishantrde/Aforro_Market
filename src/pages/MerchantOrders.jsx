import { useEffect, useState } from 'react';
import { postJSON } from '../api';
import { ui, statusStyle } from '../theme';

export default function MerchantOrders({onBack}){
      const [orders, setOrders] = useState([]);
      
    useEffect(() => {
        fetch('/store/merchant/orders', {credentials: "include"})
            .then(res => res.json())
            .then(data => setOrders(data))
            .catch(err => console.error(err))
    }, [])

    async function cancel(orderId) {
        const { ok, data } = await postJSON(`/store/orders/${orderId}/cancel`, {});
        if (ok) {
        setOrders(prev => prev.map(o => (o.id === orderId ? { ...o, status: 'CANCELLED' } : o)));
        } else {
        alert(data.error || data.detail || 'Could not cancel');
        }
    }

    async function status_packed(orderId) {
        const { ok, data } = await postJSON(`/store/orders/${orderId}/status`, {status: 'PACKED'});
        if (ok) {
        setOrders(prev => prev.map(o => (o.id === orderId ? { ...o, status: 'PACKED' } : o)));
        } else {
        alert(data.error || data.detail || 'Could not update the status');
        }
    }

    async function status_out_for_delivery(orderId) {
        const { ok, data } = await postJSON(`/store/orders/${orderId}/status`, {status: 'OUT_FOR_DELIVERY'});
        if (ok) {
        setOrders(prev => prev.map(o => (o.id === orderId ? { ...o, status: 'OUT_FOR_DELIVERY' } : o)));
        } else {
        alert(data.error || data.detail || 'Could not update the status');
        }
    }
    

    async function status_confirm(orderId) {
        const { ok, data } = await postJSON(`/store/orders/${orderId}/status`, {status:"CONFIRMED"});
        if (ok) {
        setOrders(prev => prev.map(o => (o.id === orderId ? { ...o, status: 'CONFIRMED' } : o)));
        } else {
        alert(data.error || data.detail || 'Could not update the status');
        }
    }

    return  (
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
            {(order.status === 'PLACED') && (
              <button onClick={() => status_confirm(order.id)} className={ui.btn}>Confirm</button>
            )}
            {(order.status === 'CONFIRMED') && (
              <button onClick={() => status_packed(order.id)} className={ui.btn}>Packed</button>
            )}
            {(order.status === 'PACKED') && (
              <button onClick={() => status_out_for_delivery(order.id)} className={ui.btn}>Out For delivery</button>
            )}
            <p className={ui.muted}>{order.store} · {order.customer}</p>
            
          </div>
          
        </div>
      ))}
    </div>
  );
}

