import requests
import random
import string
import itertools
from concurrent.futures import ThreadPoolExecutor
from colorama import init, Fore, Style
import os
os.system('title Discord.gg/KayyShop')

init(autoreset=True)

elephant_art = r"""
               _.-- ,.--.
             .'   .'    /
             | @       |'..--------._    
            /      \._/              '.
           /  .-.-                     \
           (  /    \                     \
            \\      '.                  | #
             \\       \   -.           / 
              :\       |    )._____.'   \
               "       |   /  \  |  \    )
                       |   |./'  :__ \.-'
                       '--'
"""
print(elephant_art)

usar_webhook = input(Fore.CYAN + "¿Deseas utilizar webhook? (s/n): " + Style.RESET_ALL).strip().lower()
if usar_webhook == "s":
    webhook_url = input(Fore.CYAN + "Introduce la URL del webhook: " + Style.RESET_ALL).strip()
else:
    webhook_url = None

proxies = []
with open('proxys.txt', 'r') as f:
    proxies = [line.strip() for line in f.readlines()]

proxy_pool = itertools.cycle(proxies)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Accept": "application/json"
}

def generar_codigo():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

def proxy_format(proxy):
    ip, port, user, pwd = proxy.split(":")
    return {
        "http": f"http://{user}:{pwd}@{ip}:{port}",
        "https": f"http://{user}:{pwd}@{ip}:{port}"
    }

def enviar_webhook(codigo):
    if webhook_url:
        data = {"content": f"Código válido encontrado: https://discord.gift/{codigo}"}
        requests.post(webhook_url, json=data)

def comprobar_codigo(codigo):
    proxy = next(proxy_pool)
    url = f"https://discord.com/api/v10/entitlements/gift-codes/{codigo}"
    proxy_dict = proxy_format(proxy)

    try:
        response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=10)
        contenido = response.json()

        if 'redeemed' in contenido and contenido['redeemed'] is False:
            resultado = f"[+] Valido: https://discord.gift/{codigo}"
            print(Fore.GREEN + resultado + Style.RESET_ALL)
            enviar_webhook(codigo)
            return resultado
        elif 'message' in contenido and 'rate limited' in contenido['message'].lower():
            print(Fore.YELLOW + f"Rate Limit detectado con proxy {proxy}. Saltando código..." + Style.RESET_ALL)
            return None
        else:
            resultado = f"[-] Invalido: https://discord.gift/{codigo}"
            print(Fore.RED + resultado + Style.RESET_ALL)
            return resultado
    except Exception as e:
        print(Fore.MAGENTA + f"ERROR con proxy {proxy}: {e}" + Style.RESET_ALL)
        return None

def modo_automatico():
    try:
        cantidad = int(input(Fore.CYAN + "Introduce la cantidad de códigos a comprobar: " + Style.RESET_ALL).strip())
    except ValueError:
        print(Fore.YELLOW + "Valor inválido. Se utilizará 100 códigos por defecto." + Style.RESET_ALL)
        cantidad = 100

    resultados = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(comprobar_codigo, generar_codigo()) for _ in range(cantidad)]
        for future in futures:
            res = future.result()
            if res:
                resultados.append(res)

    with open('resultados.txt', 'w') as file:
        file.write('\n'.join(resultados))
    print(Fore.CYAN + "Comprobación completada. Resultados guardados en 'resultados.txt'." + Style.RESET_ALL)

def modo_manual():
    codigo = input(Fore.CYAN + "Introduce el código para comprobar (ej: .../YQm8DAsAYQqntZwT): " + Style.RESET_ALL).strip()
    resultado = comprobar_codigo(codigo)
    if not resultado:
        print(Fore.YELLOW + "No se pudo completar la comprobación." + Style.RESET_ALL)

def main():
    opcion = input(Fore.CYAN + "Selecciona una opción:\n1. Generar y comprobar automáticamente códigos\n2. Introducir código manualmente para comprobar\nTu elección (1 o 2): " + Style.RESET_ALL)
    if opcion == "1":
        modo_automatico()
    elif opcion == "2":
        modo_manual()
    else:
        print(Fore.YELLOW + "Opción inválida. Por favor, elige 1 o 2." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
