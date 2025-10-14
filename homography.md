# perspective transform matrix
  matrix = cv2.getPerspectiveTransform(src, dst)
  src and dst are 4 corners of quadrilaterals, the matrix maps src to dst.

# the demo app
- generate 4 random rectangles adjacent to each other.
- allow user to grap one corner of a rectangle and move it using mouse
- apply the transform matrix to all the vertices in realtime.
