import pygame as pg
import os, sys

def main():
    # initialize
    pg.init()
    resolution = 600, 200
    screen = pg.display.set_mode(resolution)

    ##    pg.mouse.set_cursor(*pg.cursors.diamond)

    fg = 250, 240, 230
    bg = 5, 5, 5
    wincolor = 40, 40, 90

    # fill background
    screen.fill(wincolor)

    # load font, prepare values
    root_dir = os.path.dirname(__file__)
    font_path = os.path.join(root_dir, "fonts", "game_over.ttf")
    font = pg.font.Font(font_path, 150)
    text = "Ready?"
    size = font.size(text)


    # no AA, transparancy, underline
    font.set_underline(0)
    ren = font.render(text, 0, fg)
    screen.blit(ren, (40, -60 + size[1]))
    #font.set_underline(0)


    # show the surface and await user quit
    pg.display.flip()
    while True:
        # use event.wait to keep from polling 100% cpu
        if pg.event.wait().type in (pg.QUIT, pg.KEYDOWN, pg.MOUSEBUTTONDOWN):
            break
    pg.quit()

if __name__ == "__main__":
    main()