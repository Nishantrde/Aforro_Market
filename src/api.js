export function getCookie(name){
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

export async function postJSON(url, body){
    const csrftoken = getCookie('csrftoken')
    try{
        const responce = await fetch(url, {
            method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken,
                },
                credentials: 'include',
                body: JSON.stringify(body)
                
            })
            let data = {}
            try{
                data = await responce.json()
            }
            catch(error){
                console.log(`${error}`);
                data = {}
            }
            return {"ok": responce.ok, "data": data}
    }
    catch(error){
        return { "ok": false, "data": { error: 'Network error' } }
    }
}


