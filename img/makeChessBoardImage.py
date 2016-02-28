#!/usr/bin/env python

# Make and save an n x n chessboard using PIL.
def makeChessBoardImage(args, n=8, pixel_width=512):

    if len(args) == 1:
        print "Provide an output filename argument."
        return

    # Define light and dark square colors.
    light = (255, 235, 205)
    dark = (139, 125, 107)

    # Return x or y coordinate the square at col or row i
    def pixelCoordinate(i):
        return i * pixel_width / n

    # Return corners of a square for creating a PIL drawing.
    def squareCorners(i, j):
        return map(pixelCoordinate, [i, j, i+1, j+1])

    # Fill in dark square color as background.
    image = Image.new("RGB", (pixel_width, pixel_width), dark)

    # Find all light squares
    light_squares = (squareCorners(i, j)
                     for i_begin, j in zip(cycle((0, 1)), range(n))
                     for i in range(i_begin, n, 2))

    # Color light squares.
    for s in light_squares:
        ImageDraw.Draw(image).rectangle(s, fill=light)

    # Save the image.
    print "Saving chess board image to " + args[1]
    image.save(args[1])

if __name__ == '__main__':
    import sys
    from PIL import Image, ImageDraw, ImageColor
    from itertools import cycle
    makeChessBoardImage(sys.argv)
