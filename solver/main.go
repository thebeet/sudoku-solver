package main

import (
	"fmt"

	"github.com/thebeet/sudoku-solver/solver/dlx"
)

func main() {
	s := dlx.NewSudoku(3)
	table, _ := s.Solve()

	for x := 0; x < 9; x++ {
		for y := 0; y < 9; y++ {
			fmt.Printf("%d ", table[x][y])
		}
		fmt.Println()
	}
}
