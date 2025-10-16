# ui_components.py
import pygame
from config import BUTTON_ACTIVE, BUTTON_BG, TEXT, PADDING, BTN_H, font

class Button:
    def __init__(self, rect, text, action=None, is_toggle=False):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.action = action
        self.active = False
        self.is_toggle = is_toggle
    def draw(self, surf, current_algo=None):
        bg_color = BUTTON_ACTIVE if self.active or (current_algo and self.text == current_algo) else BUTTON_BG
        pygame.draw.rect(surf, bg_color, self.rect, border_radius=6)
        txt = font.render(self.text, True, TEXT)
        tw, th = txt.get_size()
        surf.blit(txt, (self.rect.x + (self.rect.width-tw)//2, self.rect.y + (self.rect.height-th)//2))
    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

class DropdownMenu:
    def __init__(self, top_button_rect, top_button_text, items, menu_key):
        self.top_button = Button(top_button_rect, top_button_text, action="toggle_menu")
        self.items = []
        self.is_open = False
        self.menu_key = menu_key
        
        y_start = top_button_rect[1] + top_button_rect[3] + PADDING
        width = top_button_rect[2]
        x = top_button_rect[0]
        
        for i, item_text in enumerate(items):
            rect = (x, y_start + i * (BTN_H + PADDING), width, BTN_H)
            self.items.append(Button(rect, item_text, action=item_text))

    def draw(self, surf, current_algo):
        if self.is_open:
            first_item = self.items[0].rect
            last_item = self.items[-1].rect
            menu_rect = pygame.Rect(
                first_item.x, first_item.y - PADDING, 
                first_item.width, 
                last_item.bottom - first_item.top + PADDING*2
            )
            pygame.draw.rect(surf, BUTTON_BG, menu_rect, border_radius=6)
            
            for item in self.items:
                item.draw(surf, current_algo)
        
        self.top_button.draw(surf)
    
    def handle_click(self, pos):
        if self.top_button.is_clicked(pos):
            self.is_open = not self.is_open
            return self.top_button.action, self.top_button.text
        
        if self.is_open:
            for item in self.items:
                if item.is_clicked(pos) and item.text != "---":
                    self.is_open = False
                    return self.menu_key, item.text
        return None, None