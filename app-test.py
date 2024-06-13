import json
from web3 import Web3
import requests

# Conectando ao nó Ethereum (pode ser um nó local ou Infura)
web3 = Web3(Web3.HTTPProvider('http://localhost:7545'))  # Altere para seu provedor

# Endereço do contrato e ABI (substitua pelo endereço do seu contrato e ABI)
contract_address = '0xEed1260a0312ba9E24437961FC6BFCB1a922b86c'
contract_abi = json.loads('''[{"inputs":[{"internalType":"uint256","name":"_duracaoLeilaoEmMinutos","type":"uint256"},{"internalType":"address payable","name":"_beneficiario","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"comprador","type":"address"},{"indexed":false,"internalType":"uint256","name":"valor","type":"uint256"}],"name":"LancesRestituidos","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"vencedor","type":"address"},{"indexed":false,"internalType":"uint256","name":"valor","type":"uint256"}],"name":"LeilaoFinalizado","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"produtor","type":"address"},{"indexed":false,"internalType":"uint256","name":"quantidade","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"precoMinimoPorKwh","type":"uint256"}],"name":"NovaOferta","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"comprador","type":"address"},{"indexed":false,"internalType":"uint256","name":"valor","type":"uint256"}],"name":"NovoLance","type":"event"},{"inputs":[],"name":"beneficiario","outputs":[{"internalType":"address payable","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address payable","name":"_produtor","type":"address"},{"internalType":"uint256","name":"_quantidadeDisponivel","type":"uint256"},{"internalType":"uint256","name":"_precoMinimoPorKwhEmReais","type":"uint256"}],"name":"definirOferta","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"etherToReais","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"fazerLance","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"finalizarLeilao","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"lances","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"leilaoAtivo","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maiorLance","outputs":[{"internalType":"address payable","name":"comprador","type":"address"},{"internalType":"uint256","name":"valor","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"melhorLance","outputs":[{"internalType":"address","name":"comprador","type":"address"},{"internalType":"uint256","name":"valor","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"oferta","outputs":[{"internalType":"address payable","name":"produtor","type":"address"},{"internalType":"uint256","name":"quantidadeDisponivel","type":"uint256"},{"internalType":"uint256","name":"precoMinimoPorKwhEmReais","type":"uint256"},{"internalType":"bool","name":"ativa","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"participantes","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"retirarLance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"tempoFinal","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]
''')

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Obter taxa de conversão de Reais para Ether
def get_eth_to_brl_conversion_rate():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=brl"
    response = requests.get(url)
    data = response.json()
    return data['ethereum']['brl']

eth_to_brl_rate = get_eth_to_brl_conversion_rate()
print(f"1 ETH = {eth_to_brl_rate} BRL")

# Função para verificar se o leilão está ativo
def is_auction_active():
    try:
        return contract.functions.leilaoAtivo().call()
    except Exception as e:
        print(e)
        return False

# Função para fazer um lance
def fazer_lance(account_address, private_key, valor_wei):
    if not is_auction_active():
        raise ValueError("Leilao ja terminou")

    nonce = web3.eth.get_transaction_count(account_address)
    transaction = contract.functions.fazerLance().build_transaction({
        'from': account_address,
        'value': valor_wei,
        'gas': 2000000,
        'gasPrice': web3.to_wei('50', 'gwei'),
        'nonce': nonce
    })
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Transaction hash: {tx_hash.hex()}")
    return tx_hash

# Função para verificar o melhor lance
def get_best_bid():
    try:
        comprador, valor = contract.functions.melhorLance().call()
        return comprador, valor
    except Exception as e:
        print(e)
        return None, None

# Contas e chaves privadas (substitua por suas próprias contas e chaves privadas)
accounts = [
    {
        'address': '0xfaE9E22c707d80adE9985d049BecFc5b111e5431',
        'private_key': '0x6fb6b301cb49d92f421656e519a172a3d088021ce69e4d1326e6c42eb44fbb16'
    },
    {
        'address': '0xD73EcC320180FC2476aB380714D0F5B0F73A3C12',
        'private_key': '0x2b956980ccfc4d1994cb9d796f86be360b85e9e0b8ec3449728ada110485a031'
    }
]

# Valores dos lances em Reais
precos_oferecidos_reais = [200, 230]  # Exemplos de lances em Reais

for i, account in enumerate(accounts):
    preco_oferecido_reais = precos_oferecidos_reais[i]
    preco_oferecido_ether = preco_oferecido_reais / eth_to_brl_rate
    preco_oferecido_wei = web3.to_wei(preco_oferecido_ether, 'ether')
    fazer_lance(account['address'], account['private_key'], preco_oferecido_wei)
    comprador, valor = get_best_bid()
    if comprador:
        print(f"Melhor lance até agora: {valor} Wei por {comprador}")

print("Todos os lances foram feitos.")

beneficiario_address = '0xCF4F0aA7C6c70C7f886C45fe93abc2d09574dB06'
beneficiario_private_key = '0xc73755d506e7ad84041025f5b17700103da4136406017d63d8172e18fa61c543'

def finalizar_leilao(beneficiario_address, beneficiario_private_key):
    if not is_auction_active():
        raise ValueError("Leilao ja terminou")

    nonce = web3.eth.get_transaction_count(beneficiario_address)
    transaction = contract.functions.finalizarLeilao().build_transaction({
        'from': beneficiario_address,
        'gas': 2000000,
        'gasPrice': web3.to_wei('50', 'gwei'),
        'nonce': nonce
    })
    signed_txn = web3.eth.account.sign_transaction(transaction, private_key=beneficiario_private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
    print(f"Finalizando leilao - Transaction hash: {tx_hash.hex()}")
    return tx_hash

finalizar_leilao(beneficiario_address, beneficiario_private_key)