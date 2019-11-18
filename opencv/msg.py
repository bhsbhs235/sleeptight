import telepot

from pprint import pprint

bot = telepot.Bot('426542096:AAH_vIVv_b29wXdZafqx2jSA9FdQKlJ04rM')
#pprint(bot.getMe())

def responseMsg():
    response = bot.getUpdates()
    pprint(response)


def sendMsg():
    bot.sendMessage(452318197, 'Warning! Unauthorized person!')



