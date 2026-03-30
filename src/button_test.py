import pygame
import sys  

from button import Button 

# ---- Test Script ---- 

pygame.init()
screen = pygame.display.set_mode((400,300))
clock = pygame.time.Clock() 

test_btn = Button(125, 120, 150, 50, "Test Button")

while True:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # check for button click 
    if test_btn.handle_event(event):
        print("Button clicked")

    # draw button 
    test_btn.draw(screen)

    pygame.display.flip()
    clock.tick(60)