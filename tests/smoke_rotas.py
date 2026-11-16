import socket
import sys
from urllib.error import URLError
from urllib.request import HTTPError, urlopen

MSG_TIMEOUT = "Servidor não respondeu a tempo, verifique a ligação ao servidor"

paths = [
    # 9 testes
    ("/live", 200),
    ("/historico", 200),
    ("/medias", 200),
    ("/medias?passo=7", 422),
    ("/medias?passo=0", 422),
    ("/nada", 404),
    # dependem do Arduino: 200 com leituras recentes, 404 (ou 503 em "/") sem elas
    ("/", 200),
    ("/media", 200),
    ("/estatisticas", 200),
]
fail = 0
passes = 0

for caminho, codigo in paths:
    obtido = None
    error = None
    try:
        r = urlopen(f"http://127.0.0.1:8000{caminho}", timeout = 3)
        obtido = r.status
    except HTTPError as e:
        obtido = e.code # salva codigo de erro (ex. 404; 500; 4xx; 5xx)
        error = e
    except URLError as e:
        obtido = None
        if isinstance(e.reason, socket.timeout):
            error = MSG_TIMEOUT
        else:
            error = "Servidor não respondeu" # custom error msg
    except TimeoutError:
        obtido = None
        error = MSG_TIMEOUT

    if obtido == codigo:
        print(f"ok     {caminho} {obtido}")
        passes += 1
    else:
        detalhe = f" ({error})" if error else ""
        print(f"FALHOU {caminho} esperado {codigo}, obtido {obtido}{detalhe}")
        fail += 1

if passes < len(paths): # apenas se algum falhar
    print(f"\n{passes} testes passaram e {fail} falharam")
# se algum teste falhar, o programa sai com o codigo 1,
# assim o `echo $?` mostra 1 quando algo falha, em vez de 0
if fail > 0:
    sys.exit(1)
