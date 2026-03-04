import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime

# Configuração da Página SEAG
st.set_page_config(page_title="Gestão SEAG 2026", layout="wide")

# URL DIRETA DA PLANILHA (Reforço de conexão)
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/12nBlopOzq1LY1CDObfaNfWPU0xxa9-P-_e1IJtDgLB4/edit?gid=0#gid=0"

# --- SISTEMA DE LOGIN ---
def verificar_senha():
    if "autenticado" not in st.session_state:
        st.session_state["autenticado"] = False

    if not st.session_state["autenticado"]:
        st.markdown("<h2 style='text-align: center;'>🔐 Acesso Restrito - SEAG</h2>", unsafe_allow_html=True)
        senha_digitada = st.text_input("Digite a senha para acessar o painel:", type="password")
        
        if st.button("Entrar"):
            if senha_digitada == "seag@123":
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta! Tente novamente.")
        return False
    return True

# --- INÍCIO DO SISTEMA PÓS-LOGIN ---
if verificar_senha():
    st.title("📊 Gestão SEAG - Recadastramento 2026")

    # Conexão com Google Sheets
    conn = st.connection("gsheets", type=GSheetsConnection)

    # Função para criar os dados iniciais se a planilha estiver limpa
    def criar_dados_iniciais():
        dados_lista = [
            ("ASSIST. ODONTO E MEDICA - DENTALSAUDE", "08.775.214/0001-13"),
            ("ASSIST. ODONTO E MÉDICA - ODONTO MAIS BRASIL", "10.770.439/0001-52"),
            ("OPERADORA DE PLANOS ODONTOLOGICOS LTDA", "04.747.029/0001-34"),
            ("ASSIST. ODONTO E MEDICA - ODONTOCLINIK", "05.207.503/0001-08"),
            ("ASSIST. ODONTO E MEDICA - ODONTOMED", "05.205.811/0001-80"),
            ("ASSIST. ODONTO E MEDICA - PLANODONT", "05.355.851/0001-88"),
            ("ASSIST. ODONTO E MEDICA - SERVDONTO PLANO", "05.194.375/0001-50"),
            ("ASSIST. ODONTOLOGICA LTDA", "02.007.821/0001-81"),
            ("ASSIST. ODONTO E MEDICA - SUL AMERICA SAUDE", "33.259.514/0001-05"),
            ("ASSIST. ODONTO E MEDICA - UBEASP", "04.112.431/0001-17"),
            ("ASSIST. ODONTO E MEDICA - UNIBRAS", "23.501.076/0001-20"),
            ("ASSIST. ODONTO E MÉDICA - UNIMED FEDERATIVA", "05.533.006/0001-10"),
            ("ASSIST. ODONTO E MEDICA - UNIODONTO", "02.259.313/0001-53"),
            ("ASSIST. ODONTO E MEDICA - USODONTO", "05.353.936/0001-20"),
            ("ASSIST.ODONTO E MÉDICA - PREVIDENT ASSIST", "04.810.828/0001-00"),
            ("ASSOCIAÇÃO - A.S.R.U.E.B.", "03.818.513/0001-83"),
            ("ASSOCIAÇÃO - ADVAM", "34.503.639/0001-30"),
            ("ASSOCIAÇÃO - AGREMIACAO RECREATIVA DOS PROF DE URUCURITUBA - AGREPU", "03.583.555/0001-44"),
            ("ASSOCIAÇÃO - AGSPME", "04.512.355/0001-90"),
            ("ASSOCIAÇÃO - APBMAM", "04.839.860/0001-53"),
            ("ASSOCIAÇÃO - ASA", "01.319.429/0001-02"),
            ("ASSOCIAÇÃO - ASFHAJ", "05.789.231/0001-33"),
            ("ASSOCIAÇÃO - ASPA", "04.441.953/0001-05"),
            ("ASSOCIAÇÃO - ASPBRAS", "05.508.431/0001-03"),
            ("ASSOCIAÇÃO - ASSEPLAN", "04.015.656/0001-87"),
            ("ASSOCIAÇÃO - ASTATE-AM", "04.533.339/0001-38"),
            ("ASSOCIAÇÃO - CASEBRAS", "04.103.111/0001-33"),
            ("ASSOCIAÇÃO - CASPEB", "04.523.771/0001-81"),
            ("ASSOCIAÇÃO - CREPI", "02.541.656/0001-52"),
            ("ASSOCIAÇÃO - CREPROM", "18.124.723/0001-14"),
            ("ASSOCIAÇÃO - APPBMAM (PRACAS PM/BM)", "04.839.860/0001-53"),
            ("ASSOCIAÇÃO - DE DELEGADOS DE POLICIA - AM", "14.312.754/0001-26"),
            ("ASSOCIAÇÃO - DEF PUBLICOS", "04.513.689/0001-23"),
            ("ASSOCIAÇÃO - DOS OFICIAIS PM/BM - AM", "04.533.741/0001-90"),
            ("ASSOCIAÇÃO - DOS PERITOS OFICIAIS - AM", "02.541.656/0001-52"),
            ("ASSOCIAÇÃO - DOS PRACAS DO ESTADO DO AM", "18.124.723/0001-14"),
            ("ASSOCIAÇÃO - DOS PROCURADORES DO AMAZONAS", "04.534.781/0001-41"),
            ("ASSOCIAÇÃO - SERV. FUNDACAO HEMOAM", "84.528.854/0001-41"),
            ("ASSOCIAÇÃO - SERVIDORES SECRETARIA SAUDE", "04.524.556/0001-04"),
            ("ASSOCIAÇÃO - SERVIDORES UEA - ASSUEA", "18.454.329/0001-73"),
            ("ASSOCIAÇÃO - FAP", "02.000.000/0001-01"),
            ("ASSOCIAÇÃO - FAZENDARIO", "01.173.141/0001-72"),
            ("ASSOCIAÇÃO - FUNC. ALFREDO DA MATTA", "03.023.341/0001-34"),
            ("ASSOCIAÇÃO - MÃOS AMIGAS", "04.707.341/0001-57"),
            ("ASSOCIAÇÃO - MILICRED", "05.333.666/0001-51"),
            ("ASSOCIAÇÃO - S.B.S. - SESAU", "22.757.567/0001-15"),
            ("ASSOCIAÇÃO - S.R.B. - SEDUC", "04.413.666/0001-25"),
            ("ASSOCIAÇÃO - SUBTENENTES E SARGENTOS PM/BM", "04.532.556/0001-57"),
            ("BANCO - ABN REAL SANTANDER", "90.400.888/0001-42"),
            ("BANCO - BMG S.A", "61.186.688/0001-76"),
            ("BANCO - BRADESCO FINANCIAMENTOS S.A", "07.207.996/0001-10"),
            ("BANCO - BRADESCO S.A", "60.746.948/0001-12"),
            ("BANCO - BRASIL S.A", "00.000.000/0001-91"),
            ("BANCO - CAIXA ECONOMICA FEDERAL", "00.360.305/0001-04"),
            ("BANCO - CETELEM S.A", "03.558.851/0001-71"),
            ("BANCO - CHINA CONSTRUCTION BANK (BRASIL)", "01.018.654/0001-85"),
            ("BANCO - COOPERATIVO SICOOB S.A", "02.038.232/0001-64"),
            ("BANCO - CRUZEIRO DO SUL S.A", "62.136.254/0001-99"),
            ("BANCO - DAYCOVAL S.A", "62.232.274/0001-80"),
            ("BANCO - FIBRA S.A", "58.616.417/0001-08"),
            ("BANCO - FICSA", "00.000.000/0001-91"),
            ("BANCO - INDUSTRIAL DO BRASIL S.A", "31.895.683/0001-16"),
            ("BANCO - ITAU UNIBANCO S.A", "60.701.190/0001-04"),
            ("BANCO - KIRTON BANK S.A.", "01.701.201/0001-89"),
            ("BANCO - MASTER S.A", "33.923.798/0001-00"),
            ("BANCO - OLE BONSUCESSO CONSIGNADO S.A", "71.351.656/0001-75"),
            ("BANCO - ORIGINAL S.A", "92.894.922/0001-08"),
            ("BANCO - PAN S.A", "59.285.411/0001-13"),
            ("BANCO - PARANA S.A", "14.353.334/0001-90"),
            ("BANCO - PAULISTA S.A", "61.325.817/0001-89"),
            ("BANCO - PINE S.A", "62.144.175/0001-20"),
            ("BANCO - RURAL S.A", "33.123.189/0001-29"),
            ("BANCO - SAFRA S.A", "58.160.789/0001-28"),
            ("BANCO - SANTANDER (BRASIL) S.A", "90.400.888/0001-42"),
            ("BANCO - SCHAHIN", "14.355.334/0001-21"),
            ("BANCO - SEMEAR S.A", "00.735.423/0001-45"),
            ("BANCO - SOFISA S.A", "60.553.123/0001-23"),
            ("BANCO - VOTORANTIM S.A", "59.588.111/0001-03"),
            ("CARTAO - CREDCESTA", "21.409.823/0001-13"),
            ("CARTAO - MEUCASHCARD", "43.209.465/0001-10"),
            ("CARTAO - NIO MEIOS DE PAGAMENTO S.A", "11.455.339/0001-40"),
            ("CARTAO - PROVER PROMOÇÃO DE VENDAS LTDA", "28.534.147/0001-00"),
            ("CLUBE - CLUBE MUNICIPAL", "04.509.387/0001-91"),
            ("COOPERATIVA - SICREDI BIOMAS", "23.532.855/0001-33"),
            ("COOPERATIVA - SICOOB AMAZONIA", "02.253.955/0001-91"),
            ("COOPERATIVA - SICREDI VALE", "23.533.155/0001-17"),
            ("FINANCEIRA - EAGLE SCD S.A.", "45.414.373/0001-11"),
            ("FINANCEIRA - EMPRESTEI CARD S.A", "33.422.551/0001-43"),
            ("FINANCEIRA - MILCRED", "03.333.666/0001-51"),
            ("FINANCEIRA - PEGCARD LTDA", "58.253.666/0001-47"),
            ("FINANCEIRA - UNIPREV", "00.000.000/0001-91"),
            ("FINANCEIRA - VALOR SCD S.A", "41.733.277/0001-75"),
            ("HABITAÇÃO - SUHAB", "04.355.353/0001-32"),
            ("INSTITUTO BENEFICENTE CANDIDO MARIANO", "04.715.355/0001-40"),
            ("OUTROS - FUNDACAO CBMAM", "12.564.383/0001-07"),
            ("PREVIDÊNCIA - BRADESCO", "33.000.000/0001-37"),
            ("SEGURADORA E PREVIDÊNCIA - AFFEAM SEGUROS", "04.533.243/0001-70"),
            ("SEGURADORA E PREVIDÊNCIA - AGF", "00.000.000/0001-91"),
            ("SEGURADORA E PREVIDÊNCIA - CAPEMISA", "08.532.743/0001-32"),
            ("SEGURADORA E PREVIDÊNCIA - GBOEX", "92.312.155/0001-25"),
            ("SEGURADORA E PREVIDÊNCIA - ITAVIDA SEGUROS", "03.000.000/0001-45"),
            ("SEGURADORA E PREVIDÊNCIA - MONGERAL AEGON", "33.608.308/0001-73"),
            ("SEGURADORA E PREVIDÊNCIA - OSB", "04.422.378/0001-41"),
            ("SEGURADORA E PREVIDÊNCIA - PINK SEGURO VIDA", "00.000.000/0001-91"),
            ("SEGURADORA E PREVIDÊNCIA - RSPREV", "26.421.353/0001-32"),
            ("SEGURADORA E PREVIDÊNCIA - SABEMI", "33.127.323/0001-05"),
            ("SEGURADORA E PREVIDÊNCIA - SABEMI SEGURADORA", "33.123.224/0001-38"),
            ("SINDICATO - SINDOCENTES UEA", "18.333.774/0001-03"),
            ("SINDICATO - SINDEPOL", "14.312.754/0001-26"),
            ("SINDICATO - SINDEIPOL", "23.334.323/0001-29"),
            ("SINDICATO - DOS FISIOTERAPEUTAS", "44.223.733/0001-90"),
            ("SINDICATO - SIMEAM", "04.523.689/0001-23"),
            ("SINDICATO - SINTAFISCO", "04.331.711/0001-55"),
            ("SINDICATO - SIFAM", "01.555.421/0001-11"),
            ("SINDICATO - SINTRASPA AM", "04.509.378/0001-43"),
            ("SINDICATO - SINDAGENTE", "18.502.524/0001-15"),
            ("SINDICATO - SINDIFISCO", "34.555.313/0001-32"),
            ("SINDICATO - SINDSAUDE", "34.333.667/0001-13"),
            ("SINDICATO - SINPOL", "34.503.376/0001-30"),
            ("SINDICATO - SINSPEAM", "00.000.000/0001-91"),
            ("SINDICATO - SINTEAM", "04.533.666/0001-41"),
            ("SINDICATO - SINTRAQUA", "05.333.666/0001-51"),
            ("SINDICATO - SISPEAM", "03.355.321/0001-35"),
            ("VEMCARD PARTICIPACOES S.A", "44.133.733/0001-03")
        ]
        return pd.DataFrame({
            'ID': range(1, len(dados_lista) + 1),
            'N° SIGED': ['' for _ in dados_lista],
            'Entidade': [d[0] for d in dados_lista],
            'CNPJ': [d[1] for d in dados_lista],
            'Status': ['Aguardando Doc' for _ in dados_lista],
            'Parecer': ['' for _ in dados_lista],
            'Diligencia': ['Não' for _ in dados_lista],
            'Encaminhado ao CTA': ['Não' for _ in dados_lista],
            'Enviado a Consigfácil': ['Não' for _ in dados_lista],
            'Data Limite': ['30/04/2026' for _ in dados_lista],
            'Data de Finalização': ['' for _ in dados_lista],
            'Observação': ['' for _ in dados_lista]
        })

    # Carregar dados da nuvem
    try:
        df = conn.read(spreadsheet=URL_PLANILHA, ttl=0)
        if df.empty or len(df.columns) < 2:
            df = criar_dados_iniciais()
            conn.update(spreadsheet=URL_PLANILHA, data=df)
            st.info("Planilha inicializada com os 124 registros!")
        df = df.fillna('')
        st.success("✅ Conectado à Planilha do Google")
    except Exception as e:
        df = criar_dados_iniciais()
        st.error(f"⚠️ Erro de Conexão: {e}")
        st.warning("Rodando com dados temporários (Offline).")

    # --- RELATÓRIO PDF ---
    def gerar_pdf_custom(dataframe, filtro_coluna, filtro_valor, titulo_relatorio):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, f"SEAG - {titulo_relatorio}", ln=True, align='C')
        pdf.set_font("Arial", 'I', 8)
        pdf.cell(190, 7, f"Gerado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}", ln=True, align='R')
        pdf.ln(5)
        
        if filtro_coluna == 'Status':
            dados_f = dataframe[dataframe[filtro_coluna].astype(str).str.strip() == filtro_valor]
        else:
            dados_f = dataframe[(dataframe[filtro_coluna].astype(str).str.len() > 0) & 
                                (dataframe[filtro_coluna].astype(str).str.upper() != 'NÃO')]

        pdf.set_font("Arial", 'B', 9)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(10, 8, "ID", 1, 0, 'C', True)
        pdf.cell(100, 8, "Entidade", 1, 0, 'L', True)
        pdf.cell(45, 8, "CNPJ", 1, 0, 'C', True)
        pdf.cell(35, 8, "SIGED / DATA", 1, 1, 'C', True)
        
        pdf.set_font("Arial", size=8)
        for _, row in dados_f.iterrows():
            col_final = str(row['Data de Finalização']) if filtro_valor == 'Finalizada' else str(row['N° SIGED'])
            pdf.cell(10, 7, str(row['ID']), 1, 0, 'C')
            pdf.cell(100, 7, str(row['Entidade'])[:55], 1)
            pdf.cell(45, 7, str(row['CNPJ']), 1, 0, 'C')
            pdf.cell(35, 7, col_final, 1, 1, 'C')
        return pdf.output(dest='S').encode('latin-1')

    # --- SIDEBAR RELATÓRIOS ---
    st.sidebar.header("📁 Central de PDFs")
    btns = [
        ("Pendentes", "Status", "Aguardando Doc"),
        ("Finalizadas", "Status", "Finalizada"),
        ("No CTA", "Encaminhado ao CTA", ""),
        ("Diligências", "Diligencia", ""),
        ("Consigfácil", "Enviado a Consigfácil", "")
    ]
    for n, c, v in btns:
        if st.sidebar.button(f"📄 Relatório: {n}"):
            pdf = gerar_pdf_custom(df, c, v, f"Entidades {n}")
            st.sidebar.download_button(f"⬇️ Baixar {n}", pdf, f"SEAG_{n}.pdf", "application/pdf")

    # --- BUSCA E TABELA ---
    busca = st.text_input("🔍 Busca Rápida (Entidade ou CNPJ):", "")
    df_filtrado = df[df['Entidade'].astype(str).str.contains(busca, case=False) | 
                     df['CNPJ'].astype(str).str.contains(str(busca))].copy()

    def estilo_linha(row):
        status = str(row['Status']).strip()
        if status == 'Finalizada': return ['background-color: #d4edda'] * len(row)
        return [''] * len(row)

    st.write(f"### 📝 Painel Online ({len(df_filtrado)} itens)")
    df_editado = st.data_editor(
        df_filtrado.style.apply(estilo_linha, axis=1),
        use_container_width=True, hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(options=["Aguardando Doc", "Finalizada"]),
            "Data de Finalização": st.column_config.TextColumn(disabled=True),
            "Diligencia": st.column_config.SelectboxColumn(options=["Não", "Sim"]),
            "Encaminhado ao CTA": st.column_config.SelectboxColumn(options=["Não", "Sim"]),
            "Enviado a Consigfácil": st.column_config.SelectboxColumn(options=["Não", "Sim"])
        }
    )

    if st.button("💾 Salvar Alterações"):
        # Atualiza o DataFrame principal com o que foi editado na tela
        for idx, row in df_editado.iterrows():
            df.loc[df['ID'] == row['ID']] = row
        
        # Datas Automáticas
        for index, row in df.iterrows():
            if str(row['Status']).strip() == 'Finalizada' and not str(row['Data de Finalização']).strip():
                df.at[index, 'Data de Finalização'] = datetime.now().strftime('%d/%m/%Y')
            elif str(row['Status']).strip() == 'Aguardando Doc':
                df.at[index, 'Data de Finalização'] = ''

        conn.update(spreadsheet=URL_PLANILHA, data=df)
        st.success("Dados sincronizados com sucesso!")
        st.rerun()

    # --- GRÁFICOS ---
    st.divider()
    c1, c2 = st.columns(2)
    with c1: st.plotly_chart(px.pie(df, names='Status', title='Progresso Geral', hole=0.3), use_container_width=True)
    with c2: st.plotly_chart(px.pie(df, names='Enviado a Consigfácil', title='Status Consigfácil'), use_container_width=True)