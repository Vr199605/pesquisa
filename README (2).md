# BeSmart • Dashboard de Avaliações

Dashboard interativo em **Streamlit** para análise das avaliações de reuniões, com visual aprimorado e gamificado.  
A versão atual **não possui aba de ranking** — apenas visão geral, detalhamento por especialista e comentários.

---

## Funcionalidades

- **Filtros laterais** por período e especialista  
- **KPIs automáticos**: total de reuniões, taxa de avaliação e média de notas  
- **Gráfico interativo**: percentual de reuniões avaliadas por especialista  
- **Resumo em tabela**: informações consolidadas com meta automática  
- **Exibição de comentários** com data e especialista  

---

## Instalação

1. Clone ou baixe este repositório:  
   ```bash
   git clone https://github.com/sua-conta/seu-repo.git
   cd seu-repo
   ```

2. Crie um ambiente virtual (opcional, mas recomendado):  
   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate      # Windows
   ```

3. Instale as dependências:  
   ```bash
   pip install -r requirements.txt
   ```

---

## Execução

1. Rode o dashboard com:  
   ```bash
   streamlit run app.py
   ```

2. O navegador abrirá automaticamente em:  
   ```
   http://localhost:8501
   ```

---

## Estrutura do Projeto

```
.
├── app.py              # Código principal do dashboard
├── requirements.txt    # Dependências do projeto
└── README.md           # Este arquivo de instruções
```

---

## Observações

- Os dados são carregados de uma planilha Google Sheets via CSV público.  
- Certifique-se de que o link do CSV está ativo e acessível.  
- O cache dos dados é atualizado automaticamente a cada 1 hora.  

---
