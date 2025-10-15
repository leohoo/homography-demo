import cv2
import numpy as np
import random

# Window size
WIDTH, HEIGHT = 800, 600

# Colors
BACKGROUND_COLOR = (0, 0, 0)
# Rectangle colors are now generated dynamically in initialize_rectangles()
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
    Initializes a grid of overlapping rectangles as Rectangle objects.
    """
    global rectangles

    grid_cols = 6
    grid_rows = 4
    num_rects = grid_cols * grid_rows
    s = 80  # size of the square
    offset = s * 3 // 4 # overlap amount

    # Calculate total grid size to center it on the screen
    grid_width = (grid_cols - 1) * offset + s
    grid_height = (grid_rows - 1) * offset + s
    start_x = (WIDTH - grid_width) // 2
    start_y = (HEIGHT - grid_height) // 2

    hw = s / 2 # half width/height

    centers = []
    for row in range(grid_rows):
        for col in range(grid_cols):
            # Add a slight random offset to break the perfect grid alignment
            rand_offset_x = random.randint(-10, 10)
            rand_offset_y = random.randint(-10, 10)
            center_x = start_x + col * offset + hw + rand_offset_x
            center_y = start_y + row * offset + hw + rand_offset_y
            centers.append((center_x, center_y))

    # Generate a list of distinct colors for each rectangle
    colors = []
    for i in range(num_rects):
        hue = int(i * (180 / num_rects)) # 180 is the hue range in OpenCV
        color_hsv = np.uint8([[[hue, 255, 200]]])
        color_bgr = cv2.cvtColor(color_hsv, cv2.COLOR_HSV2BGR)[0][0]
        colors.append(tuple(map(int, color_bgr)))

    rectangles = [Rectangle(center, s, s, colors[i]) for i, center in enumerate(centers)]

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

            # Highlight the selected rectangle by changing its fill color to white
            fill_color = rectangles[i].color
            if dragged_point_info and dragged_point_info['rect_idx'] == i:
                fill_color = (255, 255, 255)  # White

            # Draw the single filled rectangle on the overlay
            cv2.fillPoly(overlay, [quad.astype(np.int32)], fill_color)
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