import sqlite3
from faker import Faker
import random
import datetime

import sqlite3
import random

def get_random_isin(db_path):
    # Conectar a la base de datos
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Consulta para obtener todos los ISIN de la tabla 'funds'
    cursor.execute("SELECT ISIN FROM funds")
    isin_list = cursor.fetchall()

    # Asegúrate de cerrar la conexión
    conn.close()

    # Extraer dos ISIN de manera aleatoria
    # fetchall() devuelve una lista de tuplas, por lo que extraemos el primer elemento de cada tupla
    isin_list = [row[0] for row in isin_list]

    number_investments = random.randint(1,3)

    # Seleccionar aleatoriamente 2 ISIN si hay más de 2 disponibles
    if len(isin_list) >= number_investments:
        return random.sample(isin_list, number_investments)
    else:
        return "No hay suficientes ISIN disponibles."



def generar_dni():
    
    possible_letters = ("T","R","W","A","G","M","Y","F","P","D","X","B","N","J", 
                        "Z","S","Q","V","H","L","C","K","E","T",)
    dni_number = random.randint(10000000, 99999999)
    dni_letter = possible_letters[dni_number % 23]

    return str(dni_number) + dni_letter



def generar_fecha_nacimiento():
   current_year  = datetime.datetime.now().year
   birthday_year = random.randint(current_year - 80, current_year - 18)  # Edad entre 18 y 80 años
   
   return birthday_year


def perfil_financiero_cliente() -> str:
    # Conjunto de frases que reflejan diferentes perfiles financieros en tercera persona
    frases_perfiles = [
    "Prefers safe and low-risk investments, such as bank deposits.",
    "Feels more comfortable investing long-term to achieve stable returns.",
    "Is a conservative investor and prefers to avoid stock market volatility.",
    "Seeks investment opportunities that offer high returns, even if they involve higher risk.",
    "Is interested in diversifying their portfolio with investments in different asset classes.",
    "Likes to closely follow the stock market and make investment decisions based on technical analysis.",
    "Prefers to invest in mutual funds managed by professionals to minimize risk.",
    "Seeks investment opportunities that are ethical and socially responsible.",
    "Is willing to take on a certain level of risk to achieve higher returns.",
    "Is interested in exploring alternative investments, such as real estate crowdfunding or venture capital.",
    "Prefers to keep a significant portion of their portfolio in cash to cover unexpected expenses.",
    "Is interested in passive investment strategies, such as index tracking.",
    "Likes to invest in companies with long-term growth potential.",
    "Is an aggressive investor and is willing to take significant risks in pursuit of high returns.",
    "Prefers to avoid speculative investments and focus on stable, safe assets.",
    "Is interested in learning more about investment strategies to maximize returns.",
    "Would like to receive personalized financial advice to optimize their investment portfolio.",
    "Seeks investments that offer tax benefits, such as retirement savings plans.",
    "Prefers to invest in real estate as a way to diversify their portfolio.",
    "Is interested in exploring the cryptocurrency market and the opportunities it offers.",
    "Interested in structured products.",
    "Is interested in investing in the forex market to diversify their portfolio.",
    "Seeks financial products that allow easy withdrawal of funds in case of need.",
    "Prefers short-term investment strategies to maximize gains in the short term.",
    "Would like to invest in tech startups as a way to bet on future growth.",
    "Is interested in investing in commercial real estate to generate passive income.",
    "Would prefer to invest in government bonds as a safe investment option.",
    "Is interested in participating in collective investment programs to share risks and profits.",
    "Would like to invest in art and collectibles as an alternative form of investment.",
    "Seeks investment opportunities that allow them to take advantage of market trends.",
    "Prefers to invest in dividends to generate regular income.",
    "Is interested in investing in commodities as a way to diversify their portfolio.",
    "Is interested in investing in index funds for diversified market exposure.",
    "Seeks investments that allow them to benefit from the economic growth of emerging markets.",
    "Prefers investment strategies based on fundamental analysis of companies.",
    "Is interested in options trading as a way to profit from market volatility.",
    "Would like to explore investment opportunities in the renewable energy sector.",
    "Seeks investment opportunities that provide tax benefits.",
    "Prefers passive investment strategies, such as dollar-cost averaging, to reduce risk.",
    "Is interested in investing in the international real estate market to diversify their portfolio.",
    "Would like to explore investment opportunities in the startup market as a way to achieve high returns.",
    "Seeks investment products that offer liquidity and flexibility.",
    "Prefers conservative investment strategies to protect their capital.",
    "Is interested in investing in infrastructure as a way to generate stable long-term income.",
    "Would like to invest in hedge funds to achieve returns that outperform the market.",
    "Seeks investment opportunities that allow them to benefit from the growth of the technology industry.",
    "Prefers investment strategies based on research and market analysis.",
    "Is interested in investing in social impact startups as a way to generate positive change.",
    "Would like to explore investment opportunities in the residential real estate market.",
    "Seeks financial products that provide protection against inflation.",
    "Prefers long-term investment strategies to maximize gains over time.",
    "Is interested in investing in pension funds as a way to secure their financial future.",
    "Would like to invest in corporate bonds as a way to diversify their investment portfolio.",
    "Seeks investment opportunities that allow them to geographically diversify their portfolio.",
    "Prefers investment strategies based on economic cycle theory to make investment decisions.",
    "Is interested in investing in real estate investment trusts (REITs) to generate passive income.",
    "Would like to explore investment opportunities in the digital art market as a way to invest in digital assets.",
    "Seeks financial products that offer a balance between risk and return.",
    "Has expressed interest in private equity investment."
]

    # Seleccionar una frase aleatoria
    frase_aleatoria = random.choice(frases_perfiles)

    # Retornar la frase seleccionada
    return frase_aleatoria
    
def generar_patrimonio():
   
    min_patrimonio = 1000
    max_patrimonio = 300000  # Puedes ajustar este valor según sea necesario
    scale = 100000  # Ajustar scale para minorista
    
    # Genera un patrimonio utilizando una distribución exponencial
    patrimonio = random.expovariate(1.0 / scale)
    
    # Asegura que el patrimonio esté dentro de los límites deseados
    patrimonio = max(min_patrimonio, min(max_patrimonio, patrimonio))
    
    return int(patrimonio)
    

def crear_tabla_clientes(conn):

    # Crear una conexión a la base de datos
    c = conn.cursor()

    # Borramos la tabla antes de crearla en caso de que exista
    try:
        c.execute('''DROP TABLE clients''')
        c.execute('''DROP TABLE investments''')
    except:
        pass

    # Crear la tabla de clientes
    c.execute('''CREATE TABLE clients (
                    DNI TEXT PRIMARY KEY,
                    name TEXT,
                    surname TEXT,
                    birth_year NUMERIC,
                    net_worth NUMERIC,
                    preferences TEXT
                    )''')
    
    # Crear la tabla de inversiones
    c.execute('''CREATE TABLE investments (
                    DNI TEXT,
                    ISIN TEXT,
                    amount NUMERIC
                    )''')

    # Generar datos sintéticos para 10000 clientes
    fake = Faker('es_ES')
    for _ in range(10000):
        dni = generar_dni()
        name = fake.first_name()
        surname = fake.last_name()
        birthday = generar_fecha_nacimiento()
        net_worth = generar_patrimonio()
        preferences = perfil_financiero_cliente()

        c.execute('''INSERT INTO clients (DNI, name, surname, birth_year, net_worth, preferences)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                        (dni, name, surname, birthday, net_worth, preferences))
        
        # Para ese cliente, crea inversiones
        for isin in get_random_isin("dbfunds.db"):
            amount = random.randint(10,30)*net_worth
            c.execute('''INSERT INTO investments (DNI, isin, amount)
                        VALUES (?, ?, ?)''',
                        (dni, isin, amount))

def main():
    conn = sqlite3.connect("dbclients.db")
    crear_tabla_clientes(conn)
    conn.commit()
    conn.close()
    print("Tabla de clientes creada y rellenada con datos sintéticos.")

if __name__ == "__main__":
    main()


