# importacao de bibliotecas necessarias para o projeto 
import streamlit as st
import pandas as pd
import plotly.express as px

# --- Configuração da Página ---
# Define o título da página, o ícone e o layout para ocupar a largura inteira.
st.set_page_config(
    page_title="Dashboard de Salários na Área de Dados",
    page_icon="📊", #emoji do grafico pode escolher qual 
    layout="wide", #formato largo
)

# --- Carregamento dos dados ---
# Carrega o conjunto de dados a partir de um arquivo CSV hospedado no GitHub.
# esse arquivo foi criado na imersao dados da alura previamente 
# na aula 03 - Manipulação de Dados com Pandas tinha o arquivo tratado
df = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")

# --- Barra Lateral (Filtros) ---
st.sidebar.header("🔍 Filtros") #titulo Filtros emoji lupa

# Filtro de Ano
anos_disponiveis = sorted(df['ano'].unique())  # Extrai anos únicos do DataFrame df
#abaixo anos selecionados recebe o multiselect com os anos disponiveis - para escolher os anos que quer filtrar
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, default=anos_disponiveis)

# Filtro de Senioridade
senioridades_disponiveis = sorted(df['senioridade'].unique())
senioridades_selecionadas = st.sidebar.multiselect("Senioridade", senioridades_disponiveis, default=senioridades_disponiveis)

# Filtro por Tipo de Contrato
contratos_disponiveis = sorted(df['contrato'].unique())
contratos_selecionados = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, default=contratos_disponiveis)

# Filtro por Tamanho da Empresa
tamanhos_disponiveis = sorted(df['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, default=tamanhos_disponiveis)

# --- Filtragem do DataFrame ---
# O dataframe principal é filtrado com base nas seleções feitas na barra lateral.
# a cada filtro pelo usuario tem que alimentar o dataframe filtrado
# o df_filtrado recebe o df original filtrado pelos anos, senioridade, contrato e tamanho da empresa selecionados
# tudo com base nos filtros alterados pelo usuario
df_filtrado = df[
    (df['ano'].isin(anos_selecionados)) &
    (df['senioridade'].isin(senioridades_selecionadas)) &
    (df['contrato'].isin(contratos_selecionados)) &
    (df['tamanho_empresa'].isin(tamanhos_selecionados))
]

# --- Conteúdo Principal ---
# Título e descrição do dashboard
st.title("🎲 Dashboard de Análise de Salários na Área de Dados")
st.markdown("Explore os dados salariais na área de dados nos últimos anos. Utilize os filtros à esquerda para refinar sua análise.")

# sempre um dashboard deve trazer algumas informações iniciais
# Exibe algumas métricas principais
# --- Métricas Principais (KPIs) ---
st.subheader("Métricas gerais (Salário anual em USD)")

if not df_filtrado.empty: # verifica se o dataframe filtrado nao esta vazio
    salario_medio = df_filtrado['usd'].mean() # calcula a media salarial
    salario_maximo = df_filtrado['usd'].max() #
    total_registros = df_filtrado.shape[0] # conta o numero de linhas do df filtrado
    cargo_mais_frequente = df_filtrado["cargo"].mode()[0] # encontra o cargo mais comum
else: # se o df filtrado estiver vazio
    #abaixo define todas as metricas como 0 ou vazio
    salario_medio, salario_maximo, total_registros, cargo_mais_frequente = 0, 0, 0, ""

col1, col2, col3, col4 = st.columns(4) # cria 4 colunas para exibir as metricas
#cada coluna exibe uma metrica diferente
# exemplo abaixo:
# Salário médio Salário máximo Total de registros Cargo mais frequente
# $157,619         $800,000     133,339            Data Scientist

col1.metric("Salário médio", f"${salario_medio:,.0f}") # exibe a media salarial formatada
col2.metric("Salário máximo", f"${salario_maximo:,.0f}") # exibe o salario maximo formatado
col3.metric("Total de registros", f"{total_registros:,}") # exibe o total de registros formatado
col4.metric("Cargo mais frequente", cargo_mais_frequente) # exibe o cargo mais frequente

st.markdown("---") # linha divisoria

# --- Análises Visuais com Plotly ---
st.subheader("Gráficos") #subtitulo graficos

col_graf1, col_graf2 = st.columns(2) # cria duas colunas para os graficos

with col_graf1: #
    if not df_filtrado.empty: # verifica se o df filtrado nao esta vazio
        #abaixo calcula os 10 cargos com maior media salarial
        # e ordena do maior para o menor
        top_cargos = df_filtrado.groupby('cargo')['usd'].mean().nlargest(10).sort_values(ascending=True).reset_index()
        #abaixo cria o grafico de barras horizontais com plotly express (px.bar)
        # e exibe no container
        # 10 cargos por salário médio
        # eixo x salario medio anual em usd
        # eixo y cargos
        # orientacao horizontal
        # titulo grafico 10 cargos por salario medio
        # label salario medio anual em usd
        # se nao colocar orientacao o padrao e vertical, mas pode colocar "v"
        grafico_cargos = px.bar(
            top_cargos, 
            x='usd', 
            y='cargo',
            orientation='h',
            title="Top 10 cargos por salário médio",
            labels={'usd': 'Média salarial anual (USD)', 'cargo': ''}
        )
        # exibe o grafico no container
        #title_x=0.1 alinha o titulo mais para a esquerda
        #st.plotly_chart exibe o grafico no streamlit
        #use_container_width=True ajusta o tamanho do grafico para o tamanho do container
        grafico_cargos.update_layout(title_x=0.1, yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(grafico_cargos, use_container_width=True)
    else: # se o df filtrado estiver vazio, gera um aviso
        st.warning("Nenhum dado para exibir no gráfico de cargos.")

with col_graf2: # cria a segunda coluna para o segundo grafico
    if not df_filtrado.empty:
        # grafico do tipo histograma para mostrar a distribuicao dos salarios anuais
        # calcula a distribuicao dos salarios anuais
        grafico_hist = px.histogram(
            df_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, use_container_width=True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de distribuição.")

#
col_graf3, col_graf4 = st.columns(2)

# abaixo grafico de pizza para mostrar a proporcao dos tipos de trabalho (remoto, presencial, hibrido)
with col_graf3:
    if not df_filtrado.empty: # verifica se o df filtrado nao esta vazio
        #abaixo calcula a contagem dos tipos de trabalho
        #reset_index() reseta o indice do dataframe 
        # e renomeia as colunas para tipo de trabalho e quantidade
        remoto_contagem = df_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho',
            hole=0.5
        )
        grafico_remoto.update_traces(textinfo='percent+label') # exibe percentual e label no grafico de pizza
        grafico_remoto.update_layout(title_x=0.1) # alinha o titulo mais para a esquerda
        st.plotly_chart(grafico_remoto, use_container_width=True) # exibe o grafico no streamlit
    else: # se o df filtrado estiver vazio, gera um aviso
        st.warning("Nenhum dado para exibir no gráfico dos tipos de trabalho.")

#a cada codigo desenvolvido pode executar o streamlit para ver o resultado


# grafico 4 desafio alura
# criar grafico que mostra diferenca entre a media salarial dos cargos de Data Scientist por pais
# para isso vamos usar o df original, nao o df filtrado

# instalar a biblioteca pycountry para converter nomes de paises em codigos ISO3    
# pip install pycountry - rodar no terminal
# importar a biblioteca pycountry
import pycountry

# cria a quarta coluna para o quarto grafico
with col_graf4: # cria a quarta coluna para o quarto grafico
    if not df_filtrado.empty: # verifica se o df filtrado nao esta vazio
        df_ds = df_filtrado[df_filtrado['cargo'] == 'Data Scientist'] # filtra apenas os cargos de Data Scientist
        # abaixo agrupa por pais e calcula a media salarial
        # o tipo de grafico sera um mapa coroplético
        # o titulo sera Salário médio de Cientista de Dados por país
        # residencia_iso3 e o codigo padrao de tres letras dos paises
        # loccations recebe os codigos dos paises 
        # o label do eixo y sera Salário médio (USD)
        # o label do eixo x sera País  
        # a documentacao para escala de cores do grafico pode ser consultada em:
        # https://plotly.com/python/builtin-colorscales/
        media_ds_pais = df_ds.groupby('residencia_iso3')['usd'].mean().reset_index() # calcula a media salarial por pais
        # cria o grafico coroplético com plotly express e exibe no container
        grafico_paises = px.choropleth(media_ds_pais,
            locations='residencia_iso3', # codigos dos paises no formato ISO3
            color='usd', # valor que define a cor dos paises
            color_continuous_scale='rdylgn', # escala de cores do grafico
            title='Salário médio de Cientista de Dados por país',
            labels={'usd': 'Salário médio (USD)', 'residencia_iso3': 'País'})
        grafico_paises.update_layout(title_x=0.1) # alinha o titulo mais para a esquerda
        st.plotly_chart(grafico_paises, use_container_width=True) # exibe o grafico no streamlit
    else:
        st.warning("Nenhum dado para exibir no gráfico de países.")

# quando o mapa fica em branco em algum país, provavelmente nao tem dados para exibir a cor nesse país
# --- Tabela de Dados Detalhados ---
st.subheader("Dados Detalhados") #subtitulo dados detalhados
st.dataframe(df_filtrado) # exibe o dataframe filtrado como uma tabela interativa no streamlit

# agora o dashboard esta completo com filtros, metricas principais, graficos e tabela de dados detalhados
# mas esta rodando localmente (localhost)
# para publicar na nuvem usar os comandos e ferramentas:
    # 1 - criar um repositório no github e subir o codigo la (caso nao tenha conta criar uma)
    # 2 - O nome do repositório ficou Imersao-dados-python-alura-2025
    # 3 - puxar o arquivo requirements.txt com as bibliotecas necessarias
    # 4 - puxar o arquivo app.py com o codigo do dashboard
    # 5 - puxar o arquivo dados-imersao-final.csv com os dados tratados
          #**importante para puxar os arquivos no git, usar add file/uplod file e buscar na pasta do projeto no pc
    # 6 - fazer o commit das alterações e publicar no github

    # qual ferramenta vai pegar esse projeto no github e publicar na nuvem?
    # 7 - usar o streamlit cloud - https://streamlit.io/cloud   
    
# *** observacoes sobre o streamlit cloud ***
# wants to access your ferdenek account procura a conta para acesso ao github
# Repository webhooks and services, sao usados para integrar o github com outras ferramentas
# Admin access, serve para permitir que a ferramenta tenha acesso total ao repositório 
# Codespace é um ambiente de desenvolvimento baseado em nuvem que permite criar, editar e executar código diretamente no navegador.
# Manage codespaces - Permite que a ferramenta gerencie os codespaces associados ao repositório.
# Repositories access - Permite que a ferramenta acesse os repositórios do usuário.
# Public repositories - Permite que a ferramenta acesse repositórios públicos do usuário.
# Organizations and teams access - Permite que a ferramenta acesse organizações e equipes associadas ao usuário.
# Read-only access - Permite que a ferramenta tenha acesso somente leitura aos dados.
# Personal user data - Permite que a ferramenta acesse dados pessoais do usuário.
# Email addresses (read-only) - Permite que a ferramenta acesse os endereços de e-mail do usuário em modo somente leitura.

# 8 - criar uma conta no streamlit cloud - usei opcao free (pode usar a conta do github para facilitar)
# 9 - permitir que o streamlit cloud acesse os repositórios do github
# 10 - clicar em New app
# 11 - selecionar o repositório que contem o projeto do dashboard
# 12 - selecionar a branch main e o arquivo app.py
# 13 - clicar em Deploy 
# 14 - aguardar a publicação do dashboard na nuvem (hospedando em nuvem)
# no item acima ele vai instalar as bibliotecas do requirements.txt automaticamente, pode demorar um pouco
# ja vai mostrar o dashboard rodando na nuvem
# Pronto! O dashboard agora está publicado na nuvem e pode ser acessado via URL fornecida pelo Streamlit Cloud.
# lembrando que no modo free do streamlit cloud, o dashboard pode entrar em modo de hibernação apos um periodo de inatividade
# que na aula falaram que é 24 horas

