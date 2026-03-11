import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px
from fpdf import FPDF
from datetime import datetime, timedelta, timezone

# Configuração da Página SEAG
st.set_page_config(page_title="Gestão SEAG 2026", layout="wide")

# URL DIRETA DA PLANILHA
URL_PLANILHA = "https://docs.google.com/spreadsheets/d/12nBlopOzq1LY1CDObfaNfWPU0xxa9-P-_e1IJtDgLB4/edit?gid=0#gid=0"

# --- FUSO HORÁRIO DE MANAUS (UTC-4) ---
FUSO_MANAUS = timezone(timedelta(hours=-4))

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

# --- FUNÇÃO DADOS INICIAIS ---
def criar_dados_iniciais():
    dados_consignatarias = [
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
        ("VEMCARD PARTICIPACOES S.A", "44.133.733/0001-03"),
        ("SEGURADORA E PREVIDÊNCIA - SULAMÉRICA SEGUROS DE PESSOAS E PREVIDÊNCIA", "01.704.513/0001-46")
    ]
    qtd = len(dados_consignatarias)
    return pd.DataFrame({
        'ID': range(1, qtd + 1),
        'N° SIGED': [''] * qtd,
        'Entidade': [d[0] for d in dados_consignatarias],
        'CNPJ': [d[1] for d in dados_consignatarias],
        'Status': ['Aguardando Doc'] * qtd,
        'Parecer': [''] * qtd,
        'Diligencia': ['Não'] * qtd,
        'Encaminhado ao CTA': ['Não'] * qtd,
        'Enviado a Consigfácil': ['Não'] * qtd,
        'Data Limite': ['29/03/2026'] * qtd, 
        'Data de Recebimento Doc.': [''] * qtd,
        'Observação': [''] * qtd,
        'Contato': [''] * qtd
    })

# --- INÍCIO DO SISTEMA PÓS-LOGIN ---
if verificar_senha():
    st.title("📊 Gestão SEAG - Recadastramento 2026")

    # Conexão GSheets com Service Account
    conn = st.connection("gsheets", type=GSheetsConnection)

    try:
        df = conn.read(ttl=0)
        
        # Inteligência de Auto-Atualização
        if df.empty or len(df.columns) < 2:
            df = criar_dados_iniciais()
            conn.update(data=df)
            st.info("Planilha inicializada automaticamente com as entidades!")
        else:
            atualizou_planilha = False
            
            # --- MIGRAÇÃO AUTOMÁTICA DE NOMES ANTIGOS ---
            if 'Data de Finalização' in df.columns:
                df = df.rename(columns={'Data de Finalização': 'Data de Recebimento Doc.'})
                atualizou_planilha = True
                
            if 'Status' in df.columns and (df['Status'] == 'Finalizada').any():
                df['Status'] = df['Status'].replace('Finalizada', 'Doc. Recebido')
                atualizou_planilha = True
            # --------------------------------------------

            if 'Contato' not in df.columns:
                df['Contato'] = ''
                atualizou_planilha = True
                
            if not df['CNPJ'].astype(str).str.contains('01.704.513/0001-46').any():
                novo_id = int(df['ID'].max()) + 1 if pd.notna(df['ID'].max()) else len(df) + 1
                nova_linha = pd.DataFrame([{
                    'ID': novo_id, 'N° SIGED': '', 'Entidade': 'SEGURADORA E PREVIDÊNCIA - SULAMÉRICA SEGUROS DE PESSOAS E PREVIDÊNCIA',
                    'CNPJ': '01.704.513/0001-46', 'Status': 'Aguardando Doc', 'Parecer': '', 'Diligencia': 'Não',
                    'Encaminhado ao CTA': 'Não', 'Enviado a Consigfácil': 'Não', 'Data Limite': '29/03/2026', 
                    'Data de Recebimento Doc.': '', 'Observação': '', 'Contato': ''
                }])
                df = pd.concat([df, nova_linha], ignore_index=True)
                atualizou_planilha = True

            if 'Data Limite' in df.columns and (df['Data Limite'] != '29/03/2026').any():
                df['Data Limite'] = '29/03/2026'
                atualizou_planilha = True
                
            if atualizou_planilha:
                conn.update(data=df)
                st.info("✅ O sistema migrou e atualizou automaticamente os dados na nuvem!")

        df = df.fillna('')
    except Exception as e:
        df = criar_dados_iniciais()
        st.error(f"⚠️ Erro de Conexão: {e}")

    # Lista total de números disponíveis (1 a 500)
    numeros_totais = [str(i) for i in range(1, 501)]
    opcoes_tabela_parecer = [""] + numeros_totais
    opcoes_tabela_diligencia = ["Não", "Sim"] + numeros_totais

    # --- GERADOR DE NUMERAÇÃO ÚNICA ---
    st.write("### 🔢 Gerador de Numeração Única")
    with st.expander("Clique aqui para puxar um número livre de Parecer ou Diligência", expanded=False):
        c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
        
        entidade_alvo = c1.selectbox("1. Entidade:", [""] + df['Entidade'].tolist())
        tipo_documento = c2.selectbox("2. Documento:", ["Parecer", "Diligencia"])
        
        usados = df[tipo_documento].astype(str).str.strip().tolist()
        livres = [n for n in numeros_totais if n not in usados]
        
        num_escolhido = c3.selectbox("3. Números Livres:", [""] + livres)
        
        if c4.button("✅ Atribuir Número"):
            if entidade_alvo and num_escolhido:
                idx = df.index[df['Entidade'] == entidade_alvo].tolist()[0]
                df.at[idx, tipo_documento] = num_escolhido
                try:
                    conn.update(data=df)
                    st.success(f"{tipo_documento} número {num_escolhido} registrado com sucesso!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao salvar no Google Sheets: {e}")
            else:
                st.warning("Preencha todos os campos primeiro.")

    # --- SIDEBAR E RELATÓRIOS ---
    def gerar_pdf_custom(dataframe, filtro_coluna, filtro_valor, titulo_relatorio):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(190, 10, f"SEAG - {titulo_relatorio}", ln=True, align='C')
        pdf.set_font("Arial", 'I', 8)
        
        data_hora_atual = datetime.now(FUSO_MANAUS).strftime('%d/%m/%Y %H:%M')
        pdf.cell(190, 7, f"Gerado em: {data_hora_atual}", ln=True, align='R')
        pdf.ln(5)
        
        if filtro_coluna == 'Status':
            dados_f = dataframe[dataframe[filtro_coluna].astype(str).str.strip() == filtro_valor]
        elif filtro_coluna == 'Diligencia':
            # --- NOVA REGRA AQUI: Tira quem não tem diligência E tira quem já foi pro CTA ---
            mask_diligencia_ativa = ~dataframe[filtro_coluna].astype(str).str.strip().isin(['', 'Não'])
            mask_nao_no_cta = dataframe['Encaminhado ao CTA'].astype(str).str.strip().str.upper() != 'SIM'
            dados_f = dataframe[mask_diligencia_ativa & mask_nao_no_cta]
            # --------------------------------------------------------------------------------
        else:
            dados_f = dataframe[(dataframe[filtro_coluna].astype(str).str.upper() == 'SIM')]

        pdf.set_font("Arial", 'B', 9)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(10, 8, "ID", 1, 0, 'C', True)
        pdf.cell(100, 8, "Entidade", 1, 0, 'L', True)
        pdf.cell(45, 8, "CNPJ", 1, 0, 'C', True)
        pdf.cell(35, 8, "SIGED / DATA", 1, 1, 'C', True)
        
        pdf.set_font("Arial", size=8)
        for _, row in dados_f.iterrows():
            info_final = str(row['Data de Recebimento Doc.']) if filtro_valor == 'Doc. Recebido' else str(row['N° SIGED'])
            pdf.cell(10, 7, str(row['ID']), 1, 0, 'C')
            pdf.cell(100, 7, str(row['Entidade'])[:55], 1)
            pdf.cell(45, 7, str(row['CNPJ']), 1, 0, 'C')
            pdf.cell(35, 7, info_final, 1, 1, 'C')
        return pdf.output(dest='S').encode('latin-1')

    st.sidebar.header("📁 Central de Relatórios")
    
    opcoes = [
        ("Pendentes", "Status", "Aguardando Doc"),
        ("Parecer SEAG", "Status", "Doc. Recebido"),
        ("No CTA", "Encaminhado ao CTA", "Sim"),
        ("Consigfácil", "Enviado a Consigfácil", "Sim"),
        ("Diligências", "Diligencia", "Ativas") 
    ]
    
    for nome, col, val in opcoes:
        if st.sidebar.button(f"📄 PDF: {nome}"):
            pdf_out = gerar_pdf_custom(df, col, val, f"Entidades {nome}")
            st.sidebar.download_button(f"⬇️ Baixar {nome}", pdf_out, f"SEAG_{nome}.pdf")

    # --- PAINEL DE EDIÇÃO (COM CRUD ATIVADO) ---
    st.write("### 📝 Painel de Controle Online")
    busca = st.text_input("🔍 Buscar Entidade ou CNPJ:", "")
    mask = df['Entidade'].astype(str).str.contains(busca, case=False) | df['CNPJ'].astype(str).str.contains(str(busca))
    df_filtrado = df[mask].copy()

    df_editado = st.data_editor(
        df_filtrado, use_container_width=True, hide_index=True,
        column_config={
            "Status": st.column_config.SelectboxColumn(options=["Aguardando Doc", "Doc. Recebido"]),
            "Parecer": st.column_config.SelectboxColumn("Parecer", options=opcoes_tabela_parecer),
            "Diligencia": st.column_config.SelectboxColumn("Diligência", options=opcoes_tabela_diligencia),
            "Encaminhado ao CTA": st.column_config.SelectboxColumn(options=["Não", "Sim"]),
            "Enviado a Consigfácil": st.column_config.SelectboxColumn(options=["Não", "Sim"]),
            "Data de Recebimento Doc.": st.column_config.TextColumn(disabled=True),
            "Contato": st.column_config.TextColumn("Contato")
        }
    )

    if st.button("💾 Salvar Alterações na Nuvem"):
        df_verificacao = df.copy()
        
        for idx, row in df_editado.iterrows():
            mascara = df_verificacao['ID'] == row['ID']
            for coluna in df_editado.columns:
                df_verificacao.loc[mascara, coluna] = row[coluna]
            
        # --- TRAVA ANTI-DUPLICAÇÃO DE PARECER E DILIGÊNCIA ---
        pareceres_ativos = df_verificacao['Parecer'].replace('', pd.NA).dropna()
        if pareceres_ativos.duplicated().any():
            duplicados = pareceres_ativos[pareceres_ativos.duplicated()].unique()
            st.error(f"❌ Erro de Numeração: O Parecer número {', '.join(duplicados)} já foi utilizado em outra entidade! Altere antes de salvar.")
            st.stop()
            
        diligencias_ativas = df_verificacao['Diligencia'].replace(['', 'Não', 'Sim'], pd.NA).dropna()
        if diligencias_ativas.duplicated().any():
            dups = diligencias_ativas[diligencias_ativas.duplicated()].unique()
            st.error(f"❌ Erro de Numeração: A Diligência número {', '.join(dups)} já foi utilizada em outra entidade! Altere antes de salvar.")
            st.stop()
        
        # Regra de Data de Recebimento
        for i, r in df_verificacao.iterrows():
            if str(r['Status']).strip() == 'Doc. Recebido' and not str(r['Data de Recebimento Doc.']).strip():
                df_verificacao.at[i, 'Data de Recebimento Doc.'] = datetime.now(FUSO_MANAUS).strftime('%d/%m/%Y')
            elif str(r['Status']).strip() == 'Aguardando Doc':
                df_verificacao.at[i, 'Data de Recebimento Doc.'] = ''

        try:
            conn.update(data=df_verificacao)
            st.success("✅ O Robô atualizou o Google Sheets com sucesso!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Erro ao salvar: {e}")

    # --- GRÁFICOS ---
    st.divider()
    col1, col2 = st.columns(2)
    with col1: st.plotly_chart(px.pie(df, names='Status', title='Progresso de Recadastramento', hole=0.3), use_container_width=True)
    with col2: st.plotly_chart(px.bar(df['Status'].value_counts(), title='Total por Status'), use_container_width=True)
