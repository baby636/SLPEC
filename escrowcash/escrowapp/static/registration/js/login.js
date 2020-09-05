const formElement = document.getElementById('login_form')
formElement.addEventListener('submit', storeToken)

function storeToken(event) {
    event.preventDefault()
    const str = document.getElementById('id_password').value
    crypto.subtle.digest('SHA-512', new TextEncoder().encode(str)).then(
    hashBuffer => {
        let hashArray = Array.from(new Uint8Array(hashBuffer))
        let hashHex = hashArray.map(
            byte => byte.toString(16).padStart(2, '0')
        ).join('')
        window.localStorage.setItem('token', hashHex)
        console.log(hashHex);
    })
    formElement.submit()
}