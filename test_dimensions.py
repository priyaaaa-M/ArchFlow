import imageio
import numpy as np
from PIL import Image
import io

def test_dimensions():
    print("Testing imageio.mimsave with different dimensions...")
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((120, 120, 3), dtype=np.uint8)
    
    try:
        imageio.mimsave("test_fail.gif", [img1, img2], duration=500)
        print("SUCCESS (Surprising!)")
    except Exception as e:
        print(f"FAILED as expected: {e}")

if __name__ == "__main__":
    test_dimensions()
