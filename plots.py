from discrete_lens import *
import matplotlib.pyplot as plt
import numpy as np

comparison_thing = radius_circle * (2 / m.sqrt(2))
num_lenses_1 = 24
num_lenses_2 = 18
angle_1 = m.pi / 10
angle_2 = m.pi / 10


def create_lenses_plots(num_lenses):
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


def get_data(lenses_list, angle_given):
    interval = (2 * m.pi) / sample
    for i in range(sample):
        angle = i * interval
        for index_lens in range(len(lenses_list)):

            unit = Vector(1, 0)
            unit.rotate(angle)
            dot = (lenses_list[index_lens].lens_face_dir.x * unit.x) + (
                    lenses_list[index_lens].lens_face_dir.y * unit.y)
            cross = (lenses_list[index_lens].lens_face_dir.x * unit.y) - (
                    lenses_list[index_lens].lens_face_dir.y * unit.x)
            if dot > 1:
                dot = 1
            elif dot < -1:
                dot = -1
            angle_to_lens = m.acos(dot)

            if cross < 0:
                angle_to_lens *= -1

            lenses_list[index_lens].mark_self_area(angle_to_lens, i, angle_given)

    sum_of_lens_faces = []
    angles = []
    for i in range(sample):
        angles.append(i * interval)
        collective_sum = 0
        for index_lens in range(len(lenses_list)):
            collective_sum += lenses_list[index_lens].area_dic[i]

        #if angle_given == angle_2:
        #    if collective_sum < 200:
        #        collective_sum *= (3 / 2)
        #    if collective_sum > 300:
        #        collective_sum *= (3 / 4)

        sum_of_lens_faces.append(collective_sum)

    return sum_of_lens_faces, angles


(sum_of_lens_faces_1, angles_1) = get_data(create_lenses_plots(num_lenses_1), angle_1)
(sum_of_lens_faces_2, angles_2) = get_data(create_lenses_plots(num_lenses_2), angle_2)

percentage_1 = []
percentage_2 = []

for index in range(len(sum_of_lens_faces_1)):
    percentage_1.append(sum_of_lens_faces_1[index] / comparison_thing)
    percentage_2.append(sum_of_lens_faces_2[index] / comparison_thing)


print(sum(percentage_2) / len(percentage_2))
print(sum(percentage_1) / len(percentage_1))

plt.plot(angles_1, percentage_1)
plt.plot(angles_2, percentage_2)
plt.axis([0, 2 * m.pi, 0, 1])
plt.ylabel('Area Covered Compared to Ideal Mirror')
plt.xlabel('Angle in radians')
plt.show()
