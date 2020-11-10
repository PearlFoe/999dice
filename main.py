import requests
from config import *

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

def main():
	try:
		account_data = login(url=API_URL, key=API_KEY, name=NAME, password=PASSWORD)
		cookie = account_data['SessionCookie']
		seed = int(account_data['ClientSeed'])
	except Exception:
		print('Ошибка во входе в аккаунт.\nПроверьте имя пользователя и пароль.')

	start_value = 10000
	value = start_value
	bet_counter = 0
	while True:
		bet_result = make_bet(url=API_URL, sessin_cookies=cookie, value=value, cliet_seed=seed)
		bet_counter += 1
		try:
			pay_out = int(bet_result['PayOut'])
			print(bet_counter, value, int(bet_result['PayOut']))
		except Exception:
			print('Недостаточно денег для осуществления ставки.')
			break

		if pay_out == 0:
			if bet_counter >= 25 and bet_counter % 5 == 0 and bet_counter % 10 != 0:
				value *= 2
			elif bet_counter == 250:
				print('---Crossed limit---\n')
				break
		else:
			value = start_value
			bet_counter = 0
		
if __name__ == '__main__':
	main()
