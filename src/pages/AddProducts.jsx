import { useEffect, useState } from 'react';
import { postJSON } from '../api';
import { ui, statusStyle } from '../theme';

export default function AddProducts({onBack}){

    return(
        <div className="mx-auto max-w-xl space-y-4">
        <div className="flex items-center justify-between gap-3 ">
                    <h1 className="text-xl font-bold text-stone-900">Your cart</h1>

            <button onClick={onBack} className={ui.btnGhost}>Back</button>
            
        </div>
        <div className={ui.card + ' divide-y divide-stone-100'}>
            {/* {cart.map(line => ( */}
            <div className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
                <div>
            <span className="font-semibold">Product Name</span>
               <input
          type="text"
          placeholder='"milk", "bread", "vegetables"...'
          className="w-full rounded-xl border border-transparent bg-stone-100 py-2.5 pl-2 pr-10 text-sm transition focus:border-amber-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-300"
        />
                <p className={ui.muted}></p>
                </div>
                <p className="font-semibold"></p>
            </div>
             {/* ))} */}
        </div>
        <div className={ui.card + ' items-center justify-between'}>
            <span className="font-semibold">Price</span>
            <input
          type="text"
          placeholder='"10", "20", "40".....'
          className="w-full rounded-xl border border-transparent bg-stone-100 py-2.5 pl-2 pr-10 text-sm transition focus:border-amber-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-300"
        />
        
        </div>

        <div className={ui.card + ' items-center justify-between'}>
            <span className="font-semibold">
                Stock
            </span>
            <input
          type="text"
          placeholder='"10", "50", "100".....'
          className="w-full rounded-xl border border-transparent bg-stone-100 py-2.5 pl-2 pr-10 text-sm transition focus:border-amber-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-amber-300"
        />
        
        </div>

        <div className="flex gap-3">
            <button onClick={onBack} className={ui.btn}>Add</button>
            
        </div>
        </div>
    )
}