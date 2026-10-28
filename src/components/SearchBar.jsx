import React from 'react';

export default function SearchBar({ query, onChange }) {
  return (
    <div className="mt-3 w-full">
      <div className="relative">
        <span className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3.5 text-stone-400">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="h-4 w-4 sm:h-5 sm:w-5">
            <path fillRule="evenodd" d="M9 3.5a5.5 5.5 0 100 11 5.5 5.5 0 000-11zM2 9a7 7 0 1112.452 4.391l3.328 3.329a.75.75 0 11-1.06 1.06l-3.329-3.328A7 7 0 012 9z" clipRule="evenodd" />
          </svg>
        </span>
        <input
          type="text"
          placeholder='Search "milk", "bread", "vegetables"...'
          className="w-full rounded-xl border border-transparent bg-stone-100 py-2.5 pl-10 pr-10 text-sm transition focus:border-amber-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-300"
          value={query}
          onChange={e => onChange(e.target.value)}
        />
        {query && (
          <button
            onClick={() => onChange('')}
            aria-label="Clear search"
            className="absolute inset-y-0 right-0 px-3 text-stone-400 hover:text-stone-700"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
}