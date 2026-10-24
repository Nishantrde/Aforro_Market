import React, { useState, useEffect } from 'react';

function ShowProducts() {
    const [products, setProducts] = useState([])

    useEffect(() => {
        fetch('/store/products')
            .then((res) => res.json())
            .then((data) => {
                setProducts(data)

            })
            .catch((err) => console.error(err))
    }, [])
    
    const categories = products.reduce((acc, product) => {
        const category = product.category || 'Uncategorized'
        
        if (!acc[category]){
            acc[category] = []
        }
        acc[category].push(product)
        return acc
    }, {})
    
    
    return (

        <div className="p-6 space-y-8">

            {/* 2. Loop through each category group */}
            {Object.entries(categories).map(([categoryName, items]) => (
                <div key={categoryName} className="space-y-4">
                    {/* Category Title */}
                    <h2 className="text-xl font-semibold text-blue-600 border-b pb-2">
                        {categoryName}
                    </h2>

                    {/* Products inside this category */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {items.map((item) => (
                            <div key={item.id} className="rounded-lg overflow-hidden shadow-lg bg-white p-4 border">
                                <div>
                                <div className="font-bold text-lg mb-1">
                                    {item.product_name}
                                </div>
                                <p className="text-gray-700 text-sm">
                                    Price: ₹{item.price}
                                </p>
                                </div>
                                <button 
                                    // onClick={() => handleBuy(item)}
                                    className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-4 rounded transition duration-200"
                                >
                                    Buy Now
                                </button>
                            </div>
                            
                        ))}

                    </div>
                </div>
            ))}
        </div>
    )

}

export default ShowProducts

