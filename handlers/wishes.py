from datetime import datetime
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from database.db import Database
from utils.states import State
from utils.keyboards import get_main_keyboard, get_wish_keyboard

async def add_wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['adding_wish'] = {}
    await update.message.reply_text(
        "Введите название желаемого товара:",
        reply_markup=ReplyKeyboardMarkup([['🔙 Отмена']], resize_keyboard=True)
    )
    return State.ADDING_TITLE

async def handle_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '🔙 Отмена':
        return await _cancel_action(update)
    
    context.user_data['adding_wish']['title'] = update.message.text
    await update.message.reply_text(
        "Введите цену:",
        reply_markup=ReplyKeyboardMarkup([['🔙 Отмена']], resize_keyboard=True)
    )
    return State.ADDING_PRICE

async def handle_price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '🔙 Отмена':
        return await _cancel_action(update)
    
    try:
        price = float(update.message.text)
        context.user_data['adding_wish']['price'] = price
        await update.message.reply_text(
            "Отправьте ссылку на товар:",
            reply_markup=ReplyKeyboardMarkup([['🔙 Отмена']], resize_keyboard=True)
        )
        return State.ADDING_LINK
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректную цену (число).")
        return State.ADDING_PRICE

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '🔙 Отмена':
        return await _cancel_action(update)
    
    context.user_data['adding_wish']['link'] = update.message.text
    await update.message.reply_text(
        "Отправьте фотографию товара или нажмите 'Пропустить':",
        reply_markup=ReplyKeyboardMarkup([['🔙 Отмена'], ['⏩ Пропустить']], resize_keyboard=True)
    )
    return State.ADDING_PHOTO

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == '🔙 Отмена':
        return await _cancel_action(update)
    
    if update.message.text == '⏩ Пропустить':
        return await save_wish(update, context)
    
    if not update.message.photo:
        await update.message.reply_text("Пожалуйста, отправьте фотографию или нажмите 'Пропустить'")
        return State.ADDING_PHOTO
    
    context.user_data['adding_wish']['photo_id'] = update.message.photo[-1].file_id
    return await save_wish(update, context)

async def save_wish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    wish_info = context.user_data['adding_wish']
    user_id = update.effective_user.id
    
    with Database() as cursor:
        if wish_info.get('photo_id'):
            cursor.execute(
                '''INSERT INTO wishes (user_id, title, price, link, photo_id, date_added)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (user_id, wish_info['title'], wish_info['price'],
                 wish_info['link'], wish_info['photo_id'], datetime.now())
            )
        else:
            cursor.execute(
                '''INSERT INTO wishes (user_id, title, price, link, date_added)
                   VALUES (?, ?, ?, ?, ?)''',
                (user_id, wish_info['title'], wish_info['price'],
                 wish_info['link'], datetime.now())
            )
        
        cursor.execute('SELECT subscriber_id FROM subscriptions WHERE target_user_id = ?', (user_id,))
        notify_subscribers(context.bot, cursor.fetchall(), update.effective_user.username, wish_info)
    
    del context.user_data['adding_wish']
    await update.message.reply_text("✅ Желание добавлено!", reply_markup=get_main_keyboard())
    return State.CHOOSING

async def show_wishlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    with Database() as cursor:
        cursor.execute(
            '''SELECT id, title, price, link, photo_id, status
               FROM wishes 
               WHERE user_id = ? AND status != 'completed'
               ORDER BY date_added DESC''', (user_id,)
        )
        active_wishes = cursor.fetchall()
        
        cursor.execute(
            '''SELECT title, price, date_added 
               FROM wishes 
               WHERE user_id = ? AND status = 'completed'
               ORDER BY date_added DESC''', (user_id,)
        )
        completed_wishes = cursor.fetchall()
    
    if not active_wishes and not completed_wishes:
        await update.message.reply_text("Ваш список желаний пуст")
        return
    
    await _send_wishes_list(update, active_wishes, completed_wishes)

async def _send_wishes_list(update: Update, active_wishes, completed_wishes):
    for wish in active_wishes:
        wish_id, title, price, link, photo_id, status = wish
        text = f"🎁 {title}\n💰 Цена: {price}\n🔗 {link}\n"
        text += "🔒 Забронировано" if status == 'booked' else "📝 Активно"
        
        reply_markup = get_wish_keyboard(wish_id, status)
        
        if photo_id:
            await update.message.reply_photo(photo_id, caption=text, reply_markup=reply_markup)
        else:
            await update.message.reply_text(text, reply_markup=reply_markup)
    
    if completed_wishes:
        completed_text = "✨ Исполненные желания:\n\n"
        completed_text += "\n".join(f"• {title} - {price}₽" for title, price, _ in completed_wishes)
        await update.message.reply_text(completed_text)

async def _cancel_action(update: Update):
    await update.message.reply_text("Действие отменено", reply_markup=get_main_keyboard())
    return State.CHOOSING

def notify_subscribers(bot, subscribers, username, wish_info):
    for subscriber in subscribers:
        try:
            bot.send_message(
                chat_id=subscriber[0],
                text=f"@{username} добавил(а) новое желание:\n"
                     f"{wish_info['title']}\n"
                     f"Цена: {wish_info['price']}"
            )
        except Exception as e:
            logging.error(f"Failed to notify subscriber {subscriber[0]}: {e}")
