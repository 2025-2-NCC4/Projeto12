from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import google.generativeai as genai
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np

app = Flask(__name__)

# 🔹 Coloque sua chave da API do Gemini aqui
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# 🔹 Função para gerar previsão simples (linear) a partir de dados históricos
def gerar_previsao():
    # Dados simulados de receita por mês
    dados = pd.DataFrame({
        "mes": [1, 2, 3, 4],
        "receita": [100, 120, 130, 150]
    })
    X = dados["mes"].values.reshape(-1,1)
    y = dados["receita"].values

    modelo = LinearRegression()
    modelo.fit(X, y)

    proximo_mes = np.array([[5]])
    previsao = modelo.predict(proximo_mes)[0]
    return previsao

# 🔹 Endpoint para o chat
@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    # 🔹 Gera a previsão
    previsao = gerar_previsao()

    # 🔹 Cria prompt para a IA, com contexto
    prompt = f"""
    Você é um assistente de dados da empresa PicMoney.
    Use o contexto abaixo para responder à pergunta do usuário.

    Contexto: A previsão de receita para o próximo mês é de R$ {previsao:.2f} mil.

    Pergunta do usuário: {user_message}
    """
    
    # 🔹 Chama a API do Gemini para gerar resposta
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    
    ai_reply = response.text.strip()
    return jsonify({"reply": ai_reply})

if __name__ == "__main__":
    app.run(port=5000, debug=True)