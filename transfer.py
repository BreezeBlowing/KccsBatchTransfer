import json
import time
import requests
from web3 import Web3

web3 = Web3(Web3.HTTPProvider('https://kcc-rpc.com'))

def getNowTime():
    return str(time.strftime("[%H:%M:%S] ", time.localtime()))

while True:

    privateKey = input(getNowTime() + "请输入你的私钥: ")
    try:
        account = web3.eth.account.from_key(privateKey.replace("0x", ""))
        print(getNowTime() + "私钥加载成功，钱包地址: " + account.address)
        break
    except BaseException as err:
        print(getNowTime() + "你输入的私钥不正确，请尝试重新输入！")

page = 1
transactionList = []
mintTransactionList = []
finishBlock = 26613096
mintInputData = '0x646174613a2c7b2270223a226b72632d3230222c226f70223a226d696e74222c227469636b223a226b636373222c22616d74223a2231303030227d'
print(getNowTime() + "(~) 开始获取交易记录，请耐心等待！")
while True:

    url = "https://scan.kcc.io/api?module=account&action=txlist&address=" + account.address +"&page=" + str(page)

    response = requests.get(url)
    responseData = response.text
    data = json.loads(responseData)
    pageTransactionList = data.get('result')

    for transaction in pageTransactionList:
        transactionList.append(transaction)

    if len(pageTransactionList) == 10000:
        print(getNowTime() + "正在获取历史交易记录中, 当前已获取 " + str(len(transactionList)) + " 个交易")
        page += 1
        continue
    else:
        print(getNowTime() + "正在获取历史交易记录中, 当前已获取 " + str(len(transactionList)) + " 个交易")
        print(getNowTime() + "获取完成.")
        break

hashList = []

for transactions in transactionList:
    blockNumber = transactions.get('blockNumber')
    blockNumber = int(blockNumber)
    inputData = transactions.get('input')
    if inputData == mintInputData and blockNumber <= finishBlock:
        mintTransactionList.append(transactions)
        hashList.append(transactions.get('hash'))

transferMap = dict()
for transactions in transactionList:
    inputData = transactions.get('input')
    toAddress = transactions.get('to')
    if len(inputData) == 66 and inputData in hashList:
        if transferMap.get(toAddress) is None:
            transferMap[toAddress] = 1
        else:
            transferMap[toAddress] = transferMap[toAddress] + 1

        hashList.remove(inputData)

print(getNowTime() + "共计获取到 (可能有效的) Mint 次数: " + str(len(mintTransactionList)) + " 剩余数量: " + str(len(hashList)) + " 已转移数量: " + str(len(mintTransactionList)-len(hashList)))
print(transferMap)
print(getNowTime() + "_______________________________________________________________________________________")
print(getNowTime() + "(~) 当前版本脚本仅能识别 Mint 出来的铭文代币，不能识别转账进入的铭文代币，请在转出后前往官网验证到账。")
print(getNowTime() + "(~) 转账完成后可能会有延迟到账的现象，这是因为官方索引器同步较慢的原因，耐心等待即可。")
print(getNowTime() + "_______________________________________________________________________________________")

while True:
    toAddress = input(getNowTime() + "请输入你要转出的地址: ")
    try:
        toAddress = web3.to_checksum_address(toAddress)
        break
    except BaseException as err:
        print(getNowTime() + "(!) 你输入的地址不合规，请重新输入。")

print(getNowTime() + "转出地址已确认，(" + toAddress + ")")

while True:
    amount = input(getNowTime() + "请输入你要转出的数量 (单位: 张): ")
    try:
        amount = int(amount)
        break
    except BaseException as err:
        print(getNowTime() + "(!) 你输入的数量不合规，请重新输入。")

print(getNowTime() + "转出数量已确认，(" + str(amount) + ") 张")
print(getNowTime() + "_______________________________________________________________________________________")
print(getNowTime() + "(~) 准备开始进行转账。")
print(getNowTime() + "(!) 转出地址: " + toAddress)
print(getNowTime() + "(!) 转出数量: " + str(amount) + " 张")
print(getNowTime() + "_______________________________________________________________________________________")

hasErr = False
for count in range(amount):

    try:
        gasPrice = web3.eth.gas_price
        print(getNowTime() + "(~) 当前第 " + str(count + 1) + " 笔")
        print(getNowTime() + "(~) 铭文ID " + str(hashList[count]))
        print(getNowTime() + "(~) Gas价格:  " + str(web3.from_wei(gasPrice, "gwei")) + " Gwei")

        latestNonce = web3.eth.get_transaction_count(account.address, 'pending')

        signed_txn = {
            "from": account.address,
            "to": toAddress,
            "value": 0,
            "gas": 30000,
            'gasPrice': gasPrice,
            "data": hashList[count],
            "nonce": latestNonce,
            'chainId': web3.eth.chain_id
        }
        sign = account.sign_transaction(signed_txn)
        send = web3.eth.send_raw_transaction(sign.rawTransaction)
        Hex = web3.to_hex(send)
        print(getNowTime() + "(~) 交易已提交: " + Hex)
        result = web3.eth.wait_for_transaction_receipt(Hex)
        print(getNowTime() + "(~) 交易已确认.")
        print(getNowTime() + "_______________________________________________________________________________________")
    except BaseException as err:
        hasErr = True
        print(getNowTime() + "转账时出现错误! 停止转账···")
        print(err)
        break

if not hasErr:
    print(getNowTime() + "(~) 转账任务均已完成")

time.sleep(1000000)