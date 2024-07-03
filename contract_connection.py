from web3 import Web3
from datetime import datetime
import pytz

class EthereumAuction:
    def __init__(self, contract_address, contract_abi):
        self.web3 = Web3(Web3.HTTPProvider('http://localhost:7545'))
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
            
            fuso_horario_sp = pytz.timezone('America/Sao_Paulo')
            tempo_final_sp = tempo_final_utc.astimezone(fuso_horario_sp)
            
            formato_saida = '%Y-%m-%d %H:%M:%S'
            tempo_final_formatado = tempo_final_sp.strftime(formato_saida)

            return tempo_final_formatado
        except Exception as e:
            print(e)
            raise ValueError("Não foi possível obter o tempo final do leilão")
        
        