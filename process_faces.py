import os

import face_recognition
import mysql.connector
import numpy as np
from dotenv import load_dotenv
from PIL import Image

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# DIRETORIO COM AS IMAGENS DOS ALUNOS
diretorio = 'imagens'

# Função para criar o banco de dados, se não existir
def criar_banco_de_dados():
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
    )
    cursor = conn.cursor()

    # Verifica se o banco de dados "sistema_reconhecimento2" existe, caso contrário cria o banco
    cursor.execute('''
        CREATE DATABASE IF NOT EXISTS sistema_reconhecimento2
        DEFAULT CHARACTER SET utf8
        DEFAULT COLLATE utf8_general_ci;
    ''')
    conn.commit()

    # Fecha a conexão após criar o banco
    conn.close()

# Função para conectar ao banco de dados "sistema_reconhecimento2"
def conectar_banco():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# Função para criar a tabela "pessoas" caso ela não exista
def criar_tabela():
    conn = conectar_banco()
    cursor = conn.cursor()

    # Cria a tabela pessoas se ela não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pessoas (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            encoding LONGBLOB NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Primeiro cria o banco de dados (caso não exista) e a tabela
criar_banco_de_dados()
criar_tabela()

print('Banco de dados e tabela criados com sucesso, ou já existiam.')

# Conectar ao banco de dados para inserir os dados
conn = conectar_banco()
cursor = conn.cursor()

# LOOP PARA PERCORRER TODAS AS PASTAS DENTRO DO DIRETÓRIO "imagens"
for pasta in os.listdir(diretorio):
    pasta_path = os.path.join(diretorio, pasta)

    # Verifica se é uma pasta (representando um aluno)
    if os.path.isdir(pasta_path):
        nome_aluno = pasta

        # LOOP PARA PERCORRER TODAS AS IMAGENS DA PASTA DO ALUNO
        for filename in os.listdir(pasta_path):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                imagem_path = os.path.join(pasta_path, filename)
                
                # REDIMENCIONANDO AS IMAGENS PARA ECONOMIA DE RECURSOS
                imagem = Image.open(imagem_path)
                imagem = imagem.resize((100, 100))

                # CONVERTENDO DE PILL PARA NUMPY
                imagem = np.array(imagem)

                # IDENTIFICAÇÃO DAS FACES NAS IMAGENS E REGISTRO DOS ENCODINGS
                face_locations = face_recognition.face_locations(imagem, model='cnn')
                encodings = face_recognition.face_encodings(imagem, face_locations, num_jitters=10)

                if len(encodings) > 0:
                    for encoding in encodings:
                        # CONVERTENDO O ENCODING PARA O FORMATO LONGBLOB
                        encoding_blob = encoding.tobytes()

                        # INSERINDO DADOS NO BANCO DE DADOS
                        cursor.execute('''
                            INSERT INTO pessoas (nome, encoding)
                            VALUES (%s, %s)
                        ''', (nome_aluno, encoding_blob))
                        conn.commit()

                        print(f'O encoding da imagem {filename} do aluno {nome_aluno} foi um sucesso.')
                else:
                    print(f'Não foi possível encontrar face na imagem {filename}.')

# FECHANDO A CONEXÃO COM O BANCO DE DADOS
conn.close()
print('Dados salvos com sucesso no banco de dados MySQL.')
