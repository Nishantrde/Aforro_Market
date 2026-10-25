import { createRoot } from 'react-dom/client';
import React, { useState, useEffect } from 'react';
import NavBar from './components/Navbar';
import Home from './pages/Home'
import SearchBar from './components/SearchBar';

function App() {
    const [user, setUser] = useState(null)
    const [loading, setLoading] = useState(true)

    
    const logoutUrl = "/user/logout"; // Default django-allauth logout url

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
    if(loading){
        return <div className="flex h-screen items-center justify-center">Loading...</div>
    }

    return (
        <>
        <header className="w-full bg-white shadow-sm px-4 py-3 sm:px-6 sm:py-4">
        <NavBar isLoggedIn = {user ? user.is_authenticated : false}
        name = {user ? user.name : ""}/>
        {/* ROW 2: Search Bar (Full width on mobile, perfectly spaced) */}
            <SearchBar/>
        </header>
        <Home/>
        </>

    );
}

export default App;

