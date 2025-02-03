import os
import json
from dotenv import load_dotenv
from web3 import Web3


load_dotenv()
infura_url = os.getenv('INFURA_URL')
private_key = os.getenv('PRIVATE_KEY')

web3 = Web3(Web3.HTTPProvider(infura_url))

if web3.is_connected():
    print("Conectado à rede Ethereum")
else:
    print("Falha na conexão com a rede Ethereum")
    exit()

account = web3.eth.account.from_key(private_key)
wallet_address = account.address
 
print(wallet_address)

wepe_contract_address = os.getenv('WEPE_CONTRACT')
uniswap_router_address = os.getenv('UNISWAP_ROUTER_ADDRESS')

with open('wepe_abi.json') as f:
    wepe_abi = json.load(f)

wepe_contract = web3.eth.contract(address=wepe_contract_address, abi=wepe_abi)

with open('uniswap_abi.json') as f:
    uniswap_router_abi = json.load(f)

uniswap_router = web3.eth.contract(address=uniswap_router_address, abi=uniswap_router_abi)

def approve_tokens(amount):
    nonce = web3.eth.get_transaction_count(wallet_address)
    txn = wepe_contract.functions.approve(uniswap_router_address, amount).build_transaction({
        'chainId': 1,
        'gas': 100000,
        'gasPrice': web3.eth.gas_price,
        'nonce': nonce,
    })
    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Aprovação de tokens enviada com hash: {tx_hash.hex()}")
    return tx_hash

def sell_all_wepe(): #desgraça
    balance = wepe_contract.functions.balanceOf(wallet_address).call()
    print(balance)
    if balance == 0:
        print("Saldo de WEPE é zero. Nada para vender.")
        return
    

    approve_tx = approve_tokens(balance)
    web3.eth.wait_for_transaction_receipt(approve_tx)

    nonce = web3.eth.get_transaction_count(wallet_address)
    deadline = web3.eth.get_block('latest')['timestamp'] + 600  
    amount_out_min = 0  # Aceitar qualquer quantidade de ETH (ajuste essa merda.)

    txn = uniswap_router.functions.swapExactTokensForETH(
        balance,
        amount_out_min,
        [wepe_contract_address, web3.to_checksum_address('0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2')],
        wallet_address,
        deadline
    ).build_transaction({
        'chainId': 1,
        'gas': 300000,
        'gasPrice': web3.eth.gas_price,
        'nonce': nonce,
    })

    signed_txn = web3.eth.account.sign_transaction(txn, private_key=private_key)
    tx_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Venda de WEPE enviada com hash: {tx_hash.hex()}")
    return tx_hash


if __name__ == "__main__":
    sell_tx = sell_all_wepe()


