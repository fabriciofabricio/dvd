"""
Implementação da classe PowerUp para o jogo DVD Bounce Simulation.
"""
import math
import pygame
from constants import YELLOW


class PowerUp:
    """Classe que representa um power-up na simulação."""
    def __init__(self, x, y):
        """
        Inicializa um power-up em uma posição específica
        
        Args:
            x (float): Posição x do power-up
            y (float): Posição y do power-up
        """
        self.x = x
        self.y = y
        self.size = 20  # Tamanho do power-up
        self.active = True
    
    def draw(self, surface):
        """
        Desenha o power-up na superfície
        
        Args:
            surface: Superfície do pygame para desenhar
        """
        if self.active:
            # Desenhar um círculo amarelo pulsante com espinhos
            pulse = (math.sin(pygame.time.get_ticks() / 200) + 1) * 0.5 * 255
            color = (255, int(pulse), 0)  # Amarelo pulsante para laranja
            
            # Círculo central
            pygame.draw.circle(surface, color, (int(self.x + self.size/2), int(self.y + self.size/2)), int(self.size/2))
            
            # Desenhar pequenos triângulos ao redor para representar espinhos
            spike_color = YELLOW
            spike_length = self.size // 3
            center_x = self.x + self.size // 2
            center_y = self.y + self.size // 2
            radius = self.size // 2
            
            # Desenhar 8 espinhos ao redor do círculo
            for angle in range(0, 360, 45):
                rad_angle = math.radians(angle)
                # Ponto na borda do círculo
                edge_x = center_x + radius * math.cos(rad_angle)
                edge_y = center_y + radius * math.sin(rad_angle)
                # Ponto da ponta do espinho
                spike_x = center_x + (radius + spike_length) * math.cos(rad_angle)
                spike_y = center_y + (radius + spike_length) * math.sin(rad_angle)
                # Pontos laterais do triângulo
                side_angle1 = math.radians(angle + 20)
                side_angle2 = math.radians(angle - 20)
                side_dist = radius * 0.5
                side_x1 = center_x + side_dist * math.cos(side_angle1)
                side_y1 = center_y + side_dist * math.sin(side_angle1)
                side_x2 = center_x + side_dist * math.cos(side_angle2)
                side_y2 = center_y + side_dist * math.sin(side_angle2)
                
                # Desenhar o triângulo do espinho
                pygame.draw.polygon(surface, spike_color, [(edge_x, edge_y), (spike_x, spike_y), (side_x1, side_y1)])
                pygame.draw.polygon(surface, spike_color, [(edge_x, edge_y), (spike_x, spike_y), (side_x2, side_y2)])
    
    def check_collision(self, square):
        """
        Verifica se o power-up colidiu com um quadrado
        
        Args:
            square: O quadrado para verificar colisão
            
        Returns:
            bool: True se há colisão, False caso contrário
        """
        if not self.active:
            return False
            
        # Simplificar a verificação de colisão tratando o power-up como um quadrado
        return (self.x < square.x + square.size and
                self.x + self.size > square.x and
                self.y < square.y + square.size and
                self.y + self.size > square.y)