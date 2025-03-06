"""
Implementação da classe Square para o jogo DVD Bounce Simulation.
"""
import random
import math
import pygame
import os
from constants import WHITE, YELLOW


class Particle:
    """Classe para representar uma partícula da explosão."""
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.lifetime = random.randint(30, 60)  # Duração em frames
        
        # Velocidade aleatória em todas as direções
        speed = random.uniform(1, 5)
        angle = random.uniform(0, 2 * math.pi)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        
        # Fade out gradual
        self.fade_speed = random.uniform(0.01, 0.05)
        self.alpha = 1.0  # Transparência inicial
    
    def update(self):
        """Atualiza a partícula."""
        self.x += self.vx
        self.y += self.vy
        
        # Adicionar gravidade leve
        self.vy += 0.05
        
        # Reduzir vida
        self.lifetime -= 1
        
        # Reduzir transparência
        self.alpha = max(0, self.alpha - self.fade_speed)
        
        # Reduzir tamanho gradualmente
        if self.size > 0.5:
            self.size -= 0.1
    
    def draw(self, surface):
        """Desenha a partícula."""
        if self.lifetime <= 0 or self.alpha <= 0:
            return
        
        # Ajustar cor com base na transparência
        r, g, b = self.color
        color_with_alpha = (r, g, b, int(self.alpha * 255))
        
        # Criar superfície com suporte a transparência
        particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(particle_surface, color_with_alpha, (int(self.size), int(self.size)), int(self.size))
        
        # Desenhar na superfície principal
        surface.blit(particle_surface, (int(self.x - self.size), int(self.y - self.size)))
    
    def is_alive(self):
        """Verifica se a partícula ainda está viva."""
        return self.lifetime > 0 and self.alpha > 0


class Square:
    """Classe que representa um quadrado na simulação."""
    def __init__(self, x, y, size, color, name=None, color_index=0):
        """
        Inicializa um quadrado com posição, tamanho e cor específicos.
        
        Args:
            x (float): Posição inicial x
            y (float): Posição inicial y
            size (int): Tamanho do quadrado
            color (tuple): Cor RGB do quadrado
            name (str, optional): Nome personalizado do quadrado
            color_index (int, optional): Índice da cor (para nomes padrão)
        """
        self.x = x
        self.y = y
        self.size = size
        self.color = color
        self.original_color = color
        
        # Garantir que name seja uma string válida
        if name is not None:
            self.name = str(name)
        else:
            # Usar valor padrão se name não for fornecido
            try:
                self.name = f"Jogador {int(color_index)+1}"
            except (ValueError, TypeError):
                self.name = "Jogador"
        
        # Imagem personalizada (opcional)
        self.image = None
        self.use_image = False  # Flag para controlar o uso da imagem
        
        # Sistema de vidas
        self.lives = 5
        self.max_lives = 5  # Máximo de vidas
        self.is_alive = True
        self.invincible_timer = 0  # Tempo de invencibilidade após perder uma vida
        
        # Atributos para os espinhos
        self.has_spikes = False
        self.spike_timer = 0
        
        # Valores de área (serão configurados pelo Game)
        self.area_x = 0
        self.area_y = 0
        self.area_size = 0
        self.min_speed = 1.5
        self.max_speed = 4.5
        
        # Velocidade inicial aleatória
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 4.5)  # Valores padrão iniciais
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        
        # Massa (para cálculos de colisão realistas)
        self.mass = size * size  # Proporcional à área
        
        # Partículas para explosão
        self.particles = []
        
        # Rastreamento de quem eliminou este quadrado
        self.killed_by = None
    
    def set_image(self, image_path):
        """
        Define uma imagem para o quadrado.
        
        Args:
            image_path (str): Caminho para o arquivo de imagem
        """
        if not os.path.exists(image_path):
            print(f"ERRO: Imagem não encontrada: {image_path}")
            self.use_image = False
            return False
            
        try:
            print(f"Carregando imagem: {image_path}")
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
            self.use_image = True
            print(f"Imagem carregada com sucesso: {image_path}")
            return True
        except (pygame.error, FileNotFoundError, TypeError) as e:
            print(f"ERRO ao carregar imagem {image_path}: {e}")
            self.image = None
            self.use_image = False
            return False
    
    def set_area(self, area_x, area_y, area_size):
        """Define a área de jogo para colisões."""
        self.area_x = area_x
        self.area_y = area_y
        self.area_size = area_size
    
    def set_speed_limits(self, min_speed, max_speed):
        """Define os limites de velocidade."""
        self.min_speed = min_speed
        self.max_speed = max_speed
    
    def take_damage(self, attacker=None):
        """
        Reduz uma vida do quadrado.
        
        Args:
            attacker: O quadrado que causou o dano (opcional)
        """
        if self.invincible_timer > 0:
            return  # Não tomar dano durante a invencibilidade

        self.lives -= 1
        
        # Ativar invencibilidade com efeito de piscar branco
        self.invincible_timer = 90  # 1.5 segundos de invencibilidade
        
        # Verificar se ainda está vivo
        if self.lives <= 0:
            self.explode()
            self.is_alive = False
            # Armazenar qual quadrado eliminou este
            self.killed_by = attacker
    
    def explode(self):
        """Cria a animação de explosão quando o quadrado perde todas as vidas."""
        # Criar partículas a partir do centro do quadrado
        center_x = self.x + self.size / 2
        center_y = self.y + self.size / 2
        
        # Gerar várias partículas com a cor do quadrado
        num_particles = 50
        for _ in range(num_particles):
            # Posição aleatória dentro do quadrado
            particle_x = random.uniform(self.x, self.x + self.size)
            particle_y = random.uniform(self.y, self.y + self.size)
            
            # Criar partícula com a cor do quadrado
            self.particles.append(Particle(particle_x, particle_y, self.original_color))
    
    def get_corners(self):
        """Retorna as coordenadas dos quatro cantos do quadrado."""
        return [
            (self.x, self.y),  # Superior esquerdo
            (self.x + self.size, self.y),  # Superior direito
            (self.x, self.y + self.size),  # Inferior esquerdo
            (self.x + self.size, self.y + self.size)  # Inferior direito
        ]
    
    def get_center(self):
        """Retorna o centro do quadrado."""
        return (self.x + self.size / 2, self.y + self.size / 2)
    
    def update(self):
        """Atualiza a posição e velocidade do quadrado"""
        # Atualizar partículas se o quadrado explodiu
        if not self.is_alive:
            for particle in self.particles:
                particle.update()
            # Remover partículas mortas
            self.particles = [p for p in self.particles if p.is_alive()]
            return
        
        # Reduzir timer de invencibilidade e aplicar efeito de piscar
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            
            # Efeito piscante durante a invencibilidade
            if self.invincible_timer % 8 < 4:  # Alternar a cada 4 frames para um piscar mais rápido
                self.color = WHITE  # Branco
            else:
                self.color = self.original_color
                
            # Quando terminar a invencibilidade, garantir que a cor volta ao normal
            if self.invincible_timer == 0:
                self.color = self.original_color
        else:
            # Se não estiver invencível, garantir que a cor é a original
            self.color = self.original_color
        
        # Atualizar a posição
        self.x += self.vx
        self.y += self.vy
        
        # Verificar colisão com as bordas da área restrita
        if self.x <= self.area_x or self.x + self.size >= self.area_x + self.area_size:
            self.vx = -self.vx
            # Garantir que não fique preso na borda
            if self.x <= self.area_x:
                self.x = self.area_x
            else:
                self.x = self.area_x + self.area_size - self.size
        
        if self.y <= self.area_y or self.y + self.size >= self.area_y + self.area_size:
            self.vy = -self.vy
            # Garantir que não fique preso na borda
            if self.y <= self.area_y:
                self.y = self.area_y
            else:
                self.y = self.area_y + self.area_size - self.size
        
        # Atualizar timer de espinhos
        if self.has_spikes and self.spike_timer > 0:
            self.spike_timer -= 1
            if self.spike_timer == 0:
                self.has_spikes = False
        
        # Variar levemente a velocidade ao longo do tempo (extra)
        self.vx += random.uniform(-0.03, 0.03)
        self.vy += random.uniform(-0.03, 0.03)
        
        # Limitar a velocidade mínima e máxima
        speed = math.sqrt(self.vx**2 + self.vy**2)
        
        if speed < self.min_speed:
            self.vx = self.vx / speed * self.min_speed
            self.vy = self.vy / speed * self.min_speed
        elif speed > self.max_speed:
            self.vx = self.vx / speed * self.max_speed
            self.vy = self.vy / speed * self.max_speed
    
    def draw(self, surface):
        """Desenha o quadrado na superfície"""
        # Desenhar partículas se o quadrado explodiu
        if not self.is_alive:
            for particle in self.particles:
                particle.draw(surface)
            return
        
        # Desenhar o quadrado base (com imagem ou cor sólida)
        if self.use_image and self.image:
            # Se estiver invencível e piscando, mostrar efeito
            if self.invincible_timer > 0 and self.invincible_timer % 8 < 4:
                # Criar uma superfície branca semitransparente
                white_overlay = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                white_overlay.fill((255, 255, 255, 150))  # Branco semi-transparente
                
                # Desenhar primeiro a imagem e depois o overlay
                surface.blit(self.image, (int(self.x), int(self.y)))
                surface.blit(white_overlay, (int(self.x), int(self.y)))
            else:
                # Desenhar apenas a imagem
                surface.blit(self.image, (int(self.x), int(self.y)))
        else:
            # Usar cor sólida se não tiver imagem ou se use_image for False
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))
        
        # Desenhar espinhos se o quadrado tiver espinhos
        if self.has_spikes:
            spike_length = self.size // 3
            spike_color = YELLOW
            
            # Desenhar espinhos em cada lado do quadrado
            # Espinhos superiores
            for i in range(3):
                x_pos = self.x + (i + 1) * self.size // 4
                pygame.draw.polygon(surface, spike_color, [
                    (x_pos, self.y),
                    (x_pos - spike_length // 2, self.y - spike_length),
                    (x_pos + spike_length // 2, self.y - spike_length)
                ])
            
            # Espinhos inferiores
            for i in range(3):
                x_pos = self.x + (i + 1) * self.size // 4
                pygame.draw.polygon(surface, spike_color, [
                    (x_pos, self.y + self.size),
                    (x_pos - spike_length // 2, self.y + self.size + spike_length),
                    (x_pos + spike_length // 2, self.y + self.size + spike_length)
                ])
            
            # Espinhos laterais esquerdos
            for i in range(3):
                y_pos = self.y + (i + 1) * self.size // 4
                pygame.draw.polygon(surface, spike_color, [
                    (self.x, y_pos),
                    (self.x - spike_length, y_pos - spike_length // 2),
                    (self.x - spike_length, y_pos + spike_length // 2)
                ])
            
            # Espinhos laterais direitos
            for i in range(3):
                y_pos = self.y + (i + 1) * self.size // 4
                pygame.draw.polygon(surface, spike_color, [
                    (self.x + self.size, y_pos),
                    (self.x + self.size + spike_length, y_pos - spike_length // 2),
                    (self.x + self.size + spike_length, y_pos + spike_length // 2)
                ])
    
    def check_collision(self, other):
        """
        Verifica se há colisão com outro quadrado
        
        Args:
            other (Square): O outro quadrado para verificar colisão
            
        Returns:
            bool: True se há colisão, False caso contrário
        """
        # Não verificar colisão se algum dos quadrados está "morto"
        if not self.is_alive or not other.is_alive:
            return False
            
        return (self.x < other.x + other.size and
                self.x + self.size > other.x and
                self.y < other.y + other.size and
                self.y + self.size > other.y)
    
    def distance_to_edge(self, other, nx, ny):
        """Calcula a distância do centro deste quadrado à borda do outro quadrado na direção especificada."""
        cx1, cy1 = self.get_center()
        
        # Verificar qual borda interceptamos
        if nx > 0:  # Direção positiva em x (direita)
            edge_x = other.x
        else:  # Direção negativa em x (esquerda)
            edge_x = other.x + other.size
            
        if ny > 0:  # Direção positiva em y (baixo)
            edge_y = other.y
        else:  # Direção negativa em y (cima)
            edge_y = other.y + other.size
        
        # Calcular distância
        dx = edge_x - cx1
        dy = edge_y - cy1
        
        return abs(dx * nx + dy * ny)
    
    def handle_collision_corner(self, other):
        """Verifica e manipula uma possível colisão de canto com outro quadrado."""
        # Obter cantos dos dois quadrados
        corners1 = self.get_corners()
        corners2 = other.get_corners()
        
        # Centro dos quadrados
        cx1, cy1 = self.get_center()
        cx2, cy2 = other.get_center()
        
        # Encontrar o par de cantos mais próximos
        min_dist = float('inf')
        nearest_corner1 = None
        nearest_corner2 = None
        
        for c1 in corners1:
            for c2 in corners2:
                dist = math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_corner1 = c1
                    nearest_corner2 = c2
        
        # Se a distância entre os cantos mais próximos for muito pequena
        # e os quadrados estão realmente próximos uns dos outros
        threshold = self.size * 0.3  # Ajuste este valor conforme necessário
        
        if min_dist < threshold:
            # Vetor do canto 1 para o canto 2
            dx = nearest_corner2[0] - nearest_corner1[0]
            dy = nearest_corner2[1] - nearest_corner1[1]
            dist = max(0.1, math.sqrt(dx**2 + dy**2))  # Evitar divisão por zero
            
            # Normalizar o vetor
            nx = dx / dist
            ny = dy / dist
            
            # Calcular a velocidade relativa na direção normal
            vrx = other.vx - self.vx
            vry = other.vy - self.vy
            vr_dot_n = vrx * nx + vry * ny
            
            # Se os quadrados estão se aproximando
            if vr_dot_n < 0:
                # Calcular o impulso com base na conservação de momentum e energia
                m1 = self.mass
                m2 = other.mass
                e = 1.0  # Coeficiente de restituição (1 = colisão elástica)
                
                j = -(1 + e) * vr_dot_n / ((1/m1) + (1/m2))
                
                # Aplicar o impulso
                self.vx -= j * nx / m1
                self.vy -= j * ny / m1
                other.vx += j * nx / m2
                other.vy += j * ny / m2
                
                # Adicionar um pequeno componente aleatório para evitar comportamentos repetitivos
                angle = random.uniform(0, math.pi/4)  # Pequena variação aleatória
                self.vx += 0.2 * math.cos(angle)
                self.vy += 0.2 * math.sin(angle)
                other.vx += 0.2 * math.cos(angle + math.pi)
                other.vy += 0.2 * math.sin(angle + math.pi)
                
                # Corrigir a sobreposição (afastar os quadrados)
                overlap = threshold - dist
                if overlap > 0:
                    self.x -= nx * overlap / 2
                    self.y -= ny * overlap / 2
                    other.x += nx * overlap / 2
                    other.y += ny * overlap / 2
                
                return True  # Colisão tratada
        
        return False  # Não foi uma colisão de canto
    
    def handle_collision(self, other):
        """
        Manipula a colisão com outro quadrado usando física melhorada
        
        Args:
            other (Square): O outro quadrado envolvido na colisão
        """
        # Verificar dano por espinhos
        if self.has_spikes and other.is_alive:
            other.take_damage(self)
        
        if other.has_spikes and self.is_alive:
            self.take_damage(other)
        
        # Tentar lidar com colisão de canto primeiro
        if self.handle_collision_corner(other):
            # Se foi uma colisão de canto, não precisamos fazer mais nada
            # Remover espinhos na colisão
            if self.has_spikes:
                self.has_spikes = False
                self.spike_timer = 0
            
            if other.has_spikes:
                other.has_spikes = False
                other.spike_timer = 0
                
            return
        
        # Calcular os centros dos quadrados
        center_x1, center_y1 = self.get_center()
        center_x2, center_y2 = other.get_center()
        
        # Vetor de colisão (do quadrado 1 para o quadrado 2)
        dx = center_x2 - center_x1
        dy = center_y2 - center_y1
        distance = max(1, math.sqrt(dx**2 + dy**2))  # Evitar divisão por zero
        
        # Normalizar o vetor de colisão
        nx = dx / distance
        ny = dy / distance
        
        # Determinar o tipo de colisão com base na direção do vetor normal
        # e na posição relativa dos quadrados
        collision_type = "unknown"
        
        # Se o vetor normal é principalmente horizontal
        if abs(nx) > abs(ny):
            if nx > 0:  # Quadrado 1 está à esquerda do quadrado 2
                collision_type = "right-left"
            else:  # Quadrado 1 está à direita do quadrado 2
                collision_type = "left-right"
        else:  # Se o vetor normal é principalmente vertical
            if ny > 0:  # Quadrado 1 está acima do quadrado 2
                collision_type = "bottom-top"
            else:  # Quadrado 1 está abaixo do quadrado 2
                collision_type = "top-bottom"
        
        # Ajustar o vetor normal com base no tipo de colisão para colisões mais precisas
        if collision_type == "right-left" or collision_type == "left-right":
            ny = 0  # Colisão puramente horizontal
            nx = 1 if nx > 0 else -1
        elif collision_type == "bottom-top" or collision_type == "top-bottom":
            nx = 0  # Colisão puramente vertical
            ny = 1 if ny > 0 else -1
        
        # Renormalizar o vetor após modificá-lo
        norm = math.sqrt(nx**2 + ny**2)
        if norm > 0:
            nx /= norm
            ny /= norm
        
        # Verificar se os quadrados estão se movendo na mesma direção e são quase paralelos
        v1_mag = math.sqrt(self.vx**2 + self.vy**2)
        v2_mag = math.sqrt(other.vx**2 + other.vy**2)
        
        if v1_mag > 0 and v2_mag > 0:
            dot_product = (self.vx * other.vx + self.vy * other.vy) / (v1_mag * v2_mag)
            
            # Se o produto escalar for próximo de 1, os vetores estão apontando 
            # aproximadamente na mesma direção
            if dot_product > 0.7:  # Limiar arbitrário para "mesma direção"
                # Decidir aleatoriamente qual quadrado mudar de direção
                if random.random() < 0.5:
                    # Mudar a direção deste quadrado por um ângulo significativo
                    angle = random.uniform(math.pi/2, math.pi)
                    speed = math.sqrt(self.vx**2 + self.vy**2)
                    self.vx = speed * math.cos(angle)
                    self.vy = speed * math.sin(angle)
                else:
                    # Mudar a direção do outro quadrado
                    angle = random.uniform(math.pi/2, math.pi)
                    speed = math.sqrt(other.vx**2 + other.vy**2)
                    other.vx = speed * math.cos(angle)
                    other.vy = speed * math.sin(angle)
            else:
                # Usar física de colisão melhorada para outros casos
                
                # Calcular as velocidades relativas na direção normal
                v1n = self.vx * nx + self.vy * ny
                v2n = other.vx * nx + other.vy * ny
                
                # Calcular as velocidades tangenciais (perpendiculares à normal)
                v1tx = self.vx - v1n * nx
                v1ty = self.vy - v1n * ny
                v2tx = other.vx - v2n * nx
                v2ty = other.vy - v2n * ny
                
                # Calcular novas velocidades normais após colisão (colisão elástica)
                # Usando conservação de momento e energia
                m1 = self.mass
                m2 = other.mass
                
                # Fórmula para colisão elástica
                new_v1n = (v1n * (m1 - m2) + 2 * m2 * v2n) / (m1 + m2)
                new_v2n = (v2n * (m2 - m1) + 2 * m1 * v1n) / (m1 + m2)
                
                # Calcular as novas velocidades combinando componentes normais e tangenciais
                self.vx = new_v1n * nx + v1tx
                self.vy = new_v1n * ny + v1ty
                other.vx = new_v2n * nx + v2tx
                other.vy = new_v2n * ny + v2ty
                
                # Adicionar um pequeno componente aleatório para evitar comportamentos repetitivos
                self.vx += random.uniform(-0.1, 0.1)
                self.vy += random.uniform(-0.1, 0.1)
                other.vx += random.uniform(-0.1, 0.1)
                other.vy += random.uniform(-0.1, 0.1)
        else:
            # Caso um dos quadrados tenha velocidade zero, aplicar um impulso simples
            self.vx = -self.vx * 0.9 + random.uniform(-0.2, 0.2)
            self.vy = -self.vy * 0.9 + random.uniform(-0.2, 0.2)
            other.vx = -other.vx * 0.9 + random.uniform(-0.2, 0.2)
            other.vy = -other.vy * 0.9 + random.uniform(-0.2, 0.2)
        
        # Remover espinhos na colisão
        if self.has_spikes:
            self.has_spikes = False
            self.spike_timer = 0
        
        if other.has_spikes:
            other.has_spikes = False
            other.spike_timer = 0
        
        # Separar os quadrados para evitar sobreposição
        # Calcular a sobreposição com base no tipo de colisão
        if collision_type == "right-left":
            overlap = (self.x + self.size) - other.x
        elif collision_type == "left-right":
            overlap = (other.x + other.size) - self.x
        elif collision_type == "bottom-top":
            overlap = (self.y + self.size) - other.y
        elif collision_type == "top-bottom":
            overlap = (other.y + other.size) - self.y
        else:
            # Fallback para o cálculo tradicional
            overlap = (self.size + other.size) / 2 - distance
        
        if overlap > 0:
            self.x -= nx * overlap / 2
            self.y -= ny * overlap / 2
            other.x += nx * overlap / 2
            other.y += ny * overlap / 2