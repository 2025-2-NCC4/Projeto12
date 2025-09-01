import dash
from dash import html, dcc, Input, Output, State
import requests

app = dash.Dash(__name__)

# 🔹 Layout da dashboard
app.layout = html.Div([
    html.H2("Dashboard PicMoney - Chat com IA"),
    
    # 🔹 Área do chat
    html.Div(id="chat-box", style={
        "border":"1px solid black",
        "height":"300px",
        "overflowY":"scroll",
        "padding":"10px",
        "marginBottom":"10px"
    }),
    
    # 🔹 Campo para digitar pergunta
    dcc.Input(id="user-input", type="text", placeholder="Digite sua pergunta...", style={"width":"70%"}),
    
    # 🔹 Botão de enviar
    html.Button("Enviar", id="send-btn", n_clicks=0)
])

# 🔹 Callback para atualizar o chat
@app.callback(
    Output("chat-box", "children"),
    Input("send-btn", "n_clicks"),
    State("user-input", "value"),
    State("chat-box", "children"),
    prevent_initial_call=True
)
def update_chat(n_clicks, user_msg, chat_history):
    if not user_msg:
        return chat_history

    # 🔹 Chama o backend Flask para obter resposta da IA
    response = requests.post("http://localhost:5000/chat", json={"message": user_msg})
    ai_reply = response.json().get("reply")

    # 🔹 Atualiza histórico de mensagens
    chat_history = chat_history or []
    chat_history.append(html.Div(f"Você: {user_msg}"))
    chat_history.append(html.Div(f"IA: {ai_reply}", style={"marginLeft":"20px","color":"blue"}))

    return chat_history

if __name__ == "__main__":
    app.run(debug=True)