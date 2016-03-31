from __future__ import division
import numpy as np
c = 299792458.0
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


def simulate_position(target, stations):
    """
    preserve target position and base station position to simulate the position we calculate out
    :param target: target position (23.55, 113.55)
    :param stations:[(23.556, 113.58), (23.548, 113.572), (23.55, 113.57), (23.56, 113.578)]
    :return: position (?, ?),
    """
    record = []
    n = np.array(target)
    br = np.array(stations[0])
    b1 = np.array(stations[1])
    b2 = np.array(stations[2])
    b3 = np.array(stations[3])

    x1 = 0
    y1 = 0
    b0 = np.array([x1, y1])

    n_c = CONST * (n - br) * 1000
    b1_c = CONST * (b1 - br) * 1000
    b2_c = CONST * (b2 - br) * 1000
    b3_c = CONST * (b3 - br) * 1000

    X = np.array([b1_c[0], b2_c[0], b3_c[0]])
    Y = np.array([b1_c[1], b2_c[1], b3_c[1]])
    b_c = np.transpose(np.array([X, Y]))

    x = n_c[0]
    y = n_c[1]

    t = np.sqrt(((X - x)**2 + (Y - y)**2)) / c
    t1 = np.sqrt(((x1 - x)**2 + (y1 - y)**2)) / c

    A = -2 * np.transpose(np.array([X - x1, Y - y1, (t - t1)*c]))
    B = x1**2 + y1**2 - X**2 - Y**2 + ((t - t1)*c)**2
    results = np.dot(np.linalg.inv(A), B)

    mu = 0
    sigma = 150
    noise = np.random.normal(mu, sigma, 2)
    n_cr = np.transpose(results[0:2]) + noise
    # n_cr = np.transpose(results[0:2]) + 20

    delta = np.array([0, 0])
    # delta = np.zeros((2, 1))
    Q = (0.5 * np.eye(3) + 0.5*np.ones((3, 3))) * (1.5**2)

    for i in xrange(200):
        n_cr =n_cr + delta
        record.append(np.sqrt(np.sum(np.abs(n_c - n_cr)**2)))
        r0 = np.sqrt(np.sum(n_cr**2))
        r1 = np.sqrt((n_cr[0] - X[0])**2 + (n_cr[1] - Y[0])**2)
        r2 = np.sqrt((n_cr[0] - X[1])**2 + (n_cr[1] - Y[1])**2)
        r3 = np.sqrt((n_cr[0] - X[2])**2 + (n_cr[1] - Y[2])**2)

        R = np.array([r1, r2, r3])
        h = c*(np.transpose(t) - t1) - (R - r0)
        a = (b0-n_cr) / r0
        b = np.array([[1, 1, 1]])
        g1 = np.dot((np.array([(b0 - n_cr)/r0])).T, np.array([[1, 1, 1]]))
        g2 = (b_c - np.dot( np.array([n_cr]).T, np.array([[1, 1, 1]])).T) / np.dot(np.array([R]).T, np.array([[1, 1]]))
        G = g1.T - g2

        delta = np.dot(np.dot(np.dot(np.linalg.inv(np.dot(np.dot(G.T, Q), G)), G.T), np.linalg.inv(Q)), h)
        D = np.sum(np.abs(delta))

        if D <= 0.02 and D >= 0.0000001:
            break

    n_cr = n_cr + np.transpose(delta)
    error = np.sqrt(np.sum(np.abs(n_c - n_cr)**2))
    n_ll = br + (n_cr * 180 /(6371*np.pi * 1000))

    return n_ll, error, record, [n_c[0], n_c[1]]


if __name__ == '__main__':
    # node_datas = [(23.556, 113.58, 1.1339702e-08), (23.548, 113.572, 8.1879206999999998e-09),
    #               (23.55, 113.57, 7.4129951e-09), (23.56, 113.578, 1.10202e-08)]
    # print(get_position(node_datas))

    target = [23.55, 113.55]
    station = [[23.556, 113.58], [23.548, 113.572], [23.55, 113.57], [23.56, 113.578]]
    res = simulate_position(target, station)
    print(res)