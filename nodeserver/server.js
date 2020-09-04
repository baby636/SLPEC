const express = require('express')


const expressApp = express()


expressApp.post('/api/build_escrow_contract', (req, res) => {
    res.status(200).send(
        {
            success: true
        }
    )
})