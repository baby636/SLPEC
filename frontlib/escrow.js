const PaymentProtocol = require('bitcore-payment-protocol')
const CryptoJS = require('crypto-js')
const jeton = require('jeton-lib')
const slpMdm = require('slp-mdm')
const bchaddr = require('bchaddrjs-slp')


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


async function getSLPBalanceForToken(address, token) {
    const balanceResponse = await fetch("https://rest.bitcoin.com/v2/slp/balancesForAddress/" + address)
    const balanceData = await balanceResponse.json()
    let balance = 0
    for (let i=0; i < balanceData.length; i++) {
        if (balanceData[i].tokenId == token){
            balance = new BigNumber(balanceData[i].balance).times(10 ** balanceData[i].decimalCount)
        }
    }
    return balance
}


async function withdrawFunds(
    withdrawAdress,
    token,
    arbitratorPublicKeyString,
    partyMakingOfferPubKeyString,
    partyTakingOfferPubKeyString,
    encryptedPrivKey,
    encryptedPrivKeySecret,
    message,
    postOfficeURL
    ) {
    const arbitratorPubKey = jeton.PublicKey(arbitratorPublicKeyString)
    const partyOnePubKey = jeton.PublicKey(partyMakingOfferPubKeyString)
    const partyTwoPubKey = jeton.PublicKey(partyTakingOfferPubKeyString)

    const outputScriptData = {
        refereePubKey: arbitratorPubKey,
        parties : [
            {message: 'partyOneTakes', pubKey: partyOnePubKey},
            {message: 'partyTwoTakes', pubKey: partyTwoPubKey}
        ]
    }
    const outScript = new jeton.escrow.OutputScript(outputScriptData)
    const escrowCashAddress = outScript.toAddress().toCashAddress()

    const balance = await getSLPBalanceForToken(escrowCashAddress, token)

    const utxoDataResponse = await fetch("https://rest.bitcoin.com/v2/address/utxo/" + escrowCashAddress)
    let utxoData = await utxoDataResponse.json()

    const estimatedTransactionSize = 2920 // just a big number to work TODO: later on calculate this
    // generate post office required data
    const postOfficeReponse = await fetch(postOfficeURL)
    let postOfficeData = await utxoDataResponse.json()
    const postOfficeSLPAddress = postOfficeData.address
    let tokenStampData;
    for (let i=0; i < postOfficeData.stamps.length; i++) {
        if (postOfficeData.stamps[i].tokenId == token){
            tokenStampData = postOfficeData.stamps[i]
        }
    }
    if (tokenStampData) {
        let stampUnitSize = new BigNumber(tokenStampData.rate / 10 ** tokenStampData.decimals)
        let stampSizeNeeded = stampUnitSize.times(
            new BigNumber(
                estimatedTransactionSize / postOfficeData.weight.integerVaule(BigNumber.ROUND_CEIL)
            )
        ).times(tokenStampData.decimals)
    }


    // inputs
    let inputUtxos = Array()
    for (let i=0; i < utxoData.utxos.length; i++) {
        utxo = utxoData.utxos[i]
        utxo.scriptPubKey = utxoData.scriptPubKey
        inputUtxos.push(
            new jeton.Transaction.UnspentOutput(utxo)
        )
    }

    let transaction = new jeton.Transaction(inputUtxos)
    // SLP
    transaction.addData()
    transaction.outputs[0].scriptBuffer = slpMdm.TokenType1.send(
        token,
        [balance.minus(stampSizeNeeded), stampSizeNeeded]
    )
    transaction.to(withdrawAdress, 546)
    transaction.to(bchaddr.toCashAddress(postOfficeSLPAddress), 546)

    // sign escrow contract
    for (let i=0; i < inputUtxos.length; i++) {
        transaction.signEscrow(
            i,
            CryptoJS.AES.decrypt(
                encryptedPrivKey,
                encryptedPrivKeySecret
            ).toString(CryptoJS.enc.Utf8),
            message,
            outScript.toScript(),
            jeton.Signature.SIGHASH_ALL | jeton.Signature.SIGHASH_FORKID | jeton.Signature.SIGHASH_ANYONECANPAY
        )
    }

    // create bip70 payment to postoffice
    let payment = new PaymentProtocol().makePayment()
    payment.set('memo', 'FREEDOM!')
    payment.set('transactions', [transaction.toBuffer()])
    
    let refundOutput = new PaymentProtocol().makeOutPut()
    refundOutput.set('amount', 546)
    refundOutput.set(
        'script',
        jeton.Script.buildPublicKeyHashOut(
            outScript.toAddress().toBuffer()
        )
    )
    payment.set('refund_to', [refundOutput.message])

    // send to post office
    const headers = {
        'Content-Type': 'application/simpleledger-payment',
        'Accept': 'application/simpleledger-paymentack, application/simpleledger-paymentrequest',
        'Content-Transfer-Encoding': 'binary'
    }
    const postOfficePaymentResponse = await fetch(
        postOfficeURL, 
        {
            method: 'POST',
            headers: headers,
            body: payment.serialize()
        }
    )
    if (postOfficePaymentResponse.status == 200) {
        window.alert('Transaction Went Through! Congrats!')
    }
    else {
        window.alert('Something went wrong! Please check console.')
        console.log('broadcast faild.')
        console.log(postOfficePaymentResponse.status)
        console.log(await postOfficePaymentResponse.json())
    }
}



window.contractCreationAcceptanceFormHandler = contractCreationAcceptanceFormHandler
window.withdrawFunds = withdrawFunds