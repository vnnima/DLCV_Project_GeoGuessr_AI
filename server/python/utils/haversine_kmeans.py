import torch


class HaversineKMeans:
    def __init__(self) -> None:
        pass

    @staticmethod
    def CompMeans(Points, Weights):
        """
        Calls the function recursively, always calculating the midpoint between two points. Either:
        - Between the first to points
        - Between the midpoint of the first K-1 points and (1/K) in the direction of the K-th point.

        Takes the Points in Radians (use torch.deg2rad beforehand)
        """
        K = Points.size(0)
        if (K == 2):
            # Endcase of recursion
            point, w = HaversineKMeans.MidPoint(Points[1:2, :], Points[0:1, :], Weights[1], Weights[0])
            return point, w
        else:
            # Standard case of recursion
            fPoint, fW = HaversineKMeans.CompMeans(Points[1:, :], Weights[1:])
            point, w = HaversineKMeans.MidPoint(fPoint, Points[0:1, :], fW, Weights[0])
            return point, w

    @staticmethod
    def MidPoint(x, y, w_x, w_y) -> torch.tensor:
        """
        x and y as Radians.

        Implements the calculation of an intermediate point from https://www.movable-type.co.uk/scripts/latlong.html .
        """
        phi_1 = x[:, 0]
        phi_2 = y[:, 0]
        lambda_1 = x[:, 1]
        lambda_2 = y[:, 1]
        f = w_y / ((w_x + w_y))

        delta = HaversineKMeans.Haversine(x, y)
        if (delta == 0):
            # The two points are the same
            return x

        a = torch.sin((1 - f) * delta) / torch.sin(delta)
        b = torch.sin(f * delta) / torch.sin(delta)

        new_x = a * torch.cos(phi_1) * torch.cos(lambda_1) + b * torch.cos(phi_2) * torch.cos(lambda_2)
        new_y = a * torch.cos(phi_1) * torch.sin(lambda_1) + b * torch.cos(phi_2) * torch.sin(lambda_2)
        z = a * torch.sin(phi_1) + b * torch.sin(phi_2)

        phi_i = torch.atan2(z, torch.sqrt(torch.pow(new_x, 2) + torch.pow(new_y, 2)))
        lambda_i = torch.atan2(new_y, new_x)

        res = torch.cat((phi_i, lambda_i), 0)[None, :]  # Add additional dimension to fit other values dimensions
        return res, w_x + w_y

    @staticmethod
    def Haversine(x, y):
        """
        Computes the Haversine distance of two points x and y.
        """
        return 2 * torch.arcsin(torch.sqrt(torch.pow(
            torch.sin((x[:, 0] - y[:, 0]) / 2), 2) +
            torch.cos(x[:, 0]) * torch.cos(y[:, 0]) * torch.pow(torch.sin((x[:, 1] - y[:, 1]) / 2), 2)))


if __name__ == "__main__":
    hvk = HaversineKMeans()
    points = torch.deg2rad(torch.tensor([(40.7128, 74.0060), (62.289834, 108.169635), (35.6895, 139.6917)]))
    weights = [1 / 3, 1 / 3, 1 / 3]
    weights = [1 / 10, 8 / 10, 1 / 10]
    midpoint = hvk.CompMeans(points, weights)
    print(midpoint)
    print(torch.rad2deg(midpoint[0])[0])
