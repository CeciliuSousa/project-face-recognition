import os
import time
import cv2

# Configurar diretório base
base_folder = "imagens"
os.makedirs(base_folder, exist_ok=True)

# Solicitar o nome da pasta
nome_pasta = input("Digite seu nome completo: ").title()
output_folder = os.path.join(base_folder, nome_pasta)
os.makedirs(output_folder, exist_ok=True)

print(f"Pasta '{nome_pasta}' criada com sucesso.")

# Abrir a webcam
cap = cv2.VideoCapture(0)  # Use 0 para a webcam padrão

# Configuração de captura
num_frames = 100

print("Iniciando captura...")

for i in range(num_frames):
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar imagem!")
        break

    # Nome do arquivo e salvamento
    filename = os.path.join(output_folder, f"Frame_{i:04d}.jpg")
    print(filename)
    cv2.imwrite(filename, frame)
    time.sleep(3 / num_frames)

print(f"Captura concluída. Imagens salvas em: {output_folder}")

cap.release()
cv2.destroyAllWindows()
