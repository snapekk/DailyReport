import streamlit as st
import pdfplumber
from datetime import datetime
import calendar

st.set_page_config(page_title="Relatório Bertioga", page_icon="⚡", layout="centered")

CLIENTES_BERTIOGA = 64400

def verifica_meta(real, meta):
    try:
        r = float(str(real).replace(',', '.'))
        m = float(str(meta).replace(',', '.'))
        return "✅" if r <= m else "❌"
    except:
        return "❓"

def extrair_linha_por_pagina(pdf, num_pagina):
    """
    Vai numa página específica do PDF (ex: 1 para a primeira) e pega a linha de Bertioga.
    Mantém as células vazias para não estragar a contagem dos índices.
    """
    try:
        if num_pagina > len(pdf.pages):
            return [] # Se a página não existir no PDF
            
        pagina = pdf.pages[num_pagina - 1] # -1 porque o Python começa a contar do zero
        tabelas = pagina.extract_tables()
        
        for tabela in tabelas:
            for linha in tabela:
                # O PULO DO GATO: Se for None (vazio), coloca "" em vez de apagar, 
                # mantendo a estrutura original do array intacta!
                linha_limpa = [str(cel).strip().replace('\n', ' ') if cel is not None else "" for cel in linha]
                
                if len(linha_limpa) > 0 and "Bertioga" in linha_limpa[0]:
                    # Garante que a lista tenha pelo menos uns 20 espaços pra não dar IndexError
                    linha_limpa = linha_limpa + [""] * (20 - len(linha_limpa))
                    return linha_limpa
    except Exception as e:
        st.error(f"Erro ao ler a página {num_pagina}: {e}")
    return []

st.title("⚡ Relatório Diário - UTD Bertioga")
st.markdown("Arrasta o **PDF completo** para a caixa abaixo. O sistema já vai ler as páginas certas (1, 2, 4, 5 e 6).")

ficheiro_carregado = st.file_uploader("Carrega o PDF do Gráfico Diário", type=["pdf"])

if ficheiro_carregado is not None:
    with st.spinner('Mapeando as páginas e extraindo dados, segura a emoção...'):
        try:
            with pdfplumber.open(ficheiro_carregado) as pdf:
                # Pegando a linha da Bertioga em cada página específica
                pag1 = extrair_linha_por_pagina(pdf, 1)
                pag2 = extrair_linha_por_pagina(pdf, 2)
                pag4 = extrair_linha_por_pagina(pdf, 4)
                pag5 = extrair_linha_por_pagina(pdf, 5)
                pag6 = extrair_linha_por_pagina(pdf, 6)

            # Verificação básica se achou na primeira página
            if not pag1:
                st.warning("⚠️ Não encontrei os dados na Página 1. Tem certeza que é o PDF certo?")
            else:
                # ==========================================
                # DICIONÁRIO MAPEADO CONFORME A SUA LISTA
                # ==========================================
                dados = {
                    # PÁGINA 1 - DEC e FEC
                    "dec_real_mes": pag1[1],
                    "dec_meta_mes": pag1[3],
                    "fec_real_mes": pag1[4],
                    "fec_meta_mes": pag1[6],
                    "dec_real_acum": pag1[7],
                    "dec_meta_acum": pag1[9],
                    "fec_real_acum": pag1[10],
                    "fec_meta_acum": pag1[12],

                    # PÁGINA 2 - TMA
                    "tma_real_mes": pag2[6] if pag2 else "0",
                    "tma_meta_mes": pag2[12] if pag2 else "0",
                    "tma_real_acum": pag2[9] if pag2 else "0",
                    "tma_meta_acum": pag2[15] if pag2 else "0",

                    # PÁGINA 4 - Interrupções Acumulado
                    "int_real_acum": pag4[2] if pag4 else "0",
                    "int_meta_acum": pag4[3] if pag4 else "0",

                    # PÁGINA 5 - Interrupções Mês
                    "int_real_mes": pag5[2] if pag5 else "0",
                    "int_meta_mes": pag5[3] if pag5 else "0",

                    # PÁGINA 6 - Reincidências Acumulado
                    "rein_real_acum": pag6[2] if pag6 else "0",
                    "rein_meta_acum": pag6[3] if pag6 else "0"
                }

                # Cálculo automático do CHI (deixei rodando por baixo dos panos, 
                # mas você preenche manual ou usa o gerado se quiser)
                try:
                    dec_meta_float = float(dados['dec_meta_mes'].replace(',', '.'))
                    dec_real_float = float(dados['dec_real_mes'].replace(',', '.'))
                    chi_restante = (dec_meta_float - dec_real_float) * CLIENTES_BERTIOGA
                    
                    hoje = datetime.now()
                    dias_no_mes = calendar.monthrange(hoje.year, hoje.month)[1]
                    dias_restantes = dias_no_mes - hoje.day
                    if dias_restantes == 0: dias_restantes = 1
                    
                    chi_dia = chi_restante / dias_restantes
                except:
                    chi_restante = 0
                    chi_dia = 0

                nome_mes = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
                mes_atual = nome_mes[datetime.now().month - 1]

                # ==========================================
                # O TEXTO FORMATADO (IDÊNTICO AO SEU MODELO)
                # ==========================================
                mensagem = f"""⚠️ *DEC e FEC- {mes_atual}* ⚠️

*DEC*

Meta mês - {dados['dec_meta_mes']}
Real mês - {dados['dec_real_mes']} {verifica_meta(dados['dec_real_mes'], dados['dec_meta_mes'])}

Meta acumulado - {dados['dec_meta_acum']}
Real acumulado - {dados['dec_real_acum']} {verifica_meta(dados['dec_real_acum'], dados['dec_meta_acum'])}

*FEC*

Meta mês - {dados['fec_meta_mes']}
Real mês - {dados['fec_real_mes']} {verifica_meta(dados['fec_real_mes'], dados['fec_meta_mes'])}

Meta acumulado - {dados['fec_meta_acum']}
Real acumulado - {dados['fec_real_acum']} {verifica_meta(dados['fec_real_acum'], dados['fec_meta_acum'])}


CHI restante mês: {int(chi_restante)}
CHI dia: {int(chi_dia)}

*TMA* Meta mês: {dados['tma_meta_mes']}
Resultado mês: {dados['tma_real_mes']} {verifica_meta(dados['tma_real_mes'], dados['tma_meta_mes'])}

Meta acumulado: {dados['tma_meta_acum']}
Resultado acumulado: {dados['tma_real_acum']} {verifica_meta(dados['tma_real_acum'], dados['tma_meta_acum'])}

*Interrupções*

Meta mês: {dados['int_meta_mes']}
Resultado mês: {dados['int_real_mes']} {verifica_meta(dados['int_real_mes'], dados['int_meta_mes'])}

Meta acumulado: {dados['int_meta_acum']}
Resultado acumulado: {dados['int_real_acum']} {verifica_meta(dados['int_real_acum'], dados['int_meta_acum'])}

*Reincidências*

Meta acumulado: {dados['rein_meta_acum']}
Resultado acumulado: {dados['rein_real_acum']} {verifica_meta(dados['rein_real_acum'], dados['rein_meta_acum'])}
"""
                st.success("✅ Relatório gerado! Confere se os números bateram com o mapeamento e manda bala:")
                st.code(mensagem, language="text")

        except Exception as e:
            st.error(f"Vish, deu algum erro crítico ao processar o arquivo: {e}")
