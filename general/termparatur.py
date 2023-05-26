import requests

def get_current_temperature():
    response = requests.get('http://api.openweathermap.org/data/2.5/weather?q=London,uk&appid=10c4ee4d9d4eb05d74b695f27210b2ee')
    data = response.json()
    #print(data)
    #print(f"testing {data['main']['temp']}")
    return data['main']['temp']

current_temperature = get_current_temperature()
print(f'The current temperature is {current_temperature} degrees Fahrenheit.')
