from vkbottle.bot import Bot, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text
import logging
import os  # Добавлено для получения порта из окружения

# Токен сообщества - бери из переменных окружения (так безопаснее)
TOKEN = "vk1.a.cGky24v-V3KbaKBZtcgy4EDe07Cxd3S37UT3_RQ2i7Q9WiSLTWhtvpPmQHjyec0ctnwNF62YGf4Bg-o1LFPKfN7w63Hw2LeCfJrCDL-itsL1F6BnFCJefhtOuzlEjKxuwyttvlauPBQEafUQPNz6wm4V3QEA_zSQ8caabvE6cyEp6D8O6HSDfIo6WVRVxHTIpYwSjImq1yaOlGkvJsWc3w"  # Вставь свой токен

bot = Bot(TOKEN)

# Состояния игры для каждого пользователя
user_states = {}

# Граф сюжета
game_states = {
    'start': {
        'text': '🌲 Ты — опытный спасатель...',
        'image': 'photo-236136653_457239018',  # твой ID фото
        'buttons': [
            {'text': '🏠 Пойти домой', 'next': 'go_home', 'color': 'green'},
            {'text': '🆘 Пойти спасать людей', 'next': 'go_rescue', 'color': 'red'}
        ]
    },
    # ... остальные состояния (скопируй из своего рабочего кода) ...
    'go_home': {
        'text': '🏡 Ты приходишь домой...',
        'image': 'photo-236136653_457239018',
        'buttons': [{'text': '🔄 Сыграть ещё', 'next': 'start', 'color': 'blue'}]
    },
    'go_rescue': {
        'text': '🚑 Ты быстро собираешь снаряжение...',
        'image': 'photo-236136653_457239018',
        'buttons': [
            {'text': '🚒 Спуститься', 'next': 'rescue_climb', 'color': 'red'},
            {'text': '📞 Ждать подмогу', 'next': 'rescue_wait', 'color': 'green'}
        ]
    },
    'rescue_climb': {
        'text': '⭐️ Героический спуск!',
        'image': 'photo-236136653_457239018',
        'buttons': [{'text': '🔄 Сыграть ещё', 'next': 'start', 'color': 'blue'}]
    },
    'rescue_wait': {
        'text': '🤝 Ты вызвал подмогу',
        'image': 'photo-236136653_457239018',
        'buttons': [{'text': '🔄 Сыграть ещё', 'next': 'start', 'color': 'blue'}]
    }
}

def create_keyboard(buttons):
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
    # Render даёт порт в переменной окружения PORT, но для бота ВК он не нужен
    # Просто запускаем бота
    bot.run_forever()
