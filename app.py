import streamlit as st
import pdfplumber
from datetime import datetime
import calendar

# Configuração da página
st.set_page_config(page_title="Gerador de Relatório - Bertioga", page_icon="⚡", layout="centered")

CLIENTES_BERTIOGA = 64400

def verifica_meta(real, meta):
    try:
        r = float(str(real).replace(',', '.'))
        m = float(str(meta).replace(',', '.'))
        return "✅" if r <= m else "❌"
    except:
        return "❓"

def extrair_dados_bertioga(ficheiro_pdf):
    try:
        with pdfplumber.open(ficheiro_pdf) as pdf:
            for page in pdf.pages:
                tabelas = page.extract_tables()
                for tabela in tabelas:
                    for linha in tabela:
                        linha_limpa = [str(cel).strip() for cel in linha if cel is not None]
                        if len(linha_limpa) > 0 and "Bertioga" in linha_limpa[0]:
                            return linha_limpa
    except Exception as e:
        st.error(f"Erro ao ler o ficheiro: {e}")
    return []

# Interface do Site
st.title("⚡ Relatório Diário - UTD Bertioga")
st.markdown("Arrasta o ficheiro PDF com os indicadores para a caixa abaixo e o relatório será gerado automaticamente.")

# Área de Drag and Drop
ficheiro_carregado = st.file_uploader("Carrega o PDF do Gráfico Diário", type=["pdf"])

if ficheiro_carregado is not None:
    with st.spinner('A processar os dados...'):
        linha_bertioga = extrair_dados_bertioga(ficheiro_carregado)

        if not linha_bertioga:
            st.warning("⚠️ Não encontrei os dados da UTD Bertioga neste ficheiro. Verifica se é o PDF correto.")
        else:
            try:
                dados = {
                    "dec_meta_mes": linha_bertioga[3],   
                    "dec_real_mes": linha_bertioga[4],
                    "dec_meta_acum": linha_bertioga[5],
                    "dec_real_acum": linha_bertioga[6],
                    
                    "fec_meta_mes": linha_bertioga[7],
                    "fec_real_mes": linha_bertioga[8],
                    "fec_meta_acum": linha_bertioga[9],
                    "fec_real_acum": linha_bertioga[10],
                    
                    "tma_meta_mes": linha_bertioga[11],
                    "tma_real_mes": linha_bertioga[12],
                    "tma_meta_acum": linha_bertioga[13],
                    "tma_real_acum": linha_bertioga[14],
                    
                    "int_meta_mes": "50", 
                    "int_real_mes": "38", 
                    "int_meta_acum": "667",
                    "int_real_acum": "668",
                    
                    "rein_meta_acum": "84",
                    "rein_real_acum": "74"
                }
                
                # Cálculo do CHI
                dec_meta_float = float(dados['dec_meta_mes'].replace(',', '.'))
                dec_real_float = float(dados['dec_real_mes'].replace(',', '.'))
                
                chi_restante = (dec_meta_float - dec_real_float) * CLIENTES_BERTIOGA
                
                hoje = datetime.now()
                dias_no_mes = calendar.monthrange(hoje.year, hoje.month)[1]
                dias_restantes = dias_no_mes - hoje.day
                if dias_restantes == 0: dias_restantes = 1
                
                chi_dia = chi_restante / dias_restantes
                
                nome_mes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
                mes_atual = nome_mes[hoje.month - 1]

                mensagem = f"""⚠️ DEC e FEC- {mes_atual} ⚠️

DEC

Meta mês - {dados['dec_meta_mes']}
Real mês - {dados['dec_real_mes']} {verifica_meta(dados['dec_real_mes'], dados['dec_meta_mes'])}

Meta acumulado - {dados['dec_meta_acum']}
Real acumulado - {dados['dec_real_acum']} {verifica_meta(dados['dec_real_acum'], dados['dec_meta_acum'])}

FEC

Meta mês - {dados['fec_meta_mes']}
Real mês - {dados['fec_real_mes']} {verifica_meta(dados['fec_real_mes'], dados['fec_meta_mes'])}

Meta acumulado - {dados['fec_meta_acum']}
Real acumulado - {dados['fec_real_acum']} {verifica_meta(dados['fec_real_acum'], dados['fec_meta_acum'])}

CHI restante mês: {int(chi_restante)}
CHI dia: {int(chi_dia)} 

TMA 

Meta mês: {dados['tma_meta_mes']}
Resultado mês: {dados['tma_real_mes']} {verifica_meta(dados['tma_real_mes'], dados['tma_meta_mes'])}

Meta acumulado: {dados['tma_meta_acum']}
Resultado acumulado: {dados['tma_real_acum']} {verifica_meta(dados['tma_real_acum'], dados['tma_meta_acum'])}

Interrupções

Meta mês: {dados['int_meta_mes']}
Resultado mês: {dados['int_real_mes']} {verifica_meta(dados['int_real_mes'], dados['int_meta_mes'])}

Meta acumulado: {dados['int_meta_acum']}
Resultado acumulado: {dados['int_real_acum']} {verifica_meta(dados['int_real_acum'], dados['int_meta_acum'])}

Reincidências

Meta acumulado: {dados['rein_meta_acum']}
Resultado acumulado: {dados['rein_real_acum']} {verifica_meta(dados['rein_real_acum'], dados['rein_meta_acum'])}
"""
                st.success("✅ Relatório gerado com sucesso! Podes copiar o texto abaixo:")
                
                # A magia acontece aqui: cria um bloco de texto fácil de copiar
                st.code(mensagem, language="text")

            except IndexError:
                st.error("⚠️ O ficheiro PDF não tem as colunas esperadas. Verifica a estrutura do documento.")
