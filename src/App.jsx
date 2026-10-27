import { createRoot } from 'react-dom/client';
import React, { useState, useEffect } from 'react';
import NavBar from './components/Navbar';
import Home from './pages/Home'
import SearchBar from './components/SearchBar';
import { postJSON } from './api'

function App() {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)
    const [cart, setCart] = useState([])
    
    const logoutUrl = "/user/logout"; // Default django-allauth logout url

    function addToCart(storeId, productId){
        setCart(prev => {
            const exists = prev.some(item => item.store_id === storeId && item.product_id === productId);
            if (exists){
                return prev.map(item=>
                    item.store_id === storeId && item.product_id === productId
                    ? { ...item, quantity: item.quantity + 1 }
                    : item
                )
            }
            return [...prev, { store_id: storeId, product_id: productId, quantity: 1 }];

        })
    }

    async function checkout(){
        if(cart.length === 0){
            return alert('Cart is empty');
        }
        const { ok, data } = await postJSON('/store/orders', { items: cart })
        if(ok){
            setCart([])
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
        name = {user ? user.name : ""}/>
        {/* ROW 2: Search Bar (Full width on mobile, perfectly spaced) */}
            <SearchBar/>
        </header>
        <Home addToCart={addToCart}/>
        </>

    );
}

export default App;

