"""Simple inverse kinematics for the two-joint arm."""

import math


UPPER_ARM_LENGTH = 0.35
ELBOW_TO_GRIP_CENTER = 0.43
SHOULDER_HEIGHT = 0.12

SHOULDER_LIMITS = (-1.57, 1.57)
ELBOW_LIMITS = (-2.0, 2.0)


def inverse_kinematics(target_x, target_z, elbow_branch=-1):
    """
    Return shoulder and elbow angles in radians for an X-Z target.

    The target is the center between the gripper fingers, in base_link
    coordinates. elbow_branch selects one of the two possible arm bends.
    """
    if elbow_branch not in (-1, 1):
        raise ValueError('elbow_branch must be -1 or 1')

    x = target_x
    z = target_z - SHOULDER_HEIGHT

    distance_squared = x * x + z * z
    cosine_elbow = (
        distance_squared
        - UPPER_ARM_LENGTH**2
        - ELBOW_TO_GRIP_CENTER**2
    ) / (2.0 * UPPER_ARM_LENGTH * ELBOW_TO_GRIP_CENTER)

    if cosine_elbow < -1.0 or cosine_elbow > 1.0:
        raise ValueError("Target is outside the arm's reachable range")

    planar_elbow = elbow_branch * math.acos(cosine_elbow)
    planar_shoulder = math.atan2(z, x) - math.atan2(
        ELBOW_TO_GRIP_CENTER * math.sin(planar_elbow),
        UPPER_ARM_LENGTH + ELBOW_TO_GRIP_CENTER * math.cos(planar_elbow),
    )

    # The URDF joints rotate around +Y, so their signs are opposite
    # to the standard planar X-Z angles above.
    shoulder_angle = -planar_shoulder
    elbow_angle = -planar_elbow

    if not SHOULDER_LIMITS[0] <= shoulder_angle <= SHOULDER_LIMITS[1]:
        raise ValueError('Calculated shoulder angle exceeds its URDF limits')

    if not ELBOW_LIMITS[0] <= elbow_angle <= ELBOW_LIMITS[1]:
        raise ValueError('Calculated elbow angle exceeds its URDF limits')

    return shoulder_angle, elbow_angle
