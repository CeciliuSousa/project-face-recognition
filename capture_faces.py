import os
import time

import cv2

# Configurar pasta para salvar as imagens
output_folder = "imagens/outros"
os.makedirs(output_folder, exist_ok=True)

# Abrir a webcam
cap = cv2.VideoCapture(1)

# Taxa de captura (FPS) e tempo de execução
fps = 25
duração = 4
num_frames = fps * duração

print("Iniciando captura...")

for i in range(num_frames):
    ret, frame = cap.read()
    if not ret:
        print("Erro ao capturar imagem!")
        break
    
    # Nome do arquivo e salvamento
    filename = os.path.join(output_folder, f"frame_{i:04d}.jpg")
    cv2.imwrite(filename, frame)
    time.sleep(3 / fps)

print(f"Captura concluída. Imagens salvas em: {output_folder}")

cap.release()
cv2.destroyAllWindows()
