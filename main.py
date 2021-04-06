from loguru import logger
import sys
import os
import requests
import json
import time
import datetime

NAME = ''
PASSWORD = ''

API_KEY = ''
API_URL = 'https://www.999dice.com/api/web.aspx'

#test comment line
logger.add('main_log_file.log', format='{time} {level} {message}', level='INFO')

def input_personal_data():
	NAME = input('Введите имя пользователя: ')
	PASSWORD = input('Введите пароль: ')
	API_KEY = input('Введите ключ API: ')

	with open('personal_data.json', 'w') as f:
		data = {'name':NAME,
				'password':PASSWORD,
				'api_key':API_KEY}
		json.dump(data, f)

def get_personal_data():
	with open('personal_data.json', 'r') as f:
		data = json.load(f)
		global NAME
		NAME = data['name']
		global PASSWORD
		PASSWORD = data['password']
		global API_KEY
		API_KEY = data['api_key']

def login(url, key, name, password):
	data = {'a':'Login',
			'Key':key,
			'Username':name,
			'Password':password}
	response = requests.post(url, data=data)

	return response.json()

def make_bet(url, sessin_cookies, value, cliet_seed):
	data = {'a':'PlaceBet',
			's':sessin_cookies,
			'PayIn':value,
			'Low':950000,
			'High':999999,
			'ClientSeed':cliet_seed,
			'Currency':'doge',
			'ProtocolVersion':2}
	response = requests.post(url, data=data)

	return response.json()

def get_balance(url, sessin_cookies):
	data = {'a':'GetBalance',
			's':sessin_cookies,
			'Currency':'doge',
			}
	response = requests.post(url, data=data)

	return int(response.json()['Balance']) * (10**-8)

def count_bet_value(balance):
	value = balance * 10**-5 - balance * 10**-5 * 0.5

	return int(value * 10**8)

def get_last_bet_info():
	'''
	Получаем информацию о последней сделанной ставке.
	Если игра была прервана по какой-либо из причин,
	то берем данные из файла и продолжаем с того же места. 
	'''
	with open('last_bet_info.json', 'r') as f:
		data = json.load(f)
		counter = data['bet_counter']
		value = data['bet_value']

		return counter, value

def put_last_bet_info(counter, value):
	with open('last_bet_info.json', 'w') as f:
		data = {'bet_counter':counter,
				'bet_value':value}
		json.dump(data, f)

def count_bet_ammount_limit(balance):
	percent = 0.8
	bet_sum = 0
	bet_value = count_bet_value(balance)
	for bet_counter in range(500):
		if bet_counter >= 25 and bet_counter % 5 == 0 and bet_counter % 10 != 0:
			bet_value *= 2
		bet_sum += bet_value * 10**-8
		if bet_sum >= balance * percent:
			return bet_counter

@logger.catch
def main():
	try:
		get_personal_data()
	except:
			print('Персональные данные для входа на сайт не найдены.\n') 
			input_personal_data()
			get_personal_data()
			
	while True:
		try:
			account_data = login(url=API_URL, key=API_KEY, name=NAME, password=PASSWORD)
			cookie = account_data['SessionCookie']
			seed = int(account_data['ClientSeed'])
			break
		except Exception:
			print('Ошибка во входе в аккаунт.\nПроверьте имя пользователя и пароль.')
			input_personal_data()
			get_personal_data()

	start_balance = get_balance(url=API_URL, sessin_cookies=cookie)
	start_value = count_bet_value(start_balance)
	percent = 0
	current_balance = start_balance

	logger.info(f'Logged into account. Start balance = {start_balance}')

	try:
		bet_counter, value = get_last_bet_info()
	except Exception:
		value = start_value
		bet_counter = 0

	while True:
		try:
			bet_result = make_bet(url=API_URL, sessin_cookies=cookie, value=value, cliet_seed=seed)
			#put_last_bet_info(bet_counter, value) #сохраняем информацию о последней ставке
			bet_counter += 1
			pay_out = int(bet_result['PayOut'])
		except (ValueError, KeyError) as e:
			print('Ошибка в осуществлении ставки.')
			print('Bet Error:', bet_result)
			logger.error(f'Bet error: {bet_result}')
			break

		os.system('cls||clear')
		print(f'{round(percent, 5)}% | {round(current_balance - start_balance, 5)} | {round(current_balance, 5)}')
		print(f'Номер ставки: {bet_counter} | Размер ставки: {value} | Выигрышь: {round(pay_out * 10**-8, 5)}')

		if bet_counter >= count_bet_ammount_limit(current_balance) - 1:	
			previous_balance = current_balance		
			current_balance = get_balance(url=API_URL, sessin_cookies=cookie)
			logger.warning(f'Crossed limit with bet counter = {bet_counter}. Previous balance = {previous_balance}. New balance = {current_balance}.')
			value = count_bet_value(current_balance)
			bet_counter = 0

		if pay_out == 0:
			if bet_counter >= 25 and bet_counter % 5 == 0 and bet_counter % 10 != 0:
				value *= 2
		else:
			current_balance = get_balance(url=API_URL, sessin_cookies=cookie)
			percent = 100 - ((start_balance / current_balance) * 100)
			if bet_counter > 100:
				logger.info(f'Got big payout ({pay_out}) on {bet_counter} bet.')

			bet_counter = 0
			'''
			if percent > 50:
				os.system('cls||clear')
				os.system('del last_bet_info.json||rm last_bet_info.json')
				print(f'Получено прибыли {balance - start_balance} doge.')
				break
			'''

			if percent > 0:
				value = count_bet_value(current_balance)
			else:
				value = start_value

if __name__ == '__main__':
	main()

