 GET /info
This method return current info about Adventurecoin network.
https://api.adventurecoin.quest/info

{

    "error": null,
    "id": "api-server",
    "result": {
        "bestblockhash": "fe9fefc9e7628069707c97ef33c6d58461033407684d76e2157768e308eec413",
        "blocks": 92928,
        "chain": "main",
        "chainwork": "000000000000000000000000000000000000000000000000000007cead24d67f",
        "difficulty": 0.0105435269807142,
        "headers": 92928,
        "mediantime": 1763508925,
        "nethash": 226959,
        "reward": 27000000000,
        "supply": 2509083000000000
    }

}

GET /height/int:height
This method return block info by given height.
https://api.adventurecoin.quest/height/1

{

    "error": null,
    "id": "api-server",
    "result": {
        "bits": "1e3fffff",
        "chainwork": "0000000000000000000000000000000000000000000000000000000000080000",
        "confirmations": 92928,
        "difficulty": 0.00006103423947912204,
        "hash": "9e1e78d9d50128bd83407ca9610aa47d33256d2791b5e302729a57703f2de367",
        "height": 1,
        "mediantime": 1746274495,
        "merkleroot": "7718f6591f1d7792c744001e3356d016bfafa4245856459760cab1a84520846e",
        "nextblockhash": "c8ec07209f6e2782b2c609616873aaba47bd65e27b1cf3bd2326b62fb839d81e",
        "nonce": 56679,
        "previousblockhash": "da4aaa17fd5f1c7db85cfebdb56e1b5d89739b9bf8c7a23c4cdf07a9649469a8",
        "size": 250,
        "strippedsize": 250,
        "time": 1746274495,
        "tx": [
            "7718f6591f1d7792c744001e3356d016bfafa4245856459760cab1a84520846e"
        ],
        "txcount": 1,
        "version": 536870912,
        "versionHex": "20000000",
        "weight": 500
    }

}

height
offset
GET /block/string:hash
This method return block info by given hash.
https://api.adventurecoin.quest/block/c8ec07209f6e2782b2c609616873aaba47bd65e27b1cf3bd2326b62fb839d81e

{

    "error": null,
    "id": "api-server",
    "result": {
        "bits": "1e3fffff",
        "chainwork": "00000000000000000000000000000000000000000000000000000000000c0000",
        "confirmations": 92927,
        "difficulty": 0.00006103423947912204,
        "hash": "c8ec07209f6e2782b2c609616873aaba47bd65e27b1cf3bd2326b62fb839d81e",
        "height": 2,
        "mediantime": 1746274495,
        "merkleroot": "e91038ce6ad3bc14a5967fdeccd516e16c763c17294721ba6eb8876fcc9ea0a8",
        "nextblockhash": "e58813d39348145c6b33efc9b2a625da3f52f6c0ea78a17f7b778d5b18b1f8a8",
        "nonce": 50110,
        "previousblockhash": "9e1e78d9d50128bd83407ca9610aa47d33256d2791b5e302729a57703f2de367",
        "size": 250,
        "strippedsize": 250,
        "time": 1746274790,
        "tx": [
            "e91038ce6ad3bc14a5967fdeccd516e16c763c17294721ba6eb8876fcc9ea0a8"
        ],
        "txcount": 1,
        "version": 536870912,
        "versionHex": "20000000",
        "weight": 500
    }

}

hash
offset
GET /header/string:hash
This method return block header by given hash.
https://api.adventurecoin.quest/header/c8ec07209f6e2782b2c609616873aaba47bd65e27b1cf3bd2326b62fb839d81e

{

    "error": null,
    "id": "api-server",
    "result": {
        "bits": "1e3fffff",
        "chainwork": "00000000000000000000000000000000000000000000000000000000000c0000",
        "confirmations": 92927,
        "difficulty": 0.00006103423947912204,
        "hash": "c8ec07209f6e2782b2c609616873aaba47bd65e27b1cf3bd2326b62fb839d81e",
        "height": 2,
        "mediantime": 1746274495,
        "merkleroot": "e91038ce6ad3bc14a5967fdeccd516e16c763c17294721ba6eb8876fcc9ea0a8",
        "nextblockhash": "e58813d39348145c6b33efc9b2a625da3f52f6c0ea78a17f7b778d5b18b1f8a8",
        "nonce": 50110,
        "previousblockhash": "9e1e78d9d50128bd83407ca9610aa47d33256d2791b5e302729a57703f2de367",
        "time": 1746274790,
        "txcount": 1,
        "version": 536870912,
        "versionHex": "20000000"
    }

}

hash
GET /range/int:height
This method return range of blocks staring from certain height.
https://api.adventurecoin.quest/range/100?offset=3

{

    "error": null,
    "id": "api-server",
    "result": [
        {
            "bits": "1d0ef229",
            "chainwork": "0000000000000000000000000000000000000000000000000000000242379cc6",
            "confirmations": 92829,
            "difficulty": 0.06690678991359851,
            "hash": "c2be0691fe6c4a7e95c7aa709311399a27763a725a3fb25e4f77275183ab001f",
            "height": 100,
            "mediantime": 1746284918,
            "merkleroot": "cb86d99f364614fa69f7883a8585c10704014b1a60dbd05b95ab01e10d7165e0",
            "nethash": 9324,
            "nextblockhash": "29b24a9c45feb53dd04a5e702b6957f31760ad666ed716ef72272fe99a5cdd3f",
            "nonce": 1700097448,
            "previousblockhash": "d1763165f97b67bc3aa32f7b83f0445977ecc7048ee0feb3f49df2547646d142",
            "size": 323,
            "strippedsize": 323,
            "time": 1746285573,
            "tx": [
                "cb86d99f364614fa69f7883a8585c10704014b1a60dbd05b95ab01e10d7165e0"
            ],
            "txcount": 1,
            "version": 536870912,
            "versionHex": "20000000",
            "weight": 646
        },
        {
            "bits": "1d0f3779",
            "chainwork": "000000000000000000000000000000000000000000000000000000023116bdfb",
            "confirmations": 92830,
            "difficulty": 0.06571631130288466,
            "hash": "d1763165f97b67bc3aa32f7b83f0445977ecc7048ee0feb3f49df2547646d142",
            "height": 99,
            "mediantime": 1746284832,
            "merkleroot": "669d4b607eb4dff1fdb99cbe4e3d61839ba7dcbafc2c4656dd105171a0595cea",
            "nethash": 9049,
            "nextblockhash": "c2be0691fe6c4a7e95c7aa709311399a27763a725a3fb25e4f77275183ab001f",
            "nonce": 402655569,
            "previousblockhash": "bd15499b1a149d53da10fc17d873a65514878e4dc0406dafb8834a48927323fa",
            "size": 323,
            "strippedsize": 323,
            "time": 1746285498,
            "tx": [
                "669d4b607eb4dff1fdb99cbe4e3d61839ba7dcbafc2c4656dd105171a0595cea"
            ],
            "txcount": 1,
            "version": 536870912,
            "versionHex": "20000000",
            "weight": 646
        },
        {
            "bits": "1d0eed27",
            "chainwork": "000000000000000000000000000000000000000000000000000000022043e469",
            "confirmations": 92831,
            "difficulty": 0.06699447462981042,
            "hash": "bd15499b1a149d53da10fc17d873a65514878e4dc0406dafb8834a48927323fa",
            "height": 98,
            "mediantime": 1746284820,
            "merkleroot": "de1f9d655ef14977f0ee8ca0e8cbedbd8354c285258cce154c959c29437ee022",
            "nethash": 8779,
            "nextblockhash": "d1763165f97b67bc3aa32f7b83f0445977ecc7048ee0feb3f49df2547646d142",
            "nonce": 1946157786,
            "previousblockhash": "93d6aefb7d4170f365ec358434e6623e6ad4ce20d4a7206fc8dd60b78efafd89",
            "size": 323,
            "strippedsize": 323,
            "time": 1746285340,
            "tx": [
                "de1f9d655ef14977f0ee8ca0e8cbedbd8354c285258cce154c959c29437ee022"
            ],
            "txcount": 1,
            "version": 536870912,
            "versionHex": "20000000",
            "weight": 646
        }
    ]

}

height
offset
GET /balance/string:address
This method return address balance.
https://api.adventurecoin.quest/balance/AFqhbXTb3zpLszvhMeKGginfhVnegDj7Em

{

    "error": null,
    "id": "api-server",
    "result": {
        "balance": 3474799977048,
        "received": 4563633998315
    }

}

address
GET /mempool/string:address
This method return address mempool transactions.
https://api.adventurecoin.quest/mempool/AFqhbXTb3zpLszvhMeKGginfhVnegDj7Em

{

    "error": null,
    "id": "api-server",
    "result": {
        "tx": [],
        "txcount": 0
    }

}

address
GET /unspent/string:address
This method return address unspent outputs.
https://api.adventurecoin.quest/unspent/AFqhbXTb3zpLszvhMeKGginfhVnegDj7Em?amount=1

{

    "error": null,
    "id": "api-server",
    "result": [
        {
            "height": 28091,
            "index": 0,
            "script": "76a91400b946035147970c3f7cc027018e83f1df450de988ac",
            "txid": "d0c37e150164d9eb06597d6bae950c3781e11310d647428579d587cf78aaac94",
            "value": 1178300000000
        }
    ]

}

address
amount
GET /history/string:address
This method return list of address transaction hashes.
https://api.adventurecoin.quest/history/AFqhbXTb3zpLszvhMeKGginfhVnegDj7Em

{

    "error": null,
    "id": "api-server",
    "result": {
        "tx": [
            "b6189c3737fb2c136da7596be0cbbdd4ebcbceb6e5f4395940c3b1177597849a",
            "9e74f6e89d782425d2b02a3ef7c5ceac1251638e492625b93efaad704bd16ab1",
            "fdfb2d9f6ea01e33f550510baf7f4450e9373df2ed83a190603019eeff070b48",
            "f695b2d8239fe8bc007fd4d60d150cf1364033bcf33fb82f13b5b144894af021",
            "4a645037047ce8c0eac00f36d198b2736497f94b4a1f2ad4abd614b816b8f420",
            "1b882a5a6a1415ad7b6aef91110c26f68443a9b847c68d8d81322a3bd22b28e0",
            "6d68178ed41445f9665055f6926d7114e5c2ed602e00801dff2cc6e89e13c33b",
            "d0c37e150164d9eb06597d6bae950c3781e11310d647428579d587cf78aaac94",
            "8be4c02f1fc277c53f7aa781b8ee04d5ad544d026f9a09a0147c590ed94b49f8",
            "8a80202d5ac31085cfcc234f0d7625df1c87a8e0e364cfd34e22e6b6539a649e"
        ],
        "txcount": 13
    }

}

address
offset
GET /transaction/string:hash
This method return info about transaction.
https://api.adventurecoin.quest/transaction/cb86d99f364614fa69f7883a8585c10704014b1a60dbd05b95ab01e10d7165e0

{

    "error": null,
    "id": "api-server",
    "result": {
        "amount": 30000000000,
        "blockhash": "c2be0691fe6c4a7e95c7aa709311399a27763a725a3fb25e4f77275183ab001f",
        "blocktime": 1746285573,
        "confirmations": 92829,
        "hash": "cb86d99f364614fa69f7883a8585c10704014b1a60dbd05b95ab01e10d7165e0",
        "height": 100,
        "hex": "01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff4c0164040534166808fabe6d6d00000000000000000000000000000000000000000000000000000000000000000100000000000000f2206a8b000000000f706f6f6c2e72706c616e742e78797a00000000030000000000000000266a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9005ed0b2000000001976a914f6167db3b8ee8a9a221965a7da6eddb87485267388ac004e5349060000001976a914abae3a054a2a7cf67185049beb6ddc811e25fe9588ac00000000",
        "locktime": 0,
        "size": 242,
        "time": 1746285573,
        "txid": "cb86d99f364614fa69f7883a8585c10704014b1a60dbd05b95ab01e10d7165e0",
        "version": 1,
        "vin": [
            {
                "coinbase": "0164040534166808fabe6d6d00000000000000000000000000000000000000000000000000000000000000000100000000000000f2206a8b000000000f706f6f6c2e72706c616e742e78797a",
                "sequence": 0
            }
        ],
        "vout": [
            {
                "n": 0,
                "scriptPubKey": {
                    "asm": "OP_RETURN aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9",
                    "hex": "6a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9",
                    "type": "nulldata"
                },
                "value": 0
            },
            {
                "n": 1,
                "scriptPubKey": {
                    "addresses": [
                        "AeD4pPi3D5kB9aMEgH3eRHoD6XMKbrpRAW"
                    ],
                    "asm": "OP_DUP OP_HASH160 f6167db3b8ee8a9a221965a7da6eddb874852673 OP_EQUALVERIFY OP_CHECKSIG",
                    "hex": "76a914f6167db3b8ee8a9a221965a7da6eddb87485267388ac",
                    "reqSigs": 1,
                    "type": "pubkeyhash"
                },
                "value": 3000000000
            },
            {
                "n": 2,
                "scriptPubKey": {
                    "addresses": [
                        "AXRdunEc71n9oKLyLabAzV9eATRgkmGzMd"
                    ],
                    "asm": "OP_DUP OP_HASH160 abae3a054a2a7cf67185049beb6ddc811e25fe95 OP_EQUALVERIFY OP_CHECKSIG",
                    "hex": "76a914abae3a054a2a7cf67185049beb6ddc811e25fe9588ac",
                    "reqSigs": 1,
                    "type": "pubkeyhash"
                },
                "value": 27000000000
            }
        ],
        "vsize": 242
    }

}

hash
GET /mempool
This method return info about mempool.
https://api.adventurecoin.quest/mempool

{

    "error": null,
    "id": "api-server",
    "result": {
        "bytes": 0,
        "maxmempool": 300000000,
        "mempoolminfee": 0.00001,
        "minrelaytxfee": 0.00001,
        "size": 0,
        "tx": [],
        "usage": 64
    }

}

GET /supply
This method return info about current coins supply.
https://api.adventurecoin.quest/supply

{

    "error": null,
    "id": "api-server",
    "result": {
        "halvings": 0,
        "height": 92917,
        "supply": 2508786000000000
    }

}

GET /fee
This method return recomended transaction fee.
https://api.adventurecoin.quest/fee

{

    "error": null,
    "id": "api-server",
    "result": {
        "blocks": 30,
        "feerate": 1000000
    }

}

GET /decode/string:raw
This method return decoded info about transaction.
https://api.adventurecoin.quest/decode/01000000010000000000000000000000000000000000000000000000000000000000000000ffffffff4c0164040534166808fabe6d6d00000000000000000000000000000000000000000000000000000000000000000100000000000000f2206a8b000000000f706f6f6c2e72706c616e742e78797a00000000030000000000000000266a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9005ed0b2000000001976a914f6167db3b8ee8a9a221965a7da6eddb87485267388ac004e5349060000001976a914abae3a054a2a7cf67185049beb6ddc811e25fe9588ac00000000

{

    "error": null,
    "id": "api-server",
    "result": {
        "hash": "cb86d99f364614fa69f7883a8585c10704014b1a60dbd05b95ab01e10d7165e0",
        "locktime": 0,
        "size": 242,
        "txid": "cb86d99f364614fa69f7883a8585c10704014b1a60dbd05b95ab01e10d7165e0",
        "version": 1,
        "vin": [
            {
                "coinbase": "0164040534166808fabe6d6d00000000000000000000000000000000000000000000000000000000000000000100000000000000f2206a8b000000000f706f6f6c2e72706c616e742e78797a",
                "sequence": 0
            }
        ],
        "vout": [
            {
                "n": 0,
                "scriptPubKey": {
                    "asm": "OP_RETURN aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9",
                    "hex": "6a24aa21a9ede2f61c3f71d1defd3fa999dfa36953755c690689799962b48bebd836974e8cf9",
                    "type": "nulldata"
                },
                "value": 0
            },
            {
                "n": 1,
                "scriptPubKey": {
                    "addresses": [
                        "AeD4pPi3D5kB9aMEgH3eRHoD6XMKbrpRAW"
                    ],
                    "asm": "OP_DUP OP_HASH160 f6167db3b8ee8a9a221965a7da6eddb874852673 OP_EQUALVERIFY OP_CHECKSIG",
                    "hex": "76a914f6167db3b8ee8a9a221965a7da6eddb87485267388ac",
                    "reqSigs": 1,
                    "type": "pubkeyhash"
                },
                "value": 30
            },
            {
                "n": 2,
                "scriptPubKey": {
                    "addresses": [
                        "AXRdunEc71n9oKLyLabAzV9eATRgkmGzMd"
                    ],
                    "asm": "OP_DUP OP_HASH160 abae3a054a2a7cf67185049beb6ddc811e25fe95 OP_EQUALVERIFY OP_CHECKSIG",
                    "hex": "76a914abae3a054a2a7cf67185049beb6ddc811e25fe9588ac",
                    "reqSigs": 1,
                    "type": "pubkeyhash"
                },
                "value": 270
            }
        ],
        "vsize": 242
    }

}

transaction
POST /broadcast
This method broadcast raw signed transaction to Adventurecoin network.
https://api.adventurecoin.quest/broadcast

{

    "result": "8d0f52a1177c7a954cf4f952532c49c8d55f9437539b544d92f83c14e1929950",
    "error": null,
    "id": "api-server"

}

raw
