import numpy as np

def conv(image, kernel):
    """ An implementation of convolution filter.

    This function uses element-wise multiplication and np.sum()
    to efficiently compute weighted sum of neighborhood at each
    pixel.

    Args -
        image: numpy array of shape (Hi, Wi).
        kernel: numpy array of shape (Hk, Wk).

    Returns -
        out: numpy array of shape (Hi, Wi).
    """
    Hi, Wi = image.shape
    Hk, Wk = kernel.shape
    out = np.zeros((Hi, Wi))

    # For this assignment, we will use edge values to pad the images.
    # Zero padding will make derivatives at the image boundary very big,
    # whereas we want to ignore the edges at the boundary.
    pad_width0 = Hk // 2
    pad_width1 = Wk // 2
    pad_width = ((pad_width0,pad_width0),(pad_width1,pad_width1))
    padded = np.pad(image, pad_width, mode='edge')

    ### YOUR CODE HERE
    for x in range(Hi):
       for y in range (Wi):
           region = padded[x: x + Hk, y: y + Wk]
           out [x,y] = np.sum(region*kernel)
       
    ### END YOUR CODE

    return out

def gaussian_kernel(size, sigma):
    """ Implementation of Gaussian Kernel.

    This function follows the gaussian kernel formula,
    and creates a kernel matrix.

    Hints:
    - Use np.pi and np.exp to compute pi and exp.

    Args:
        size: int of the size of output matrix.
        sigma: float of sigma to calculate kernel.

    Returns:
        kernel: numpy array of shape (size, size).
    """

    kernel = np.zeros((size, size))

    ### YOUR CODE HERE
    
      # Calculate the center of the kernel
    center = size // 2

    # Calculate the constant factor in the Gaussian formula
    constant = 1/(2 * np.pi * sigma**2)

    # Fill in the kernel matrix using the Gaussian formula
    for x in range(size):
        for y in range(size):
            # Calculate the distance from the center
            distance = -1*(((x - center)**2 + (y - center)**2)/(2 * sigma**2))
            # Compute the Gaussian value for this position
            kernel[x, y] =constant * np.exp(distance)
    
    ### END YOUR CODE

    return kernel

def partial_x(image):
    """ Computes partial x-derivative of input img.

    Hints:
        - You may use the conv function in defined in this file.

    Args:
        image: numpy array of shape (H, W).
    Returns:
        out: x-derivative image.
    """

    out = None

    ### YOUR CODE HERE
    
    dx_matrix = np.array([[-1/2, 0, 1/2]])
    out = conv(image, dx_matrix)
    
    ### END YOUR CODE

    return out

def partial_y(image):
    """ Computes partial y-derivative of input img.

    Hints:
        - You may use the conv function in defined in this file.

    Args:
        image: numpy array of shape (H, W).
    Returns:
        out: y-derivative image.
    """

    out = None

    ### YOUR CODE HERE
    
    dy_matrix = np.array([[-1/2], [0], [1/2]])
    out = conv(image, dy_matrix)
    
    ### END YOUR CODE

    return out

def gradient(image):
    """ Returns gradient magnitude and direction of input img.

    Args:
        image: Grayscale image. Numpy array of shape (H, W).

    Returns:
        G: Magnitude of gradient at each pixel in img.
            Numpy array of shape (H, W).
        theta: Direction(in degrees, 0 <= theta < 360) of gradient
            at each pixel in img. Numpy array of shape (H, W).

    Hints:
        - Use np.sqrt and np.arctan2 to calculate square root and arctan
    """
    G = np.zeros(image.shape)
    theta = np.zeros(image.shape)

    ### YOUR CODE HERE
    
    Gx = partial_x(image)
    Gy = partial_y(image)
    G = Gx**2 + Gy**2
    G = np.sqrt(G)
    theta = np.arctan(Gy,Gx)\
    
    #converting theta to degrees
    theta = ((theta*180) /  np.pi) % 360
    ### END YOUR CODE

    return G, theta

def non_maximum_suppression(G, theta):
    """ Performs non-maximum suppression.

    This function performs non-maximum suppression along the direction
    of gradient (theta) on the gradient magnitude image (G).

    Args:
        G: gradient magnitude image with shape of (H, W).
        theta: direction of gradients with shape of (H, W).

    Returns:
        out: non-maxima suppressed image.
    """
    H, W = G.shape
    out = np.zeros((H, W))

    # Round the gradient direction to the nearest 45 degrees
    theta = np.floor((theta + 22.5) / 45) * 45

    ### BEGIN YOUR CODE
    #-- setting an array to suitable pos comparison
    ang = np.zeros_like(theta, dtype=[('x', int), ('y', int)])
    ang[(theta == 0) | (theta == 0+180) | (theta == 360)] = (0, 1)
    ang[(theta == 45) | (theta == 45+180)] = (1, 1)
    ang[(theta == 90) | (theta == 90+180)] = (1,0)
    ang[(theta == 135) | (theta == 135+180)] = (-1, 1)

    padding = 1 #padding to avoid bound errors
    pad = np.pad(G, ((padding, padding), (padding, padding)), mode='constant')

    condition1 = (ang['x'] == 0) & (ang['y'] == 1)
    condition2 = (ang['x'] == 1) & (ang['y'] == 0)
    condition3 = (ang['x'] == 1) & (ang['y'] == 1)
    condition4 = (ang['x'] == -1) & (ang['y'] == 1)
    mask = (condition1 | condition2 | condition3 | condition4)
    x_indices, y_indices = np.where(mask)
    # Perform the comparison to set values in 'G' to 0 if condition not satisfied
    for x, y in zip(x_indices, y_indices):
        if (G[x, y] >= pad[x+1 + ang[x, y][0], y+1 + ang[x, y][1]]) and (G[x, y] >= pad[x+1 - ang[x, y][0], y+1 - ang[x, y][1]]):
            out[x, y] = G[x, y]
        else:
            out[x, y] = 0
    ### END YOUR CODE

    return out


def double_thresholding(img, high, low):
    """
    Args:
        img: numpy array of shape (H, W) representing NMS edge response.
        high: high threshold(float) for strong edges.
        low: low threshold(float) for weak edges.

    Returns:
        strong_edges: Boolean array which represents strong edges.
            Strong edeges are the pixels with the values greater than
            the higher threshold.
        weak_edges: Boolean array representing weak edges.
            Weak edges are the pixels with the values smaller or equal to the
            higher threshold and greater than the lower threshold.
    """

    strong_edges = np.zeros(img.shape, dtype=bool)
    weak_edges = np.zeros(img.shape, dtype=bool)

    ### YOUR CODE HERE
    strong_edges = img > high
    weak_edges = np.logical_and(img <= high, img > low)
    ### END YOUR CODE

    return strong_edges, weak_edges


def get_neighbors(y, x, H, W):
    """ Return indices of valid neighbors of (y, x).

    Return indices of all the valid neighbors of (y, x) in an array of
    shape (H, W). An index (i, j) of a valid neighbor should satisfy
    the following:
        1. i >= 0 and i < H
        2. j >= 0 and j < W
        3. (i, j) != (y, x)

    Args:
        y, x: location of the pixel.
        H, W: size of the image.
    Returns:
        neighbors: list of indices of neighboring pixels [(i, j)].
    """
    neighbors = []

    for i in (y-1, y, y+1):
        for j in (x-1, x, x+1):
            if i >= 0 and i < H and j >= 0 and j < W:
                if (i == y and j == x):
                    continue
                neighbors.append((i, j))

    return neighbors

def link_edges(strong_edges, weak_edges):
    """ Find weak edges connected to strong edges and link them.

    Iterate over each pixel in strong_edges and perform breadth first
    search across the connected pixels in weak_edges to link them.
    Here we consider a pixel (a, b) is connected to a pixel (c, d)
    if (a, b) is one of the eight neighboring pixels of (c, d).

    Args:
        strong_edges: binary image of shape (H, W).
        weak_edges: binary image of shape (H, W).
    
    Returns:
        edges: numpy boolean array of shape(H, W).
    """

    H, W = strong_edges.shape
    indices = np.stack(np.nonzero(strong_edges)).T
    edges = np.zeros((H, W), dtype=bool)

    # Make new instances of arguments to leave the original
    # references intact
    weak_edges = np.copy(weak_edges)
    edges = np.copy(strong_edges)

    ### YOUR CODE HERE
    for y, x in indices:
        for i, j in get_neighbors(y, x, H, W):
            if weak_edges[i, j] and not edges[i, j]:
                visit = [(i, j)]
                edges[i, j] = True
                # using a visit for BFS
                while len(visit) > 0:
                    i1, j1 = visit.pop(0)
                    for a, b in get_neighbors(i1, j1, H, W):
                        if weak_edges[a, b] and not edges[a, b]:
                            edges[a, b] = True
                            visit.append((a, b))
                        
    ### END YOUR CODE

    return edges

def canny(img, kernel_size=5, sigma=1.4, high=20, low=15):
    """ Implement canny edge detector by calling functions above.

    Args:
        img: binary image of shape (H, W).
        kernel_size: int of size for kernel matrix.
        sigma: float for calculating kernel.
        high: high threshold for strong edges.
        low: low threashold for weak edges.
    Returns:
        edge: numpy array of shape(H, W).
    """
    ### YOUR CODE HERE
     # 1 suppress noise
    kernel = gaussian_kernel(kernel_size, sigma)
    smoothed = conv(img, kernel)

    # Compute gradient magnitude and direction
    G, t = gradient(smoothed)

    # Apply Non-Maximum Suppression
    nMS = non_maximum_suppression(G, t)

    # Use hysteresis and connectivity analysis to detect edges
    s_edges, w_edges = double_thresholding(nMS, high, low)
    edge = link_edges(s_edges, w_edges)
    ### END YOUR CODE

    return edge


def hough_transform(img):
    """ Transform points in the input image into Hough space.

    Use the parameterization:
        rho = x * cos(theta) + y * sin(theta)
    to transform a point (x,y) to a sine-like function in Hough space.

    Args:
        img: binary image of shape (H, W).
        
    Returns:
        accumulator: numpy array of shape (m, n).
        rhos: numpy array of shape (m, ).
        thetas: numpy array of shape (n, ).
    """
    # Set rho and theta ranges
    W, H = img.shape
    diag_len = int(np.ceil(np.sqrt(W * W + H * H)))
    rhos = np.linspace(-diag_len, diag_len, diag_len * 2.0 + 1)
    thetas = np.deg2rad(np.arange(-90.0, 90.0))

    # Cache some reusable values
    cos_t = np.cos(thetas)
    sin_t = np.sin(thetas)
    num_thetas = len(thetas)

    # Initialize accumulator in the Hough space
    accumulator = np.zeros((2 * diag_len + 1, num_thetas), dtype=np.uint64)
    ys, xs = np.nonzero(img)

    # Transform each point (x, y) in image
    # Find rho corresponding to values in thetas
    # and increment the accumulator in the corresponding coordinate
    ### YOUR CODE HERE
    
    
    
    
    
    
    ### END YOUR CODE

    return accumulator, rhos, thetas
