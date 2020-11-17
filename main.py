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
	value = balance / 10000000

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

	try:
		bet_counter, value = get_last_bet_info()
	except:
		value = start_value
		bet_counter = 0

	while True:
		try:
			bet_result = make_bet(url=API_URL, sessin_cookies=cookie, value=value, cliet_seed=seed)
			put_last_bet_info(bet_counter, value) #сохраняем информацию о последней ставке
			bet_counter += 1
			pay_out = int(bet_result['PayOut'])
		except Exception:
			print('Ошибка в осуществлении ставки.')
			print('Bet Error:', bet_result)
			break

		os.system('cls||clear')
		print(f'{percent}% прибыли.')
		print(f'Номер ставки: {bet_counter} | Размер ставки: {value} | Выигрышь: {pay_out}')

		if pay_out == 0:
			if bet_counter >= 25 and bet_counter % 5 == 0 and bet_counter % 10 != 0:
				value *= 2
			elif bet_counter == 250:
				print('---Crossed limit---\n')
				break
		else:
			balance = get_balance(url=API_URL, sessin_cookies=cookie)	
			percent = 100 - ((start_balance / balance) * 100)
			bet_counter = 0
			if percent > 5:
				os.system('cls||clear')
				os.system('del last_bet_info.json||rm last_bet_info.json')
				print(f'Получено прибыли {balance - start_balance} doge.')
				break

			if percent > 0:
				value = count_bet_value(balance)
			else:
				value = start_value

if __name__ == '__main__':	
	main()
