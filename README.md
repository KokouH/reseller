Программа для автоматической перепродажи предметов в стиме.

В конечном варианте, она должна сама линейно поправляет свои параметры. Для максимизации прибыли.

Для запуска установите зависимости
`
python -m pip install -r requirements.txt
`

Добавьте файл src/config.py
```
REDIS_HOST = "localhost"
REDIS_PORT = 6379

USE_BOT = True

TOKEN_TG = "2**************************G4" # TELEGRAM BOT TOKEN
CHAT_ID = 1*******2 # TELEGRAM CHAT ID FOR STAT

acc_data_1 = (
	"5****************************9", # STEAM_API_KEY
	"f*********1", # STEAM_LOGIN
	"5********2", # STEAM_PASSWORD
	"guards/guard.maFile", # PATH TO GUARD MAFILE
	proxies={'http':'http://login:password@example.com:8080'} # Если нужно задать прокси для аккаунта
)
```

В файле main.py можно настраивать запускаемые модули
`
need_start.append("analize") - сборщик данных( сохраняет все в таблицу )

need_start.append('updater') - снимает ордера на покупку и продажу если они не актульны

need_start.append('buyer') - выставляет ордера на покупку по таблице и внутренним параметрам( можно менять внутри файла src/ordersDispatcher/mainBuyer.py )

need_start.append("seller") - тоже, что и buyer, только на продажу( можно менять внутри файла src/ordersDispatcher/mainSeller.py )

need_start.append('balanceCalc') - Производит полный расчет капитала( учитывает Баланс, ордера на продажу( сумма получаемая ), вещи в инвентарях раста и тф2( берет цену из таблицы с учетом комиссии ) )
`