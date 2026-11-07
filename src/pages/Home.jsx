import React, { useState, useEffect } from 'react';
import { ui } from '../theme';

function Home({ addToCart, query = '' }) {
  const [products, setProducts] = useState([]);
  const [stock, setStock] = useState({});
  const [stockLoaded, setStockLoaded] = useState(false);

  useEffect(() => {
    fetch('/store/products')
      .then(res => res.json())
      .then(data => setProducts(data))
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    fetch('/store/stock')
      .then(res => res.json())
      .then(data => {
        const map = {};
        data.forEach(r => { map[r.store_id + '-' + r.product_id] = r.stock; });
        setStock(map);
        setStockLoaded(true);
      })
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const ws = new WebSocket(`${proto}://${window.location.host}/ws/stock/`);
    ws.onmessage = (e) => {
      const m = JSON.parse(e.data);
      setStock(prev => ({ ...prev, [m.store_id + '-' + m.product_id]: m.stock }))
    };
    return () => ws.close();
  }, []);



  // Every typed word must appear in the product name. Empty query shows all.
  const words = query.toLowerCase().split(/\s+/).filter(Boolean);
  const visible = products.filter(p =>
    words.every(w => p.product_name.toLowerCase().includes(w))
  );

  const categories = visible.reduce((acc, product) => {
    const category = product.category || 'Uncategorized';
    if (!acc[category]) acc[category] = [];
    acc[category].push(product);
    return acc;
  }, {});

  async function handelBuy(item) {
    try {
      const res = await fetch(`/store/products/${item.id}/stores`);
      const stores = await res.json();
      if (stores.length === 0) return alert('Out of stock');
      addToCart(stores[0].store_id, item);
    } catch {
      return alert('Network error');
    }
  }

    function totalFor(productId) {
    let sum = 0;
    for (const key in stock) {
      if (key.endsWith('-' + productId)) sum += stock[key];
    }
    return sum;
  }


  return (
    <div className="space-y-8">
      {words.length > 0 && visible.length === 0 && (
        <p className={ui.card + ' text-center ' + ui.muted}>No products match "{query}"</p>
      )}
      {Object.entries(categories).map(([categoryName, items]) => (
        <section key={categoryName} className="space-y-3">
          <h2 className={ui.heading + ' border-b border-stone-200 pb-2'}>{categoryName}</h2>
          <div className="grid grid-cols-2 gap-3 sm:gap-4 md:grid-cols-3">
            {items.map(item => (
              <div key={item.id} className={ui.card + ' flex flex-col justify-between gap-3'}>
                <div>
                  <p className="font-semibold text-stone-900">{item.product_name}</p>
                  <p className="mt-1 text-lg font-bold text-green-700">₹{item.price}</p>
                  {stockLoaded && (() => {
                    const total = totalFor(item.id);
                    if (total === 0) return <p className="text-sm font-semibold text-red-600">Out of stock</p>;
                    if (total <= 5) return <p className="text-sm font-semibold text-amber-600">Only {total} left</p>;
                    return null;
                  })()}
                </div>
                <button onClick={() => handelBuy(item)} className={ui.btn + ' w-full'}>
                  Add to cart
                </button>
              </div>
            ))}
          </div>
        </section>
      ))}
    </div>
  );
}

export default Home;