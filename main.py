from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import requests
from app_otim import EthereumAuction

contract_address = '0x8cfb9aCe569d5f975B1e0c761ce276D0358B5DF8'
contract_abi = json.loads('''[{"inputs":[{"internalType":"uint256","name":"_duracaoLeilaoEmMinutos","type":"uint256"},{"internalType":"address payable","name":"_beneficiario","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"comprador","type":"address"},{"indexed":false,"internalType":"uint256","name":"valor","type":"uint256"}],"name":"LancesRestituidos","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"vencedor","type":"address"},{"indexed":false,"internalType":"uint256","name":"valor","type":"uint256"}],"name":"LeilaoFinalizado","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"produtor","type":"address"},{"indexed":false,"internalType":"uint256","name":"quantidade","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"precoMinimoPorKwh","type":"uint256"}],"name":"NovaOferta","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"comprador","type":"address"},{"indexed":false,"internalType":"uint256","name":"valor","type":"uint256"}],"name":"NovoLance","type":"event"},{"inputs":[],"name":"beneficiario","outputs":[{"internalType":"address payable","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address payable","name":"_produtor","type":"address"},{"internalType":"uint256","name":"_quantidadeDisponivel","type":"uint256"},{"internalType":"uint256","name":"_precoMinimoPorKwhEmReais","type":"uint256"}],"name":"definirOferta","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"etherToReais","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"fazerLance","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"finalizarLeilao","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"lances","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"leilaoAtivo","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maiorLance","outputs":[{"internalType":"address payable","name":"comprador","type":"address"},{"internalType":"uint256","name":"valor","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"melhorLance","outputs":[{"internalType":"address","name":"comprador","type":"address"},{"internalType":"uint256","name":"valor","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"oferta","outputs":[{"internalType":"address payable","name":"produtor","type":"address"},{"internalType":"uint256","name":"quantidadeDisponivel","type":"uint256"},{"internalType":"uint256","name":"precoMinimoPorKwhEmReais","type":"uint256"},{"internalType":"bool","name":"ativa","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"participantes","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"retirarLance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"tempoFinal","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]''')

ethereum_auction = EthereumAuction(contract_address, contract_abi)

app = FastAPI()

class LanceRequest(BaseModel):
    account_address: str
    private_key: str
    lance_reais: float

class FinalizarLeilaoRequest(BaseModel):
    beneficiario_address: str
    beneficiario_private_key: str

@app.post("/fazer-lance/")
async def fazer_lance(request: LanceRequest):
    try:
        valor_ethereum = request.lance_reais / get_eth_to_brl_conversion_rate()
        valor_wei = ethereum_auction.web3.to_wei(valor_ethereum, 'ether')
        tx_hash = ethereum_auction.fazer_lance(request.account_address, request.private_key, valor_wei)
        return {"status": "success", "transaction_hash": tx_hash.hex()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/finalizar-leilao/")
async def finalizar_leilao(request: FinalizarLeilaoRequest):
    try:
        tx_hash = ethereum_auction.finalizar_leilao(request.beneficiario_address, request.beneficiario_private_key)
        vencedor = ethereum_auction.get_best_bid()
        return {"status": "success", "transaction_hash": tx_hash.hex(), "vencedor": vencedor[0]}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

def get_eth_to_brl_conversion_rate():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=brl"
    response = requests.get(url)
    data = response.json()
    return data['ethereum']['brl']

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)