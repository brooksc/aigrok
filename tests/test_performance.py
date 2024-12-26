"""
Performance test utilities and benchmarking functions.
"""

import time
import statistics
from typing import List, Callable
from dataclasses import dataclass
from functools import wraps


@dataclass
class PerformanceMetrics:
    """Container for performance test metrics."""

    mean_time: float
    median_time: float
    min_time: float
    max_time: float
    std_dev: float
    samples: List[float]
    percentile_95: float
    percentile_99: float


def measure_performance(
    func: Callable,
    *args,
    warmup_iterations: int = 3,
    test_iterations: int = 10,
    **kwargs,
) -> PerformanceMetrics:
    """
    Measure performance of a function with warmup period and multiple iterations.

    Args:
        func: Function to measure
        warmup_iterations: Number of warmup runs (default: 3)
        test_iterations: Number of test runs (default: 10)
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        PerformanceMetrics with timing statistics
    """
    # Warmup phase
    for _ in range(warmup_iterations):
        func(*args, **kwargs)

    # Test phase
    times: List[float] = []
    for _ in range(test_iterations):
        start_time = time.perf_counter()
        func(*args, **kwargs)
        end_time = time.perf_counter()
        times.append(end_time - start_time)

    # Calculate metrics
    sorted_times = sorted(times)
    return PerformanceMetrics(
        mean_time=statistics.mean(times),
        median_time=statistics.median(times),
        min_time=min(times),
        max_time=max(times),
        std_dev=statistics.stdev(times) if len(times) > 1 else 0,
        samples=times,
        percentile_95=sorted_times[int(0.95 * len(times))],
        percentile_99=sorted_times[int(0.99 * len(times))],
    )


def performance_test(
    baseline_factor: float = 2.0, warmup_iterations: int = 3, test_iterations: int = 10
):
    """
    Decorator for performance tests that compares against a baseline.

    Args:
        baseline_factor: Maximum allowed slowdown factor compared to baseline
        warmup_iterations: Number of warmup runs
        test_iterations: Number of test runs
    """

    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            metrics = measure_performance(
                func,
                *args,
                warmup_iterations=warmup_iterations,
                test_iterations=test_iterations,
                **kwargs,
            )

            # Get baseline from test case if available
            test_case = kwargs.get("test_case", {})
            baseline = test_case.get("baseline_time")

            if baseline:
                # Compare against baseline with allowed factor
                max_allowed = baseline * baseline_factor
                if metrics.percentile_95 > max_allowed:
                    raise AssertionError(
                        f"Performance degraded: p95={metrics.percentile_95:.3f}s > "
                        f"max_allowed={max_allowed:.3f}s (baseline={baseline:.3f}s)"
                    )

            return metrics

        return wrapper

    return decorator


def establish_baseline(
    func: Callable,
    *args,
    warmup_iterations: int = 5,
    test_iterations: int = 20,
    **kwargs,
) -> float:
    """
    Establish a performance baseline for a function.

    Args:
        func: Function to baseline
        warmup_iterations: Number of warmup runs (default: 5)
        test_iterations: Number of test runs (default: 20)
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Baseline execution time (95th percentile)
    """
    metrics = measure_performance(
        func,
        *args,
        warmup_iterations=warmup_iterations,
        test_iterations=test_iterations,
        **kwargs,
    )
    return metrics.percentile_95
