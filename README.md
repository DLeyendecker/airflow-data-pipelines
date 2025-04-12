# Pipeline com Apache Airflow

Este projeto simula um pipeline de dados utilizando o **Apache Airflow**, que realiza o monitoramento e processamento de arquivos JSON gerados por turbinas eólicas. Os dados são armazenados em um banco **PostgreSQL** e e-mails são enviados com base em regras de temperatura.

## Objetivo

- Monitorar arquivos com dados de sensores (JSON).
- Processar os dados com operadores do Airflow.
- Armazenar os dados em um banco PostgreSQL.
- Enviar e-mails de alerta com base na temperatura.

## Componentes da DAG

### **FileSensorTask**
- Verifica o arquivo em intervalos regulares.
- Não monitora a pasta indefinidamente.
- Não inicializa a DAG quando o arquivo for disponibilizado.
- Não tem conhecimento das execuções anteriores da DAG.
- `filepath`: verifica se o arquivo existe antes de prosseguir.
- `fs_conn_id`: conexão com o arquivo através de conexão do Airflow. Conexão padrão: `fs_default`.

### **windturbine (simulador)**
- Gera um arquivo JSON com a seguinte estrutura:
  ```json
  {
    "idtemp": "1",
    "powerfactor": "0.8837929080361997",
    "hydraulicpressure": "78.86011124702158",
    "temperature": "25.279809506572597",
    "timestamp": "2023-03-19 17:26:55.230351"
  }

  - Vamos usar um arquivo pronto.
- Notebook Python simula a geração do arquivo.

## **schedule_interval**
- A cada 3 minutos:

- No desenvolvimento, vamos usar `None`.

## **PythonOperator**
- Deverá ler o JSON.
- Colocar as 5 variáveis no `XCom`.
- Excluir o arquivo.

## **BranchPythonOperator**
- Se a temperatura for maior ou igual a 24°C, manda e-mail de **alerta**.
- Caso contrário, manda e-mail **informativo**.

## **PostgresOperator**
- Cria a tabela.
- Insere os dados.

## **Pré-Etapas**
- Criar conexão para o `FileSensorTask`.
- Criar variável com caminho do arquivo JSON.

![image](https://github.com/user-attachments/assets/8c317dba-f6a1-4412-96ac-03eb6fbea7a0)
