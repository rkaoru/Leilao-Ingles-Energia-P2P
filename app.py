from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from pymongo import MongoClient
from fastapi.middleware.cors import CORSMiddleware
import json
import requests
from contract_connection import EthereumAuction
from bson import ObjectId 
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client.tcc
collection = db.ofertas

contract_address = '0xAe015Fe67407fefC1363C58Ad6E6d2ccBf43EF66'
contract_abi = json.loads('''[{"inputs":[{"internalType":"uint256","name":"_duracaoLeilaoEmMinutos","type":"uint256"},{"internalType":"address payable","name":"_beneficiario","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"comprador","type":"address"},{"indexed":false,"internalType":"uint256","name":"valor","type":"uint256"}],"name":"LancesRestituidos","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"vencedor","type":"address"},{"indexed":false,"internalType":"uint256","name":"valor","type":"uint256"}],"name":"LeilaoFinalizado","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"produtor","type":"address"},{"indexed":false,"internalType":"uint256","name":"quantidade","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"precoMinimoPorKwh","type":"uint256"}],"name":"NovaOferta","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"comprador","type":"address"},{"indexed":false,"internalType":"uint256","name":"valor","type":"uint256"}],"name":"NovoLance","type":"event"},{"inputs":[],"name":"beneficiario","outputs":[{"internalType":"address payable","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address payable","name":"_produtor","type":"address"},{"internalType":"uint256","name":"_quantidadeDisponivel","type":"uint256"},{"internalType":"uint256","name":"_precoMinimoPorKwhEmReais","type":"uint256"}],"name":"definirOferta","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"etherToReais","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"fazerLance","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"finalizarLeilao","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"lances","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"leilaoAtivo","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maiorLance","outputs":[{"internalType":"address payable","name":"comprador","type":"address"},{"internalType":"uint256","name":"valor","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"melhorLance","outputs":[{"internalType":"address","name":"comprador","type":"address"},{"internalType":"uint256","name":"valor","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"oferta","outputs":[{"internalType":"address payable","name":"produtor","type":"address"},{"internalType":"uint256","name":"quantidadeDisponivel","type":"uint256"},{"internalType":"uint256","name":"precoMinimoPorKwhEmReais","type":"uint256"},{"internalType":"bool","name":"ativa","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"participantes","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"retirarLance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"tempoFinal","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"tempoFinalLeilao","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]''')
ethereum_auction = EthereumAuction(contract_address, contract_abi)

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:5500", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Oferta(BaseModel):
    nome: str
    endereco_publico: str
    endereco_privado: str
    energia_disponivel: float
    preco_minimo: float

class OfertaInDB(Oferta):
    id: str
    time_limit: str
    maior_lance_publico: str = None
    maior_lance_valor: float = None
    quantidade_desejada: float = None

class LanceRequest(BaseModel):
    account_address: str
    private_key: str
    lance_reais: float
    oferta_id: str
    quantidade_desejada: float

class FinalizarLeilaoRequest(BaseModel):
    oferta_id: str
    beneficiario_address: str
    beneficiario_private_key: str

@app.post("/ofertas/", response_model=OfertaInDB)
def criar_oferta(oferta: Oferta):
    oferta_dict = oferta.dict()
    tempo_final_leilao = ethereum_auction.get_tempo_final_leilao()
    oferta_in_db = OfertaInDB(**oferta_dict, id="", time_limit=tempo_final_leilao) 
    result = collection.insert_one(oferta_in_db.dict())  
    oferta_in_db.id = str(result.inserted_id)  
    return oferta_in_db

@app.get("/ofertas/", response_model=List[OfertaInDB])
def listar_ofertas():
    ofertas = []
    for oferta in collection.find():
        oferta["id"] = str(oferta["_id"])
        del oferta["_id"]  
        ofertas.append(oferta)
    return ofertas

@app.post("/fazer_lance/")
async def fazer_lance(request: LanceRequest):
    try:
        valor_ethereum = request.lance_reais / get_eth_to_brl_conversion_rate()
        valor_wei = ethereum_auction.web3.to_wei(valor_ethereum, 'ether')
        tx_hash = ethereum_auction.fazer_lance(request.account_address, request.private_key, valor_wei)
        
        collection.update_one(
            {"_id": ObjectId(request.oferta_id)},
            {"$set": {
                "maior_lance_publico": request.account_address,
                "maior_lance_valor": request.lance_reais,
                "quantidade_desejada": request.quantidade_desejada
            }}
        )
        
        return {"status": "success", "transaction_hash": tx_hash.hex()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/finalizar_leilao/")
async def finalizar_leilao(request: FinalizarLeilaoRequest):
    try:
        tx_hash = ethereum_auction.finalizar_leilao(request.beneficiario_address, request.beneficiario_private_key)
        result = collection.delete_one({"_id": ObjectId(request.oferta_id)})
        return {"status": "success", "transaction_hash": tx_hash.hex()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get("/maior_lance/{oferta_id}")
def get_maior_lance(oferta_id: str):
    try:
        oferta = collection.find_one({"_id": ObjectId(oferta_id)})
        if oferta is None:
            raise HTTPException(status_code=404, detail="Oferta não encontrada")
        
        maior_lance_valor = oferta.get("maior_lance_valor", 0.0)
        maior_lance_comprador = oferta.get("maior_lance_publico", "")
        quantidade_proposta = oferta.get("quantidade_desejada", 0.0)

        return {
            "maior_lance": maior_lance_valor,
            "comprador": maior_lance_comprador,
            "quantidade_proposta": quantidade_proposta
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    
@app.get("/tempo_final_leilao/")
async def get_tempo_final_leilao():
    try:
        tempo_final = ethereum_auction.get_tempo_final_leilao()
        return {"tempo_final": tempo_final}
    except Exception as e:
        return {"error": str(e)}

def get_eth_to_brl_conversion_rate():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=brl"
    response = requests.get(url)
    data = response.json()
    return data['ethereum']['brl']
    # valor_ether_hoje = 19455 #19/06/2024
    # return valor_ether_hoje

def remover_ofertas_expiradas(collection):
    try:
        current_time = datetime.now()
        for oferta in collection.find():
            tempo_limite_oferta = datetime.strptime(oferta["time_limit"], "%Y-%m-%d %H:%M:%S")
            if current_time > tempo_limite_oferta:
                collection.delete_one({"_id": oferta["_id"]})
                print(f"Oferta expirada removida: {oferta['_id']}")
    except Exception as e:
        print(f"Erro ao remover ofertas expiradas: {str(e)}")

@app.post("/remover_ofertas_expiradas/")
async def remover_ofertas_expiradas_endpoint():
    remover_ofertas_expiradas(collection)
    return {"message": "Ofertas expiradas removidas imediatamente."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
