import React, {useEffect, useRef, useState} from 'react';
import Popup from 'reactjs-popup';
import SearchBar from './SearchBar';

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const handleLogout = async () => {
    try{
        const csrftoken = getCookie('csrftoken'); // Grab Django's CSRF token
        const response = await fetch('/user/logout',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,
            },
            credentials: 'include',
            
        })
        console.log("here");
        
        if(response.ok){
            window.location.href = "/"
        }
    } catch(error){
        console.log("Logout Failed: ",error);
        
    }
}



function LoginButton({ isLoggedIn, loginUrl, username }) {
    useEffect(()=>{
        function handelClickOutside(event){
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                console.log("clicked");
                
            }
        }
    })
    if (isLoggedIn) {
        return (
            <Popup trigger=
            {
                <button 
                    className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white font-medium text-xs sm:text-sm rounded-lg shadow-sm transition truncate max-w-[120px]"
                >
                    Hi, {username}
                </button>
            } position = "bottom center">
            
                <button onClick={handleLogout}
                 className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white font-medium text-xs sm:text-sm rounded-lg shadow-sm transition truncate max-w-[120px]" >Logout</button>
        
            </Popup>
        );
    }
    return (
        <a 
            href={loginUrl}
            className="px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white font-medium text-xs sm:text-sm rounded-lg shadow-sm transition"
        >
            Login
        </a>
    );
}

export default function NavBar({ isLoggedIn = false, name }) {
    const loginUrl = window.DJANGO_GOOGLE_LOGIN_URL || "#";

    return (
        <>
        
            {/* ROW 1: Logo, Login, and Cart */}
            <div className="flex justify-between items-center w-full">
                {/* Logo on the Left */}
                <img
                    src="/static/logo/aforoo_logo.png" 
                    alt="aforro logo" 
                    className="h-8 sm:h-10 w-auto object-contain"
                />

                {/* Right Side Actions (Login + Cart) */}
                <div className="flex items-center gap-2 sm:gap-3 shrink-0">
                    <LoginButton isLoggedIn={isLoggedIn} loginUrl={loginUrl} username={name} />
                    
                    {/* Cart button */}
                    <div className="relative p-1 text-gray-700 hover:text-black transition">
                        <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="size-7 sm:size-8">
                            <path d="M3 4h2.2l2.3 10.5h9.8L19.5 7H6"/>
                            <circle cx="9.5" cy="19" r="1.5"/>
                            <circle cx="16.5" cy="19" r="1.5"/>
                        </svg>
                    </div>
                </div>
            </div>

            
            </>
    );
}


