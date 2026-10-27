import { createRoot } from 'react-dom/client';
import React, { useState, useEffect } from 'react';
import NavBar from './components/Navbar';
import Home from './pages/Home'
import SearchBar from './components/SearchBar';
import { postJSON } from './api'
import Cart from './pages/Cart'

function App() {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)
    const [cart, setCart] = useState([])
    const [page, setPage] = useState('home')
    

    function addToCart(storeId, product){
        setCart(prev => {
            const exists = prev.some(line => line.store_id === storeId && line.product_id === product.id);
            if (exists){
                return prev.map(line =>
                    line.store_id === storeId && line.product_id === product.id
                    ? { ...line, quantity: line.quantity + 1 }
                    : line
                )
            }
            return [...prev, {
                store_id: storeId,
                product_id: product.id,
                name: product.product_name,
                price: product.price,
                quantity: 1
            }];
        })
    }


    async function checkout(){
        if (!user) return alert('Please login first');

        if(cart.length === 0){
            return alert('Cart is empty');
        }
        const { ok, data } = await postJSON('/store/orders', { items: cart })
        if(ok){
            setCart([])
            setPage('home')
            return alert("Order placed")
        }
        else{
            alert(data.error || data.detail || "Could not place order")
        }

    }


    useEffect(() => {
        fetch('/user/api/user/me', {
            credentials: "include",
        })
            .then((res) => res.json())
            .then((data) => {
                if (data.is_authenticated) {
                    setUser(data)
                    
                }
                setLoading(false)
            })
            .catch((err) => {
                console.log("Failed to fetch the session", err)
                setLoading(false)
            })
    }, [])

    console.log(cart);
    
    if(loading){
        return <div className="flex h-screen items-center justify-center">Loading...</div>
    }

    return (
        <>
        <header className="w-full bg-white shadow-sm px-4 py-3 sm:px-6 sm:py-4">
            <button onClick={checkout}>Checkout ({cart.length})</button>
        <NavBar isLoggedIn = {user ? user.is_authenticated : false}
        name = {user ? user.name : ""} onCartClick={() => setPage('cart')} />
            <SearchBar/>
        </header>
        {page === 'home' && <Home addToCart={addToCart} />}
        {page === 'cart' && <Cart cart={cart} onCheckout={checkout} onBack={() => setPage('home')} />}
        </>

    );
}

export default App;

