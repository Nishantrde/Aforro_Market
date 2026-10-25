import React, {useEffect, useRef, useState} from 'react';




export default function SearchBar(){
    const [query, setQuery] = useState('')
    const [suggestions, setSuggestions] = useState([])

    // On each keystroke, the effect starts a 300ms timer.
    // Only when you stop typing for 300ms does the timer finish and the fetch run.
    // If you type again within 300ms, React first runs the function you return. This is called cleanup, and it cancels the old timer. Then it starts a new one.

    useEffect(()=>{
        let cancelled = false                      
        if (query.trim() === '') {
                setSuggestions([])
                return
            }
        const timer = setTimeout(()=>{
            
            fetch(`/store/products?q=${encodeURIComponent(query.trim())}`)
            .then((res) => res.json())
            .then((data) => {
                if (!cancelled) setSuggestions(data.slice(0, 5))
            })
        }, 300)
        
        return () => {
            cancelled = true
            clearTimeout(timer)
        }
    },[query])

    return(
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
                value={query} onChange={(e)=>{setQuery(e.target.value)}}
            />
            {suggestions.length > 0 && (
                <ul className="absolute z-20 mt-2 w-full bg-white rounded-xl shadow-lg border">
                    {suggestions.map((item)=>(
                        <li key={item.id} className="px-4 py-2 hover:bg-amber-50 cursor-pointer text-sm" onClick={() => { setQuery(item.product_name); setSuggestions([]) }}>
                            {item.product_name}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    </div>
    )
}


