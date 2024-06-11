from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from web3 import Web3

# Conexão com o nó Ethereum (Ganache)
ganache_url = 'http://127.0.0.1:7545'
w3 = Web3(Web3.HTTPProvider(ganache_url))

# Endereço e ABI do contrato
contract_address = '0xf8897b96Cc9980Fad2DAB220960De10bf913d0A3'
contract_abi = [
    # ABI fornecida pelo usuário
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "address",
                "name": "vencedor",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "valor",
                "type": "uint256"
            }
        ],
        "name": "FimDoLeilao",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "fimLeilao",
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
                "name": "ofertante",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "valor",
                "type": "uint256"
            }
        ],
        "name": "NovaMaiorProposta",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "proposta",
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
                "name": "restituido",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "uint256",
                "name": "valor",
                "type": "uint256"
            }
        ],
        "name": "RestituicaoOferta",
        "type": "event"
    },
    {
        "inputs": [],
        "name": "antigaOferta",
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
        "name": "antigoOfertante",
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
        "name": "casa",
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
        "name": "iniLeilao",
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
        "name": "maiorOferta",
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
        "name": "maiorOfertante",
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
        "name": "tempoLeilao",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]

# Inicializa o contrato
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

# Inicializa o FastAPI
app = FastAPI()

# Modelos de dados
class Proposal(BaseModel):
    value: float  # Valor em Ether
    sender: str
    private_key: str

class Sender(BaseModel):
    sender: str
    private_key: str

# Endpoints

@app.get("/maior_oferta")
async def get_maior_oferta():
    try:
        maior_oferta = contract.functions.maiorOferta().call()
        maior_ofertante = contract.functions.maiorOfertante().call()
        return {"maior_oferta": maior_oferta, "maior_ofertante": maior_ofertante}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/proposta")
async def post_proposta(proposal: Proposal):
    try:
        value = proposal.value
        sender = proposal.sender
        private_key = proposal.private_key

        # Converte o valor para Wei
        value_in_wei = int(value * 1e18)

        # Cria a transação
        nonce = w3.eth.get_transaction_count(sender)
        tx = {
            'chainId': 1,
            'gas': 2000000,
            'gasPrice': int(50 * 1e9),
            'nonce': nonce,
            'to': contract.address,
            'value': value_in_wei,
            'data': b''
        }

        # Assina a transação
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return {"tx_hash": w3.toHex(tx_hash)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fim_leilao")
async def post_fim_leilao(sender: Sender):
    try:
        casa = contract.functions.casa().call()
        if sender.sender.lower() != casa.lower():
            raise HTTPException(status_code=403, detail="Apenas o endereço da casa pode executar esta função")

        # Cria a transação
        nonce = w3.eth.get_transaction_count(sender.sender)
        tx = contract.functions.fimLeilao().buildTransaction({
            'chainId': 1,
            'gas': 2000000,
            'gasPrice': Web3.toWei('50', 'gwei'),
            'nonce': nonce
        })

        # Assina a transação
        signed_tx = w3.eth.account.sign_transaction(tx, sender.private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        return {"tx_hash": w3.toHex(tx_hash)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
