import numpy as np
from shapely.geometry import Point


def create_axes_based_on_3_points_in_plane(
    p1: Point, p2: Point, p3: Point
) -> tuple[
    tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]
]:
    # The three points define a plane, we can use them to create axes
    # v1 is the vector from p1 to p2
    # v2 is the vector from p1 to p3
    # v3 is the normal vector to the plane defined by p1, p2, p3
    v1 = np.array([p2.x - p1.x, p2.y - p1.y, p2.z - p1.z])
    v2 = np.array([p3.x - p1.x, p3.y - p1.y, p3.z - p1.z])
    v3 = np.cross(v1, v2)
    v3 = v3 / np.linalg.norm(v3)

    return (tuple(v1), tuple(v2), tuple(v3))


if __name__ == "__main__":
    p1 = Point(0, 0, 0)
    p2 = Point(2, 1, 0)
    p3 = Point(0, 0, 1)

    v1, v2, v3 = create_axes_based_on_3_points_in_plane(p1, p2, p3)
    print("v1:", f"{v1[0]:.2f}", f"{v1[1]:.2f}", f"{v1[2]:.2f}")
    print("v2:", f"{v2[0]:.2f}", f"{v2[1]:.2f}", f"{v2[2]:.2f}")
    print("v3:", f"{v3[0]:.2f}", f"{v3[1]:.2f}", f"{v3[2]:.2f}")

    print("v2:", v2)
    print("v3:", v3)
    print("stopp")
