def cannot_reach_destination(n, m, obstacles):
    max_blocked_column = 0
    seconds = 0

    for i in range(len(obstacles)):
        x, y = obstacles[i]
        max_blocked_column = max(max_blocked_column, y)

        if max_blocked_column >= m:
            break

        seconds += 1

    return seconds

if __name__ == "__main__":
    # 读取输入
    n, m = map(int, input().split())
    obstacles = [tuple(map(int, input().split())) for _ in range((n - 1) * m)]

    # 调用函数得到结果
    result = cannot_reach_destination(n, m, obstacles)

    # 输出结果
    print(result)
