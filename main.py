import sys
import os
import requests
import json
import time

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

def count_new_bet_value(start_balance, new_balance, start_value):
	key_value = start_balance / (start_value * 10**-8)
	value = new_balance / key_value

	return int(value * 10**8)

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
	start_value = 10000
	value = start_value
	bet_counter = 0
	while True:
		try:
			bet_result = make_bet(url=API_URL, sessin_cookies=cookie, value=value, cliet_seed=seed)
			bet_counter += 1
			pay_out = int(bet_result['PayOut'])

			#print(bet_counter, value, pay_out)
		except Exception:
			print('Ошибка в осуществлении ставки.')
			print('Bet Error:', bet_result)
			break

		if pay_out == 0:
			if bet_counter >= 25 and bet_counter % 5 == 0 and bet_counter % 10 != 0:
				value *= 2
			elif bet_counter == 250:
				print('---Crossed limit---\n')
				break
		else:
			balance = get_balance(url=API_URL, sessin_cookies=cookie)
			os.system('cls||clear')
			percent = 100 - ((start_balance / balance) * 100)
			bet_counter = 0
			if percent > 5:
				print(f'Получено прибыли {balance - start_balance} doge.')
				break

			print(f'{percent}% прибыли.')
			if percent > 0:
				value = count_new_bet_value(start_balance=start_balance, new_balance=balance, start_value=start_value)
			else:
				value = start_value

if __name__ == '__main__':
	main()
