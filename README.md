# 🏫 FECAP - Fundação de Comércio Álvares Penteado

<p align="center">
<a href= "https://www.fecap.br/"><img src="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRhZPrRa89Kma0ZZogxm0pi-tCn_TLKeHGVxywp-LXAFGR3B1DPouAJYHgKZGV0XTEf4AE&usqp=CAU" alt="FECAP - Fundação de Comércio Álvares Penteado" border="0"></a>
</p>

# Projeto 12: Análise PicMoney - Dashboard

## Nome do Grupo: Radonix

## Integrantes: <a href="https://www.linkedin.com/in/gabrielcarvalhomota/">Gabriel Carvalho</a>, <a href="https://www.linkedin.com/in/sik4s/">Guilherme Siqueira</a>, <a href="https://www.linkedin.com/in/rluizreis/">Rodrigo Reis</a>, <a href="https://www.linkedin.com/in/vitória-maciel-8308a42a6/">Vitória Leticia Maciel</a>.

## Professores Orientadores: <a href="https://www.linkedin.com/in/eduardo-savino/">Eduardo Savino Gomes</a>, <a href="https://www.linkedin.com/in/lucymari/">Lucy Mari Tabuti</a>, <a href="https://www.linkedin.com/in/professorrodnil/">Rodnil Lisbôa</a>, <a href="https://www.linkedin.com/in/mauricio-lopes-da-cunha-5630492a/">Mauricio Lopes da Cunha</a>.

## 💰 Descrição - Projeto PicMoney

<p align="center">
  <img src="img/gif_picmoney.gif" alt="Demonstração do Dashboard" width="100%">
</p>
<p align="center">
  Project by <a>Gabriel Carvalho, Guilherme Siqueira, Rodrigo Reis, Vitória Maciel</a>
</p>

Nosso projeto visa criar um dashboard interativo para a startup PicMoney, que usa realidade aumentada para distribuir cupons de desconto. A ideia é montar uma ferramenta para os diretores da empresa (como CEO e CFO), que junte as informações mais importantes — financeiras, operacionais e estratégicas — em um só lugar para facilitar a análise do negócio.   

Na prática, o painel vai permitir que cada diretor veja os dados mais relevantes para a sua área de um jeito simples e personalizado. O objetivo final é transformar uma grande quantidade de números em uma visão clara que ajude os executivos a tomar decisões melhores para a empresa. 
<br><br>

## 🚀 Ferramentas e Funcionalidades
Este projeto foi construído utilizando um conjunto de ferramentas modernas de Python para análise e visualização de dados, com foco em interatividade e performance.

🛠️ <b>Ferramentas Utilizadas</b>  
Linguagem Principal: Python  
Framework Web/Dashboard: Streamlit (para a criação da interface interativa multi-página)  
Banco de Dados: MySQL (utilizado como a fonte de dados central, hospedando os dados transacionais e cadastrais)  
Análise e Manipulação de Dados: Pandas (para limpeza, transformação, derivação e agregação dos dados)  
Visualização de Dados (Gráficos): Plotly Express (para a criação de todos os gráficos interativos, incluindo barras, linhas, dispersão, rosca e os mapas de calor)  
Dados Geoespaciais: GeoJSON (arquivo de "molde" para os limites dos bairros de São Paulo)  
Estilização Customizada: HTML/CSS (injetado via Streamlit para aplicar a paleta de cores neon, o tema escuro e o layout customizado)  
IA (Módulo Adicional): Google Gemini API (google-generativeai) (utilizado na página de Chatbot para interação em linguagem natural)  

✨ <b>Principais Funcionalidades</b>  
O dashboard é uma aplicação multi-página totalmente funcional, dividida por perfil de usuário:  
Autenticação (Back-end): Um sistema de login (desenvolvido em Flask) que direciona o usuário (CEO ou CFO) para seu respectivo painel.  
Design Customizado: Interface com tema escuro e paleta de cores neon (verde e amarelo).  
Filtros Dinâmicos Globais: Um painel lateral persistente que permite filtrar todos os dados do dashboard por Intervalo de Datas, Categoria de Parceiro e Bairro, com funcionalidade de "Selecionar Todos".  

## 🎨 Figma
https://www.figma.com/design/XSnCrIA0VI2R1HRHaQzGYF/PI_PicMoney?node-id=63-3&p=f&t=seDTZs1m6twetZBW-0 
<br><br>

## 🛠 Estrutura de pastas

```
├── documentos/
│   ├── Entrega1/
│   │   ├── Análise_Inferencial_de_Dados/
│   │   ├── Engenharia_de_Software_e_Arquitetura_de_Sistemas/
│   │   ├── Projeto_Interdisciplinar_Ciência_de_Dados/
│   │   └── Contabilidade_e_Finanças/
│   ├── Entrega2/
│   │   ├── Análise_Inferencial_de_Dados/
│   │   ├── Engenharia_de_Software_e_Arquitetura_de_Sistemas/
│   │   ├── Projeto_Interdisciplinar_Ciência_de_Dados/
│   │   └── Contabilidade_e_Finanças/
│   ├── Banner_FECAP_CCOMP4_Radonix.pdf
│   ├── Banner_FECAP_CCOMP4_Radonix.pptx
│   ├── Documentação.docx
│   ├── Documentação.pdf
├── imagens/
├── src/
│   ├── Entrega1/
│   │   ├── frontend/
│   │   └── backend/
│   ├── Entrega2/
│   │   ├── frontend/
│   │   └── backend/
│   ├── db_PicMoney/
└── readme.md<br>
```

<b>📄 README.MD</b>: Arquivo que serve como guia e explicação geral sobre o projeto.

Há também 4 pastas que seguem da seguinte forma:

<b>🗂️ Documentos</b>: Toda a documentação geral do projeto. Além das entregas das disciplinas do semestre.

<b>📷 imagens</b>: Imagens utilizadas para documentação e explicação do projeto.

<b>🧑‍💻 src</b>: Pasta que contém o código fonte (frontend e backend).

## 🛠 Instalação
<b>1 - Pré-requisitos:</b>  
Antes de começar, garanta que você tenha os seguintes softwares instalados em sua máquina:  
* Python (versão 3.9 ou superior)
* Git (para clonar o repositório)
* Um servidor MySQL (como o MySQL Community Server ou XAMPP) em execução.

<b>2 - Configuração do Ambiente</b>  
<b>Clonar o Repositório Abra seu terminal e clone este repositório:</b>  
```sh
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```
<b>3 - Instalar as Bibliotecas Python Este projeto requer várias bibliotecas. Instale todas com pip.</b>  
<b>4 - Execute o Projeto</b>  

## 💻 Configuração para Desenvolvimento
Todas as dependências estão no arquivo [requirements](src/Entrega02/requirements.txt).

## 📋 Licença/License
PicMoney © 2025 by Gabriel Carvalho, Guilherme Siqueira, Rodrigo Luiz, Vitória Maciel is licensed under CC BY 4.0

## 🎓 Referências
- Python PYTHON Software Foundation. Python.org. [S.l.]: Python Software Foundation, 2025. Disponível em: https://www.python.org/.  
- Streamlit STREAMLIT, Inc. Streamlit Documentation. [S.l.]: Streamlit, Inc., 2025. Disponível em: https://docs.streamlit.io/.  
- Pandas THE PANDAS Development Team. pandas documentation. [S.l.]: Pandas Development Team, 2025. Disponível em: https://pandas.pydata.org/docs/.  
- Plotly (incluindo Plotly Express) PLOTLY. Plotly Python Graphing Library. [S.l.]: Plotly, 2025. Disponível em: https://plotly.com/python/.  
- NumPy THE NUMPY COMMUNITY. NumPy documentation. [S.l.]: The NumPy community, 2025. Disponível em: https://numpy.org/doc/.  
- Flask PALLETS. Flask Documentation. [S.l.]: Pallets, 2025. Disponível em: https://flask.palletsprojects.com/.  
- SQLAlchemy SQLALCHEMY authors and contributors. SQLAlchemy documentation. [S.l.]: SQLAlchemy authors and contributors, 2025. Disponível em: https://docs.sqlalchemy.org/en/20/.  
- Google Gemini API (Google AI Studio) GOOGLE. Gemini API documentation. [S.l.]: Google, 2025. Disponível em: https://ai.google.dev/docs/gemini_api.  
- Galeria Pública do Tableau TABLEAU. Galeria Pública. [S.l.]: Tableau, 2025. Disponível em: https://public.tableau.com/pt-br/s/gallery.  
- Galeria de Histórias de Dados do Power BI (Microsoft) MICROSOFT. Power BI Data Stories Gallery. [S.l.]: Microsoft, 2025. Disponível em: https://community.fabric.microsoft.com/t5/Data-Stories-Gallery/bd-p/DataStoriesGallery.  
- Exemplos e Modelos de Dashboards (Datapin) DATAPIN. 25+ Best Interactive Dashboard Examples & Templates for 2024. [S.l.]: Datapin, 2024. Disponível em: https://www.datapin.com/blog/interactive-dashboard-examples.  
