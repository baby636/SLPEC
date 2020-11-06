# SLPEscrowCash
Noncustodial new-user-friendly escrow service, making it the easiest possible to onboard new BCH users

Here I'm tackling a problem that I myself face, doing consultation and contract work and stuff like that,
I try to onboard new people I work with to use crypto. But it's so hard and complicated for them. So I'm create this service making it the easiest way possible for new users to come to crypto world when doing this type of stuff.

One other issue that is there is the BCH price change, you can't really put BCH to escrow for one months. SLP and stable coins solve that so I'm building it on
1- SLP
2- Vin Armani's postage protocol to solve the gas issue providing users a pure SLP experience
and PSF's implementation of a POST OFFICE SERVER

3-  A smart contract so the service can only say who gets the fund in case of problem and not be in possession of funds in any way whatsoever

4- Bitcoin.com's Link library to integrate with badger wallet to send assets and get addresses to withdraw funds to.

5- Implemented BIP70 to take 1% fee out of contracts but found out badger doesn't allow self signed certs to do payment requests. Knowing that other teams got the same issue, I forked and fixed it to find out it it has an issue with calculating fees properly so I disabled the it all together for now.

I use Django and python to handle most of the CRUD, and JS to do SLP and BCH parts.


All for trying to provide the best experience a new user can get to help adoption and for others to be able to deal on the internet totally trustless with no worries about the price change of assets.
