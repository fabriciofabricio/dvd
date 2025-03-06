"""
Constantes e configurações globais para o jogo DVD Bounce Simulation.
"""
import pygame

# Inicializar o Pygame (para fontes)
pygame.init()

# Configurações da janela
WIDTH = 800
HEIGHT = 600
TITLE = "Simulação de Colisão - Estilo DVD"

# Configurações do jogo (serão ajustáveis no menu)
MARGIN = 100  # Margem entre a borda da janela e a área restrita
AREA_SIZE = min(WIDTH, HEIGHT) - 2 * MARGIN  # Tamanho da área quadrada
AREA_X = (WIDTH - AREA_SIZE) // 2  # Posição X da área restrita
AREA_Y = (HEIGHT - AREA_SIZE) // 2  # Posição Y da área restrita
SQUARE_SIZE = 50
MIN_SPEED = 1.5
MAX_SPEED = 4.5

# Temporizadores
POWERUP_INTERVAL = 240  # 4 segundos a 60 FPS
SPIKE_DURATION = 300  # 5 segundos a 60 FPS
COLLISION_FLASH_DURATION = 10  # Duração do flash de colisão

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
DARK_GRAY = (50, 50, 50)
LIGHT_GRAY = (200, 200, 200)
YELLOW = (255, 255, 0)

# Cores vibrantes para os quadrados
VIBRANT_COLORS = [
    (255, 50, 50),    # Vermelho vibrante
    (50, 255, 50),    # Verde vibrante
    (50, 50, 255),    # Azul vibrante
    (255, 255, 50),   # Amarelo vibrante
    (255, 50, 255)    # Magenta vibrante
]

# Fontes
MENU_FONT = pygame.font.SysFont("Arial", 24)
TITLE_FONT = pygame.font.SysFont("Arial", 32, bold=True)
INFO_FONT = pygame.font.SysFont("Arial", 16)