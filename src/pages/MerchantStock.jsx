import { useEffect, useState } from 'react';
import { postJSON } from '../api';
import { ui } from '../theme';

export default function MerchantStock({ onBack }) {
  const [rows, setRows] = useState([]);
  const [edits, setEdits] = useState({});   // typed values, keyed by "storeId-productId"

  useEffect(() => {
    fetch('/store/merchant/stock/list', { credentials: 'include' })
      .then(res => res.json())
      .then(data => setRows(data))
      .catch(err => console.error(err));
  }, []);

  async function save(row) {
    const k = row.store_id + '-' + row.product_id;
    const value = edits[k];
    // TODO 1: if value is undefined (nothing typed), return
    if(value === undefined){
        return
    }
    // TODO 2: const { ok, data } = await postJSON('/store/merchant/stock', {store_id: row.store_id, product_id: row.product_id, stock: value})
    const { ok, data } = await postJSON('/store/merchant/stock', {store_id: row.store_id, product_id: row.product_id, stock: value})
    
    // TODO 3: if ok, update that row's stock in rows (like MyOrders does with setOrders + map); else alert(data.error || 'Could not save')
    if (ok) {
        setRows(prev => prev.map(r =>
            (r.store_id === row.store_id && r.product_id === row.product_id)
            ? { ...r, stock: data.stock }
            : r
        ));
        setEdits(prev => { const next = { ...prev }; delete next[k]; return next; });
    } 
    else {
        alert(data.error || data.detail || 'Could not save');
    }
  }

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-stone-900">Shop stock</h1>
        <button onClick={onBack} className={ui.btnGhost}>Back</button>
      </div>

      {rows.length === 0 && <p className={ui.card + ' text-center ' + ui.muted}>No stock rows</p>}

      {rows.map(row => {
        const k = row.store_id + '-' + row.product_id;
        return (
          <div key={k} className={ui.card + ' flex items-center justify-between gap-3'}>
            <div>
              <p className="font-semibold">{row.name}</p>
              <p className={ui.muted}>{row.store} · now {row.stock}</p>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="number" min="0"
                className="w-20 rounded-lg border border-stone-300 px-2 py-1"
                value={edits[k] ?? row.stock}
                onChange={e => setEdits(prev => ({ ...prev, [k]: e.target.value }))}
              />
              <button onClick={() => save(row)} className={ui.btn}>Save</button>
            </div>
          </div>
        );
      })}
    </div>
  );
}