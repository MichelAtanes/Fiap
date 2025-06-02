# Import FASTAPI
from fastapi import FastAPI

# Import Pydantic
from pydantic import BaseModel

# Import Pandas
#import pandas as pd 

# Import Selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from selenium.webdriver.common.by import By
import time



wait = WebDriverWait(webdriver, 10)


# # Configurar opções do Chrome
# chrome_options = Options()
# chrome_options.add_argument("--headless")  # Execute o Chrome em modo headless
# chrome_options.add_argument("--no-sandbox")
# chrome_options.add_argument("--disable-dev-shm-usage")
 
# # Inicializar o WebDriver
# service = Service()
# driver = webdriver.Chrome()

# Web Scraping
## Coloca o navegador em tela cheia




options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)


# ... (imports permanecem iguais) ...

# Inicializar o WebDriver
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# URLs exatamente como fornecidas
urls = [
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02",
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_03",
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04",
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05",
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_06"
]

all_data = []  # Armazenar todos os dados coletados

for url in urls:
    print(f"\nAcessando URL: {url}")
    driver.get(url)
    
    try:
        # Aguardar a tabela principal carregar
        wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "table.tb_base.tb_dados")
        ))
        
        # Coletar todos os elementos TD da tabela
        tds = driver.find_elements(By.CSS_SELECTOR, "table.tb_base.tb_dados td")
        
        # Filtrar apenas os elementos com as classes relevantes
        page_data = []
        for td in tds:
            class_name = td.get_attribute('class')
            if class_name in ['tb_item', 'tb_subitem']:
                page_data.append(td.text)
        
        # Armazenar dados coletados desta URL
        all_data.append({
            "url": url,
            "data": page_data
        })
        
        print(f"Coletados {len(page_data)} itens de {url}")
        
    except Exception as e:
        print(f"Erro ao acessar {url}: {str(e)}")
        all_data.append({
            "url": url,
            "error": str(e)
        })

# Fechar o navegador
driver.quit()

# Exibir resultados
print("\nResumo da coleta:")
for result in all_data:
    if "data" in result:
        print(f"URL: {result['url']} - Itens: {len(result['data'])}")
    else:
        print(f"URL: {result['url']} - Erro: {result['error']}")

# ... (código FastAPI permanece igual) ...

# Define a estrutura basica e a documentação
app = FastAPI(
    title="Projeto 1",
    version="1.0.0",
    description="API inicial do curso de ML"
)

items = []

class item(BaseModel):
    name: str # nome de item
    description: str = None # descrção opcional
    price: float = None # Preço opcional
    quantity: int = None # quantidade opcional


@app.get("/")
async def home():
    return "Hello, FastAPI!"

@app.get("/items")
async def get_items ():
    return items

@app.post ("/items", status_code=201)
async def create_item(item: item):
    items.append(item.dict())
    return item
# main.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",  # Permite conexões de qualquer IP
        port=8000,        # Porta padrão
        reload=True,       # Recarrega automaticamente durante o desenvolvimento
        workers=4          # Número de processos worker
    )