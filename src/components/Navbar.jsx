import React from 'react';

export default function NavBar() {
    const loginUrl = window.DJANGO_GOOGLE_LOGIN_URL || "#";

    return (
        <header className="w-full flex justify-between items-center px-6 py-4 bg-white shadow-sm">
            {/* Logo on the Far Left */}
            <img
                src="/static/logo/aforoo_logo.png" 
                alt="aforro logo" 
                className="h-10 w-auto object-contain"
            />
            {/* 2. Search Bar in the Center */}
            <div className="flex-1 max-w-xl mx-4">
                <div className="relative">
                    <span className="absolute inset-y-0 left-0 flex items-center pl-3.5 pointer-events-none text-black">
                        <svg
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                            fill="currentColor"
                            className="h-5 w-5">
                            <path
                                fillRule="evenodd"
                                d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z"
                                clipRule="evenodd" />
                        </svg>
                    </span>
                    <input 
                        type="text" 
                        placeholder='Search "milk", "bread", "vegetables"...' 
                        className="w-full pl-10 pr-4 py-2 bg-gray-100 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-amber-400 focus:bg-white transition border border-transparent focus:border-amber-400"
                    />
                    
                </div>
            </div>
            {/* Login Button on the Far Right */}
            <div className="flex items-center gap-3 shrink-0">
            <a 
                href={loginUrl}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-semibold text-sm rounded-lg shadow-sm transition"
            >
                Login
            </a>
            {/* Cart button */}
                  <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" class="size-[1.9rem] shrink-0"><path d="M3 4h2.2l2.3 10.5h9.8L19.5 7H6"/><circle cx="9.5" cy="19" r="1.5"/><circle cx="16.5" cy="19" r="1.5"/></svg>
                  </div>
        </header>
    );
}