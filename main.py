import random
from time import sleep
from tkinter import BOTH, Button, Canvas, Tk


class Point:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class Line:
    def __init__(self, start: Point, end: Point):
        self.start = start
        self.end = end

    def draw(self, canvas: Canvas, fill_color: str = "black"):
        canvas.create_line(
            self.start.x, self.start.y, self.end.x, self.end.y, fill=fill_color, width=2
        )
        canvas.pack(fill=BOTH, expand=True)


class Window:
    def __init__(self, width: int, height: int):
        self.__root = Tk()
        self.__root.title("Maze Solver")
        self.__canvas = Canvas(self.__root, width=width, height=height - 50, bg="white")
        self.__canvas.pack(fill=BOTH, expand=True)
        self.__running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)
        self.__button = Button(
            self.__root, text="New Maze", command=self.clear_and_create_new_maze
        )
        self.__button.pack()
        self.__solve_button = Button(self.__root, text="Solve", command=self.solve_maze)
        self.__solve_button.pack()

    def solve_maze(self):
        if self.solve_function:
            solved = self.solve_function()
            print("Solved:", solved)
        else:
            print("No solve function")

    def clear_canvas(self):
        self.__canvas.delete("all")

    def clear_and_create_new_maze(self):
        self.clear_canvas()
        create_new_maze(self)

    def redraw(self):
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self):
        self.__running = True
        while self.__running:
            self.redraw()
        print("Window closed")

    def close(self):
        self.__running = False

    def draw_line(self, line: Line, fill_color: str = "black"):
        line.draw(self.__canvas, fill_color)


class Cell:
    def __init__(
        self,
        win: Window | None = None,
        has_left_wall: bool = True,
        has_top_wall: bool = True,
        has_right_wall: bool = True,
        has_bottom_wall: bool = True,
    ):
        self.has_left_wall = has_left_wall
        self.has_top_wall = has_top_wall
        self.has_right_wall = has_right_wall
        self.has_bottom_wall = has_bottom_wall
        self._x1 = None
        self._y1 = None
        self._x2 = None
        self._y2 = None
        self._win = win
        self.visited = False

    def draw(self, x1: int, y1: int, x2: int, y2: int):
        if self._win is None:
            return
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2
        wall_color = "black"
        no_wall_color = "white"

        if self.has_left_wall:
            self._win.draw_line(Line(Point(x1, y1), Point(x1, y2)), wall_color)
        else:
            self._win.draw_line(Line(Point(x1, y1), Point(x1, y2)), no_wall_color)

        if self.has_top_wall:
            self._win.draw_line(Line(Point(x1, y1), Point(x2, y1)), wall_color)
        else:
            self._win.draw_line(Line(Point(x1, y1), Point(x2, y1)), no_wall_color)

        if self.has_right_wall:
            self._win.draw_line(Line(Point(x2, y1), Point(x2, y2)), wall_color)
        else:
            self._win.draw_line(Line(Point(x2, y1), Point(x2, y2)), no_wall_color)

        if self.has_bottom_wall:
            self._win.draw_line(Line(Point(x1, y2), Point(x2, y2)), wall_color)
        else:
            self._win.draw_line(Line(Point(x1, y2), Point(x2, y2)), no_wall_color)

    def draw_move(self, to_cell, undo=False):
        x_mid = (self._x1 + self._x2) / 2
        y_mid = (self._y1 + self._y2) / 2

        to_x_mid = (to_cell._x1 + to_cell._x2) / 2
        to_y_mid = (to_cell._y1 + to_cell._y2) / 2

        fill_color = "red"
        if undo:
            fill_color = "gray"

        # moving left
        if self._x1 > to_cell._x1:
            line = Line(Point(self._x1, y_mid), Point(x_mid, y_mid))
            self._win.draw_line(line, fill_color)
            line = Line(Point(to_x_mid, to_y_mid), Point(to_cell._x2, to_y_mid))
            self._win.draw_line(line, fill_color)

        # moving right
        elif self._x1 < to_cell._x1:
            line = Line(Point(x_mid, y_mid), Point(self._x2, y_mid))
            self._win.draw_line(line, fill_color)
            line = Line(Point(to_cell._x1, to_y_mid), Point(to_x_mid, to_y_mid))
            self._win.draw_line(line, fill_color)

        # moving up
        elif self._y1 > to_cell._y1:
            line = Line(Point(x_mid, y_mid), Point(x_mid, self._y1))
            self._win.draw_line(line, fill_color)
            line = Line(Point(to_x_mid, to_cell._y2), Point(to_x_mid, to_y_mid))
            self._win.draw_line(line, fill_color)

        # moving down
        elif self._y1 < to_cell._y1:
            line = Line(Point(x_mid, y_mid), Point(x_mid, self._y2))
            self._win.draw_line(line, fill_color)
            line = Line(Point(to_x_mid, to_y_mid), Point(to_x_mid, to_cell._y1))
            self._win.draw_line(line, fill_color)


class Maze:
    def __init__(
        self,
        x1: int,
        y1: int,
        num_rows: int,
        num_cols: int,
        cell_size_x: int,
        cell_size_y: int,
        win: Window | None = None,
        seed: int | None = None,
    ):
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.win = win
        self._cells = []
        if seed is not None:
            random.seed(seed)

        self._create_cells()

    def _create_cells(self):
        for i in range(self.num_cols):
            column = []
            for j in range(self.num_rows):
                cell = Cell(win=self.win)
                column.append(cell)
            self._cells.append(column)

        for i in range(self.num_cols):
            for j in range(self.num_rows):
                self._draw_cell(i, j)

    def _draw_cell(self, i, j):
        if self.win is None:
            return
        x1 = self.x1 + i * self.cell_size_x
        y1 = self.y1 + j * self.cell_size_y
        x2 = x1 + self.cell_size_x
        y2 = y1 + self.cell_size_y
        self._cells[i][j].draw(x1, y1, x2, y2)
        self._animate()

    def _animate(self):
        if self.win is None:
            return
        self.win.redraw()
        sleep(0.001)

    def _break_entrance_and_exit(self):
        top_left_cell = self._cells[0][0]
        top_left_cell.has_top_wall = False
        self._draw_cell(0, 0)

        bottom_right_cell = self._cells[self.num_cols - 1][self.num_rows - 1]
        bottom_right_cell.has_bottom_wall = False
        self._draw_cell(self.num_cols - 1, self.num_rows - 1)

    def _break_walls_r(self, i, j):
        self._cells[i][j].visited = True
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        while True:
            possible_directions = []
            for di, dj in directions:
                ni, nj = i + di, j + dj
                if (
                    0 <= ni < self.num_cols
                    and 0 <= nj < self.num_rows
                    and not self._cells[ni][nj].visited
                ):
                    possible_directions.append((ni, nj))

            if not possible_directions:
                self._draw_cell(i, j)
                return

            ni, nj = random.choice(possible_directions)

            if ni == i - 1:
                self._cells[i][j].has_left_wall = False
                self._cells[ni][nj].has_right_wall = False

            elif ni == i + 1:
                self._cells[i][j].has_right_wall = False
                self._cells[ni][nj].has_left_wall = False

            elif nj == j - 1:
                self._cells[i][j].has_top_wall = False
                self._cells[ni][nj].has_bottom_wall = False

            elif nj == j + 1:
                self._cells[i][j].has_bottom_wall = False
                self._cells[ni][nj].has_top_wall = False

            self._break_walls_r(ni, nj)

    def _reset_cells_visited(self):
        for i in range(self.num_cols):
            for j in range(self.num_rows):
                self._cells[i][j].visited = False

    def solve(self):
        self._reset_cells_visited()
        return self._solve_r(0, 0)

    def _solve_r(self, i, j):
        self._animate()

        # vist the current cell
        self._cells[i][j].visited = True

        # if we are at the end cell, we are done!
        if i == self.num_cols - 1 and j == self.num_rows - 1:
            return True

        # move left if there is no wall and it hasn't been visited
        if (
            i > 0
            and not self._cells[i][j].has_left_wall
            and not self._cells[i - 1][j].visited
        ):
            self._cells[i][j].draw_move(self._cells[i - 1][j])
            if self._solve_r(i - 1, j):
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i - 1][j], True)

        # move right if there is no wall and it hasn't been visited
        if (
            i < self.num_cols - 1
            and not self._cells[i][j].has_right_wall
            and not self._cells[i + 1][j].visited
        ):
            self._cells[i][j].draw_move(self._cells[i + 1][j])
            if self._solve_r(i + 1, j):
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i + 1][j], True)

        # move up if there is no wall and it hasn't been visited
        if (
            j > 0
            and not self._cells[i][j].has_top_wall
            and not self._cells[i][j - 1].visited
        ):
            self._cells[i][j].draw_move(self._cells[i][j - 1])
            if self._solve_r(i, j - 1):
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i][j - 1], True)

        # move down if there is no wall and it hasn't been visited
        if (
            j < self.num_rows - 1
            and not self._cells[i][j].has_bottom_wall
            and not self._cells[i][j + 1].visited
        ):
            self._cells[i][j].draw_move(self._cells[i][j + 1])
            if self._solve_r(i, j + 1):
                return True
            else:
                self._cells[i][j].draw_move(self._cells[i][j + 1], True)

        # we went the wrong way let the previous cell know by returning False
        return False


def create_new_maze(win: Window):
    maze = Maze(50, 50, 15, 15, 35, 35, win)
    maze._break_entrance_and_exit()
    maze._break_walls_r(0, 0)
    maze._reset_cells_visited()
    return maze


def main():
    win = Window(800, 650)
    maze = create_new_maze(win)

    win.solve_function = maze.solve

    win.wait_for_close()


if __name__ == "__main__":
    main()
