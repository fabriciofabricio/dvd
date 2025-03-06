"""
Ferramenta para diagnosticar o carregamento de imagens no pygame.
Salve como check_images.py e execute para verificar se as imagens estão sendo carregadas corretamente.
"""
import pygame
import os
import sys

def check_images():
    # Inicializar pygame
    pygame.init()
    screen = pygame.display.set_mode((400, 200))
    pygame.display.set_caption("Verificador de Imagens")
    
    # Verificar se a pasta images existe
    if not os.path.exists('images'):
        print("ERRO: A pasta 'images' não existe")
        return False
        
    # Listar todos os arquivos na pasta images
    files = os.listdir('images')
    image_files = [f for f in files if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
    
    if not image_files:
        print("AVISO: Não foram encontradas imagens na pasta 'images'")
        print("Adicione arquivos de imagem (.png, .jpg, .jpeg, .bmp) à pasta images")
        return False
    
    # Tentar carregar cada imagem
    successful_loads = 0
    for img_file in image_files:
        try:
            path = os.path.join('images', img_file)
            print(f"Tentando carregar: {path}")
            
            # Verificar se o arquivo existe
            if not os.path.isfile(path):
                print(f"  ERRO: Arquivo não existe: {path}")
                continue
                
            # Tentar carregar a imagem
            image = pygame.image.load(path)
            
            # Verificar se a imagem foi carregada com sucesso
            if image:
                print(f"  SUCESSO: Imagem carregada: {img_file}")
                successful_loads += 1
            else:
                print(f"  ERRO: Falha ao carregar imagem: {img_file}")
                
        except Exception as e:
            print(f"  ERRO ao carregar {img_file}: {e}")
    
    # Resultados finais
    print("\nResultados:")
    print(f"- Total de arquivos de imagem encontrados: {len(image_files)}")
    print(f"- Imagens carregadas com sucesso: {successful_loads}")
    
    if successful_loads > 0:
        print("\nAs imagens foram encontradas e carregadas com sucesso.")
        print("Para usá-las no jogo, certifique-se de que os nomes das imagens")
        print("correspondam aos caminhos em game.py (square_configs).")
        return True
    else:
        print("\nNenhuma imagem foi carregada com sucesso.")
        print("Verifique se as imagens estão no formato correto e no local correto.")
        return False

if __name__ == "__main__":
    result = check_images()
    print("\nPressione qualquer tecla para sair...")
    input()
    sys.exit(0 if result else 1)