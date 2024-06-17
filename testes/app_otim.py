from web3 import Web3
from datetime import datetime, timezone
import pytz

class EthereumAuction:
    def __init__(self, contract_address, contract_abi):
        self.web3 = Web3(Web3.HTTPProvider('http://localhost:7545'))  # Altere para seu provedor
        self.contract = self.web3.eth.contract(address=contract_address, abi=contract_abi)

    def is_auction_active(self):
        try:
            return self.contract.functions.leilaoAtivo().call()
        except Exception as e:
            print(e)
            return False

    def fazer_lance(self, account_address, private_key, valor_wei):
        if not self.is_auction_active():
            raise ValueError("Leilao ja terminou")

        nonce = self.web3.eth.get_transaction_count(account_address)
        transaction = self.contract.functions.fazerLance().build_transaction({
            'from': account_address,
            'value': valor_wei,
            'gas': 2000000,
            'gasPrice': self.web3.to_wei('50', 'gwei'),
            'nonce': nonce
        })
        signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"Transaction hash: {tx_hash.hex()}")
        return tx_hash

    def get_best_bid(self):
        try:
            comprador, valor = self.contract.functions.melhorLance().call()
            return comprador, valor
        except Exception as e:
            print(e)
            return None, None

    def finalizar_leilao(self, beneficiario_address, beneficiario_private_key):
        if not self.is_auction_active():
            raise ValueError("Leilao ja terminou")

        nonce = self.web3.eth.get_transaction_count(beneficiario_address)
        transaction = self.contract.functions.finalizarLeilao().build_transaction({
            'from': beneficiario_address,
            'gas': 2000000,
            'gasPrice': self.web3.to_wei('50', 'gwei'),
            'nonce': nonce
        })
        signed_txn = self.web3.eth.account.sign_transaction(transaction, private_key=beneficiario_private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        print(f"Finalizando leilao - Transaction hash: {tx_hash.hex()}")
        return tx_hash

    def maior_lance(self):
        return self.contract.functions.maiorLance().call()
    
    def get_tempo_final_leilao(self):
        try:
            tempo_final_seconds = self.contract.functions.tempoFinal().call()
            tempo_final_utc = datetime.fromtimestamp(tempo_final_seconds, tz=pytz.utc)
            
            # Convertendo para o fuso-horário de São Paulo (BRT)
            fuso_horario_sp = pytz.timezone('America/Sao_Paulo')
            tempo_final_sp = tempo_final_utc.astimezone(fuso_horario_sp)
            
            # Formato desejado para a saída
            formato_saida = '%Y-%m-%d %H:%M:%S'
            tempo_final_formatado = tempo_final_sp.strftime(formato_saida)

            return tempo_final_formatado
        except Exception as e:
            print(e)
            raise ValueError("Não foi possível obter o tempo final do leilão")
        
        
# Exemplo de utilização da classe EthereumAuction:

# if __name__ == "__main__":
#     # Endereço do contrato e ABI (substitua pelo endereço do seu contrato e ABI)
#     contract_address = '0x03506Cccb18Fee3C790F8aA764961F221AbBdFe3'
#     contract_abi = json.loads('''[{"inputs":[{"internalType":"uint256","name":"_duracaoLeilaoEmMinutos","type":"uint256"},{"internalType":"address payable","name":"_beneficiario","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"comprador","type":"address"},{"indexed":false,"internalType":"uint256","name":"valor","type":"uint256"}],"name":"LancesRestituidos","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"vencedor","type":"address"},{"indexed":false,"internalType":"uint256","name":"valor","type":"uint256"}],"name":"LeilaoFinalizado","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"produtor","type":"address"},{"indexed":false,"internalType":"uint256","name":"quantidade","type":"uint256"},{"indexed":false,"internalType":"uint256","name":"precoMinimoPorKwh","type":"uint256"}],"name":"NovaOferta","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"comprador","type":"address"},{"indexed":false,"internalType":"uint256","name":"valor","type":"uint256"}],"name":"NovoLance","type":"event"},{"inputs":[],"name":"beneficiario","outputs":[{"internalType":"address payable","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address payable","name":"_produtor","type":"address"},{"internalType":"uint256","name":"_quantidadeDisponivel","type":"uint256"},{"internalType":"uint256","name":"_precoMinimoPorKwhEmReais","type":"uint256"}],"name":"definirOferta","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"etherToReais","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"fazerLance","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[],"name":"finalizarLeilao","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"lances","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"leilaoAtivo","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"maiorLance","outputs":[{"internalType":"address payable","name":"comprador","type":"address"},{"internalType":"uint256","name":"valor","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"melhorLance","outputs":[{"internalType":"address","name":"comprador","type":"address"},{"internalType":"uint256","name":"valor","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"oferta","outputs":[{"internalType":"address payable","name":"produtor","type":"address"},{"internalType":"uint256","name":"quantidadeDisponivel","type":"uint256"},{"internalType":"uint256","name":"precoMinimoPorKwhEmReais","type":"uint256"},{"internalType":"bool","name":"ativa","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"participantes","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"retirarLance","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"tempoFinal","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]''')

#     # Criando uma instância da classe EthereumAuction
#     ethereum_auction = EthereumAuction(contract_address, contract_abi)

#     def get_eth_to_brl_conversion_rate():
#         url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=brl"
#         response = requests.get(url)
#         data = response.json()
#         return data['ethereum']['brl']

#     # Exemplo de fazer um lance
#     account_address = '0xfaE9E22c707d80adE9985d049BecFc5b111e5431'
#     private_key = '0x6fb6b301cb49d92f421656e519a172a3d088021ce69e4d1326e6c42eb44fbb16'
#     lance_reais = 250
#     lance_ether = lance_reais / get_eth_to_brl_conversion_rate()
#     valor_wei = ethereum_auction.web3.to_wei(lance_ether, 'ether')
#     ethereum_auction.fazer_lance(account_address, private_key, valor_wei)

#     # Exemplo de finalizar o leilão
#     beneficiario_address = '0xCF4F0aA7C6c70C7f886C45fe93abc2d09574dB06'
#     beneficiario_private_key = '0xc73755d506e7ad84041025f5b17700103da4136406017d63d8172e18fa61c543'
#     ethereum_auction.finalizar_leilao(beneficiario_address, beneficiario_private_key)
