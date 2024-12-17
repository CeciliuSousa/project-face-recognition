import os
import time

import cv2
import face_recognition
import mysql.connector
import numpy as np
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Função para conectar ao banco de dados
def conectar_banco():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )

# Função para carregar os encodings do banco de dados
def carregar_encodings():
    conn = conectar_banco()
    # cursor para enviar comandos sql para o banco
    cursor = conn.cursor()
    # executa um comando sql no banco de dados
    cursor.execute('SELECT nome, encoding FROM pessoas')
    # recupera todos os resultados da consulta
    dados = cursor.fetchall()
    # fecha a conexão com o banco
    conn.close()

    # inicializando variaveis para receber uma lista de nomes e encodings do banco
    nomes = []
    encodings = []

    # Laço que percorre os dados armazenado nas variaveis os resultados
    for nome, encoding_bin in dados:
        try:
            # Converte o encoding armazenado em binário para numpy array
            # Importante para a comparação com os encodings dos frames
            encoding = np.frombuffer(encoding_bin, dtype=np.float64)
            
            # Condicional que verifica se cada encoding possui 128 informações faciais
            if encoding.shape == (128,):
                # append - adiciona novos elementos no final da lista
                nomes.append(nome)
                encodings.append(encoding)
            else:
                print(f'Encoding inválido para {nome}: {encoding.shape}')
        except Exception as e:
            print(f'Erro ao processar encoding para {nome}: {e}')

    return nomes, encodings

# Função para exibir apenas o primeiro e o segundo nome
def formatar_nome(nome):
    partes = nome.split()
    if len(partes) > 1:
        return f"{partes[0]} {partes[1]}"
    return partes[0]

# Função para realizar o reconhecimento facial
def identificar_rostos():
    nomes, encodings_banco = carregar_encodings()

    # Inicializa captura de vídeo
    video_capture = cv2.VideoCapture(0)
    # Redimensionando o tamanho do video 3 - largura / 4 altura
    # !280 x 720 pixels
    video_capture.set(3, 1280)
    video_capture.set(4, 720)

    # Condigional para verificar se a câmera está funcionando
    if not video_capture.isOpened():
        print('Erro ao acessar a câmera. Certifique-se de que ela está conectada e funcionando.')
        return

    # Caso esteja funcionando, rodar a câmera
    while True:
        ret, frame = video_capture.read()

        # Verifica se existem frames, caso contário desliga a câmera
        if not ret:
            print('Erro ao capturar o frame. Finalizando...')
            break

        # Inverter o vídeo horizontalmente
        frame = cv2.flip(frame, 1)

        # Converte o frame para RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detecta localizações faciais com o modelo cnn que é mais robusto que o hog
        # Face Recognition disponibiliza 3 modelos de detecção, sendo eles o cnn, hog e ResNet-34
        face_locations = face_recognition.face_locations(rgb_frame, model='hog')

        if not face_locations:
            # mostra uma mensagem se um rosto não for detectado a cada 10 segundos
            time.sleep(10)
            print('Nenhum rosto detectado neste frame.')
            continue

        # Calcula os encodings para os rostos detectados
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=1)

        # Iterando sobre as localizações e encodings das faces
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            # Comparando os encodings do frame com os encodings armazenados no bando de dados
            matches = face_recognition.compare_faces(encodings_banco, face_encoding, tolerance=0.6)
            # Caso a comparação seja falsa, mostra o nome desconhecido na tela
            name = 'Desconhecido'

            # Verifica se algum dos valores da lista 'matches' é verdadeiro
            if True in matches:
                # Se o macthes é verdadeiro então retorar o nome para best macth index
                best_match_index = matches.index(True)
                # formata o nome mostrando apaenas o primeiro e segundo
                name = formatar_nome(nomes[best_match_index])

            # Desenha retângulo ao redor do rosto
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Exibe o nome abaixo do retângulo
            cv2.putText(frame, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)


        # Exibe o frame com a janela "Reconhecimento Facial"
        cv2.imshow('Reconhecimento Facial', frame)

        # Sai do loop ao pressionar 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Libera os recursos
    video_capture.release()
    cv2.destroyAllWindows()

# Inicialização do sistema
if __name__ == "__main__":
    try:
        identificar_rostos()
    except Exception as e:
        print(f'Ocorreu um erro: {e}')
