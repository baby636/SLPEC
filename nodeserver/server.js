const PaymentProtocol = require('bitcore-payment-protocol')
const express = require('express')
const jeton = require('jeton-lib')
const slpMdm = require('slp-mdm')
const BigNumber = require('bignumber.js')
const fs = require('fs')


const expressApp = express()
expressApp.use(express.urlencoded())
expressApp.use(express.json())

// TODO: use a HD wallet instead
const arbitratorPrivateKeyWIF = 'L22Y7NoNWPrhUbANpGrpcNQuHF2GzHW8J2MaDU6SQ4kcCwWQEmKg'
const arbitratorPublicKeyString = '025e46fdba10a39410082b5867aea3d5af2f6041ad82787e88cb1efe2574504862'
const x509Cert = fs.readFileSync('my.crt', "utf8");
const x509PrivateKey = fs.readFileSync('my.key', "utf8");


expressApp.post('/api/build_escrow_contract', (req, res) => {
    const arbitratorPubKey = jeton.PublicKey(arbitratorPublicKeyString)
    const partyOnePubKey = jeton.PublicKey(req.body.party_making_offer_pub_key)
    const partyTwoPubKey = jeton.PublicKey(req.body.party_making_offer_pub_key)
    
    const outputScriptData = {
        refereePubKey: arbitratorPubKey,
        parties : [
            {message: 'partyOneTakes', pubKey: partyOnePubKey},
            {message: 'partyTwoTakes', pubKey: partyTwoPubKey}
        ]
    }
    const outScript = new jeton.escrow.OutputScript(outputScriptData)
    console.log(outScript)
    const escrowCashAddress = outScript.toAddress().toCashAddress()

    res.status(200).send(
        {
            success: true,
            address: escrowCashAddress
        }
    )
})

expressApp.post('/api/release_contract', (req, res) => {
    const message = req.body.message
    const arbitratorPrivateKey = jeton.PrivateKey(arbitratorPrivateKeyWIF)

    // make sure message is valid
    assert(message == 'partyOneTakes' || message == 'partyTwoTakes')

    // signature for taker party to spend the funds
    const signature = jeton.Signature.signCDS(message, arbitratorPrivateKey)

    res.status(200).send({
        success: true,
        signature: signature.toString(),
	    arbitrator_pub_key: arbitratorPublicKeyString
    })

})

expressApp.post('/api/create_op_return_outputs', (req, res) => {
    BigNumber.set({ROUNDING_MODE: BigNumber.ROUND_UP})

    const arbitratorPubKey = jeton.PublicKey(arbitratorPublicKeyString)
    const feeAddress = arbitratorPubKey.toAddress()
    const contractAddress = jeton.Address(req.body.address)
    const token = req.body.token
    const amount = new BigNumber(req.body.amount)
    const fee = amount.times(0.01)


    const OPReturnScript = slpMdm.TokenType1.send(
        token,
        [amount.integerValue(), fee.integerValue()]
    ).toString('hex')
    const contractOutScript = jeton.Script.buildPublicKeyHashOut(contractAddress).toHex()
    const feeOutScript = jeton.Script.buildPublicKeyHashOut(feeAddress).toHex()

    res.status(200).send(
        {
            success: true,
            op_return: OPReturnScript,
            contract_output: contractOutScript,
            fee_output: feeOutScript
        }
    )
})

expressApp.post('/api/sign_payment_request', (req, res) => {
    console.log(req.body)

    const body = PaymentProtocol.PaymentRequest.decode(Buffer.from(req.body.payment_request,'hex'))
    let paymentRequest = new PaymentProtocol('BCH').makePaymentRequest(body)
    let certificates = new PaymentProtocol("BCH").makeX509Certificates();
    certificates.set("certificate", [ x509Cert ]);
    paymentRequest.set("pki_type", "x509+sha256");
    paymentRequest.set("pki_data", certificates.serialize());
    paymentRequest.sign(x509PrivateKey)
    
    console.log(paymentRequest)
    res.status(200).send(
        {
            success: true,
            payment_request: paymentRequest.serialize().toString('hex'),
        }
    )
})

expressApp.listen(3000, ()=>{console.log('server listening on port 3000')})
