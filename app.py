from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from web3 import Web3
from pydantic import BaseModel
import time
from typing import Optional
from typing import List

# Conexão com o nó Ethereum
ganache_url = 'http://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(ganache_url))

# Endereço e ABI do contrato
contract_address = '0x0415C7A80D22BDEaA7d0Aa9F5E451d67DfAb755a'
contract_abi = [
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_quantidadeDisponivel",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_precoMinimoPorKwhEmReais",
				"type": "uint256"
			}
		],
		"name": "cadastrarOferta",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "address",
				"name": "comprador",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "quantidade",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "preco",
				"type": "uint256"
			}
		],
		"name": "CompraEfetuada",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_ofertaIndex",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_quantidadeDesejada",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_precoOferecidoEmReais",
				"type": "uint256"
			}
		],
		"name": "fazerProposta",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "finalizarCompra",
		"outputs": [],
		"stateMutability": "payable",
		"type": "function"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "address",
				"name": "produtor",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "quantidade",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "precoMinimoPorKwh",
				"type": "uint256"
			}
		],
		"name": "NovaOferta",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "address",
				"name": "comprador",
				"type": "address"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "ofertaIndex",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "quantidade",
				"type": "uint256"
			},
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "preco",
				"type": "uint256"
			}
		],
		"name": "NovaProposta",
		"type": "event"
	},
	{
		"anonymous": False,
		"inputs": [
			{
				"indexed": False,
				"internalType": "uint256",
				"name": "ofertaIndex",
				"type": "uint256"
			}
		],
		"name": "OfertaEsgotada",
		"type": "event"
	},
	{
		"inputs": [],
		"name": "comprador",
		"outputs": [
			{
				"internalType": "address",
				"name": "",
				"type": "address"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "etherToReais",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "numeroOfertas",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"name": "ofertas",
		"outputs": [
			{
				"internalType": "address",
				"name": "produtor",
				"type": "address"
			},
			{
				"internalType": "uint256",
				"name": "quantidadeDisponivel",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "precoMinimoPorKwhEmReais",
				"type": "uint256"
			},
			{
				"internalType": "bool",
				"name": "ativa",
				"type": "bool"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "precoTotal",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "quantidadeComprada",
		"outputs": [
			{
				"internalType": "uint256",
				"name": "",
				"type": "uint256"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [],
		"name": "visualizarOfertas",
		"outputs": [
			{
				"components": [
					{
						"internalType": "address",
						"name": "produtor",
						"type": "address"
					},
					{
						"internalType": "uint256",
						"name": "quantidadeDisponivel",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "precoMinimoPorKwhEmReais",
						"type": "uint256"
					},
					{
						"internalType": "bool",
						"name": "ativa",
						"type": "bool"
					}
				],
				"internalType": "struct MercadoEnergia.Oferta[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
] # ABI do contrato

# Instanciar contrato
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Oferta(BaseModel):
    quantidade_disponivel: int
    preco_minimo_por_kwh_em_reais: int
    sender_address: str

@app.post("/cadastrar_oferta")
async def cadastrar_oferta(oferta: Oferta):
    try:
        tx_hash = contract.functions.cadastrarOferta(
            oferta.quantidade_disponivel, oferta.preco_minimo_por_kwh_em_reais
        ).transact({'from': oferta.sender_address})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return {"message": "Oferta cadastrada com sucesso", "transaction_hash": tx_hash.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/offers")
async def get_offers():
    result = contract.functions.visualizarOfertas().call()
    offers = []
    for offer in result:
        offers.append({
            "produtor": offer[0],
            "quantidadeDisponivel": offer[1],
            "precoMinimoPorKwhEmReais": offer[2],
            "ativa": offer[3]
        })
    return {"offers": offers, "transaction_hash": None}

@app.post("/fazer_proposta/{oferta_index}/{quantidade_desejada}/{preco_oferecido_em_reais}")
async def fazer_proposta(oferta_index: int, quantidade_desejada: int, preco_oferecido_em_reais: int, sender_address: str):
    try:
        tx_hash = contract.functions.fazerProposta(oferta_index, quantidade_desejada, preco_oferecido_em_reais).transact({'from': sender_address})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return {"message": "Proposta feita com sucesso", "transaction_hash": tx_hash.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/finalizar_compra/")
async def finalizar_compra(sender_address: str):
    try:
        tx_hash = contract.functions.finalizarCompra().transact({'from': sender_address, 'value': contract.functions.precoTotal().call()})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return {"message": "Compra finalizada com sucesso", "transaction_hash": tx_hash.hex()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# @app.get("/encontrar_melhor_oferta/{quantidade_desejada}")
# async def encontrar_melhor_oferta(quantidade_desejada: int):
#     try:
#         melhor_oferta = contract.functions._encontrarMelhorOferta(quantidade_desejada).call()
#         return {"melhor_oferta": melhor_oferta}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))