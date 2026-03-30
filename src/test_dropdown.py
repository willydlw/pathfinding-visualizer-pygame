import pygame 
import sys 

from header import Header

def main():
    pygame.init() 
    screen = pygame.display.set_mode((600,400))
    clock = pygame.time.Clock() 

    header = Header(600, 50)
    last_event_text = "None"

    while True:
        screen.fill((30, 30, 30))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit() 

        result = header.handle_events(event)
        if result:
            last_event_text = result 

        # Display selection status at bottom
        font = pygame.font.SysFont('Arial', 20)
        status = font.render(f"Status: {last_event_text}", True, (0, 255, 0))
        screen.blit(status, (20, 360))
        

        header.draw(screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()