from flask import Flask, render_template, request, url_for 

# Cria a aplicação Flask
app = Flask(__name__)


# ---------- VALIDAÇÕES ----------

# Verifica se o número contém apenas 0 e 1
def validar_binario(numero):
    return numero != "" and all(c in "01" for c in numero)


# Verifica se o número é decimal
def validar_decimal(numero):
    return numero != "" and all(c in "0123456789" for c in numero)


# Verifica se o hexadecimal é válido
def validar_hexadecimal(numero):
    return numero != "" and all(c.upper() in "0123456789ABCDEF" for c in numero)


# ---------- FUNÇÕES AUXILIARES ----------

# Remove zeros à esquerda
def remover_zeros_esquerda(numero):
    return numero.lstrip("0") or "0"


# Completa os números com zeros para ficarem do mesmo tamanho
def completar_zeros_esquerda(a, b):
    while len(a) < len(b):
        a = "0" + a

    while len(b) < len(a):
        b = "0" + b

    return a, b


# Converte um dígito hexadecimal para decimal
def digito_hex_para_decimal(c):
    c = c.upper()

    if "0" <= c <= "9":
        return ord(c) - ord("0")

    return ord(c) - ord("A") + 10


# Converte decimal para dígito hexadecimal
def decimal_para_digito_hex(n):
    if n < 10:
        return chr(ord("0") + n)

    return chr(ord("A") + n - 10)


# ---------- CONVERSÕES ----------

# Binário -> Decimal
def binario_para_decimal(binario):
    decimal = 0

    for bit in binario:
        decimal = decimal * 2 + (bit == "1")

    return decimal


# Decimal -> Binário
def decimal_para_binario(decimal):
    if decimal == 0:
        return "0"

    resultado = ""

    while decimal > 0:
        resultado = str(decimal % 2) + resultado
        decimal //= 2

    return resultado


# Hexadecimal -> Decimal
def hexadecimal_para_decimal(hexadecimal):
    decimal = 0

    for c in hexadecimal:
        decimal = decimal * 16 + digito_hex_para_decimal(c)

    return decimal


# Decimal -> Hexadecimal
def decimal_para_hexadecimal(decimal):
    if decimal == 0:
        return "0"

    resultado = ""

    while decimal > 0:
        resultado = decimal_para_digito_hex(decimal % 16) + resultado
        decimal //= 2

    return resultado


# Binário -> Hexadecimal
def binario_para_hexadecimal(binario):
    return decimal_para_hexadecimal(
        binario_para_decimal(binario)
    )


# Hexadecimal -> Binário
def hexadecimal_para_binario(hexadecimal):
    return decimal_para_binario(
        hexadecimal_para_decimal(hexadecimal)
    )


# ---------- OPERAÇÕES BINÁRIAS ----------

# Soma binária
def soma_binaria(a, b):

    # Iguala o tamanho dos números
    a, b = completar_zeros_esquerda(a, b)

    transporte = 0
    resultado = ""

    # Percorre os bits da direita para a esquerda
    for i in range(len(a) - 1, -1, -1):

        soma = int(a[i]) + int(b[i]) + transporte

        resultado = str(soma % 2) + resultado

        transporte = soma // 2

    # Adiciona transporte final
    if transporte:
        resultado = "1" + resultado

    return remover_zeros_esquerda(resultado)


# Compara dois binários
def comparar_binarios(a, b):

    a = remover_zeros_esquerda(a)
    b = remover_zeros_esquerda(b)

    if len(a) > len(b):
        return 1

    if len(a) < len(b):
        return -1

    return (a > b) - (a < b)


# Subtração binária
def subtracao_binaria(a, b):

    negativo = False

    # Verifica qual número é maior
    if comparar_binarios(a, b) < 0:
        a, b = b, a
        negativo = True

    a, b = completar_zeros_esquerda(a, b)

    emprestimo = 0
    resultado = ""

    for i in range(len(a) - 1, -1, -1):

        bit_a = int(a[i]) - emprestimo
        bit_b = int(b[i])

        if bit_a < bit_b:
            bit_a += 2
            emprestimo = 1

        else:
            emprestimo = 0

        resultado = str(bit_a - bit_b) + resultado

    resultado = remover_zeros_esquerda(resultado)

    if negativo:
        return "-" + resultado

    return resultado


# Multiplicação binária
def multiplicacao_binaria(a, b):

    resultado = "0"

    # Inverte o segundo número
    b = b[::-1]

    for i in range(len(b)):

        # Soma apenas quando o bit é 1
        if b[i] == "1":
            resultado = soma_binaria(
                resultado,
                a + "0" * i
            )

    return remover_zeros_esquerda(resultado)


# ---------- OPERAÇÕES HEXADECIMAIS ----------

# Soma hexadecimal
def soma_hexadecimal(a, b):

    a, b = completar_zeros_esquerda(
        a.upper(),
        b.upper()
    )

    transporte = 0
    resultado = ""

    for i in range(len(a) - 1, -1, -1):

        soma = (
            digito_hex_para_decimal(a[i]) +
            digito_hex_para_decimal(b[i]) +
            transporte
        )

        resultado = (
            decimal_para_digito_hex(soma % 16)
            + resultado
        )

        transporte = soma // 16

    if transporte:
        resultado = (
            decimal_para_digito_hex(transporte)
            + resultado
        )

    return remover_zeros_esquerda(resultado)


# Subtração hexadecimal
def subtracao_hexadecimal(a, b):

    negativo = False

    # Verifica qual hexadecimal é maior
    if hexadecimal_para_decimal(a) < hexadecimal_para_decimal(b):
        a, b = b, a
        negativo = True

    a, b = completar_zeros_esquerda(
        a.upper(),
        b.upper()
    )

    emprestimo = 0
    resultado = ""

    for i in range(len(a) - 1, -1, -1):

        va = digito_hex_para_decimal(a[i]) - emprestimo
        vb = digito_hex_para_decimal(b[i])

        if va < vb:
            va += 16
            emprestimo = 1

        else:
            emprestimo = 0

        resultado = (
            decimal_para_digito_hex(va - vb)
            + resultado
        )

    resultado = remover_zeros_esquerda(resultado)

    if negativo:
        return "-" + resultado

    return resultado


# ---------- CÓDIGO GRAY ----------

# Binário -> Gray
def binario_para_gray(binario):

    gray = binario[0]

    for i in range(1, len(binario)):

        gray += str(
            int(binario[i - 1]) ^
            int(binario[i])
        )

    return gray


# Gera a tabela Gray
def gerar_gray(bits):

    tabela = []

    for i in range(2 ** bits):

        # Converte decimal para binário
        binario = decimal_para_binario(i).zfill(bits)

        # Converte binário para Gray
        gray = binario_para_gray(binario)

        tabela.append((i, binario, gray))

    return tabela


# ---------- FLASK ----------

# Página principal
@app.route("/", methods=["GET", "POST"])
def index():

    resultado = None
    tabela_gray = None
    erro = None

    # Verifica se o utilizador enviou um formulário
    if request.method == "POST":

        # Descobre qual ação foi escolhida
        acao = request.form["acao"]

        try:

            # ---------- TABELA GRAY ----------
            if acao == "gray":

                bits = int(request.form["bits"])

                tabela_gray = gerar_gray(bits)

            # ---------- CONVERSÕES ----------
            elif acao == "conversao":

                tipo = request.form["tipo_conversao"]

                numero = request.form["numero"]

                # Binário -> Decimal
                if tipo == "bin_dec" and validar_binario(numero):
                    resultado = binario_para_decimal(numero)

                # Decimal -> Binário
                elif tipo == "dec_bin" and validar_decimal(numero):
                    resultado = decimal_para_binario(int(numero))

                # Decimal -> Hexadecimal
                elif tipo == "dec_hex" and validar_decimal(numero):
                    resultado = decimal_para_hexadecimal(int(numero))

                # Hexadecimal -> Decimal
                elif tipo == "hex_dec" and validar_hexadecimal(numero):
                    resultado = hexadecimal_para_decimal(numero)

                # Binário -> Hexadecimal
                elif tipo == "bin_hex" and validar_binario(numero):
                    resultado = binario_para_hexadecimal(numero)

                # Hexadecimal -> Binário
                elif tipo == "hex_bin" and validar_hexadecimal(numero):
                    resultado = hexadecimal_para_binario(numero)

                else:
                    erro = "Número inválido."

            # ---------- OPERAÇÕES ----------
            elif acao == "operacao":

                tipo = request.form["tipo_operacao"]

                a = request.form["valor_a"]
                b = request.form["valor_b"]

                # Soma binária
                if tipo == "soma_bin":
                    resultado = soma_binaria(a, b)

                # Subtração binária
                elif tipo == "sub_bin":
                    resultado = subtracao_binaria(a, b)

                # Multiplicação binária
                elif tipo == "mult_bin":
                    resultado = multiplicacao_binaria(a, b)

                # Soma hexadecimal
                elif tipo == "soma_hex":
                    resultado = soma_hexadecimal(a, b)

                # Subtração hexadecimal
                elif tipo == "sub_hex":
                    resultado = subtracao_hexadecimal(a, b)

        # Caso aconteça algum erro
        except:
            erro = "Erro nos dados inseridos."

    # Envia os dados para o HTML
    return render_template(
        "index.html",
        resultado=resultado,
        tabela_gray=tabela_gray,
        erro=erro
    )


# Inicia o servidor Flask
if __name__ == "__main__":
    app.run(debug=True)