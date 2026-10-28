import React from 'react';
import Popup from 'reactjs-popup';
import SearchBar from './SearchBar';
import { getCookie } from '../api';
import { ui } from '../theme';

const handleLogout = async () => {
  try {
    const csrftoken = getCookie('csrftoken');
    const response = await fetch('/user/logout', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrftoken },
      credentials: 'include',
    });
    if (response.ok) window.location.href = '/';
  } catch (error) {
    console.log('Logout Failed: ', error);
  }
};

function LoginButton({ isLoggedIn, loginUrl, username }) {
  if (isLoggedIn) {
    return (
      <Popup
        trigger={<button className={ui.btn + ' max-w-[130px] truncate'}>Hi, {username}</button>}
        position="bottom center"
      >
        <button onClick={handleLogout} className={ui.btnDanger}>Logout</button>
      </Popup>
    );
  }
  return <a href={loginUrl} className={ui.btn}>Login</a>;
}

export default function NavBar({ isLoggedIn = false, name, cartCount = 0, query = '', onSearch, onCartClick, onOrdersClick, onLogoClick }) {
  const loginUrl = window.DJANGO_GOOGLE_LOGIN_URL || '#';

  return (
    <header className="sticky top-0 z-30 border-b border-stone-200 bg-white/95 backdrop-blur">
      <div className={ui.container + ' py-3'}>
        <div className="flex items-center justify-between gap-3">
          <img
            src="/static/logo/aforoo_logo.png"
            alt="aforro logo"
            onClick={onLogoClick}
            className="h-8 w-auto cursor-pointer object-contain sm:h-10"
          />
          <div className="flex shrink-0 items-center gap-2 sm:gap-3">
            <button onClick={onOrdersClick} className="text-sm font-semibold text-stone-600 transition hover:text-green-700">
              My orders
            </button>
            <button onClick={onCartClick} aria-label="Cart" className="relative p-1 text-stone-700 transition hover:text-green-700">
              <svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" className="size-7 sm:size-8">
                <path d="M3 4h2.2l2.3 10.5h9.8L19.5 7H6" />
                <circle cx="9.5" cy="19" r="1.5" />
                <circle cx="16.5" cy="19" r="1.5" />
              </svg>
              {cartCount > 0 && (
                <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-amber-400 px-1 text-xs font-bold text-stone-900">
                  {cartCount}
                </span>
              )}
            </button>
            <LoginButton isLoggedIn={isLoggedIn} loginUrl={loginUrl} username={name} />
          </div>
        </div>
        <SearchBar query={query} onChange={onSearch} />  
    </div>
    </header>
  );
}