"""
用 NumPy 模拟 GPU 的分块归约（tiled reduction），演示 grid / block 划分思想。

这个脚本不需要 GPU，纯 CPU 即可运行：
    python3 examples/tiled_reduction.py

它要说明的是：GPU 上求一个大数组的和，不是一个线程从头加到尾，
而是先由每个 block 各自算出局部和，再把这些局部和归约成最终结果。
"""

import numpy as np


def naive_sum(data: np.ndarray) -> float:
    """朴素做法：串行累加。对应 CPU 上的单线程写法。"""
    total = 0.0
    for x in data:
        total += float(x)
    return total


def block_partial_sums(data: np.ndarray, block_size: int) -> np.ndarray:
    """
    第一阶段：每个 block 归约自己负责的那一段，产出局部和。

    对应 GPU 上的一个 kernel：grid 中的每个 block 处理 block_size 个元素，
    块内线程先并行累加、再通过共享内存做块内归约。
    这里用 reshape + sum(axis=1) 表达同一件事。
    """
    n = data.size
    # grid 大小 = 向上取整，最后一个 block 可能不满，需要补零
    grid_size = (n + block_size - 1) // block_size
    padded_len = grid_size * block_size

    padded = np.zeros(padded_len, dtype=data.dtype)
    padded[:n] = data

    # 每一行就是一个 block 负责的数据段
    tiles = padded.reshape(grid_size, block_size)
    return tiles.sum(axis=1)


def tiled_sum(data: np.ndarray, block_size: int = 256) -> float:
    """
    完整的两阶段归约。

    阶段一：grid_size 个 block 并行产出 grid_size 个局部和
    阶段二：把局部和再归约成一个标量
    """
    partials = block_partial_sums(data, block_size)
    return float(partials.sum())


def main() -> None:
    rng = np.random.default_rng(seed=42)
    data = rng.random(100_000, dtype=np.float64)

    block_size = 256
    grid_size = (data.size + block_size - 1) // block_size

    reference = float(data.sum())
    naive = naive_sum(data)
    tiled = tiled_sum(data, block_size)
    partials = block_partial_sums(data, block_size)

    print("=" * 58)
    print("分块归约示例 / Tiled reduction demo")
    print("=" * 58)
    print(f"元素总数 n           : {data.size}")
    print(f"block 大小           : {block_size}")
    print(f"grid 大小 (block 数) : {grid_size}")
    print(f"局部和数组长度       : {partials.size}")
    print(f"补零的元素个数       : {grid_size * block_size - data.size}")
    print("-" * 58)
    print(f"NumPy 参考结果       : {reference:.9f}")
    print(f"串行累加结果         : {naive:.9f}")
    print(f"两阶段分块归约结果   : {tiled:.9f}")
    print("-" * 58)

    # 浮点加法不满足结合律，不同的求和顺序会有微小的舍入差异，
    # 因此这里用容差比较，而不是判断完全相等。
    assert np.isclose(tiled, reference, rtol=1e-12, atol=0.0)
    assert np.isclose(naive, reference, rtol=1e-9, atol=0.0)

    print(f"分块 vs 参考的绝对差 : {abs(tiled - reference):.3e}")
    print(f"串行 vs 参考的绝对差 : {abs(naive - reference):.3e}")
    print("校验通过：三种求和方式在浮点容差范围内一致。")
    print("=" * 58)


if __name__ == "__main__":
    main()
