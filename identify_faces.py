import os

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
    cursor = conn.cursor()
    cursor.execute('SELECT nome, encoding FROM pessoas')
    dados = cursor.fetchall()
    conn.close()

    nomes = []
    encodings = []

    for nome, encoding_bin in dados:
        try:
            # Converte o encoding armazenado em binário para numpy array
            encoding = np.frombuffer(encoding_bin, dtype=np.float64)
            if encoding.shape == (128,):
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
    video_capture = cv2.VideoCapture(1)
    video_capture.set(3, 1280)
    video_capture.set(4, 720)

    if not video_capture.isOpened():
        print('Erro ao acessar a câmera. Certifique-se de que ela está conectada e funcionando.')
        return

    while True:
        ret, frame = video_capture.read()

        if not ret:
            print('Erro ao capturar o frame. Finalizando...')
            break

        # Inverter o vídeo horizontalmente
        frame = cv2.flip(frame, 1)

        # Converte o frame para RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detecta localizações faciais
        face_locations = face_recognition.face_locations(rgb_frame, model='hog')

        if not face_locations:
            print('Nenhum rosto detectado neste frame.')
            continue

        # Calcula os encodings para os rostos detectados
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=1)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(encodings_banco, face_encoding, tolerance=0.6)
            name = 'Desconhecido'

            if True in matches:
                best_match_index = matches.index(True)
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
