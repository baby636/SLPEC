const CryptoJS = require('crypto-js')
const jeton = require('jeton-lib')


function contractCreationAcceptanceFormHandler(formElementId, pubKeyElementId, privKeyElementId, token) {
    const form = document.getElementById(formElementId)
    const pubKeyElement =  document.getElementById(pubKeyElementId)
    const privKeyElement =  document.getElementById(privKeyElementId)

    function submitEventHandler(event) {
        event.preventDefault()
        pkey = jeton.PrivateKey()
        pubKeyElement.setAttribute(
            'value',
            pkey.toPublicKey().toString('hex')
            )
        privKeyElement.setAttribute(
            'value',
            CryptoJS.AES.encrypt(pkey.toWIF(), token).toString()
            )

        form.submit()
    }
    form.addEventListener('submit', submitEventHandler)
}

window.contractCreationAcceptanceFormHandler = contractCreationAcceptanceFormHandler
