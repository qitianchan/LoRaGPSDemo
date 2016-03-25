from __future__ import division
import numpy as np
c = 3 * 10 ** 8
CONST = 6371 * np.pi / 180


def get_position(four_node_data):
    """
    get position for the node
    :param four_node_data: a four element list of node data contains (longitude, latitude, time)
    :return:  tuple (longitude, latitude)
    >>> node_datas = [(23.556, 113.58, 1.1339702e-08),(23.548, 113.5728.1879206999999998e-09), (23.55, 113.57, 7.4129951e-09), (23.56, 113.578, 1.10202e-08)]
    >>> get_position(node_datas)
    >>>(23.549999994309413, 113.54999933765345)
    """
    assert isinstance(four_node_data, list), 'argument should be a list'
    assert len(four_node_data) == 4, 'argument should have 4 element'
    x1 = 0
    y1 = 0
    br = np.array(four_node_data[0][:2])
    b1 = np.array(four_node_data[1][:2])
    b2 = np.array(four_node_data[2][:2])
    b3 = np.array(four_node_data[3][:2])
    b1_c = CONST * (b1 - br)
    b2_c = CONST * (b2 - br)
    b3_c = CONST * (b3 - br)
    X = np.array([b1_c[0], b2_c[0], b3_c[0]])
    Y = np.array([b1_c[1], b2_c[1], b3_c[1]])

    t1 = float(four_node_data[0][2])
    T = np.array([
             four_node_data[1][2],
             four_node_data[2][2],
             four_node_data[3][2]
    ])

    A = -2 * np.array([X - x1, Y - y1, (T - t1) * c])
    B = x1**2 + y1**2 - (X**2) - (Y**2) + (((T-t1)*c)**2)
    res = np.dot(B, np.linalg.inv(A))
    n_cr = res[:2]
    n_r = br + n_cr / CONST
    return tuple(n_r)

if __name__ == '__main__':
    node_datas = [(23.556, 113.58, 1.1339702e-08), (23.548, 113.572, 8.1879206999999998e-09),
                  (23.55, 113.57, 7.4129951e-09), (23.56, 113.578, 1.10202e-08)]
    print(get_position(node_datas))

