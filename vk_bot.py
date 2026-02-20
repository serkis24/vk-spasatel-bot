from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text
import logging
import os

# Сначала пробуем получить токен из переменной окружения (для Render)
TOKEN = os.environ.get("VK_TOKEN")

# Если переменная не найдена, пробуем прочитать из файла (для локальной работы)
if not TOKEN:
    try:
        with open('token.txt', 'r', encoding='utf-8') as f:
            TOKEN = f.read().strip()
        print("✅ Токен успешно загружен из файла token.txt")
    except FileNotFoundError:
        print("❌ Ошибка: токен не найден!")
        print("На Render добавь VK_TOKEN в Environment Variables")
        print("Локально создай файл token.txt с токеном")
        exit(1)
    except Exception as e:
        print(f"❌ Ошибка при чтении токена: {e}")
        exit(1)
else:
    print("✅ Токен загружен из переменной окружения VK_TOKEN")

bot = Bot(TOKEN)

# Состояния игры для каждого пользователя
user_states = {}

# Граф сюжета
game_states = {
    'start': {
        'text': '🌲 Ты — опытный спасатель. Стоит ясный день, но по рации пришёл сигнал бедствия из леса. В то же время ты очень устал после тяжёлой смены и хочешь домой. Что выберешь?',
        'image': 'photo-236136653_457239018',
        'buttons': [
            {'text': '🏠 Пойти домой', 'next': 'go_home', 'color': 'green'},
            {'text': '🆘 Пойти спасать людей', 'next': 'go_rescue', 'color': 'red'}
        ]
    },
    'go_home': {
        'text': '🏡 Ты приходишь домой, пьёшь горячий чай и смотришь телевизор. В новостях передают, что в лесу, откуда был сигнал, всё обошлось — туристы выбрались сами. Ты выспался и чувствуешь себя отдохнувшим.',
        'image': 'photo-236136653_457239018',
        'buttons': [
            {'text': '🔄 Сыграть ещё', 'next': 'start', 'color': 'blue'}
        ]
    },
    'go_rescue': {
        'text': '🚑 Ты быстро собираешь снаряжение и выезжаешь в лес. На месте ты обнаруживаешь, что группа туристов провалилась в старую шахту. Одни ранены, другие в панике. Тебе нужно быстро принять решение:',
        'image': 'photo-236136653_457239018',
        'buttons': [
            {'text': '🚒 Спуститься и помогать', 'next': 'rescue_climb', 'color': 'red'},
            {'text': '📞 Вызвать подмогу и ждать', 'next': 'rescue_wait', 'color': 'green'}
        ]
    },
    'rescue_climb': {
        'text': '⭐️ Ты спускаешься в шахту. Один из туристов сильно ранен, и ты оказываешь ему первую помощь. Благодаря твоим действиям, удаётся стабилизировать его состояние до приезда основной спасательной группы. Тебя награждают медалью "За отвагу"!',
        'image': 'photo-236136653_457239018',
        'buttons': [
            {'text': '🔄 Сыграть ещё', 'next': 'start', 'color': 'blue'}
        ]
    },
    'rescue_wait': {
        'text': '🤝 Ты вызываешь подмогу и организуешь лагерь наверху. Через час приезжает специализированная команда с лебёдками. Всех туристов благополучно поднимают на поверхность. Ты действовал осторожно, но профессионально.',
        'image': 'photo-236136653_457239018',
        'buttons': [
            {'text': '🔄 Сыграть ещё', 'next': 'start', 'color': 'blue'}
        ]
    }
}

def create_keyboard(buttons):
    """Создает клавиатуру из кнопок"""
    keyboard = Keyboard(inline=True)
    
    for i, btn in enumerate(buttons):
        if btn['color'] == 'green':
            color = KeyboardButtonColor.POSITIVE
        elif btn['color'] == 'red':
            color = KeyboardButtonColor.NEGATIVE
        else:
            color = KeyboardButtonColor.PRIMARY
        
        keyboard.add(Text(btn['text'], payload={"cmd": btn['next']}), color=color)
        
        if i < len(buttons) - 1:
            keyboard.row()
    
    return keyboard

@bot.on.message(text=["/start", "Начать", "start"])
async def start_handler(message: Message):
    user_id = message.from_id
    user_states[user_id] = 'start'
    
    state = game_states['start']
    keyboard = create_keyboard(state['buttons'])
    
    await message.answer("🎮 Добро пожаловать в игру 'Спасатель'!")
    await message.answer(state['text'], keyboard=keyboard, attachment=state['image'])

@bot.on.message()
async def message_handler(message: Message):
    user_id = message.from_id
    current_state = user_states.get(user_id, 'start')
    text = message.text
    
    for state_key, state in game_states.items():
        for btn in state['buttons']:
            if btn['text'] == text:
                new_state = btn['next']
                user_states[user_id] = new_state
                
                target = game_states[new_state]
                keyboard = create_keyboard(target['buttons'])
                
                await message.answer(target['text'], keyboard=keyboard, attachment=target['image'])
                return
    
    state = game_states[current_state]
    keyboard = create_keyboard(state['buttons'])
    await message.answer("Нажми на кнопку!", keyboard=keyboard)

@bot.on.message(text=["/reset", "Заново", "сначала"])
async def reset_handler(message: Message):
    user_id = message.from_id
    user_states[user_id] = 'start'
    
    state = game_states['start']
    keyboard = create_keyboard(state['buttons'])
    
    await message.answer("🔄 Игра перезапущена!", keyboard=keyboard, attachment=state['image'])

if __name__ == "__main__":
    print("🤖 Бот ВК запущен...")
    bot.run_forever()

