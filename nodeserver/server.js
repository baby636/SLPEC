const express = require('express')
const jeton = require('jeton-lib')


const expressApp = express()
expressApp.use(express.urlencoded())
expressApp.use(express.json())

// TODO: use a HD wallet instead
const arbitratorPrivateKeyWIF = 'L22Y7NoNWPrhUbANpGrpcNQuHF2GzHW8J2MaDU6SQ4kcCwWQEmKg'
const arbitratorPublicKeyString = '025e46fdba10a39410082b5867aea3d5af2f6041ad82787e88cb1efe2574504862'


expressApp.post('/api/build_escrow_contract', (req, res) => {
    const arbitratorPubKey = jeton.PublicKey(arbitratorPublicKeyString)
    const partyOnePubKey = jeton.PublicKey(req.body.party_making_offer_pub_key)
    const partyTwoPubKey = jeton.PublicKey(req.body.party_making_offer_pub_key)
    
    const outputScriptData = {
        refereePubKey: arbitratorPubKey,
        parties : [
            {message: 'partyOneTakes', pubKey: partyOnePubKey},
            {message: 'partyTwoTakes', pubkey: partyTwoPubKey}
        ]
    }
    const outScript = new new jeton.escrow.OutputScript(outputScriptData)
    const escrowCashAddress = outScript.toAddress()

    res.status(200).send(
        {
            success: true,
            address: escrowCashAddress
        }
    )
})

expressApp.listen(3000, ()=>{console.log('server listening on port 3000')})
