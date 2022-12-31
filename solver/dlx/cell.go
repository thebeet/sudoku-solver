package dlx

type Cell struct {
	row, col              int
	left, right, up, down *Cell
}

func NewCell() *Cell {
	c := &Cell{}
	c.left = c
	c.right = c
	c.up = c
	c.down = c
	return c
}

func hideRow(row *Cell) {
	for pointer := row.right; pointer != row; pointer = pointer.right {
		pointer.up.down = pointer.down
		pointer.down.up = pointer.up
	}
}

func showRow(row *Cell) {
	for pointer := row.right; pointer != row; pointer = pointer.right {
		pointer.up.down = pointer
		pointer.down.up = pointer
	}
}

func hideColumn(col *Cell) {
	col.left.right = col.right
	col.right.left = col.left
}

func showColumn(col *Cell) {
	col.left.right = col
	col.right.left = col
}
