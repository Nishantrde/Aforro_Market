import React, { useState, useEffect } from 'react';
import NavBar from './components/Navbar';
import Home from './pages/Home';
import { postJSON } from './api';
import Cart from './pages/Cart';
import MyOrders from './pages/MyOrders';
import MerchantOrders from './pages/MerchantOrders';
import { ui } from './theme';

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [cart, setCart] = useState([]);
  const [page, setPage] = useState('home');
  const [query, setQuery] = useState('');

  function addToCart(storeId, product) {
    setCart(prev => {
      const exists = prev.some(line => line.store_id === storeId && line.product_id === product.id);
      if (exists) {
        return prev.map(line =>
          line.store_id === storeId && line.product_id === product.id
            ? { ...line, quantity: line.quantity + 1 }
            : line
        );
      }
      return [...prev, {
        store_id: storeId,
        product_id: product.id,
        name: product.product_name,
        price: product.price,
        quantity: 1,
      }];
    });
  }

  async function checkout() {
    if (!user) return alert('Please login first');
    if (cart.length === 0) return alert('Cart is empty');
    const { ok, data } = await postJSON('/store/orders', { items: cart });
    if (ok) {
      setCart([]);
      setPage('orders');
    } else {
      alert(data.error || data.detail || 'Could not place order');
    }
  }

  useEffect(() => {
    fetch('/user/api/user/me', { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        if (data.is_authenticated) setUser(data);
        setLoading(false);
      })
      .catch(err => {
        console.log('Failed to fetch the session', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div className="flex h-screen items-center justify-center text-stone-500">Loading...</div>;
  }

  const cartCount = cart.reduce((sum, line) => sum + line.quantity, 0);

  return (
    <div className={ui.page}>
      <NavBar
        isLoggedIn={user ? user.is_authenticated : false}
        name={user ? user.name : ''}
        cartCount={cartCount}
        query={query}
        onSearch={value => { setQuery(value); setPage('home'); }}
        onCartClick={() => setPage('cart')}
        onOrdersClick={() => setPage('orders')}
        onLogoClick={() => setPage('home')}
        onMerchantOrdersClick={() => setPage('merchant_orders')}
        />
      <main className={ui.container + ' py-6'}>
        {page === 'home' && <Home addToCart={addToCart} query={query} />}
        {page === 'cart' && <Cart cart={cart} onCheckout={checkout} onBack={() => setPage('home')} />}
        {page === 'orders' && <MyOrders onBack={() => setPage('home')} />}
        {page === 'merchant_orders' && <MerchantOrders onBack={() => setPage('home')} />}
      </main>
    </div>
  );
}

export default App;