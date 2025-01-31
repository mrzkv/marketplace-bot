from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, callback_data
from bot_services.database_functions import insert_new_user_info, check_user_ban_info, get_user_data_by_user_id, \
    get_user_profile_data, insert_profile_data
from bot_services.data_validation import check_phone_number
import html

class ProfileChange(StatesGroup):
    name_surname = State()
    photo = State()
    address = State()
    phone_number = State()

router = Router()

@router.message(Command('profile'))
async def get_user_profile(data: types.Message) -> None:
    # Проверка всего
    await insert_new_user_info(data.from_user.id, data.from_user.username, data.from_user.full_name)
    ban_data = await check_user_ban_info(data.from_user.id)
    if ban_data:
        await data.answer(text=ban_data)
        return None
    # Основной блок
    profile_data = await get_user_profile_data(data.from_user.id)
    if profile_data.phone_number != '' and profile_data.home_address != '' and profile_data.surname_name != '':
        user_data = await get_user_data_by_user_id(data.from_user.id)

        kb = [[types.InlineKeyboardButton(text='Вернуться назад', callback_data='get_start_menu'),
               types.InlineKeyboardButton(text='Изменить данные',callback_data='change_profile_data')]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

        text_data = (f'Имя Фамилия: {html.escape(profile_data.surname_name)}\n'
                     f'Телефон: {html.escape(profile_data.phone_number)}\n'
                     f'Адрес: {html.escape(profile_data.home_address)}\n'
                     f'Дата регистрации: {html.escape(user_data.registration_date)}\n')
        if profile_data.photo == '':
            await data.answer(text=text_data, reply_markup=keyboard)
        else:
            await data.answer_photo(photo=profile_data.photo,caption=text_data, reply_markup=keyboard)
        return None
    else:
        kb = [[types.InlineKeyboardButton(text='Вернуться назад', callback_data='get_start_menu'),
               types.InlineKeyboardButton(text='Заполнить профиль', callback_data='change_profile_data')]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
        await data.answer(text='Вы еще не заполнили профиль.\nХотите заполнить?',reply_markup=keyboard)


    #await msg.answer(text=f'Hello, {html.escape(msg.from_user.username)}.')

@router.callback_query(F.data == 'change_profile_data')
async def change_profile_data(data: types.CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    # Проверка всего
    await insert_new_user_info(data.from_user.id, data.from_user.username, data.from_user.full_name)
    ban_data = await check_user_ban_info(data.from_user.id)
    if ban_data:
        await data.answer(text=ban_data)
        await data.message.delete()
        return None
    # Основной блок
    text_data = 'Введите ваши имя и фамилию:'
    await state.set_state(ProfileChange.name_surname)
    kb = [[types.InlineKeyboardButton(text='Вернуться назад', callback_data='end_of_changing_profile')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await data.message.answer(text=text_data, reply_markup=keyboard)

@router.message(ProfileChange.name_surname)
async def change_profile_data_name_surname(data: types.Message, state: FSMContext) -> None:
    await state.clear()
    # Проверка всего
    await insert_new_user_info(data.from_user.id, data.from_user.username, data.from_user.full_name)
    ban_data = await check_user_ban_info(data.from_user.id)
    if ban_data:
        await data.answer(text=ban_data)
        return None
    # Основной блок
    await insert_profile_data(data.from_user.id, data.text, 'name_surname')
    text_data = 'Отправьте фотографию для профиля'
    await state.set_state(ProfileChange.photo)
    kb = [[types.InlineKeyboardButton(text='Закончить ввод данных', callback_data='end_of_changing_profile'), types.InlineKeyboardButton(text='Нету фото', callback_data='profile_change_without_photo')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await data.answer(text=text_data, reply_markup=keyboard)



@router.message(ProfileChange.photo)
async def change_profile_data_photo(data: types.Message, state: FSMContext) -> None:
    kb = [[types.InlineKeyboardButton(text='Закончить ввод данных', callback_data='end_of_changing_profile')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    if not data.photo:
        await data.answer(text='❌ Это не фото!', reply_markup=keyboard)
        return None
    else:
        await state.clear()
    # Проверка всего
    await insert_new_user_info(data.from_user.id, data.from_user.username, data.from_user.full_name)
    ban_data = await check_user_ban_info(data.from_user.id)
    if ban_data:
        await data.answer(text=ban_data)
        return None
    # Основной блок
    await insert_profile_data(data.from_user.id, data.photo[-1].file_id, 'photo_data')
    text_data = 'Введите ваш номер телефона'
    await state.set_state(ProfileChange.phone_number)
    await data.answer(text=text_data,reply_markup=keyboard)

@router.callback_query(F.data == 'profile_change_without_photo')
async def change_profile_data_without_photo(data: types.CallbackQuery, state: FSMContext) -> None:
    kb = [[types.InlineKeyboardButton(text='Закончить ввод данных', callback_data='end_of_changing_profile')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    # Проверка всего
    await insert_new_user_info(data.from_user.id, data.from_user.username, data.from_user.full_name)
    ban_data = await check_user_ban_info(data.from_user.id)
    if ban_data:
        await data.message.answer(text=ban_data)
        return None
    # Основной блок
    await state.clear()
    await state.set_state(ProfileChange.phone_number)
    text_data = 'Введите ваш номер телефона'
    await data.message.answer(text=text_data, reply_markup=keyboard)


@router.message(ProfileChange.phone_number)
async def change_profile_data_phone_number(data: types.Message, state: FSMContext) -> None:
    kb = [[types.InlineKeyboardButton(text='Закончить ввод данных', callback_data='end_of_changing_profile')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    if not await check_phone_number(data.text):
        text_data = '❌ Вы ввели неверный номер телефона!'
        await data.answer(text=text_data, reply_markup=keyboard)
        return None
    else:
        await state.clear()
    # Проверка всего
    await insert_new_user_info(data.from_user.id, data.from_user.username, data.from_user.full_name)
    ban_data = await check_user_ban_info(data.from_user.id)
    if ban_data:
        await data.answer(text=ban_data)
        return None
    # Основной блок
    await insert_profile_data(data.from_user.id, data.text, 'phone_number')
    text_data = 'Введите ваш адрес'
    await state.set_state(ProfileChange.address)
    await data.answer(text=text_data,reply_markup=keyboard)

@router.message(ProfileChange.address)
async def change_profile_data_address(data: types.Message, state: FSMContext) -> None:
    kb = [[types.InlineKeyboardButton(text='Закончить ввод данных', callback_data='end_of_changing_profile')]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    await state.clear()
    # Проверка всего
    await insert_new_user_info(data.from_user.id, data.from_user.username, data.from_user.full_name)
    ban_data = await check_user_ban_info(data.from_user.id)
    if ban_data:
        await data.answer(text=ban_data)
        return None
    # Основной блок
    await insert_profile_data(data.from_user.id, data.text, 'home_address')
    profile_data = await get_user_profile_data(data.from_user.id)
    user_data = await get_user_data_by_user_id(data.from_user.id)
    text_data = (f'Имя Фамилия: {profile_data.surname_name}\n'
                 f'Телефон: {profile_data.phone_number}\n'
                 f'Адрес: {profile_data.home_address}\n'
                 f'Дата регистрации: {user_data.registration_date}\n')
    if profile_data.photo:
        photo_data = profile_data.photo
        await data.answer_photo(photo=photo_data, caption=text_data, reply_markup=keyboard)
    else:
        await data.answer(text=text_data, reply_markup=keyboard)

@router.callback_query(F.data == 'end_of_changing_profile')
async def end_of_edit_profile(data: types.Message, state: FSMContext) -> None:
    await state.clear()
    # Проверка всего
    await insert_new_user_info(data.from_user.id, data.from_user.username, data.from_user.full_name)
    ban_data = await check_user_ban_info(data.from_user.id)
    if ban_data:
        await data.message.answer(text=ban_data)
        return None
    # Основной блок
    profile_data = await get_user_profile_data(data.from_user.id)
    if profile_data.phone_number != '' and profile_data.home_address != '' and profile_data.surname_name != '':
        user_data = await get_user_data_by_user_id(data.from_user.id)

        kb = [[types.InlineKeyboardButton(text='Вернуться назад', callback_data='get_start_menu'),
               types.InlineKeyboardButton(text='Изменить данные',callback_data='change_profile_data')]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)

        text_data = (f'Имя Фамилия: {html.escape(profile_data.surname_name)}\n'
                     f'Телефон: {html.escape(profile_data.phone_number)}\n'
                     f'Адрес: {html.escape(profile_data.home_address)}\n'
                     f'Дата регистрации: {html.escape(user_data.registration_date)}\n')
        if profile_data.photo == '':
            await data.message.answer(text=text_data, reply_markup=keyboard)
        else:
            await data.message.answer_photo(photo=profile_data.photo,caption=text_data, reply_markup=keyboard)
        return None
    else:
        kb = [[types.InlineKeyboardButton(text='Вернуться назад', callback_data='get_start_menu'),
               types.InlineKeyboardButton(text='Заполнить профиль', callback_data='change_profile_data')]]
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
        await data.message.answer(text='Вы еще не заполнили профиль.\nХотите заполнить?',reply_markup=keyboard)