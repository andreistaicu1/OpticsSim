from tkinter import *
import math as m

focal_length_r = 150
focal_length_small_factor = 10
radial_length_r = 300
sample_size_r = 500
sample_length_r = m.pi / 4
incoming_light_angle = m.pi
factor_sample = 4


class Vector:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def scale(self, scalar):
        self.x *= scalar
        self.y *= scalar

    def rotate(self, angle):
        # possible problem?
        new_x = (self.x * m.cos(angle)) - (self.y * m.sin(angle))
        new_y = (self.x * m.sin(angle)) + (self.y * m.cos(angle))
        self.x = new_x
        self.y = new_y

    def magnitude(self):
        return m.sqrt(m.pow(self.x, 2) + m.pow(self.y, 2))

    def add(self, v):
        return Vector(self.x + v.x, self.y + v.y)


class TorusLens:

    def __init__(self, focal_length, radial_length):
        self.focal_length = focal_length
        self.radial_length = radial_length

    def get_focal_point(self, angle, radius_vector, factor):
        adjust_distance = abs(m.tan(angle)) * self.focal_length
        # adjust_distance = 0

        normal_vector = Vector(radius_vector.x, radius_vector.y)
        normal_vector.rotate(m.pi / 2)
        normal_vector.scale(((factor * adjust_distance) / normal_vector.magnitude()))

        focal_point = Vector(radius_vector.x, radius_vector.y)
        focal_point.scale(1 - (self.focal_length / self.radial_length))

        return focal_point.add(normal_vector)


def draw_circle(canvas_s, color, radius, center):
    (x, y) = center
    start_x = x - radius
    start_y = y - radius
    finish_x = x + radius
    finish_y = y + radius
    return canvas_s.create_oval(start_x, start_y, finish_x, finish_y, outline=color, width=10)


def generate_plot(canvas_s, sample_size, sample_length, torus_lens):
    center = Vector(400, 400)
    split_sphere = sample_size * factor_sample
    incoming_light = Vector(1, 0)
    incoming_light.rotate(incoming_light_angle)

    box = []

    for i in range(split_sphere):

        angle = (m.pi * 2) * (i / split_sphere)
        radial_point = Vector(torus_lens.radial_length, 0)
        radial_point.rotate(angle)
        dot = (radial_point.x * incoming_light.x) + (radial_point.y * incoming_light.y)

        if dot > 0:
            angle_to_lens = m.acos(dot / radial_point.magnitude())
            if angle_to_lens < (m.pi / factor_sample):
                factor = 1

                cross = (radial_point.x * incoming_light.y) - (radial_point.y * incoming_light.x)
                if cross > 0:
                    factor = -1

                focal_point = torus_lens.get_focal_point(angle_to_lens, radial_point, factor)

                box.append(focal_point)

                graph_focal = focal_point.add(center)
                graph_radial = radial_point.add(center)
                draw_circle(canvas_s, 'black', 2, (graph_focal.x, graph_focal.y))
                draw_circle(canvas_s, 'blue', 2, (graph_radial.x, graph_radial.y))
                # canvas_s.create_line(graph_radial.x, graph_radial.y, graph_focal.x, graph_focal.y, fill='red')

        max_magnitude = 0
        square_radius = Vector(0, 0)

        small_focal_vector = Vector(-1 * focal_length_r * (1 / focal_length_small_factor), 0)
        small_focal_vector.rotate(incoming_light_angle)

        new_box = []

        for coordinate in box:

            small_lens_loc = coordinate.add(small_focal_vector)
            new_box.append(small_lens_loc)
            graph_small = small_lens_loc.add(center)
            draw_circle(canvas_s, 'red', 2, (graph_small.x, graph_small.y))

        for coordinate in new_box:

            if coordinate.magnitude() > max_magnitude:
                if coordinate.x > coordinate.y:
                    square_radius = Vector(coordinate.x, coordinate.x)
                else:
                    square_radius = Vector(coordinate.y, coordinate.y)
                max_magnitude = coordinate.magnitude()

        end_point = Vector(-1 * square_radius.x, -1 * square_radius.y)

        square = [square_radius, end_point]
        draw_square = []

        for item in square:
            draw_square.append(item.add(center))

        canvas_s.create_oval(draw_square[0].x, draw_square[0].y, draw_square[1].x, draw_square[1].y, outline='red')


if __name__ == '__main__':
    root = Tk()
    root.geometry('800x800')
    c = Canvas(root, width=800, height=800)
    c.pack()

    lens = TorusLens(focal_length_r, radial_length_r)
    draw_circle(c, 'black', radial_length_r, (400, 400))
    generate_plot(c, sample_size_r, sample_length_r, lens)

    root.mainloop()
