# Import FASTAPI
from fastapi import FastAPI, Query
from typing import Optional

# Import Pydantic
from pydantic import BaseModel

# Import Selenium
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configuração do WebDriver
options = Options()
options.headless = True
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

# URLs para scraping
urls = [
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_02",
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_03",
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_04",
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_05",
    "http://vitibrasil.cnpuv.embrapa.br/index.php?opcao=opt_06"
]

# Coleta de dados
scraped_data = []

for url in urls:
    print(f"Acessando URL: {url}")
    driver.get(url)
    
    try:
        # Aguarda a tabela carregar
        wait.until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "table.tb_base.tb_dados")
        ))
        
        # Coleta todos os elementos da tabela
        tds = driver.find_elements(By.CSS_SELECTOR, "table.tb_base.tb_dados td")
        
        # Processa os dados
        current_category = None
        for td in tds:
            class_name = td.get_attribute('class')
            text = td.text.strip()
            
            if class_name == 'tb_item':
                current_category = text
            elif class_name == 'tb_subitem' and current_category:
                scraped_data.append({
                    "categoria": current_category,
                    "item": text,
                    "url": url
                })
        
        print(f"Coletados {len(tds)} elementos de {url}")
        
    except Exception as e:
        print(f"Erro ao processar {url}: {str(e)}")

driver.quit()
print("\nColeta de dados concluída!")

# API FastAPI
app = FastAPI(
    title="API de Dados Vitibrasil",
    version="1.0.0",
    description="API para consulta de dados do Vitibrasil"
)

class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

items_db = []

@app.get("/")
async def home():
    return {
        "message": "Bem-vindo à API Vitibrasil",
        "endpoints": {
            "/get": "Busca itens por nome (parâmetro: item_name)",
            "/items": "Lista todos os itens cadastrados",
            "/data": "Lista todos os dados coletados"
        }
    }

@app.get("/get")
async def get_item(item_name: str = Query(..., description="Nome do item para busca")):
    results = []
    for item in scraped_data:
        if item_name.lower() in item['item'].lower():
            results.append(item)
    
    if not results:
        return {"message": f"Nenhum item encontrado com o nome '{item_name}'"}
    
    return results

@app.get("/data")
async def get_all_data():
    return scraped_data

@app.get("/items")
async def get_items():
    return items_db

@app.post("/items", status_code=201)
async def create_item(item: Item):
    items_db.append(item.dict())
    return item

# Execução do servidor
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=4
    )

