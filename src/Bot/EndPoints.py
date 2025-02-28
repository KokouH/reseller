from Bot.MESSAGES import *
from Bot.BotMain import BotMain

from multiprocessing import Process
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

need_start = list()
working = False

temp_names = ["analize", "updater", "buyer", "seller", "balanceCalc"]

work_proc: Process | None = None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	global need_start, working, temp_names

	if work_proc == None:
		working = False
	else:
		if not work_proc.is_alive():
			working = False

	if working:
		await update.message.reply_text("Working..")
		return

	keyboard = [
		[InlineKeyboardButton(f"{name}{' +' if name in need_start else ''}", callback_data=str(i))] 
			for i, name in enumerate(temp_names)
	]
	keyboard.append([InlineKeyboardButton(f"Start", callback_data=str(len(temp_names)))])
	# print(keyboard)
	reply_markup = InlineKeyboardMarkup(keyboard)
	await update.message.reply_text(START_MESSAGE, reply_markup=reply_markup)
	
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
	global need_start, working, temp_names

	query = update.callback_query
	await query.answer()

	if (int(query.data) == len(temp_names)):
		working = True
		work_proc = BotMain(need_start)
		work_proc.start()
		await query.edit_message_text('\n'.join(i for i in need_start))
		working = False
		need_start = list()
		return

	comm = temp_names[int(query.data)]
	if (comm in need_start):
		need_start.remove(comm)
	else:
		need_start.append(comm)

	keyboard = [
		[InlineKeyboardButton(f"{name}{' +' if name in need_start else ''}", callback_data=str(i))] 
			for i, name in enumerate(temp_names)
	]
	keyboard.append([InlineKeyboardButton(f"Start", callback_data=str(len(temp_names)))])
	reply_markup = InlineKeyboardMarkup(keyboard)

	await query.edit_message_reply_markup(reply_markup=reply_markup)
