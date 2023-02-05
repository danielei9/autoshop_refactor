import CoinWallet 
import time
def cb(data):
    print("cb " + str(data))
    
cW = CoinWallet.CoinWallet(cb)

time.sleep(1)
cW.reset()
cW.setup()
#     cW.startReceivingMode()
time.sleep(2)
cW.enableInsertCoins()
time.sleep(2)
#     print(cW.cashBackRoutine(0.85))

while True:
    s_r = ''
    while s_r not in ('1', '2', '3', '4', '4', '5', 'r'):
        s_r = input("(1) Mode Input Coin (Polling and denoms)\n"
                            "(2) Mode PayOut (add space and quantity) \n"
                            "(3) RESET MACHINE \n"
                            "(4) STATUS MACHINE \n"
                            "(5) TUBE STATUS \n"
                            "(6) Enabke insert coins \n"
                            "(R)eturn ").lower()
        if s_r == '1':
            cW.enableInsertCoins()
            cW.startReceivingMode()
            break
        elif s_r == '2':
            qnty = ' '
            while qnty in (' '):
                qnty = input("Quantity to pay: ")
            print(cW.cashBackRoutine(float(qnty)))
            break
        elif s_r == '3':
            print("Reset")
            cW.reset()
            break
        elif s_r == '4':
            print("setup")
            cW.setup()
            break
        elif s_r == '5':
            cW.tubeStatus()
            break
        elif s_r == '6':
            cW.enableInsertCoins()
            break
