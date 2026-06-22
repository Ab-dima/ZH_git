

from pprint import pprint


from lesson222 import Rectangle, Square, Circle

rect1 = Rectangle(3,4)

rect2 = Rectangle(12,5)

# print(rect1.get_rect_area(),rect2.get_rect_area())


sq1 = Square(5)
sq2 = Square(7)


cir1 = Circle(5)
cir2 = Circle(7)

# print(sq1.get_square_area(), sq2.get_square_area())


figures = [rect1,sq2,sq1,rect2, cir1,cir2]


for figure in figures:
    print(figure, figure.get_area())
