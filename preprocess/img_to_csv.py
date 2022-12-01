import csv
import os


def get_filenames(directory):
    """Get every filename in a given directory"""
    filenames = []
    for filename in os.listdir(directory):
        filenames.append(filename)
    return filenames


def extract_coordinates(filenames):
    """Extract the coordinates from the list of filenames.
    The filename is in the format `img_<lat>,<long>.jpg`"""
    coordinates = []

    for filename in filenames:
        latitude = filename.split(',')[0]
        longitude = filename.split(',')[1].replace('.jpg', "")
        coordinates.append((filename, latitude, longitude))

    return coordinates


def main():
    IMAGE_DIR = "D:\\geogussr1"

    # Get the filenames
    filenames = get_filenames(IMAGE_DIR)

    # Extract the coordinates
    coordinates = extract_coordinates(filenames)

    # Write the coordinates to a csv file
    with open("coordinates.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["filename", "latitude", "longitude"])
        writer.writerows(coordinates)


if __name__ == "__main__":
    main()
