import cv2
import numpy as np

# Window size
WIDTH, HEIGHT = 800, 600

# Colors
BACKGROUND_COLOR = (0, 0, 0)
RECTANGLE_COLORS = [
    (255, 180, 130),  # Light Blue
    (130, 255, 180),  # Mint Green
    (180, 130, 255),  # Lavender
    (130, 220, 255)   # Light Orange
]
OUTLINE_COLOR = (255, 255, 255)
VERTEX_COLOR = (0, 165, 255) # Orange
HINT_COLOR = (255, 0, 0) # Blue
VERTEX_RADIUS = 5
DRAG_VERTEX_COLOR = (0, 0, 255) # Red

class Rectangle:
    """Represents a single rectangle with its properties."""
    def __init__(self, center, width, height, color):
        cx, cy = center
        hw = width / 2
        hh = height / 2
        vertices = [
            (cx - hw, cy - hh),
            (cx + hw, cy - hh),
            (cx + hw, cy + hh),
            (cx - hw, cy + hh)
        ]
        self.initial_vertices = np.array(vertices, dtype=np.float32)
        self.color = color

# State variables
rectangles = []
dragged_point_info = None # Will store {'rect_idx': i, 'vertex_idx': j, 'pos': (x, y)}

def initialize_rectangles():
    """
    Initializes the four overlapping rectangles as Rectangle objects.
    """
    global rectangles
    s = 150  # size of the square

    # Define centers of the four rectangles
    center1 = (240, 180)
    center2 = (330, 200)
    center3 = (300, 312)
    center4 = (412, 300)

    centers = [center1, center2, center3, center4]
    print(centers)
    rectangles = [Rectangle(center, s, s, RECTANGLE_COLORS[i]) for i, center in enumerate(centers)]

def mouse_callback(event, x, y, flags, param):
    """Handles mouse events for dragging vertices."""
    global dragged_point_info

    displayed_quads = param['displayed_quads']

    if event == cv2.EVENT_LBUTTONDOWN:
        min_dist = float('inf')
        selected_vertex = None
        for i, quad in enumerate(displayed_quads):
            for j, vertex in enumerate(quad):
                dist = np.linalg.norm(np.array(vertex) - np.array([x, y]))
                if dist < VERTEX_RADIUS * 2 and dist < min_dist:
                    min_dist = dist
                    selected_vertex = {'rect_idx': i, 'vertex_idx': j}

        if selected_vertex:
            dragged_point_info = {
                'rect_idx': selected_vertex['rect_idx'],
                'vertex_idx': selected_vertex['vertex_idx'],
                'pos': (x, y)
            }

    elif event == cv2.EVENT_MOUSEMOVE:
        if dragged_point_info:
            dragged_point_info['pos'] = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        dragged_point_info = None

def main():
    """Main function to run the demo."""
    global dragged_point_info

    initialize_rectangles()

    window_name = "Homography Demo"
    cv2.namedWindow(window_name)

    initial_quads = [rect.initial_vertices for rect in rectangles]

    while True:
        # Create a blank canvas
        canvas = np.full((HEIGHT, WIDTH, 3), BACKGROUND_COLOR, dtype=np.uint8)

        displayed_quads = [np.copy(rect.initial_vertices) for rect in rectangles]

        if dragged_point_info:
            r_idx = dragged_point_info['rect_idx']
            v_idx = dragged_point_info['vertex_idx']
            pos = dragged_point_info['pos']

            src_quad = rectangles[r_idx].initial_vertices
            dst_quad = np.copy(rectangles[r_idx].initial_vertices)
            dst_quad[v_idx] = pos

            try:
                matrix = cv2.getPerspectiveTransform(src_quad, dst_quad)
                all_initial_points = np.concatenate(initial_quads, axis=0)
                transformed_points = cv2.perspectiveTransform(all_initial_points.reshape(-1, 1, 2), matrix)
                transformed_points = transformed_points.reshape(len(rectangles), 4, 2)
                displayed_quads = [transformed_points[i] for i in range(len(rectangles))]
            except cv2.error:
                pass # Ignore collinear points error

        # --- Drawing ---
        # To achieve a true transparency effect where rectangles can be seen through each other,
        # we need to blend each one individually.
        alpha = 0.5  # Set transparency level

        for i, quad in enumerate(displayed_quads):
            # Create a temporary overlay for the current rectangle
            overlay = canvas.copy()
            # Draw the single filled rectangle on the overlay
            cv2.fillPoly(overlay, [quad.astype(np.int32)], rectangles[i].color)
            # Blend the overlay with the main canvas
            cv2.addWeighted(overlay, alpha, canvas, 1 - alpha, 0, canvas)

        # Draw all outlines on top after the fills are blended
        for quad in displayed_quads:
            cv2.polylines(canvas, [quad.astype(np.int32)], isClosed=True, color=OUTLINE_COLOR, thickness=1)

        for i, quad in enumerate(displayed_quads):
            for j, vertex in enumerate(quad):
                color = VERTEX_COLOR  # Default color (Orange)

                if dragged_point_info:
                    dragged_rect_idx = dragged_point_info['rect_idx']
                    dragged_vert_idx = dragged_point_info['vertex_idx']

                    # If the vertex is part of the rectangle being transformed
                    if i == dragged_rect_idx:
                        if j == dragged_vert_idx:
                            # The vertex being dragged is Red
                            color = DRAG_VERTEX_COLOR
                        else:
                            # The other 3 vertices of the same rectangle are Blue
                            color = HINT_COLOR
                
                cv2.circle(canvas, tuple(vertex.astype(np.int32)), VERTEX_RADIUS, color, -1)

        cv2.setMouseCallback(window_name, mouse_callback, {'displayed_quads': displayed_quads})
        cv2.imshow(window_name, canvas)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q') or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()