import React, {useEffect, useRef, useState} from 'react';
import Popup from 'reactjs-popup';

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
                <a href="/user/logout" className="px-3 py-1.5 bg-red-600 hover:bg-red-700 text-white font-medium text-xs sm:text-sm rounded-lg shadow-sm transition truncate max-w-[120px]" >Logout</a>
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
        <header className="w-full bg-white shadow-sm px-4 py-3 sm:px-6 sm:py-4">
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

            {/* ROW 2: Search Bar (Full width on mobile, perfectly spaced) */}
            <div className="mt-3 w-full">
                <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-gray-400">
                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4 sm:h-5 sm:w-5">
                            <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clipRule="evenodd" />
                        </svg>
                    </span>
                    <input 
                        type="text" 
                        placeholder='Search "milk", "bread", "vegetables"...' 
                        className="w-full pl-10 pr-4 py-2 bg-gray-100 rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:bg-white transition border border-transparent focus:border-amber-400"
                    />
                </div>
            </div>
        </header>
    );
}