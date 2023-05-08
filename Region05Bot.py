import telebot;
from telebot import types
from pathlib import Path
import time
import os
import torch
import utils

botName = 'Region05Bot'
botToken  = '6225025889:AAE5x0jbl-tyb8Ky8vD3BMfP4-au7EXJpBU'
dirname1 = 'data' 
dirname2 = 'fromTelImg'

bot = telebot.TeleBot(botToken);
signs = {
0:'Неисправность аккумулятора',
1:'Низкое давление масла',
2:'Неполадка двигателя',
3:'Повышенная температура',
4:'Неисправность ручного тормоза',
5:'Неполадка двигателя',
6:'Ошибка подушки безопасности',
7:'Низкое давление в шинах',
8:'Система стабилизации отключена',
9:'Неисправность антиблокировочной системы тормозов'
}

@bot.message_handler(content_types=['photo'])
def getUserPhoto(message):
    #bot.send_message(message.chat.id, 
    #     f"Подождите немного:{message.from_user.id}",
    #     parse_mode='html')
    markup = types.InlineKeyboardMarkup()
    bot.send_message(message.chat.id,'Подождите немного пжл...', reply_markup=markup)    
    fileID = message.photo[-1].file_id   
    file_info = bot.get_file(fileID)    
    downloaded_file = bot.download_file(file_info.file_path)
    
    base_filename = time.strftime("%Y%m%d-%H%M%S")
    os.makedirs(os.path.join(dirname1, dirname2,base_filename)) #создали папку base_filename
    
    with open(os.path.join(dirname1, dirname2, base_filename,base_filename+'.jpg'), 'wb') as new_file:
        new_file.write(downloaded_file)
    #запускаем yola
    arg = "python detect.py --weights best.pt --img 640 --conf 0.5 --source data/fromTelImg/"+str(base_filename)+" --save-txt"    
    #os.system("python detect.py --weights best.pt --img 640 --conf 0.5 --source data/fromTelImg --save-txt")
    os.system(arg)
    path = 'runs/detect/' # Путь к вашей папке
    dir_list = [os.path.join(path, x) for x in os.listdir(path)]
    #определяем  папку с наибольшим индексом
    s = []
    for j in dir_list:
        x = j.split("runs/detect/exp")[1]
        if (x!=''):
           s.append(int(x))
    index = max(s)       
    dir_result = "runs/detect/exp" + str(index)    
    photo = open(os.path.join(dir_result,base_filename+'.jpg'),'rb')
    bot.send_photo(message.chat.id, photo)
    try:
        # отправляем текстовое описание
        file1 = open(os.path.join(dir_result,'labels',base_filename+'.txt'), 'r')
        Lines = file1.readlines()
    
        for line in Lines:
            s = line.strip()
            x = s.split()
            num = int(x[0].strip())        
            bot.send_message(message.chat.id,signs[num], parse_mode='html')
    except:
            print('Ошибка обработки изображения')
            bot.send_message(message.chat.id,'Ошибка обработки изображения', parse_mode='html')
    #ссылки для верификации
    markup = types.InlineKeyboardMarkup()    
    markup.add(types.InlineKeyboardButton("Для верификации посмотрите на сайте", 
                                          url = "https://pikabu.ru/story/znacheniya_znachkov_na_pribornoy_paneli_avto_4461993"))    
                                          
    bot.send_message(message.chat.id,'Если сомневаетесь, то проверьте по ссылке снизу', reply_markup=markup)
    #bot.send_message(message.chat.id,'https://pikabu.ru/story/znacheniya_znachkov_na_pribornoy_paneli_avto_4461993', reply_markup=markup)
    
    
bot.polling(non_stop = True)