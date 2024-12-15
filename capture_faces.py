import os
import time
import cv2

# Configurar diretório base
base_folder = "imagens"
# os.makedirs criar uma pasta nova, exist_ok verifica se uma pasta com o mesmo nome já existe
os.makedirs(base_folder, exist_ok=True)

# Solicitar o nome da pasta
# input - pede para o usuário inserir algo no terminal
# title - torna a primeira letra de cada palavra maiúscula
nome_pasta = input("Digite seu nome completo: ").title()
# os.path.join contrói o caminho para a nova pasta criada, juntando o diretorio principal e a nova pasta
output_folder = os.path.join(base_folder, nome_pasta)
# os.makedirs criar uma pasta nova, exist_ok verifica se uma pasta com o mesmo nome já existe
os.makedirs(output_folder, exist_ok=True)

# print para mostrar se a nova pasta foi criada e qual é o nome dela
print(f"Pasta '{nome_pasta}' criada com sucesso.")

# Abrir a webcam
cap = cv2.VideoCapture(0)

# Configuração de captura
num_frames = 100

print("Iniciando captura...")

# Laço para percorrer a quantidade pedida de frames, no caso 100 vezes
for i in range(num_frames):
    # iniciando frames da câmera com a função read
    ret, frame = cap.read()

    # Verifica se existem frames, caso contário desliga a câmera
    if not ret:
        print("Erro ao capturar imagem!")
        break

    # construindo o caminho do diretório principal até o frame capturado do aluno
    filename = os.path.join(output_folder, f"Frame_{i:04d}.jpg")
    # mostrand mensagens de cada frame sendo capturado
    print(filename)
    # salvando as imagens dentro da pasta do aluno
    cv2.imwrite(filename, frame)
    # tempo em segundos para intervalo de cada captura
    time.sleep(25 / num_frames)

# mostrando uma mensagem de conclusão
print(f"Captura concluída. Imagens salvas em: {output_folder}")

# liberando memória do computador
cap.release()
cv2.destroyAllWindows()
