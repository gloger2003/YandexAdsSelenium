from python_rucaptcha import ImageCaptcha
# Введите ключ от сервиса RuCaptcha, из своего аккаунта
RUCAPTCHA_KEY = ""
# Ссылка на изображения для расшифровки
image_link = ""
# Возвращается JSON содержащий информацию для решения капчи
user_answer = ImageCaptcha.ImageCaptcha(rucaptcha_key=RUCAPTCHA_KEY).captcha_handler(captcha_link=image_link)

if not user_answer['error']:
	# решение капчи
	print(user_answer['captchaSolve'])
	print(user_answer['taskId'])
elif user_answer['error']:
	# Тело ошибки, если есть
	print(user_answer ['errorBody'])
	print(user_answer ['errorBody'])