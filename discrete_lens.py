from light import *
import xlwt

lens_count = 20
angle_accepted = m.pi / 8
sample = 400
radius_circle = 350
lens_height = 1
focal_length_discrete = 250
size = Vector(800, 800)


def can_consider(angle):
    return (angle_accepted > angle >= 0) or ((-1 * angle_accepted) < angle <= 0)


class Lens:

    def __init__(self, area, focal_length, edge_1, edge_2):
        self.area = area
        self.focal_length = focal_length
        self.edge_1 = edge_1
        self.edge_2 = edge_2

        edge_2.scale(-1)
        lens_axis_v = edge_1.add(edge_2)
        self.lens_axis = Vector(lens_axis_v.x, lens_axis_v.y)
        edge_2.scale(-1)

        self.lens_face_dir = lens_axis_v
        self.lens_face_dir.rotate(-1 * m.pi / 2)
        self.lens_face_dir.scale(1 / lens_axis_v.magnitude())

        center_lens = edge_2.add(Vector((1 / 2) * self.lens_axis.x, (1 / 2) * self.lens_axis.y))
        self.center_lens = center_lens
        self.focal_point = center_lens.add(Vector(self.lens_face_dir.x * self.focal_length,
                                                  self.lens_face_dir.y * self.focal_length))

    def incident_area(self, angle):
        return m.cos(angle) * self.area

    def calculate_focal_point_adjust(self, angle):
        change = self.focal_length * (m.tan(angle))
        focal_point_v = Vector(self.lens_axis.x, self.lens_axis.y)
        focal_point_v.scale(change / focal_point_v.magnitude())
        return focal_point_v

    def mark_area(self, lens_num, angle, sheet, angle_index):
        if not can_consider(angle):
            sheet.write(angle_index + 1, lens_num + 1, '0')
            return

        area = self.incident_area(angle)
        sheet.write(angle_index + 1, lens_num + 1, str(area))


def fill_excel_sheet(lenses_list):
    work = xlwt.Workbook()
    sheet1 = work.add_sheet('First sample')

    interval = (2 * m.pi) / sample
    for i in range(sample):
        angle = i * interval
        sheet1.write(i + 1, 0, str(angle))
        for index_lens in range(len(lenses_list)):

            unit = Vector(1, 0)
            unit.rotate(angle)
            dot = (lenses_list[index_lens].lens_face_dir.x * unit.x) + (lenses_list[index_lens].lens_face_dir.y * unit.y)
            cross = (lenses_list[index_lens].lens_face_dir.x * unit.y) - (lenses_list[index_lens].lens_face_dir.y * unit.x)
            if dot > 1:
                dot = 1
            elif dot < -1:
                dot = -1
            angle_to_lens = m.acos(dot)

            if cross < 0:
                angle_to_lens *= -1

            lenses_list[index_lens].mark_area(index_lens, angle_to_lens, sheet1, i)

    work.save('first_sample_data.xls')


def create_lenses(num_lenses):
    if num_lenses < 3:
        return

    lenses_list = []

    interval = (2 * m.pi) / num_lenses
    for i in range(num_lenses):
        first_edge_rot = i * interval
        second_edge_rot = ((i + 1) % num_lenses) * interval

        radius = Vector(1, 0)
        radius.scale(radius_circle)

        edge_1 = Vector(radius.x, radius.y)
        edge_1.rotate(first_edge_rot)
        edge_1 = edge_1.add(Vector((1 / 2) * size.x, (1 / 2) * size.y))

        edge_2 = Vector(radius.x, radius.y)
        edge_2.rotate(second_edge_rot)
        edge_2 = edge_2.add(Vector((1 / 2) * size.x, (1 / 2) * size.y))

        axis = edge_1.add(Vector(-1 * edge_2.x, -1 * edge_2.y))
        width = axis.magnitude()

        single_lens = Lens(lens_height * width, focal_length_discrete, edge_1, edge_2)
        lenses_list.append(single_lens)

    return lenses_list


def draw_lenses(list_lenses, canvas_s):
    for lens_index in range(len(list_lenses)):
        item = list_lenses[lens_index]
        canvas_s.create_line(item.edge_1.x, item.edge_1.y, item.edge_2.x, item.edge_2.y, fill='black')
        draw_circle(canvas_s, 'black', 2, (item.focal_point.x, item.focal_point.y))


def get_dict_focal_points(list_lenses):
    focal_dict = {}
    interval = (2 * m.pi) / sample

    for i in range(sample):
        angle = i * interval
        values = []
        for single_lens in list_lenses:

            unit = Vector(1, 0)
            unit.rotate(angle)
            dot = (single_lens.lens_face_dir.x * unit.x) + (single_lens.lens_face_dir.y * unit.y)
            cross = (single_lens.lens_face_dir.x * unit.y) - (single_lens.lens_face_dir.y * unit.x)
            if dot > 1:
                dot = 1
            elif dot < -1:
                dot = -1
            angle_to_lens = m.acos(dot)

            if cross < 0:
                angle_to_lens *= -1

            if can_consider(angle_to_lens):
                focal_point_move = single_lens.calculate_focal_point_adjust(angle_to_lens)
                true_focal = single_lens.focal_point.add(focal_point_move)
                values.append(true_focal)
            else:
                values.append(Vector(0, 0))

        focal_dict[i] = values

    return focal_dict


def key_handler(event):
    """Handle key presses."""
    global handle_list
    global current_angle

    interval = (2 * m.pi) / sample

    if event.keysym == 'q':
        quit()

    if event.keysym == 'a':
        for thing in handle_list:
            c.delete(thing)
        handle_list = []
        new_angle = (current_angle + 1) % sample

        unit = Vector(1, 0)
        unit.rotate(new_angle * interval)
        unit.scale(-1 * radius_circle - 30)
        unit = unit.add(Vector(400, 400))
        handle_list.append(c.create_line(400, 400, unit.x, unit.y, fill='blue'))

        points = focal_point_dict[new_angle]
        for item in points:
            handle_list.append(draw_circle(c, 'red', 2, (item.x, item.y)))
        current_angle = new_angle

    if event.keysym == 'd':
        for thing in handle_list:
            c.delete(thing)
        handle_list = []
        new_angle = current_angle - 1
        if new_angle < 0:
            new_angle = sample - 1

        unit = Vector(1, 0)
        unit.rotate(new_angle * interval)
        unit.scale(-1 * radius_circle - 30)
        unit = unit.add(Vector(400, 400))
        handle_list.append(c.create_line(400, 400, unit.x, unit.y, fill='blue'))

        points = focal_point_dict[new_angle]
        for item in points:
            handle_list.append(draw_circle(c, 'red', 2, (item.x, item.y)))
        current_angle = new_angle


if __name__ == '__main__':
    root = Tk()
    root.geometry('800x800')
    c = Canvas(root, width=800, height=800)
    c.pack()

    fill_excel_sheet(create_lenses(lens_count))

    lenses = create_lenses(lens_count)
    draw_lenses(lenses, c)
    focal_point_dict = get_dict_focal_points(lenses)
    handle_list = []
    root.bind('<q>', key_handler)
    root.bind('<a>', key_handler)
    root.bind('<d>', key_handler)
    current_angle = 0
    root.mainloop()
