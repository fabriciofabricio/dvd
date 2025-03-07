"""
Implementação do menu do jogo DVD Bounce Simulation.
"""
import pygame
from constants import (
    WIDTH, HEIGHT, MARGIN, MIN_SPEED, MAX_SPEED, SQUARE_SIZE,
    MENU_FONT, TITLE_FONT, BLACK, WHITE, YELLOW
)
from maps import AVAILABLE_MAPS

def show_map_selection(window, current_map_index=0):
    """
    Exibe um menu para selecionar mapas
    
    Args:
        window: Superfície principal do pygame
        current_map_index: Índice do mapa atual
        
    Returns:
        int: Índice do mapa selecionado ou -1 para cancelar
    """
    # Opções do menu
    selected_option = 0
    menu_active = True
    
    # Título e instruções
    title = "SELEÇÃO DE MAPA"
    instructions = "Use as setas para navegar, ENTER para selecionar, ESC para voltar"
    
    while menu_active:
        # Preencher a tela com um fundo escuro semitransparente
        menu_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        menu_surface.fill((0, 0, 0, 200))  # RGBA: preto com 80% de opacidade
        
        # Título do menu
        title_rendered = TITLE_FONT.render(title, True, WHITE)
        title_rect = title_rendered.get_rect(center=(WIDTH // 2, 100))
        menu_surface.blit(title_rendered, title_rect)
        
        # Instruções
        inst_rendered = MENU_FONT.render(instructions, True, (180, 180, 180))
        inst_rect = inst_rendered.get_rect(center=(WIDTH // 2, 150))
        menu_surface.blit(inst_rendered, inst_rect)
        
        # Renderizar a lista de mapas
        for i, game_map in enumerate(AVAILABLE_MAPS):
            color = YELLOW if i == selected_option else WHITE
            text = game_map.name
            
            # Adicionar indicador de seleção para o mapa atual
            if i == current_map_index:
                text += " (Atual)"
                
            rendered_text = MENU_FONT.render(text, True, color)
            text_rect = rendered_text.get_rect(center=(WIDTH // 2, 200 + i * 50))
            menu_surface.blit(rendered_text, text_rect)
        
        # Opção "Voltar"
        back_color = YELLOW if selected_option == len(AVAILABLE_MAPS) else WHITE
        back_text = MENU_FONT.render("Voltar", True, back_color)
        back_rect = back_text.get_rect(center=(WIDTH // 2, 200 + len(AVAILABLE_MAPS) * 50))
        menu_surface.blit(back_text, back_rect)
        
        # Sobrepor a superfície do menu à tela principal
        window.blit(menu_surface, (0, 0))
        pygame.display.flip()
        
        # Processar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return -1
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return current_map_index  # Manter o mapa atual
                
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % (len(AVAILABLE_MAPS) + 1)
                
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % (len(AVAILABLE_MAPS) + 1)
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected_option == len(AVAILABLE_MAPS):  # Opção "Voltar"
                        return current_map_index
                    else:
                        return selected_option  # Retornar o índice do mapa selecionado

def show_menu(window, current_config=None):
    """
    Exibe um menu para ajustar as configurações do jogo
    
    Args:
        window: Superfície principal do pygame
        current_config: Dicionário com as configurações atuais
        
    Returns:
        tuple: (continuar_jogo, configurações_atualizadas, resetar)
               continuar_jogo é um booleano que indica se o jogo deve continuar
               configurações_atualizadas é um dicionário com as novas configurações
               resetar é um booleano que indica se as configurações devem ser resetadas
    """
    # Configurações iniciais para o menu (usar valores atuais ou padrão)
    if current_config:
        margin = current_config.get('margin', MARGIN)
        square_size = current_config.get('square_size', SQUARE_SIZE)
        min_speed = current_config.get('min_speed', MIN_SPEED)
        max_speed = current_config.get('max_speed', MAX_SPEED)
        lives = current_config.get('lives', 5)  # Novo: vidas dos quadrados
        map_index = current_config.get('map_index', 0)  # Novo: índice do mapa
    else:
        margin = MARGIN
        square_size = SQUARE_SIZE
        min_speed = MIN_SPEED
        max_speed = MAX_SPEED
        lives = 5  # Valor padrão para vidas
        map_index = 0  # Mapa padrão
    
    # Opções do menu
    options = [
        "Tamanho dos Quadrados: {}",
        "Margem da Área: {}",
        "Velocidade Mínima: {:.1f}",
        "Velocidade Máxima: {:.1f}",
        "Vidas dos Quadrados: {}",
        "Selecionar Mapa: {}",  # Nova opção
        "Restaurar Configurações Padrão",
        "Voltar ao Jogo",
        "Sair"
    ]
    
    selected_option = 0
    menu_active = True
    reset_config = False
    
    while menu_active:
        # Preencher a tela com um fundo escuro semitransparente
        menu_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        menu_surface.fill((0, 0, 0, 200))  # RGBA: preto com 80% de opacidade
        
        # Título do menu
        title = TITLE_FONT.render("MENU DE CONFIGURAÇÕES", True, WHITE)
        title_rect = title.get_rect(center=(WIDTH // 2, 100))
        menu_surface.blit(title, title_rect)
        
        # Renderizar as opções do menu
        for i, option in enumerate(options):
            if i == 0:
                text = option.format(square_size)
            elif i == 1:
                text = option.format(margin)
            elif i == 2:
                text = option.format(min_speed)
            elif i == 3:
                text = option.format(max_speed)
            elif i == 4:
                text = option.format(lives)
            elif i == 5:
                # Mostrar o nome do mapa selecionado
                text = option.format(AVAILABLE_MAPS[map_index].name)
            else:
                text = option
            
            color = YELLOW if i == selected_option else WHITE
            rendered_text = MENU_FONT.render(text, True, color)
            text_rect = rendered_text.get_rect(center=(WIDTH // 2, 180 + i * 50))
            menu_surface.blit(rendered_text, text_rect)
            
            # Adicionar setas para as opções ajustáveis
            if i < 5:  # Primeiras 5 opções são ajustáveis com setas
                left_arrow = MENU_FONT.render("<", True, color)
                right_arrow = MENU_FONT.render(">", True, color)
                menu_surface.blit(left_arrow, (WIDTH // 2 - 150, 180 + i * 50 - 12))
                menu_surface.blit(right_arrow, (WIDTH // 2 + 150, 180 + i * 50 - 12))
        
        # Sobrepor a superfície do menu à tela principal
        window.blit(menu_surface, (0, 0))
        pygame.display.flip()
        
        # Processar eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, {}, False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    menu_active = False  # Fechar o menu
                
                elif event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(options)
                
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(options)
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if selected_option == 5:  # Selecionar Mapa
                        new_map_index = show_map_selection(window, map_index)
                        if new_map_index >= 0:  # Se não cancelou
                            map_index = new_map_index
                    elif selected_option == 6:  # Restaurar padrões
                        margin = MARGIN
                        square_size = SQUARE_SIZE
                        min_speed = MIN_SPEED
                        max_speed = MAX_SPEED
                        lives = 5  # Restaurar vidas para o padrão
                        map_index = 0  # Restaurar mapa para o padrão
                        reset_config = True
                    elif selected_option == 7:  # Voltar ao jogo
                        menu_active = False
                    elif selected_option == 8:  # Sair
                        return False, {}, False
                
                # Ajustar valores com as setas esquerda/direita
                elif event.key == pygame.K_LEFT:
                    if selected_option == 0:  # Tamanho dos quadrados
                        square_size = max(10, square_size - 5)
                    elif selected_option == 1:  # Margem da área
                        margin = max(10, margin - 10)
                    elif selected_option == 2:  # Velocidade mínima
                        min_speed = max(0.5, min_speed - 0.5)
                    elif selected_option == 3:  # Velocidade máxima
                        max_speed = max(min_speed + 0.5, max_speed - 0.5)
                    elif selected_option == 4:  # Vidas dos quadrados
                        lives = max(1, lives - 1)  # Mínimo de 1 vida
                    elif selected_option == 5:  # Navegar entre mapas
                        map_index = (map_index - 1) % len(AVAILABLE_MAPS)
                
                elif event.key == pygame.K_RIGHT:
                    if selected_option == 0:  # Tamanho dos quadrados
                        square_size = min(100, square_size + 5)
                    elif selected_option == 1:  # Margem da área
                        margin = min(min(WIDTH, HEIGHT) // 2 - 50, margin + 10)
                    elif selected_option == 2:  # Velocidade mínima
                        min_speed = min(max_speed - 0.5, min_speed + 0.5)
                    elif selected_option == 3:  # Velocidade máxima
                        max_speed = min(10.0, max_speed + 0.5)
                    elif selected_option == 4:  # Vidas dos quadrados
                        lives = min(10, lives + 1)  # Máximo de 10 vidas
                    elif selected_option == 5:  # Navegar entre mapas
                        map_index = (map_index + 1) % len(AVAILABLE_MAPS)
    
    # Retornar as configurações atualizadas
    return True, {
        'margin': margin,
        'square_size': square_size,
        'min_speed': min_speed,
        'max_speed': max_speed,
        'lives': lives,
        'map_index': map_index  # Incluir índice do mapa nas configurações
    }, reset_config