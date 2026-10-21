import { createRoot } from 'react-dom/client';
import React, { useState, useEffect } from 'react';
import NavBar from './components/Navbar';

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
    console.log("User: ",user);
    if(loading){
        return <div className="flex h-screen items-center justify-center">Loading...</div>
    }

    return (
        <NavBar/>
    );
}

export default App;

