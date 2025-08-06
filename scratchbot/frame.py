
import numpy as np

def create_frame_old(normal,origin):
    # Normalize the normal vector
    z_axis = np.array(normal)
    z_axis = z_axis / np.linalg.norm(z_axis)

    # Generate an arbitrary orthogonal vector for the X-axis
    temp_vector = np.array([1, 0, 0]) if abs(z_axis[0]) < 0.9 else np.array([0, 1, 0])
    x_axis = np.cross(temp_vector, z_axis)
    x_axis = x_axis / np.linalg.norm(x_axis)

    # Generate the Y-axis as orthogonal to both Z and X
    y_axis = np.cross(z_axis, x_axis)

    # Construct the rotation matrix
    rotation_matrix = np.array([x_axis, y_axis, z_axis]).T

    # Build the homogeneous transformation matrix
    frame = np.eye(4)
    frame[:3, :3] = rotation_matrix  # Set rotation
    frame[:3, 3] = origin            # Set translation

    return frame


def transform_to_base_frame(frame_matrix, point_in_frame):
    """
    Transforms a point in the custom frame to the robot's base frame.
    """
    point_in_frame_homogeneous = np.append(point_in_frame, 1)  # Convert to homogeneous coordinates
    point_in_base = np.dot(frame_matrix, point_in_frame_homogeneous)
    return point_in_base[:3]  # Return only the XYZ part

def create_frame(normal, origin):
    # Normalize the normal vector to get the Z-axis
    z_axis = np.array(normal)
    z_axis = z_axis / np.linalg.norm(z_axis)

    # Choose an arbitrary vector to generate the X-axis
    # If the normal is not aligned with the X-axis, we use (1, 0, 0)
    temp_vector = np.array([1, 0, 0]) if abs(z_axis[0]) < 0.9 else np.array([0, 1, 0])
    
    # Compute the X-axis (orthogonal to the Z-axis)
    x_axis = np.cross(temp_vector, z_axis)
    x_axis = x_axis / np.linalg.norm(x_axis)

    # Compute the Y-axis (orthogonal to both Z and X)
    y_axis = np.cross(z_axis, x_axis)

    # Construct the rotation matrix (X, Y, Z axes)
    rotation_matrix = np.array([x_axis, y_axis, z_axis]).T

    # Create the homogeneous transformation matrix
    frame = np.eye(4)
    frame[:3, :3] = rotation_matrix  # Rotation matrix in the top-left 3x3 part
    frame[:3, 3] = origin  # Translation vector in the last column

    return frame


def computeNormal(p1, p2, p3):
    """
    Computes the normal vector of a plane defined by three points.
    Assumes all points are distinct and not collinear.
    :param p1: [x1, y1, z1] - First point
    :param p2: [x2, y2, z2] - Second point
    :param p3: [x3, y3, z3] - Third point
    :return: [nx, ny, nz] - Normalized normal vector
    """
    # Convert points to numpy arrays
    p1, p2, p3 = np.array(p1), np.array(p2), np.array(p3)

    # Compute two vectors in the plane
    v1 = p2 - p1
    v2 = p3 - p1

    # Compute the cross product to find the normal
    normal = np.cross(v1, v2)

    # Normalize the normal vector
    normal = normal / np.linalg.norm(normal)

    return normal



def getTranslationVector(p1,p2,p3):
	P1 = np.array(p1)
	P2 = np.array(p2)
	P3 = np.array(p3)

	# Step 2: Find vectors on the second plane
	v1 = P2 - P1
	v2 = P3 - P1

	# Find the normal vector to the plane (cross product of v1 and v2)
	normal = np.cross(v1, v2)
	normal = normal / np.linalg.norm(normal)  # Normalize the normal vector

	# Step 3: Define the rotation matrix
	# We want to rotate the original z-axis (0, 0, 1) to align with the normal vector
	z_axis = np.array([0, 0, 1])

	# Use the cross product to find the rotation axis and angle
	rotation_axis = np.cross(z_axis, normal)
	rotation_axis = rotation_axis / np.linalg.norm(rotation_axis)  # Normalize the rotation axis

	# Calculate the angle between the z-axis and the normal
	angle = np.arccos(np.dot(z_axis, normal))

	# Construct the rotation matrix using Rodrigues' rotation formula
	K = np.array([[0, -rotation_axis[2], rotation_axis[1]],
		[rotation_axis[2], 0, -rotation_axis[0]],
		[-rotation_axis[1], rotation_axis[0], 0]])

	R = np.eye(3) + np.sin(angle) * K + (1 - np.cos(angle)) * np.outer(rotation_axis, rotation_axis)

	# Step 4: Define the translation vector (move origin of original plane to P1)
	translation = P1

	return R, translation

def transform_point(point,R, translation):
	point = np.array(point)
	rotated_point = R.dot(point)  # Apply the rotation
	translated_point = rotated_point + translation  # Apply the translation
	return translated_point



def rotation_matrix(axis, angle):
    # Normalize the rotation axis
    axis = axis / np.linalg.norm(axis)
    
    # Using the Rodrigues' rotation formula to create the rotation matrix
    cos_theta = np.cos(angle)
    sin_theta = np.sin(angle)
    dot = np.dot(axis, axis)
    
    # Cross-product matrix of the axis
    cross_product_matrix = np.array([
        [0, -axis[2], axis[1]],
        [axis[2], 0, -axis[0]],
        [-axis[1], axis[0], 0]
    ])
    
    # Rotation matrix formula
    R = cos_theta * np.eye(3) + sin_theta * cross_product_matrix + (1 - cos_theta) * np.outer(axis, axis)
    return R


def create_rotation_matrix_for_plane(p1, p2, p3):
    # Define the base plane normal (for the XY plane: (0, 0, 1))
    base_normal = np.array([0, 0, 1])
    
    # Calculate the normal vector of the plane defined by p1, p2, p3
    plane_normal = computeNormal(p1, p2, p3)
    
    # Compute the axis of rotation (cross product of the base normal and the plane normal)
    rotation_axis = np.cross(base_normal, plane_normal)
    
    # Compute the angle of rotation (arccos of the dot product between the normals)
    angle = np.arccos(np.dot(base_normal, plane_normal))
    
    # If the axis is very small (i.e., the normals are parallel), no rotation is needed
    if np.linalg.norm(rotation_axis) < 1e-6:
        return np.eye(3)
    
    # Create the rotation matrix
    R = rotation_matrix(rotation_axis, angle)
    return R

def apply_rotation_matrix(rotation_matrix, point):
    """
    Apply the rotation matrix to the given point (x, y, z).
    """
    point_vector = np.array(point)  # Convert point to numpy array
    rotated_point = np.dot(rotation_matrix, point_vector)  # Apply the rotation
    return rotated_point