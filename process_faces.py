import os

import face_recognition
import mysql.connector
import numpy as np
from dotenv import load_dotenv
from PIL import Image

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Diretório onde armazenamos as subpastas com imagens dos alunos
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

# Loop para percorrer todas as pastas no dirétorio princial "imagens"
# listdir - lista todas as pastas dentro do diretorio principal
for pasta in os.listdir(diretorio):
    # contruindo o caminho do diretório
    pasta_path = os.path.join(diretorio, pasta)

    # isdir - verifica se é uma pasta (representando um aluno)
    if os.path.isdir(pasta_path):
        # armazena o nome da pasta em uma variavel
        nome_aluno = pasta

        # Loop para percorrer todas as imagens dentro da pasta do aluno
        for filename in os.listdir(pasta_path):
            # passando as extensões das imagens que devem ser buscadas nos diretórios
            if filename.endswith('.jpg') or filename.endswith('.png'):
                # contruindo o caminho do arquivo dentro do diretorio
                imagem_path = os.path.join(pasta_path, filename)
                
                # armazenando as imagens dentro de uma variavel
                imagem = Image.open(imagem_path)
                # redimensionando cada imagem para um tamanho 100 x 100
                imagem = imagem.resize((100, 100))

                # Convertendo de PILL para Numpy
                imagem = np.array(imagem)

                # Detecta localizações faciais com o modelo hog que é mais robusto que o cnn
                face_locations = face_recognition.face_locations(imagem, model='hog')
                # Extraindo os dados faciais de cada imagem
                encodings = face_recognition.face_encodings(imagem, face_locations, num_jitters=10)

                # laço que percorre os encodings e verifica se o valor é maior que 0
                # para não gastar recurso percorrendo dados vazios
                if len(encodings) > 0:
                    for encoding in encodings:
                        # Convertendo os encodings para bytes
                        encoding_blob = encoding.tobytes()

                        # Inserindo o nome e os encodings de cada imagem no banco de dados
                        cursor.execute('''
                            INSERT INTO pessoas (nome, encoding)
                            VALUES (%s, %s)
                        ''', (nome_aluno, encoding_blob))
                        conn.commit()

                        print(f'O encoding da imagem {filename} do aluno {nome_aluno} foi um sucesso.')
                else:
                    print(f'Não foi possível encontrar face na imagem {filename}.')

# Fechando a conexão com o banco de dados
conn.close()
print('Dados salvos com sucesso no banco de dados MySQL.')
