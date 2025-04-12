# 💨 Projeto Final - Pipeline com Apache Airflow

Este projeto simula um pipeline de dados utilizando o **Apache Airflow**, que realiza o monitoramento e processamento de arquivos JSON gerados por turbinas eólicas. Os dados são armazenados em um banco PostgreSQL e e-mails são enviados com base em regras de temperatura.

## 📌 Objetivo

- Monitorar arquivos com dados de sensores (JSON).
- Processar os dados com operadores do Airflow.
- Armazenar os dados em um banco PostgreSQL.
- Enviar e-mails de alerta com base na temperatura.

## ⚙️ Componentes da DAG

### 📁 **FileSensorTask**
- Verifica se o arquivo existe antes de iniciar a DAG.
- Não dispara a DAG automaticamente quando o arquivo é criado.
- Usa conexão `fs_default` (precisa ser criada no Airflow).

### 🌀 **windturbine (simulador)**
- Gera um arquivo JSON com a seguinte estrutura:
```json
{
  "idtemp": "1",
  "powerfactor": "0.88",
  "hydraulicpressure": "78.86",
  "temperature": "25.27",
  "timestamp": "2023-03-19 17:26:55.230351"
}

Simulado por um notebook Python.

🐍 PythonOperator
Lê o conteúdo do JSON.

Envia as 5 variáveis via XCom.

Exclui o arquivo após leitura.

🌡️ BranchPythonOperator
Verifica a variável temperature:

Se ≥ 24°C → envia e-mail de alerta.

Se < 24°C → envia e-mail informativo.

🗃️ PostgresOperator
Cria a tabela no PostgreSQL (caso não exista).

Insere os dados recebidos do JSON.

🧭 Agendamento
Executa a cada 3 minutos:


![image](https://github.com/user-attachments/assets/8c317dba-f6a1-4412-96ac-03eb6fbea7a0)
