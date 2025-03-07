"""
Definição dos mapas para o jogo DVD Bounce Simulation.
"""
from constants import BLACK, DARK_GRAY, WIDTH, HEIGHT

# Classe base para mapas
class GameMap:
    """Classe base para mapas do jogo."""
    def __init__(self, name, bg_color=BLACK, area_color=DARK_GRAY):
        self.name = name
        self.bg_color = bg_color
        self.area_color = area_color
        self.obstacles = []
    
    def is_position_blocked(self, x, y, size):
        """
        Verifica se uma posição específica colide com algum obstáculo no mapa.
        
        Args:
            x (int): Posição X para verificar
            y (int): Posição Y para verificar
            size (int): Tamanho do objeto para verificar
            
        Returns:
            bool: True se a posição estiver bloqueada, False caso contrário
        """
        import pygame
        test_rect = pygame.Rect(x, y, size, size)
        
        for obstacle in self.obstacles:
            if test_rect.colliderect(obstacle):
                return True
        
        return False
        
    def draw(self, surface, area_x, area_y, area_size):
        """Desenha elementos específicos do mapa."""
        pass
        
    def check_collision(self, square):
        """Verifica colisão com elementos do mapa."""
        return False

# Mapa básico (padrão)
class BasicMap(GameMap):
    """Mapa básico sem obstáculos."""
    def __init__(self):
        super().__init__(name="Mapa Básico", bg_color=BLACK, area_color=DARK_GRAY)
        
    def draw(self, surface, area_x, area_y, area_size):
        """Não faz nada além do que já é renderizado no jogo base."""
        pass

# Mapa com obstáculo central
class CenterObstacleMap(GameMap):
    """Mapa com um obstáculo no centro."""
    def __init__(self):
        super().__init__(name="Obstáculo Central", bg_color=(20, 20, 40), area_color=(30, 30, 50))
        
    def draw(self, surface, area_x, area_y, area_size):
        """Desenha um obstáculo no centro do mapa."""
        import pygame
        obstacle_size = area_size // 4
        obstacle_x = area_x + (area_size - obstacle_size) // 2
        obstacle_y = area_y + (area_size - obstacle_size) // 2
        
        # Armazenar o obstáculo para verificação de colisão
        self.obstacles = [pygame.Rect(obstacle_x, obstacle_y, obstacle_size, obstacle_size)]
        
        # Desenhar o obstáculo
        pygame.draw.rect(surface, (80, 80, 100), self.obstacles[0])
        pygame.draw.rect(surface, (150, 150, 180), self.obstacles[0], 2)
        
    def check_collision(self, square):
        """Verifica colisão com o obstáculo central."""
        import pygame
        square_rect = pygame.Rect(square.x, square.y, square.size, square.size)
        
        for obstacle in self.obstacles:
            if square_rect.colliderect(obstacle):
                # Determinar qual lado colidiu e inverter a velocidade correspondente
                if abs(square.x + square.size - obstacle.x) < 10 or abs(square.x - obstacle.x - obstacle.width) < 10:
                    square.vx = -square.vx
                    # Ajustar posição para evitar ficar preso no obstáculo
                    if square.x + square.size > obstacle.x and square.x < obstacle.x:
                        square.x = obstacle.x - square.size
                    elif square.x < obstacle.x + obstacle.width and square.x + square.size > obstacle.x + obstacle.width:
                        square.x = obstacle.x + obstacle.width
                
                if abs(square.y + square.size - obstacle.y) < 10 or abs(square.y - obstacle.y - obstacle.height) < 10:
                    square.vy = -square.vy
                    # Ajustar posição para evitar ficar preso no obstáculo
                    if square.y + square.size > obstacle.y and square.y < obstacle.y:
                        square.y = obstacle.y - square.size
                    elif square.y < obstacle.y + obstacle.height and square.y + square.size > obstacle.y + obstacle.height:
                        square.y = obstacle.y + obstacle.height
                
                return True
                
        return False

# Mapa com quatro obstáculos nos cantos
class FourCornersMap(GameMap):
    """Mapa com obstáculos nos quatro cantos."""
    def __init__(self):
        super().__init__(name="Quatro Cantos", bg_color=(20, 40, 20), area_color=(30, 50, 30))
        
    def draw(self, surface, area_x, area_y, area_size):
        """Desenha quatro obstáculos nos cantos do mapa."""
        import pygame
        self.obstacles = []
        
        # Tamanho de cada obstáculo
        obstacle_size = area_size // 6
        
        # Criar obstáculos nos quatro cantos
        corners = [
            (area_x, area_y),  # Superior esquerdo
            (area_x + area_size - obstacle_size, area_y),  # Superior direito
            (area_x, area_y + area_size - obstacle_size),  # Inferior esquerdo
            (area_x + area_size - obstacle_size, area_y + area_size - obstacle_size)  # Inferior direito
        ]
        
        for corner in corners:
            obstacle = pygame.Rect(corner[0], corner[1], obstacle_size, obstacle_size)
            self.obstacles.append(obstacle)
            
            # Desenhar o obstáculo
            pygame.draw.rect(surface, (80, 120, 80), obstacle)
            pygame.draw.rect(surface, (150, 200, 150), obstacle, 2)
    
    def check_collision(self, square):
        """Verifica colisão com os obstáculos nos cantos."""
        import pygame
        square_rect = pygame.Rect(square.x, square.y, square.size, square.size)
        
        for obstacle in self.obstacles:
            if square_rect.colliderect(obstacle):
                # Determinar qual lado colidiu e inverter a velocidade correspondente
                if abs(square.x + square.size - obstacle.x) < 10 or abs(square.x - obstacle.x - obstacle.width) < 10:
                    square.vx = -square.vx
                    # Ajustar posição para evitar ficar preso no obstáculo
                    if square.x + square.size > obstacle.x and square.x < obstacle.x:
                        square.x = obstacle.x - square.size
                    elif square.x < obstacle.x + obstacle.width and square.x + square.size > obstacle.x + obstacle.width:
                        square.x = obstacle.x + obstacle.width
                
                if abs(square.y + square.size - obstacle.y) < 10 or abs(square.y - obstacle.y - obstacle.height) < 10:
                    square.vy = -square.vy
                    # Ajustar posição para evitar ficar preso no obstáculo
                    if square.y + square.size > obstacle.y and square.y < obstacle.y:
                        square.y = obstacle.y - square.size
                    elif square.y < obstacle.y + obstacle.height and square.y + square.size > obstacle.y + obstacle.height:
                        square.y = obstacle.y + obstacle.height
                
                return True
                
        return False

# Mapa com túnel em cruz
class CrossMap(GameMap):
    """Mapa com túnel em formato de cruz."""
    def __init__(self):
        super().__init__(name="Cruz", bg_color=(40, 20, 20), area_color=(50, 30, 30))
        
    def draw(self, surface, area_x, area_y, area_size):
        """Desenha quatro blocos formando um túnel em cruz."""
        import pygame
        self.obstacles = []
        
        # Largura do túnel
        tunnel_width = area_size // 3
        
        # Posição do túnel horizontal
        tunnel_y = area_y + (area_size - tunnel_width) // 2
        
        # Posição do túnel vertical
        tunnel_x = area_x + (area_size - tunnel_width) // 2
        
        # Criar os quatro blocos que formam a cruz
        blocks = [
            # Superior esquerdo
            (area_x, area_y, tunnel_x - area_x, tunnel_y - area_y),
            # Superior direito
            (tunnel_x + tunnel_width, area_y, area_x + area_size - (tunnel_x + tunnel_width), tunnel_y - area_y),
            # Inferior esquerdo
            (area_x, tunnel_y + tunnel_width, tunnel_x - area_x, area_y + area_size - (tunnel_y + tunnel_width)),
            # Inferior direito
            (tunnel_x + tunnel_width, tunnel_y + tunnel_width, 
             area_x + area_size - (tunnel_x + tunnel_width), area_y + area_size - (tunnel_y + tunnel_width))
        ]
        
        for block in blocks:
            obstacle = pygame.Rect(block[0], block[1], block[2], block[3])
            self.obstacles.append(obstacle)
            
            # Desenhar o obstáculo
            pygame.draw.rect(surface, (120, 80, 80), obstacle)
            pygame.draw.rect(surface, (200, 150, 150), obstacle, 2)
    
    def check_collision(self, square):
        """Verifica colisão com os blocos da cruz."""
        import pygame
        square_rect = pygame.Rect(square.x, square.y, square.size, square.size)
        
        for obstacle in self.obstacles:
            if square_rect.colliderect(obstacle):
                # Determinar qual lado colidiu e inverter a velocidade correspondente
                if abs(square.x + square.size - obstacle.x) < 10 or abs(square.x - obstacle.x - obstacle.width) < 10:
                    square.vx = -square.vx
                    # Ajustar posição para evitar ficar preso no obstáculo
                    if square.x + square.size > obstacle.x and square.x < obstacle.x:
                        square.x = obstacle.x - square.size
                    elif square.x < obstacle.x + obstacle.width and square.x + square.size > obstacle.x + obstacle.width:
                        square.x = obstacle.x + obstacle.width
                
                if abs(square.y + square.size - obstacle.y) < 10 or abs(square.y - obstacle.y - obstacle.height) < 10:
                    square.vy = -square.vy
                    # Ajustar posição para evitar ficar preso no obstáculo
                    if square.y + square.size > obstacle.y and square.y < obstacle.y:
                        square.y = obstacle.y - square.size
                    elif square.y < obstacle.y + obstacle.height and square.y + square.size > obstacle.y + obstacle.height:
                        square.y = obstacle.y + obstacle.height
                
                return True
                
        return False

# Lista de mapas disponíveis
AVAILABLE_MAPS = [
    BasicMap(),
    CenterObstacleMap(),
    FourCornersMap(),
    CrossMap()
]